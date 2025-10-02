# Auto-Configured Development Environment
# All names and paths are auto-generated - no manual input needed!

# Project Configuration
project_name = "taskmanager"
environment  = "dev"
aws_region   = "us-west-2"

# VPC Configuration
vpc_cidr = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs = ["10.0.10.0/24", "10.0.20.0/24"]

# Application Configuration
app_port        = 5125
container_image = "aribdev/taskmanager:v3.0"

# ALB Configuration
certificate_arn = ""  # Leave empty for HTTP only, or provide SSL certificate ARN
enable_deletion_protection = false
enable_access_logs = true
log_retention_days = 7

# ECS Configuration
ecs_cpu             = 512
ecs_memory          = 1024
ecs_desired_count   = 1
ecs_min_capacity    = 1
ecs_max_capacity    = 3
enable_autoscaling  = true
enable_container_insights = true

# Database Configuration (optional for dev)
enable_rds = false
db_name    = "taskmanager"
db_username = "taskmanager"
db_instance_class = "db.t3.micro"
db_allocated_storage = 20
db_backup_retention_period = 7
db_multi_az = false
db_deletion_protection = false
db_skip_final_snapshot = true

# Environment Variables
environment_variables = [
  {
    name  = "FLASK_ENV"
    value = "development"
  },
  {
    name  = "PYTHONUNBUFFERED"
    value = "1"
  }
]

# DNS Configuration (optional)
domain_name = ""
route53_zone_id = ""

# Tags
tags = {
  Owner       = "DevOps Team"
  CostCenter  = "Engineering"
  Environment = "Development"
}
