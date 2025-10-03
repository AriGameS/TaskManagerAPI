#!/bin/bash

# AWS Multi-Region Cleanup Script
# This script will help clean up resources across all AWS regions

echo "🚨 WARNING: This script will attempt to delete AWS resources across ALL regions!"
echo "Make sure you want to proceed with this cleanup."
echo ""
read -p "Type 'YES' to continue: " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ Cleanup cancelled."
    exit 1
fi

# Get all regions
REGIONS=$(aws ec2 describe-regions --query 'Regions[*].RegionName' --output text)

echo "🔍 Found regions: $REGIONS"
echo ""

for region in $REGIONS; do
    echo "🔍 Checking region: $region"
    
    # Check for VPCs
    VPCS=$(aws ec2 describe-vpcs --region $region --query 'Vpcs[*].VpcId' --output text 2>/dev/null)
    if [ ! -z "$VPCS" ] && [ "$VPCS" != "None" ]; then
        echo "  📍 VPCs found: $VPCS"
        
        # Check for taskmanager tagged VPCs
        TASKMANAGER_VPCS=$(aws ec2 describe-vpcs --region $region --filters "Name=tag:Project,Values=taskmanager" --query 'Vpcs[*].VpcId' --output text 2>/dev/null)
        if [ ! -z "$TASKMANAGER_VPCS" ] && [ "$TASKMANAGER_VPCS" != "None" ]; then
            echo "    🎯 TaskManager VPCs: $TASKMANAGER_VPCS"
        fi
    fi
    
    # Check for Load Balancers
    ALBS=$(aws elbv2 describe-load-balancers --region $region --query 'LoadBalancers[*].LoadBalancerName' --output text 2>/dev/null)
    if [ ! -z "$ALBS" ] && [ "$ALBS" != "None" ]; then
        echo "  ⚖️  Load Balancers found: $ALBS"
    fi
    
    # Check for ECS Clusters
    ECS_CLUSTERS=$(aws ecs list-clusters --region $region --query 'clusterArns[*]' --output text 2>/dev/null)
    if [ ! -z "$ECS_CLUSTERS" ] && [ "$ECS_CLUSTERS" != "None" ]; then
        echo "  🐳 ECS Clusters found: $ECS_CLUSTERS"
    fi
    
    # Check for RDS Instances
    RDS_INSTANCES=$(aws rds describe-db-instances --region $region --query 'DBInstances[*].DBInstanceIdentifier' --output text 2>/dev/null)
    if [ ! -z "$RDS_INSTANCES" ] && [ "$RDS_INSTANCES" != "None" ]; then
        echo "  🗄️  RDS Instances found: $RDS_INSTANCES"
    fi
    
    echo ""
done

echo "📊 Summary complete!"
echo ""
echo "💡 Next steps:"
echo "1. Review the resources listed above"
echo "2. Use AWS Console to delete resources manually for safety"
echo "3. Or run individual cleanup commands for specific regions"
echo ""
echo "🔧 To delete TaskManager resources only:"
echo "   Run: ./cleanup-taskmanager-only.sh"
