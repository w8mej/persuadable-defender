terraform {
  required_version = ">= 1.5.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 6.0.0"
    }
  }
}

provider "oci" {
  region = var.region
}

locals {
  freeform_tags = merge(
    {
      Project        = "persuadable-defender"
      Environment    = "confidential-enclave"
      SecurityDomain = "IL6-SAP-CANDIDATE"
    },
    var.tags
  )
}

module "network" {
  source = "./network"

  compartment_ocid    = var.compartment_ocid
  vcn_cidr            = var.vcn_cidr
  private_subnet_cidrs = var.private_subnet_cidrs
  freeform_tags       = local.freeform_tags
}

module "compute" {
  source = "./compute_conf"

  compartment_ocid = var.compartment_ocid
  subnet_ids       = module.network.private_subnet_ids
  nsg_id           = module.network.nsg_id
  shape            = var.shape
  image_ocid       = var.image_ocid
  freeform_tags    = local.freeform_tags
}

output "vcn_id" {
  value = module.network.vcn_id
}

output "vm_ids" {
  value = module.compute.vm_ids
}
