# Terraform Infrastructure as Code Guide

## Overview

This guide explains the Terraform infrastructure setup for TaskManagerAPI, providing a complete AWS deployment solution with ECS Fargate, RDS PostgreSQL, and Application Load Balancer.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                           │
│                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Route 53      │    │        CloudWatch               │ │
│  │   (DNS)         │    │     (Monitoring & Logs)         │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Application Load Balancer                  │ │
│  │                   (ALB)                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                ECS Fargate Cluster                      │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │ │
│  │  │   Task 1    │ │   Task 2    │ │   Task 3    │      │ │
│  │  │ TaskManager │ │ TaskManager │ │ TaskManager │      │ │
│  │  └─────────────┘ └─────────────┘ └─────────────┘      │ │
│  └─────────────────────────────────────────────────────────┘ │
│           │                                               │
│           ▼                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              RDS PostgreSQL                             │ │
│  │              (Multi-AZ in Prod)                         │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    VPC                                  │ │
│  │  ┌─────────────┐              ┌─────────────┐          │ │
│  │  │   Public    │              │   Private   │          │ │
│  │  │  Subnets    │              │   Subnets   │          │ │
│  │  │             │              │             │          │ │
│  │  │    ALB      │              │   ECS + RDS │          │ │
│  │  └─────────────┘              └─────────────┘          │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
terraform/
├── modules/
│   ├── vpc/                 # VPC with public/private subnets
│   ├── security/            # Security groups and IAM roles
│   ├── alb/                 # Application Load Balancer
│   ├── ecs/                 # ECS cluster, service, and task definition
│   └── rds/                 # RDS PostgreSQL database
├── environments/
│   ├── dev/                 # Development environment
│   └── prod/                # Production environment
└── README.md
```

## Prerequisites

### 1. AWS CLI Configuration
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

### 2. Terraform Installation
```bash
# Install Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### 3. Docker Image Preparation
```bash
# Build and push your Docker image to ECR
aws ecr create-repository --repository-name taskmanager
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
docker build -t taskmanager .
docker tag taskmanager:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/taskmanager:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/taskmanager:latest
```

## Quick Start

### 1. Development Environment

```bash
# Navigate to dev environment
cd terraform/environments/dev

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration
nano terraform.tfvars

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

### 2. Production Environment

```bash
# Navigate to prod environment
cd terraform/environments/prod

# Copy example configuration
cp terraform.tfvars.example terraform.tfvars

# Edit configuration with production values
nano terraform.tfvars

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Deploy infrastructure
terraform apply
```

## Configuration

### Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `project_name` | Name of the project | `taskmanager` | `taskmanager` |
| `environment` | Environment name | `dev` | `prod` |
| `aws_region` | AWS region | `us-west-2` | `us-east-1` |
| `container_image` | Docker image URI | `taskmanager:latest` | `123456789012.dkr.ecr.us-west-2.amazonaws.com/taskmanager:latest` |
| `certificate_arn` | SSL certificate ARN | `""` | `arn:aws:acm:us-west-2:123456789012:certificate/12345678-1234-1234-1234-123456789012` |

### VPC Configuration

| Variable | Description | Default | Production |
|----------|-------------|---------|------------|
| `vpc_cidr` | VPC CIDR block | `10.0.0.0/16` | `10.0.0.0/16` |
| `public_subnet_cidrs` | Public subnet CIDRs | `["10.0.1.0/24", "10.0.2.0/24"]` | `["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]` |
| `private_subnet_cidrs` | Private subnet CIDRs | `["10.0.10.0/24", "10.0.20.0/24"]` | `["10.0.10.0/24", "10.0.20.0/24", "10.0.30.0/24"]` |

### ECS Configuration

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `ecs_cpu` | CPU units | `512` | `1024` |
| `ecs_memory` | Memory in MB | `1024` | `2048` |
| `ecs_desired_count` | Desired tasks | `1` | `3` |
| `ecs_min_capacity` | Min tasks | `1` | `2` |
| `ecs_max_capacity` | Max tasks | `3` | `20` |

### RDS Configuration

| Variable | Description | Development | Production |
|----------|-------------|-------------|------------|
| `db_instance_class` | Instance type | `db.t3.micro` | `db.t3.small` |
| `db_allocated_storage` | Storage in GB | `20` | `100` |
| `db_multi_az` | Multi-AZ deployment | `false` | `true` |
| `db_backup_retention_period` | Backup retention days | `7` | `30` |

## Modules

### 1. VPC Module (`modules/vpc/`)

**Purpose**: Creates a VPC with public and private subnets across multiple availability zones.

**Features**:
- VPC with DNS support
- Public subnets with Internet Gateway
- Private subnets with NAT Gateways
- VPC endpoints for S3 and ECR
- Route tables and associations

**Key Resources**:
- `aws_vpc`
- `aws_internet_gateway`
- `aws_nat_gateway`
- `aws_subnet`
- `aws_route_table`

### 2. Security Module (`modules/security/`)

**Purpose**: Creates security groups and IAM roles for secure access.

**Features**:
- ALB security group (HTTP/HTTPS)
- ECS tasks security group
- RDS security group
- Redis security group (if needed)
- IAM roles for ECS execution and tasks

**Key Resources**:
- `aws_security_group`
- `aws_iam_role`
- `aws_iam_role_policy`

### 3. ALB Module (`modules/alb/`)

**Purpose**: Creates Application Load Balancer with target groups and listeners.

**Features**:
- Application Load Balancer
- Target group with health checks
- HTTP to HTTPS redirect
- SSL/TLS termination
- Access logging to S3

**Key Resources**:
- `aws_lb`
- `aws_lb_target_group`
- `aws_lb_listener`
- `aws_s3_bucket` (for logs)

### 4. ECS Module (`modules/ecs/`)

**Purpose**: Creates ECS cluster, service, and task definition.

**Features**:
- ECS Fargate cluster
- Task definition with container configuration
- ECS service with load balancer integration
- Auto scaling policies
- CloudWatch logging

**Key Resources**:
- `aws_ecs_cluster`
- `aws_ecs_task_definition`
- `aws_ecs_service`
- `aws_appautoscaling_target`

### 5. RDS Module (`modules/rds/`)

**Purpose**: Creates PostgreSQL database with high availability.

**Features**:
- RDS PostgreSQL instance
- Multi-AZ deployment (production)
- Automated backups
- Performance Insights
- Secrets Manager integration
- CloudWatch logging

**Key Resources**:
- `aws_db_instance`
- `aws_db_subnet_group`
- `aws_db_parameter_group`
- `aws_secretsmanager_secret`

## Deployment Workflow

### 1. Initial Setup

```bash
# Create S3 bucket for Terraform state
aws s3 mb s3://your-terraform-state-bucket

# Create DynamoDB table for state locking
aws dynamodb create-table \
    --table-name terraform-state-lock \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### 2. Environment-Specific Deployment

```bash
# Development
cd terraform/environments/dev
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=dev/terraform.tfstate" \
               -backend-config="region=us-west-2" \
               -backend-config="dynamodb_table=terraform-state-lock"
terraform plan
terraform apply

# Production
cd terraform/environments/prod
terraform init -backend-config="bucket=your-terraform-state-bucket" \
               -backend-config="key=prod/terraform.tfstate" \
               -backend-config="region=us-west-2" \
               -backend-config="dynamodb_table=terraform-state-lock"
terraform plan
terraform apply
```

### 3. CI/CD Integration

```yaml
# .github/workflows/terraform-deploy.yml
name: Terraform Deploy
on:
  push:
    branches: [main]
    paths: ['terraform/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      
      - name: Terraform Init
        run: terraform init
        working-directory: terraform/environments/prod
        
      - name: Terraform Plan
        run: terraform plan
        working-directory: terraform/environments/prod
        
      - name: Terraform Apply
        run: terraform apply -auto-approve
        working-directory: terraform/environments/prod
```

## Monitoring and Observability

### 1. CloudWatch Dashboard

The infrastructure automatically creates a CloudWatch dashboard with:
- ECS service metrics (CPU, Memory)
- ALB metrics (Response time, Request count, Error rates)
- RDS metrics (CPU, Connections, Memory)

### 2. CloudWatch Alarms

Production environment includes alarms for:
- High CPU utilization (>80%)
- High memory utilization (>85%)
- High response time (>2 seconds)

### 3. SNS Notifications

Alerts are sent to configured email addresses via SNS topics.

## Security Best Practices

### 1. Network Security
- Private subnets for application and database
- Security groups with least privilege access
- VPC endpoints for AWS services

### 2. Data Security
- RDS encryption at rest
- Secrets Manager for database credentials
- SSL/TLS termination at ALB

### 3. Access Control
- IAM roles with minimal permissions
- No hardcoded credentials
- Resource-based policies

## Cost Optimization

### 1. Development Environment
- Single AZ deployment
- Smaller instance types
- Reduced backup retention
- No Multi-AZ RDS

### 2. Production Environment
- Multi-AZ for high availability
- Auto scaling for cost efficiency
- Reserved instances for predictable workloads
- S3 lifecycle policies for logs

## Troubleshooting

### Common Issues

1. **Terraform State Lock**
   ```bash
   terraform force-unlock <lock-id>
   ```

2. **ECS Service Not Starting**
   ```bash
   # Check ECS service events
   aws ecs describe-services --cluster taskmanager-cluster --services taskmanager-service
   
   # Check task definition
   aws ecs describe-task-definition --task-definition taskmanager-task
   ```

3. **ALB Health Check Failures**
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   ```

4. **RDS Connection Issues**
   ```bash
   # Check security groups
   aws ec2 describe-security-groups --group-ids <security-group-id>
   
   # Check RDS status
   aws rds describe-db-instances --db-instance-identifier taskmanager-db
   ```

### Useful Commands

```bash
# View all resources
terraform state list

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0

# Refresh state
terraform refresh

# Destroy infrastructure
terraform destroy

# Output specific values
terraform output alb_dns_name
```

## Best Practices

### 1. State Management
- Use remote state with S3 backend
- Enable state locking with DynamoDB
- Separate state files per environment

### 2. Code Organization
- Use modules for reusability
- Separate environments
- Version control all configurations

### 3. Security
- Never commit sensitive data
- Use variables and secrets
- Regular security audits

### 4. Monitoring
- Enable CloudWatch Container Insights
- Set up comprehensive alerting
- Monitor costs and usage

## Next Steps

1. **Secrets Management**: Integrate with AWS Secrets Manager
2. **Kubernetes**: Consider EKS for advanced orchestration
3. **CI/CD**: Implement automated deployment pipelines
4. **Monitoring**: Add APM tools like DataDog or New Relic
5. **Backup**: Implement automated backup strategies

## Support

For issues and questions:
- Check AWS CloudWatch logs
- Review Terraform documentation
- Consult AWS support
- Check GitHub issues

---

This infrastructure provides a production-ready, scalable, and secure deployment for TaskManagerAPI on AWS.
