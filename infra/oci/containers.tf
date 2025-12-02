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

variable "lab_image" {
  type        = string
  description = "OCIR image for Lab."
}

variable "malignant_image" {
  type        = string
  description = "OCIR image for MalignantAgent."
}

variable "gao_image" {
  type        = string
  description = "OCIR image for GAO."
}

variable "freeform_tags" {
  type        = map(string)
  description = "Freeform tags."
  default     = {}
}

locals {
  containers = {
    lab = var.lab_image
    malignant = var.malignant_image
    gao = var.gao_image
  }
}

resource "oci_container_instances_container_instance" "this" {
  for_each = local.containers

  compartment_id = var.compartment_ocid
  display_name   = "pd-${each.key}"
  shape          = "CI.Standard.E4.Flex"
  shape_config {
    ocpus = 1
    memory_in_gbs = 2
  }

  vnics {
    subnet_id        = var.subnet_ids[0]
    nsg_ids          = [var.nsg_id]
    assign_public_ip = "false"
  }

  containers {
    display_name = "pd-${each.key}-container"
    image_url    = each.value

    environment_variables = {
      PD_ROLE = upper(each.key)
    }
  }

  freeform_tags = var.freeform_tags
}

output "container_ids" {
  value = { for k, v in oci_container_instances_container_instance.this : k => v.id }
}
