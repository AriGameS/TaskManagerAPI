# TaskManagerAPI Infrastructure as Code

This directory contains Terraform configurations for deploying TaskManagerAPI on AWS with a complete, production-ready infrastructure.

## 🏗️ Architecture

The infrastructure includes:

- **VPC** with public and private subnets across multiple AZs
- **Application Load Balancer** with SSL termination
- **ECS Fargate** for containerized application hosting
- **RDS PostgreSQL** for data persistence
- **CloudWatch** for monitoring and logging
- **Auto Scaling** for high availability
- **Security Groups** and **IAM roles** for secure access

## 📁 Directory Structure

```
terraform/
├── modules/                    # Reusable Terraform modules
│   ├── vpc/                   # VPC with subnets, IGW, NAT
│   ├── security/              # Security groups and IAM roles
│   ├── alb/                   # Application Load Balancer
│   ├── ecs/                   # ECS cluster, service, tasks
│   └── rds/                   # RDS PostgreSQL database
├── environments/              # Environment-specific configurations
│   ├── dev/                   # Development environment
│   └── prod/                  # Production environment
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **Docker** for building application images
4. **AWS Account** with appropriate permissions

### 1. Development Environment

```bash
# Navigate to dev environment
cd terraform/environments/dev

# Copy and customize configuration
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

### 2. Production Environment

```bash
# Navigate to prod environment
cd terraform/environments/prod

# Copy and customize configuration
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with production values

# Initialize and deploy
terraform init
terraform plan
terraform apply
```

### 3. Using the Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy-terraform.sh

# Deploy development environment
./scripts/deploy-terraform.sh dev apply

# Deploy production environment
./scripts/deploy-terraform.sh prod apply
```

## 🔧 Configuration

### Key Variables

| Variable | Description | Dev Default | Prod Default |
|----------|-------------|-------------|--------------|
| `project_name` | Project identifier | `taskmanager` | `taskmanager` |
| `environment` | Environment name | `dev` | `prod` |
| `aws_region` | AWS region | `us-west-2` | `us-west-2` |
| `container_image` | Docker image URI | `taskmanager:latest` | `taskmanager:latest` |
| `certificate_arn` | SSL certificate ARN | `""` | Required |
| `ecs_cpu` | ECS task CPU | `512` | `1024` |
| `ecs_memory` | ECS task memory | `1024` | `2048` |
| `ecs_desired_count` | Desired tasks | `1` | `3` |

### Environment-Specific Settings

#### Development
- Single AZ deployment
- Smaller instance types
- No Multi-AZ RDS
- Reduced backup retention
- HTTP only (no SSL)

#### Production
- Multi-AZ deployment
- Larger instance types
- Multi-AZ RDS
- Extended backup retention
- HTTPS with SSL certificate
- CloudWatch alarms
- SNS notifications

## 📊 Monitoring

### CloudWatch Dashboard
Automatically created dashboard includes:
- ECS service metrics (CPU, Memory)
- ALB metrics (Response time, Request count)
- RDS metrics (CPU, Connections, Memory)

### Alarms (Production Only)
- High CPU utilization (>80%)
- High memory utilization (>85%)
- High response time (>2 seconds)

### Logs
- ECS application logs in CloudWatch
- ALB access logs in S3
- RDS logs in CloudWatch

## 🔒 Security

### Network Security
- Private subnets for application and database
- Security groups with least privilege
- VPC endpoints for AWS services

### Data Security
- RDS encryption at rest
- Secrets Manager for credentials
- SSL/TLS termination at ALB

### Access Control
- IAM roles with minimal permissions
- No hardcoded credentials
- Resource-based policies

## 💰 Cost Optimization

### Development
- Single AZ deployment
- Smaller instance types
- Reduced backup retention
- No Multi-AZ RDS

### Production
- Multi-AZ for high availability
- Auto scaling for efficiency
- Reserved instances for predictable workloads
- S3 lifecycle policies

## 🔄 CI/CD Integration

### GitHub Actions
The repository includes a GitHub Actions workflow for:
- Terraform plan on pull requests
- Terraform apply on main branch
- Security scanning with TFSec and Checkov
- Cost estimation with Infracost

### Manual Deployment
```bash
# Plan deployment
./scripts/deploy-terraform.sh dev plan

# Apply changes
./scripts/deploy-terraform.sh dev apply

# Destroy infrastructure
./scripts/deploy-terraform.sh dev destroy
```

## 🛠️ Modules

### VPC Module
Creates a VPC with:
- Public subnets with Internet Gateway
- Private subnets with NAT Gateways
- VPC endpoints for S3 and ECR
- Route tables and associations

### Security Module
Creates:
- Security groups for ALB, ECS, RDS
- IAM roles for ECS execution and tasks
- Policies for CloudWatch and Secrets Manager

### ALB Module
Creates:
- Application Load Balancer
- Target group with health checks
- HTTP to HTTPS redirect
- SSL/TLS termination
- Access logging to S3

### ECS Module
Creates:
- ECS Fargate cluster
- Task definition with container config
- ECS service with load balancer
- Auto scaling policies
- CloudWatch logging

### RDS Module
Creates:
- RDS PostgreSQL instance
- Multi-AZ deployment (production)
- Automated backups
- Performance Insights
- Secrets Manager integration

## 🚨 Troubleshooting

### Common Issues

1. **Terraform State Lock**
   ```bash
   terraform force-unlock <lock-id>
   ```

2. **ECS Service Not Starting**
   ```bash
   aws ecs describe-services --cluster taskmanager-cluster --services taskmanager-service
   ```

3. **ALB Health Check Failures**
   ```bash
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   ```

4. **RDS Connection Issues**
   ```bash
   aws rds describe-db-instances --db-instance-identifier taskmanager-db
   ```

### Useful Commands

```bash
# View all resources
terraform state list

# Refresh state
terraform refresh

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0

# Output specific values
terraform output alb_dns_name
```

## 📚 Documentation

- [Terraform Guide](../TERRAFORM_GUIDE.md) - Comprehensive deployment guide
- [Docker Guide](../DOCKER_GUIDE.md) - Container configuration
- [CI/CD Guide](../GITHUB_ACTIONS_PRESENTATION.md) - Pipeline documentation

## 🤝 Contributing

1. Make changes to Terraform configurations
2. Test with `terraform plan`
3. Create pull request
4. Review and merge

## 📞 Support

For issues and questions:
- Check AWS CloudWatch logs
- Review Terraform documentation
- Consult AWS support
- Check GitHub issues

---

This infrastructure provides a production-ready, scalable, and secure deployment for TaskManagerAPI on AWS.
