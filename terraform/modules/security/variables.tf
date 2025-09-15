# Security Module Variables

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "taskmanager"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_id" {
  description = "ID of the VPC"
  type        = string
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
}

variable "app_port" {
  description = "Port on which the application runs"
  type        = number
  default     = 5125
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}
