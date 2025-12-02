# OCI Terraform Stack (Enclaved Container Deployment)

This directory contains a **reference Terraform configuration** for deploying the
three Cognitive Light Cone projects as **independent container workloads** inside
a highly restricted OCI Virtual Cloud Network (VCN).

> ⚠️ **Important Compliance Disclaimer**
>
> - This is **not** a complete DoD IL6 / SAP implementation.
> - It targets a network + identity pattern that is compatible with:
>   - Private subnets only.
>   - No Internet Gateway.
>   - Service Gateway for OCI service access.
>   - Clear compartment boundaries.
> - Actual IL6/SAP deployments must go through your organization’s formal
>   accreditation and enclave design process.

## High-Level Design

- **VCN with Private Subnets**
  - No Internet Gateway.
  - Optional NAT Gateway *omitted by default*.
  - Service Gateway for:
    - OCI Registry (OCIR)
    - Logging, Metrics
- **OCIR Repositories**
  - One per project (lab, malignant, gao), referenced by image.
- **Container Instances (or OKE)**
  - Example uses **OCI Container Instances** for simplicity.
  - Each project runs as a separate container instance in private subnets.
- **Network Security Groups**
  - Restrictive ingress/egress rules.
  - Optional internal-only traffic between components.

## Files

- `main.tf` – provider wiring and high-level composition.
- `network.tf` – VCN, subnets, gateways, and NSGs.
- `containers.tf` – container instances for each project.
- `variables.tf` – configurable inputs (compartment, images, CIDRs).
- `outputs.tf` – surface useful IDs for monitoring and further integration.

## Usage (Outline)

1. Push images to OCIR (`phx.ocir.io/...` or appropriate region):

   ```bash
   docker login <region>.ocir.io
   docker build -t <region>.ocir.io/<tenancy-namespace>/persuadable-defender-lab:latest -f docker/Dockerfile.lab .
   docker push <region>.ocir.io/<tenancy-namespace>/persuadable-defender-lab:latest
   # repeat for malignant and gao
   ```

2. Terraform:

   ```bash
   cd infra/oci
   terraform init
   terraform apply \
     -var "region=us-gov-phoenix-1" \
     -var "compartment_ocid=ocid1.compartment.oc1..xxxx" \
     -var "lab_image=phx.ocir.io/tenancy/persuadable-defender-lab:latest" \
     -var "malignant_image=..." \
     -var "gao_image=..."
   ```

Integrate this with your existing OCI enclave or Dedicated Region design as
appropriate for IL6/SAP workloads.
