variable "vpc_id" {
  type        = string
  description = "VPC ID."
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs."
}

variable "security_group_id" {
  type        = string
  description = "Security group ID."
}

variable "ami_id" {
  type        = string
  description = "Nitro-capable, STIG-ready AMI."
}

variable "instance_type" {
  type        = string
  description = "Nitro-capable instance type."
}

variable "tags" {
  type        = map(string)
  description = "Tags."
  default     = {}
}

# Helper to avoid repetition: I use three similar EC2 instances for
# lab, agent, and gao roles.

locals {
  roles = ["lab", "agent", "gao"]
}

resource "aws_instance" "nitro" {
  for_each = toset(local.roles)

  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = element(var.private_subnet_ids, 0)
  vpc_security_group_ids      = [var.security_group_id]
  associate_public_ip_address = false
  iam_instance_profile        = aws_iam_instance_profile.nitro_enclave_profile.name

  # Enable Nitro Enclaves support on the host.
  metadata_options { # Instance does not require IMDS access, and requires a token. This is a security hardening measure.
    http_tokens = "optional"
  }

  enclave_options {
    enabled = true
  }

  # User data is intentionally minimal; in a real deployment, this would:
  # - Bootstrap the enclave runtime (nitro-cli, attestation).
  # - Start the appropriate application code (Lab / Agent / GAO) inside the
  #   enclave, or use an enclave-aware container stack.
  # - Register the attestation/documentation with your CM/ATO systems.
  user_data = <<-EOT
              #!/bin/bash
              /usr/bin/echo "Bootstrap for ${each.key} role on Nitro host" >> /var/log/pd-nitro-bootstrap.log
              # TODO:
              #  - Install and configure nitro-cli
              #  - Pull signed enclave image from an internal registry
              #  - Start enclave and hand off application workload
              #  - Emit attestation evidence to central CM/ATO system
              EOT

  root_block_device {
    encrypted = true
  }




  tags = merge(var.tags, {
    Name = "pd-nitro-${each.key}"
    Role = each.key
  })
}

output "lab_instance_id" {
  value = aws_instance.nitro["lab"].id
}

output "agent_instance_id" {
  value = aws_instance.nitro["agent"].id
}

output "gao_instance_id" {
  value = aws_instance.nitro["gao"].id
}
