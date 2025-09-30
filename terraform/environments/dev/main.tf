# Development Environment Configuration
# TaskManagerAPI on AWS with ECS Fargate

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

  backend "s3" {
    # Configure backend in terraform.tfvars or via environment variables
    # bucket = "your-terraform-state-bucket"
    # key    = "dev/terraform.tfstate"
    # region = "us-west-2"
  }
}

# Provider configuration
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "terraform"
    }
  }
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

# VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name = var.project_name
  environment  = var.environment
  vpc_cidr     = var.vpc_cidr

  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs

  enable_nat_gateway = var.enable_nat_gateway
  enable_vpn_gateway = var.enable_vpn_gateway

  tags = var.tags
}

# Security Module
module "security" {
  source = "../../modules/security"

  project_name = var.project_name
  environment  = var.environment

  vpc_id                = module.vpc.vpc_id
  private_subnet_cidrs  = module.vpc.private_subnet_cidrs
  app_port              = var.app_port

  tags = var.tags
}

# ALB Module
module "alb" {
  source = "../../modules/alb"

  project_name = var.project_name
  environment  = var.environment

  vpc_id                = module.vpc.vpc_id
  public_subnet_ids     = module.vpc.public_subnet_ids
  alb_security_group_id = module.security.alb_security_group_id

  app_port              = var.app_port
  certificate_arn       = var.certificate_arn
  enable_deletion_protection = var.enable_deletion_protection
  enable_access_logs    = var.enable_access_logs
  log_retention_days    = var.log_retention_days

  tags = var.tags
}

# RDS Module (optional for development)
module "rds" {
  count = var.enable_rds ? 1 : 0

  source = "../../modules/rds"

  project_name = var.project_name
  environment  = var.environment

  private_subnet_ids     = module.vpc.private_subnet_ids
  rds_security_group_id  = module.security.rds_security_group_id

  db_name                = var.db_name
  db_username            = var.db_username
  engine_version         = var.db_engine_version
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  max_allocated_storage  = var.db_max_allocated_storage
  backup_retention_period = var.db_backup_retention_period
  multi_az               = var.db_multi_az
  deletion_protection    = var.db_deletion_protection
  skip_final_snapshot    = var.db_skip_final_snapshot
  performance_insights_enabled = var.db_performance_insights_enabled
  enable_cloudwatch_logs = var.db_enable_cloudwatch_logs
  log_retention_days     = var.log_retention_days

  tags = var.tags
}

# ECS Module
module "ecs" {
  source = "../../modules/ecs"

  project_name = var.project_name
  environment  = var.environment

  container_image = var.container_image
  app_port        = var.app_port
  cpu             = var.ecs_cpu
  memory          = var.ecs_memory
  desired_count   = var.ecs_desired_count

  private_subnet_ids              = module.vpc.private_subnet_ids
  ecs_tasks_security_group_id     = module.security.ecs_tasks_security_group_id
  ecs_task_execution_role_arn     = module.security.ecs_task_execution_role_arn
  ecs_task_role_arn               = module.security.ecs_task_role_arn
  target_group_arn                = module.alb.target_group_arn

  environment_variables = var.environment_variables
  secrets = var.enable_rds ? [
    {
      name      = "DATABASE_URL"
      valueFrom = "arn:aws:secretsmanager:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:secret:${var.project_name}-db-password"
    }
  ] : []

  enable_container_insights = var.enable_container_insights
  log_retention_days        = var.log_retention_days
  enable_autoscaling        = var.enable_autoscaling
  min_capacity              = var.ecs_min_capacity
  max_capacity              = var.ecs_max_capacity
  cpu_target_value          = var.ecs_cpu_target_value
  memory_target_value       = var.ecs_memory_target_value

  tags = var.tags
}

# Route 53 Record (optional)
resource "aws_route53_record" "app" {
  count = var.domain_name != "" ? 1 : 0

  zone_id = var.route53_zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = module.alb.alb_dns_name
    zone_id                = module.alb.alb_zone_id
    evaluate_target_health = true
  }
}

# CloudWatch Dashboard
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
            ["AWS/ECS", "CPUUtilization", "ServiceName", module.ecs.service_name, "ClusterName", module.ecs.cluster_name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "ECS Service Metrics"
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
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", module.alb.alb_arn_suffix],
            [".", "RequestCount", ".", "."],
            [".", "HTTPCode_Target_2XX_Count", ".", "."],
            [".", "HTTPCode_Target_4XX_Count", ".", "."],
            [".", "HTTPCode_Target_5XX_Count", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = data.aws_region.current.name
          title   = "ALB Metrics"
          period  = 300
        }
      }
    ]
  })
}
