variable "region" {
  description = "OCI region."
  type        = string
}

variable "tenancy_ocid" {
  type        = string
  description = "Tenancy OCID."
}

variable "compartment_ocid" {
  description = "OCID of the compartment to host the enclave."
  type        = string
}

variable "vcn_cidr" {
  description = "CIDR block for the VCN."
  type        = string
  default     = "10.52.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets."
  type        = list(string)
  default     = ["10.52.1.0/24", "10.52.2.0/24"]
}

variable "lab_image" {
  description = "OCIR image for the Lab container."
  type        = string
}

variable "malignant_image" {
  description = "OCIR image for the MalignantAgent container."
  type        = string
}

variable "gao_image" {
  description = "OCIR image for the GAO container."
  type        = string
}

variable "tags" {
  description = "Defined tags for governance/traceability."
  type        = map(string)
  default     = {}
}
