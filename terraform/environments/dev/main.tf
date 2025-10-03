# Development Environment Configuration
# TaskManagerAPI on AWS with ECS Fargate - COMPLETELY FIXED VERSION

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Using local backend for testing - no manual configuration needed
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key    = "dev/terraform.tfstate"
  #   region = "us-west-2"
  # }
}

# Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# Local values
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# VPC Module - FIXED: Removed unsupported single_nat_gateway
module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  enable_nat_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = local.common_tags
}

# Security Module
module "security" {
  source = "../../modules/security"

  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.vpc.vpc_id
  private_subnet_cidrs = var.private_subnet_cidrs
  app_port             = var.app_port

  tags = local.common_tags
}

# ALB Module
module "alb" {
  source = "../../modules/alb"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.vpc.vpc_id
  public_subnet_ids          = module.vpc.public_subnet_ids
  alb_security_group_id      = module.security.alb_security_group_id
  app_port                   = var.app_port
  certificate_arn            = var.certificate_arn
  enable_deletion_protection = var.enable_deletion_protection
  enable_access_logs         = var.enable_access_logs
  log_retention_days         = var.log_retention_days

  tags = local.common_tags
}

# ECS Module - FIXED: Using correct argument names
module "ecs" {
  source = "../../modules/ecs"

  project_name                = var.project_name
  environment                 = var.environment
  container_image             = var.container_image
  app_port                    = var.app_port
  cpu                         = var.ecs_cpu
  memory                      = var.ecs_memory
  desired_count               = var.ecs_desired_count
  private_subnet_ids          = module.vpc.private_subnet_ids
  ecs_tasks_security_group_id = module.security.ecs_tasks_security_group_id
  ecs_task_execution_role_arn = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn           = module.security.ecs_task_role_arn
  target_group_arn            = module.alb.target_group_arn
  environment_variables = var.enable_rds ? concat(var.environment_variables, [
    {
      name  = "DB_HOST"
      value = module.rds[0].db_instance_address
    },
    {
      name  = "DB_NAME"
      value = module.rds[0].db_instance_name
    },
    {
      name  = "DB_USER"
      value = module.rds[0].db_instance_username
    },
    {
      name  = "DB_PORT"
      value = tostring(module.rds[0].db_instance_port)
    }
  ]) : var.environment_variables
  secrets = var.enable_rds ? [
    {
      name      = "DB_PASSWORD"
      valueFrom = module.rds[0].db_instance_password_secret_arn
    }
  ] : []
  enable_container_insights = var.enable_container_insights
  log_retention_days        = var.log_retention_days
  enable_autoscaling        = var.enable_autoscaling
  min_capacity              = var.ecs_min_capacity
  max_capacity              = var.ecs_max_capacity

  tags = local.common_tags
}

# RDS Module (Optional for dev) - FIXED: Using correct variable names
module "rds" {
  count = var.enable_rds ? 1 : 0

  source = "../../modules/rds"

  project_name            = var.project_name
  environment             = var.environment
  private_subnet_ids      = module.vpc.private_subnet_ids
  rds_security_group_id   = module.security.rds_security_group_id
  db_name                 = var.db_name
  db_username             = var.db_username
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  backup_retention_period = var.db_backup_retention_period
  multi_az                = var.db_multi_az
  deletion_protection     = var.db_deletion_protection
  skip_final_snapshot     = var.db_skip_final_snapshot

  tags = local.common_tags
}

# CloudWatch Dashboard - FIXED: Removed unsupported tags
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", module.alb.alb_arn_suffix],
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", module.alb.alb_arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_Target_2XX_Count", "LoadBalancer", module.alb.alb_arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_Target_4XX_Count", "LoadBalancer", module.alb.alb_arn_suffix],
            ["AWS/ApplicationELB", "HTTPCode_Target_5XX_Count", "LoadBalancer", module.alb.alb_arn_suffix]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "Application Load Balancer Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", module.ecs.ecs_service_name, "ClusterName", module.ecs.ecs_cluster_name],
            ["AWS/ECS", "MemoryUtilization", "ServiceName", module.ecs.ecs_service_name, "ClusterName", module.ecs.ecs_cluster_name]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "ECS Service Metrics"
          period  = 300
        }
      }
    ]
  })
}