#!/bin/bash

# Test CI/CD Pipeline Locally
# This script simulates what the GitHub Actions will do

set -e

echo "🚀 Testing CI/CD Pipeline Locally"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Step 1: Run tests
echo ""
echo "📋 Step 1: Running Tests"
echo "------------------------"
if python3 -m pytest tests/ -v; then
    print_status "Tests passed"
else
    print_error "Tests failed"
    exit 1
fi

# Step 2: Build Docker image
echo ""
echo "🐳 Step 2: Building Docker Image"
echo "--------------------------------"
if docker build --platform linux/amd64 -t aribdev/taskmanager:test .; then
    print_status "Docker image built successfully"
else
    print_error "Docker build failed"
    exit 1
fi

# Step 3: Test Docker image locally
echo ""
echo "🧪 Step 3: Testing Docker Image"
echo "-------------------------------"
docker run -d -p 5126:5125 --name test-cicd aribdev/taskmanager:test
sleep 10

if curl -f http://localhost:5126/health; then
    print_status "Docker image test passed"
else
    print_error "Docker image test failed"
    docker stop test-cicd
    docker rm test-cicd
    exit 1
fi

docker stop test-cicd
docker rm test-cicd

# Step 4: Check if ready for deployment
echo ""
echo "🔍 Step 4: Pre-deployment Checks"
echo "-------------------------------"

# Check if Docker Hub credentials are available
if docker login --username aribdev --password-stdin <<< "$DOCKER_PASSWORD" 2>/dev/null; then
    print_status "Docker Hub credentials available"
else
    print_warning "Docker Hub credentials not set (DOCKER_PASSWORD env var)"
fi

# Check if AWS credentials are available
if aws sts get-caller-identity &>/dev/null; then
    print_status "AWS credentials available"
else
    print_warning "AWS credentials not configured"
fi

# Check if Terraform is available
if terraform version &>/dev/null; then
    print_status "Terraform is available"
else
    print_warning "Terraform not installed"
fi

echo ""
echo "🎉 Local CI/CD Test Complete!"
echo "============================="
echo ""
echo "Next steps:"
echo "1. Set up GitHub Secrets (see .github/SETUP_SECRETS.md)"
echo "2. Push your changes to main branch"
echo "3. Watch the deployment in GitHub Actions"
echo ""
echo "Your app will be automatically deployed to:"
echo "http://taskmanager-alb-13296148.us-west-2.elb.amazonaws.com/"
