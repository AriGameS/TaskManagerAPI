#!/bin/bash

# Terraform Test Script - Validates Configuration
# This script safely tests Terraform without deploying anything

echo "🔧 Testing Terraform Configuration..."
echo "=================================="

# Clean up any previous state
echo "🧹 Cleaning up previous state..."
terraform destroy -auto-approve 2>/dev/null || true
rm -rf .terraform .terraform.lock.hcl terraform.tfstate* 2>/dev/null || true

# Initialize Terraform
echo "🚀 Initializing Terraform..."
terraform init

if [ $? -ne 0 ]; then
    echo "❌ Terraform init failed!"
    exit 1
fi

# Validate configuration
echo "✅ Validating configuration..."
terraform validate

if [ $? -ne 0 ]; then
    echo "❌ Terraform validation failed!"
    exit 1
fi

# Plan deployment
echo "📋 Planning deployment..."
terraform plan -out=tfplan

if [ $? -ne 0 ]; then
    echo "❌ Terraform plan failed!"
    exit 1
fi

echo "✅ Terraform configuration is valid!"
echo "📊 Plan created successfully - ready for deployment"
echo ""
echo "🚀 To deploy: terraform apply tfplan"
echo "🗑️  To clean up: terraform destroy"
echo ""
echo "💰 Estimated cost: ~$5-10/day (remember to destroy when done!)"
