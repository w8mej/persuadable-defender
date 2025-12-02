variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the VPC."
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private subnets."
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to resources."
  default     = {}
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(var.tags, {
    Name = "persuadable-defender-vpc"
  })
}

resource "aws_subnet" "private" {
  count                   = length(var.private_subnet_cidrs)
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  map_public_ip_on_launch = false

  tags = merge(var.tags, {
    Name = "persuadable-defender-private-${count.index}"
  })
}

# No Internet Gateway: enclaved design forbids direct Internet access.
# All communication to AWS APIs should go through VPC endpoints.

resource "aws_security_group" "ecs" {
  name        = "persuadable-defender-ecs-sg"
  description = "Security group for enclaved ECS tasks"
  vpc_id      = aws_vpc.this.id

  # Deny-all inbound by default; add explicit rules as needed.
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
    description = "No inbound by default"
  }

  # Allow all egress within the VPC and to VPC endpoints (which resolve to ENIs in the VPC).
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.this.cidr_block]
    description = "Egress only within VPC CIDR"
  }

  tags = merge(var.tags, {
    Name = "persuadable-defender-ecs-sg"
  })
}

# Example VPC endpoint for CloudWatch Logs (extend as needed).
resource "aws_vpc_endpoint" "logs" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.logs"
  vpc_endpoint_type = "Interface"

  private_dns_enabled = true
  security_group_ids  = [aws_security_group.ecs.id]
  subnet_ids          = [for s in aws_subnet.private : s.id]

  tags = merge(var.tags, {
    Name = "persuadable-defender-logs-endpoint"
  })
}

data "aws_region" "current" {}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "private_subnet_ids" {
  value = [for s in aws_subnet.private : s.id]
}

output "ecs_security_group_id" {
  value = aws_security_group.ecs.id
}
