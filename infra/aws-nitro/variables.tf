variable "aws_region" {
  description = "AWS region (e.g., us-gov-west-1)."
  type        = string
}

variable "partition_hint" {
  description = "Human-readable partition hint (e.g., aws-us-gov, aws-secret, aws-topsecret). Used for documentation only."
  type        = string
  default     = "aws-us-gov"
}

variable "vpc_id" {
  description = "ID of an existing VPC to use. If not provided, a new VPC will be created using `vpc_cidr`."
  type        = string
  default     = null
}

variable "vpc_cidr" {
  description = "CIDR for enclave VPC."
  type        = string
  default     = "10.62.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs."
  type        = list(string)
  default     = ["10.62.1.0/24", "10.62.2.0/24"]
}

variable "ami_id" {
  description = "Nitro-capable, STIG-ready AMI ID (to be replaced by IL6-approved image)."
  type        = string
}

variable "instance_type" {
  description = "Nitro-capable instance type (e.g., m5.xlarge, c5.xlarge)."
  type        = string
  default     = "m5.xlarge"
}

variable "tags" {
  description = "Common tags for IL6/SAP traceability (e.g., SystemID, ATO-ID)."
  type        = map(string)
  default     = {}
}
