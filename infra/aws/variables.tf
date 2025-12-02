variable "aws_region" {
  description = "AWS region (use appropriate Gov/IL-specific partition/region in real deployments)."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.42.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.42.1.0/24", "10.42.2.0/24"]
}

variable "ecs_task_cpu" {
  description = "Fargate task CPU units for each service."
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Fargate task memory (MiB) for each service."
  type        = number
  default     = 512
}

variable "lab_image" {
  description = "ECR image URI for the C-Lcone Lab service."
  type        = string
}

variable "malignant_image" {
  description = "ECR image URI for the MalignantAgent service."
  type        = string
}

variable "gao_image" {
  description = "ECR image URI for the GAO Orchestrator service."
  type        = string
}

variable "ecs_service_desired_count" {
  description = "Desired count for Fargate services."
  type        = number
  default     = 1
}

variable "tags" {
  description = "Common tags to apply to all resources."
  type        = map(string)
  default     = {}
}
