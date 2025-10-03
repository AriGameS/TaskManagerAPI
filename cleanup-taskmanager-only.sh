#!/bin/bash

# TaskManager Project Cleanup Script
# This script will clean up ONLY TaskManager tagged resources

echo "🧹 TaskManager Project Cleanup"
echo "This will delete resources tagged with Project=taskmanager"
echo ""

# Get all regions
REGIONS=$(aws ec2 describe-regions --query 'Regions[*].RegionName' --output text)

for region in $REGIONS; do
    echo "🔍 Checking region: $region"
    
    # Find TaskManager VPCs
    TASKMANAGER_VPCS=$(aws ec2 describe-vpcs --region $region --filters "Name=tag:Project,Values=taskmanager" --query 'Vpcs[*].VpcId' --output text 2>/dev/null)
    
    if [ ! -z "$TASKMANAGER_VPCS" ] && [ "$TASKMANAGER_VPCS" != "None" ]; then
        echo "  🎯 Found TaskManager VPCs: $TASKMANAGER_VPCS"
        
        for vpc in $TASKMANAGER_VPCS; do
            echo "    🗑️  Deleting VPC: $vpc"
            
            # Delete NAT Gateways first
            NAT_GATEWAYS=$(aws ec2 describe-nat-gateways --region $region --filter "Name=vpc-id,Values=$vpc" --query 'NatGateways[*].NatGatewayId' --output text 2>/dev/null)
            if [ ! -z "$NAT_GATEWAYS" ] && [ "$NAT_GATEWAYS" != "None" ]; then
                for nat in $NAT_GATEWAYS; do
                    echo "      🔄 Deleting NAT Gateway: $nat"
                    aws ec2 delete-nat-gateway --nat-gateway-id $nat --region $region 2>/dev/null
                done
            fi
            
            # Wait for NAT gateways to be deleted
            echo "      ⏳ Waiting for NAT gateways to be deleted..."
            sleep 60
            
            # Detach and delete Internet Gateway
            IGW=$(aws ec2 describe-internet-gateways --region $region --filters "Name=attachment.vpc-id,Values=$vpc" --query 'InternetGateways[*].InternetGatewayId' --output text 2>/dev/null)
            if [ ! -z "$IGW" ] && [ "$IGW" != "None" ]; then
                echo "      🌐 Detaching Internet Gateway: $IGW"
                aws ec2 detach-internet-gateway --internet-gateway-id $IGW --vpc-id $vpc --region $region 2>/dev/null
                aws ec2 delete-internet-gateway --internet-gateway-id $IGW --region $region 2>/dev/null
            fi
            
            # Delete subnets
            SUBNETS=$(aws ec2 describe-subnets --region $region --filters "Name=vpc-id,Values=$vpc" --query 'Subnets[*].SubnetId' --output text 2>/dev/null)
            if [ ! -z "$SUBNETS" ] && [ "$SUBNETS" != "None" ]; then
                for subnet in $SUBNETS; do
                    echo "      📍 Deleting subnet: $subnet"
                    aws ec2 delete-subnet --subnet-id $subnet --region $region 2>/dev/null || echo "        ⚠️  Could not delete $subnet (may have dependencies)"
                done
            fi
            
            # Delete route tables (except main)
            ROUTE_TABLES=$(aws ec2 describe-route-tables --region $region --filters "Name=vpc-id,Values=$vpc" --query 'RouteTables[?Associations[0].Main!=`true`].RouteTableId' --output text 2>/dev/null)
            if [ ! -z "$ROUTE_TABLES" ] && [ "$ROUTE_TABLES" != "None" ]; then
                for rt in $ROUTE_TABLES; do
                    echo "      🛣️  Deleting route table: $rt"
                    aws ec2 delete-route-table --route-table-id $rt --region $region 2>/dev/null || echo "        ⚠️  Could not delete $rt"
                done
            fi
            
            # Delete security groups (except default)
            SECURITY_GROUPS=$(aws ec2 describe-security-groups --region $region --filters "Name=vpc-id,Values=$vpc" --query 'SecurityGroups[?GroupName!=`default`].GroupId' --output text 2>/dev/null)
            if [ ! -z "$SECURITY_GROUPS" ] && [ "$SECURITY_GROUPS" != "None" ]; then
                for sg in $SECURITY_GROUPS; do
                    echo "      🔒 Deleting security group: $sg"
                    aws ec2 delete-security-group --group-id $sg --region $region 2>/dev/null || echo "        ⚠️  Could not delete $sg"
                done
            fi
            
            # Finally delete VPC
            echo "      🗑️  Deleting VPC: $vpc"
            aws ec2 delete-vpc --vpc-id $vpc --region $region 2>/dev/null || echo "        ⚠️  Could not delete VPC $vpc"
        done
    fi
    
    # Delete TaskManager Load Balancers
    ALBS=$(aws elbv2 describe-load-balancers --region $region --query 'LoadBalancers[?contains(LoadBalancerName, `taskmanager`)].LoadBalancerArn' --output text 2>/dev/null)
    if [ ! -z "$ALBS" ] && [ "$ALBS" != "None" ]; then
        for alb in $ALBS; do
            echo "  ⚖️  Deleting Load Balancer: $alb"
            aws elbv2 delete-load-balancer --load-balancer-arn $alb --region $region 2>/dev/null
        done
    fi
    
    # Delete TaskManager ECS Clusters
    ECS_CLUSTERS=$(aws ecs list-clusters --region $region --query 'clusterArns[?contains(@, `taskmanager`)]' --output text 2>/dev/null)
    if [ ! -z "$ECS_CLUSTERS" ] && [ "$ECS_CLUSTERS" != "None" ]; then
        for cluster in $ECS_CLUSTERS; do
            echo "  🐳 Deleting ECS Cluster: $cluster"
            aws ecs delete-cluster --cluster $cluster --region $region 2>/dev/null
        done
    fi
    
    # Delete TaskManager RDS Instances
    RDS_INSTANCES=$(aws rds describe-db-instances --region $region --query 'DBInstances[?contains(DBInstanceIdentifier, `taskmanager`)].DBInstanceIdentifier' --output text 2>/dev/null)
    if [ ! -z "$RDS_INSTANCES" ] && [ "$RDS_INSTANCES" != "None" ]; then
        for rds in $RDS_INSTANCES; do
            echo "  🗄️  Deleting RDS Instance: $rds"
            aws rds delete-db-instance --db-instance-identifier $rds --skip-final-snapshot --region $region 2>/dev/null
        done
    fi
    
    echo ""
done

echo "✅ TaskManager cleanup complete!"
echo ""
echo "💡 If some resources couldn't be deleted, they may have dependencies."
echo "   Check the AWS Console for any remaining resources."
