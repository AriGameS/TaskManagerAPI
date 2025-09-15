# RDS Module Outputs

output "db_instance_id" {
  description = "ID of the RDS instance"
  value       = aws_db_instance.main.id
}

output "db_instance_arn" {
  description = "ARN of the RDS instance"
  value       = aws_db_instance.main.arn
}

output "db_instance_endpoint" {
  description = "Endpoint of the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "Address of the RDS instance"
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "Port of the RDS instance"
  value       = aws_db_instance.main.port
}

output "db_instance_name" {
  description = "Name of the database"
  value       = aws_db_instance.main.db_name
}

output "db_instance_username" {
  description = "Username of the database"
  value       = aws_db_instance.main.username
}

output "db_instance_password_secret_arn" {
  description = "ARN of the secret containing the database password"
  value       = aws_secretsmanager_secret.db_password.arn
}

output "db_instance_password_secret_name" {
  description = "Name of the secret containing the database password"
  value       = aws_secretsmanager_secret.db_password.name
}

output "db_subnet_group_id" {
  description = "ID of the DB subnet group"
  value       = aws_db_subnet_group.main.id
}

output "db_subnet_group_arn" {
  description = "ARN of the DB subnet group"
  value       = aws_db_subnet_group.main.arn
}

output "db_parameter_group_id" {
  description = "ID of the DB parameter group"
  value       = aws_db_parameter_group.main.id
}

output "db_parameter_group_arn" {
  description = "ARN of the DB parameter group"
  value       = aws_db_parameter_group.main.arn
}

output "db_option_group_id" {
  description = "ID of the DB option group"
  value       = var.create_option_group ? aws_db_option_group.main[0].id : null
}

output "db_option_group_arn" {
  description = "ARN of the DB option group"
  value       = var.create_option_group ? aws_db_option_group.main[0].arn : null
}

output "enhanced_monitoring_role_arn" {
  description = "ARN of the enhanced monitoring role"
  value       = var.monitoring_interval > 0 ? aws_iam_role.rds_enhanced_monitoring[0].arn : null
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = var.enable_cloudwatch_logs ? aws_cloudwatch_log_group.postgresql[0].name : null
}

output "cloudwatch_log_group_arn" {
  description = "ARN of the CloudWatch log group"
  value       = var.enable_cloudwatch_logs ? aws_cloudwatch_log_group.postgresql[0].arn : null
}
