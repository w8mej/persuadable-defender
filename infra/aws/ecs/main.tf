variable "vpc_id" {
  type        = string
  description = "VPC ID for ECS tasks."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for Fargate tasks."
}

variable "security_group_id" {
  type        = string
  description = "Security group ID to attach to ECS tasks."
}

variable "ecs_task_cpu" {
  type        = number
  description = "CPU units for tasks."
}

variable "ecs_task_memory" {
  type        = number
  description = "Memory (MiB) for tasks."
}

variable "lab_image" {
  type        = string
  description = "ECR image URI for Lab service."
}

variable "malignant_image" {
  type        = string
  description = "ECR image URI for MalignantAgent service."
}

variable "gao_image" {
  type        = string
  description = "ECR image URI for GAO service."
}

variable "desired_count" {
  type        = number
  description = "Desired count for services."
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
  default     = {}
}

resource "aws_ecs_cluster" "this" {
  name = "persuadable-defender-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

# IAM roles and task definitions are simplified here; in IL-like environments,
# you would scope these down with least-privilege policies, STIG-compliant
# boundary controls, and centralized logging.

resource "aws_iam_role" "task_execution" {
  name               = "persuadable-defender-task-exec"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json

  tags = var.tags
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "task_exec_policy" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Helper to define a task definition
locals {
  container_common = {
    cpu               = var.ecs_task_cpu
    memory            = var.ecs_task_memory
    essential         = true
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = "/ecs/persuadable-defender"
        awslogs-region        = data.aws_region.current.name
        awslogs-stream-prefix = "ecs"
      }
    }
  }
}

data "aws_region" "current" {}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/persuadable-defender"
  retention_in_days = 30
  tags              = var.tags
}

# Task definitions and services for each project
module "lab_service" {
  source = "./service"

  cluster_arn       = aws_ecs_cluster.this.arn
  service_name      = "pd-lab"
  image             = var.lab_image
  container_name    = "lab"
  cpu               = var.ecs_task_cpu
  memory            = var.ecs_task_memory
  desired_count     = var.desired_count
  subnet_ids        = var.private_subnet_ids
  security_group_id = var.security_group_id
  execution_role_arn = aws_iam_role.task_execution.arn
  tags              = var.tags
}

module "malignant_service" {
  source = "./service"

  cluster_arn       = aws_ecs_cluster.this.arn
  service_name      = "pd-malignant"
  image             = var.malignant_image
  container_name    = "malignant"
  cpu               = var.ecs_task_cpu
  memory            = var.ecs_task_memory
  desired_count     = var.desired_count
  subnet_ids        = var.private_subnet_ids
  security_group_id = var.security_group_id
  execution_role_arn = aws_iam_role.task_execution.arn
  tags              = var.tags
}

module "gao_service" {
  source = "./service"

  cluster_arn       = aws_ecs_cluster.this.arn
  service_name      = "pd-gao"
  image             = var.gao_image
  container_name    = "gao"
  cpu               = var.ecs_task_cpu
  memory            = var.ecs_task_memory
  desired_count     = var.desired_count
  subnet_ids        = var.private_subnet_ids
  security_group_id = var.security_group_id
  execution_role_arn = aws_iam_role.task_execution.arn
  tags              = var.tags
}

output "cluster_arn" {
  value = aws_ecs_cluster.this.arn
}
