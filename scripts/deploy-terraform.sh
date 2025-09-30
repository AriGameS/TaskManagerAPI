#!/bin/bash

# Terraform Deployment Script for TaskManagerAPI
# Usage: ./deploy-terraform.sh [dev|prod] [plan|apply|destroy]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install Terraform first."
        exit 1
    fi
    
    # Check if aws cli is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Please run 'aws configure' first."
        exit 1
    fi
    
    print_success "All prerequisites met!"
}

# Function to build and push Docker image
build_and_push_image() {
    local environment=$1
    local aws_region=$2
    local account_id=$3
    
    print_status "Building and pushing Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $account_id.dkr.ecr.$aws_region.amazonaws.com
    
    # Build image
    docker build -t taskmanager .
    
    # Tag image
    docker tag taskmanager:latest $account_id.dkr.ecr.$aws_region.amazonaws.com/taskmanager:latest
    docker tag taskmanager:latest $account_id.dkr.ecr.$aws_region.amazonaws.com/taskmanager:$environment-$(date +%Y%m%d-%H%M%S)
    
    # Push image
    docker push $account_id.dkr.ecr.$aws_region.amazonaws.com/taskmanager:latest
    docker push $account_id.dkr.ecr.$aws_region.amazonaws.com/taskmanager:$environment-$(date +%Y%m%d-%H%M%S)
    
    print_success "Docker image built and pushed successfully!"
}

# Function to create ECR repository if it doesn't exist
create_ecr_repository() {
    local aws_region=$1
    
    print_status "Checking ECR repository..."
    
    if ! aws ecr describe-repositories --repository-names taskmanager --region $aws_region &> /dev/null; then
        print_status "Creating ECR repository..."
        aws ecr create-repository --repository-name taskmanager --region $aws_region
        print_success "ECR repository created!"
    else
        print_success "ECR repository already exists!"
    fi
}

# Function to deploy infrastructure
deploy_infrastructure() {
    local environment=$1
    local action=$2
    
    print_status "Deploying infrastructure for $environment environment..."
    
    # Navigate to environment directory
    cd terraform/environments/$environment
    
    # Check if terraform.tfvars exists
    if [ ! -f "terraform.tfvars" ]; then
        print_warning "terraform.tfvars not found. Copying from example..."
        cp terraform.tfvars.example terraform.tfvars
        print_warning "Please edit terraform.tfvars with your configuration before proceeding."
        exit 1
    fi
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Validate configuration
    print_status "Validating Terraform configuration..."
    terraform validate
    
    # Plan or apply
    if [ "$action" = "plan" ]; then
        print_status "Planning Terraform deployment..."
        terraform plan
    elif [ "$action" = "apply" ]; then
        print_status "Applying Terraform configuration..."
        terraform apply -auto-approve
        
        # Get outputs
        print_success "Deployment completed! Getting outputs..."
        echo ""
        echo "=== DEPLOYMENT OUTPUTS ==="
        terraform output
        echo ""
        
        # Get application URL
        if [ "$environment" = "prod" ]; then
            app_url=$(terraform output -raw application_url)
        else
            alb_dns=$(terraform output -raw alb_dns_name)
            app_url="http://$alb_dns"
        fi
        
        print_success "Application URL: $app_url"
        
    elif [ "$action" = "destroy" ]; then
        print_warning "This will destroy all infrastructure in $environment environment!"
        read -p "Are you sure? (yes/no): " confirm
        if [ "$confirm" = "yes" ]; then
            print_status "Destroying infrastructure..."
            terraform destroy -auto-approve
            print_success "Infrastructure destroyed!"
        else
            print_status "Destruction cancelled."
        fi
    else
        print_error "Invalid action: $action. Use 'plan', 'apply', or 'destroy'."
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments:"
    echo "  dev   - Development environment"
    echo "  prod  - Production environment"
    echo ""
    echo "Actions:"
    echo "  plan   - Plan the deployment"
    echo "  apply  - Apply the configuration"
    echo "  destroy - Destroy the infrastructure"
    echo ""
    echo "Examples:"
    echo "  $0 dev plan"
    echo "  $0 prod apply"
    echo "  $0 dev destroy"
}

# Main script
main() {
    # Check arguments
    if [ $# -ne 2 ]; then
        show_usage
        exit 1
    fi
    
    local environment=$1
    local action=$2
    
    # Validate environment
    if [ "$environment" != "dev" ] && [ "$environment" != "prod" ]; then
        print_error "Invalid environment: $environment. Use 'dev' or 'prod'."
        exit 1
    fi
    
    # Validate action
    if [ "$action" != "plan" ] && [ "$action" != "apply" ] && [ "$action" != "destroy" ]; then
        print_error "Invalid action: $action. Use 'plan', 'apply', or 'destroy'."
        exit 1
    fi
    
    print_status "Starting deployment for $environment environment with action: $action"
    
    # Check prerequisites
    check_prerequisites
    
    # Get AWS account info
    local aws_region=$(aws configure get region)
    local account_id=$(aws sts get-caller-identity --query Account --output text)
    
    print_status "AWS Region: $aws_region"
    print_status "AWS Account ID: $account_id"
    
    # Create ECR repository if needed
    if [ "$action" = "apply" ]; then
        create_ecr_repository $aws_region
        build_and_push_image $environment $aws_region $account_id
    fi
    
    # Deploy infrastructure
    deploy_infrastructure $environment $action
    
    print_success "Deployment script completed!"
}

# Run main function
main "$@"
