variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR."
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnet CIDRs."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
}

resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = merge(var.tags, {
    Name = "pd-nitro-vpc"
  })
}

resource "aws_subnet" "private" {
  count                   = length(var.private_subnet_cidrs)
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.private_subnet_cidrs[count.index]
  map_public_ip_on_launch = false

  tags = merge(var.tags, {
    Name = "pd-nitro-private-${count.index}"
  })
}

resource "aws_security_group" "nitro" {
  name        = "pd-nitro-sg"
  description = "Nitro enclave host SG (no public ingress)."
  vpc_id      = aws_vpc.this.id

  # No unsolicited inbound.
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = []
    description = "Deny-all inbound by default"
  }

  # Egress only to VPC CIDR (and to interface endpoints if created).
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [aws_vpc.this.cidr_block]
    description = "Egress within enclave VPC only"
  }

  tags = merge(var.tags, {
    Name = "pd-nitro-sg"
  })
}

output "vpc_id" {
  value = aws_vpc.this.id
}

output "private_subnet_ids" {
  value = [for s in aws_subnet.private : s.id]
}

output "sg_id" {
  value = aws_security_group.nitro.id
}
