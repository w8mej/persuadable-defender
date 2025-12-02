variable "cluster_arn" {
  type        = string
  description = "ECS cluster ARN."
}

variable "service_name" {
  type        = string
  description = "ECS service name."
}

variable "image" {
  type        = string
  description = "Container image."
}

variable "container_name" {
  type        = string
  description = "Container name."
}

variable "cpu" {
  type        = number
  description = "CPU units."
}

variable "memory" {
  type        = number
  description = "Memory (MiB)."
}

variable "desired_count" {
  type        = number
  description = "Desired task count."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnets for tasks."
}

variable "security_group_id" {
  type        = string
  description = "Security group for tasks."
}

variable "execution_role_arn" {
  type        = string
  description = "Task execution role ARN."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
  default     = {}
}

resource "aws_ecs_task_definition" "this" {
  family                   = var.service_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([
    {
      name  = var.container_name
      image = var.image
      cpu   = var.cpu
      memory = var.memory
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/persuadable-defender"
          awslogs-region        = data.aws_region.current.name
          awslogs-stream-prefix = var.service_name
        }
      }
    }
  ])

  tags = var.tags
}

data "aws_region" "current" {}

resource "aws_ecs_service" "this" {
  name            = var.service_name
  cluster         = var.cluster_arn
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnet_ids
    security_groups = [var.security_group_id]
    assign_public_ip = false
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  tags = var.tags
}

output "service_arn" {
  value = aws_ecs_service.this.arn
}
