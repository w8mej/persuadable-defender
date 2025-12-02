variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID."
}

variable "vcn_cidr" {
  type        = string
  description = "VCN CIDR."
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "Private subnet CIDRs."
}

variable "freeform_tags" {
  type        = map(string)
  description = "Freeform tags."
  default     = {}
}

resource "oci_core_vcn" "this" {
  compartment_id = var.compartment_ocid
  cidr_block     = var.vcn_cidr
  display_name   = "persuadable-defender-vcn"
  dns_label      = "pdvcn"

  freeform_tags = var.freeform_tags
}

# Service gateway for private access to OCI services (e.g., OCIR, Logging).
data "oci_core_services" "all" {}

locals {
  all_services = { for s in data.oci_core_services.all.services : s.name => s }
}

resource "oci_core_service_gateway" "sgw" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.this.id
  display_name   = "pd-service-gateway"

  services {
    service_id = local.all_services["All.*Services.*In.*Oracle.*Services.*Network"].id
  }

  freeform_tags = var.freeform_tags
}

resource "oci_core_subnet" "private" {
  count                = length(var.private_subnet_cidrs)
  compartment_id       = var.compartment_ocid
  vcn_id               = oci_core_vcn.this.id
  cidr_block           = var.private_subnet_cidrs[count.index]
  display_name         = "pd-private-${count.index}"
  dns_label            = "pdpriv${count.index}"
  prohibit_public_ip_on_vnic = true

  route_table_id = oci_core_vcn.this.default_route_table_id

  freeform_tags = var.freeform_tags
}

resource "oci_core_network_security_group" "nsg" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.this.id
  display_name   = "pd-container-nsg"

  freeform_tags = var.freeform_tags
}

# NSG: deny-all baseline; explicit rules can be added here as needed.
resource "oci_core_network_security_group_security_rule" "egress_all_vcn" {
  network_security_group_id = oci_core_network_security_group.nsg.id
  direction                 = "EGRESS"
  protocol                  = "all"

  destination      = oci_core_vcn.this.cidr_block
  destination_type = "CIDR_BLOCK"
}

output "vcn_id" {
  value = oci_core_vcn.this.id
}

output "private_subnet_ids" {
  value = [for s in oci_core_subnet.private : s.id]
}

output "nsg_id" {
  value = oci_core_network_security_group.nsg.id
}
