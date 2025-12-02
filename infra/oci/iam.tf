resource "oci_identity_dynamic_group" "container_instances" {
  compartment_id = var.tenancy_ocid
  name           = "pd-container-instances-dg"
  description    = "Dynamic group for Persuadable Defender container instances"
  matching_rule  = "ALL {resource.type = 'computecontainerinstance', resource.compartment.id = '${var.compartment_ocid}'}"
}

resource "oci_identity_policy" "container_instances_policy" {
  compartment_id = var.compartment_ocid
  name           = "pd-container-instances-policy"
  description    = "Least privilege policy for container instances"
  
  statements = [
    "Allow dynamic-group pd-container-instances-dg to read secret-bundles in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group pd-container-instances-dg to use keys in compartment id ${var.compartment_ocid}"
  ]
}
