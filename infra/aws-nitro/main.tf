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

locals {
  common_tags = merge(
    {
      Project        = "persuadable-defender"
      Environment    = "nitro-enclave"
      PartitionHint  = var.partition_hint
      SecurityDomain = "IL6-SAP-CANDIDATE"
    },
    var.tags
  )
}

module "network" {
  source = "./network"

  vpc_cidr            = var.vpc_cidr
  private_subnet_cidrs = var.private_subnet_cidrs
  tags                = local.common_tags
}

module "nitro" {
  source = "./ec2_nitro"

  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  security_group_id  = module.network.sg_id

  ami_id        = var.ami_id
  instance_type = var.instance_type

  tags = local.common_tags
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "lab_instance_id" {
  value = module.nitro.lab_instance_id
}

output "agent_instance_id" {
  value = module.nitro.agent_instance_id
}

output "gao_instance_id" {
  value = module.nitro.gao_instance_id
}
