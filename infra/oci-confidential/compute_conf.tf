variable "compartment_ocid" {
  type        = string
  description = "Compartment OCID."
}

variable "subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs."
}

variable "nsg_id" {
  type        = string
  description = "Network Security Group ID."
}

variable "shape" {
  type        = string
  description = "VM shape compatible with confidential workloads."
}

variable "image_ocid" {
  type        = string
  description = "OCID of hardened/STIG-ready image."
}

variable "freeform_tags" {
  type        = map(string)
  description = "Freeform tags."
  default     = {}
}

locals {
  roles = ["lab", "agent", "gao"]
}

resource "oci_core_instance" "vm" {
  for_each = toset(local.roles)

  compartment_id = var.compartment_ocid
  display_name   = "pd-conf-${each.key}"

  shape = var.shape

  shape_config {
    ocpus         = 1
    memory_in_gbs = 4
  }

  source_details {
    source_type = "image"
    source_id   = var.image_ocid
  }

  create_vnic_details {
    subnet_id        = element(var.subnet_ids, 0)
    nsg_ids          = [var.nsg_id]
    assign_public_ip = false
  }

  metadata = {
    user_data = base64encode(<<-EOT
      #cloud-config
      runcmd:
        - echo "Bootstrap for ${each.key} role in confidential enclave" >> /var/log/pd-conf-bootstrap.log
        # TODO:
        #  - Apply local hardening steps (if not already baked into image).
        #  - Start the appropriate Python service (Lab / Agent / GAO).
        #  - Wire to internal logging/monitoring endpoints.
        #  - Emit evidence to CM/ATO systems.
      EOT
    )
  }

  freeform_tags = merge(var.freeform_tags, {
    Role = each.key
  })
}

output "vm_ids" {
  value = { for k, v in oci_core_instance.vm : k => v.id }
}
