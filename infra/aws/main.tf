terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Common tags for traceability / IL-style accountability.
locals {
  common_tags = merge(
    {
      Project   = "persuadable-defender"
      Owner     = "security-research"
      Structure = "enclaved-fargate"
    },
    var.tags
  )
}

module "network" {
  source = "./network"

  vpc_cidr           = var.vpc_cidr
  private_subnet_cidrs = var.private_subnet_cidrs
  tags               = local.common_tags
}

module "ecs" {
  source = "./ecs"

  vpc_id            = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  security_group_id = module.network.ecs_security_group_id

  ecs_task_cpu    = var.ecs_task_cpu
  ecs_task_memory = var.ecs_task_memory

  lab_image       = var.lab_image
  malignant_image = var.malignant_image
  gao_image       = var.gao_image

  desired_count = var.ecs_service_desired_count

  tags = local.common_tags
}

output "vpc_id" {
  description = "ID of the VPC used for enclaved services."
  value       = module.network.vpc_id
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster hosting the services."
  value       = module.ecs.cluster_arn
}
