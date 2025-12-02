variable "region" {
  description = "OCI Government or Dedicated Region."
  type        = string
}

variable "compartment_ocid" {
  description = "Compartment OCID for the confidential enclave."
  type        = string
}

variable "vcn_cidr" {
  description = "CIDR for the confidential VCN."
  type        = string
  default     = "10.72.0.0/16"
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs."
  type        = list(string)
  default     = ["10.72.1.0/24", "10.72.2.0/24"]
}

variable "shape" {
  description = "VM shape compatible with confidential / hardened workloads (e.g., VM.Standard.E4.Flex)."
  type        = string
  default     = "VM.Standard.E4.Flex"
}

variable "image_ocid" {
  description = "OCID of STIG-ready / hardened image (to be supplied by your golden image pipeline)."
  type        = string
}

variable "tags" {
  description = "Freeform tags for IL6/SAP traceability."
  type        = map(string)
  default     = {}
}
