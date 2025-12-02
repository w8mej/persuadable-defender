# OCI Confidential / Dedicated Region Stack (Conceptual IL6/SAP Pattern)

This directory contains a **reference Terraform configuration** for running the
three Cognitive Light Cone projects inside **OCI Container Instances or VMs**
within a **Dedicated Region or Government region**, using a pattern compatible
with high-assurance IL6/SAP expectations.

> ⚠️ **Critical Compliance Note**
>
> - This configuration is **not** a complete IL6/SAP solution.
> - It assumes:
>   - You are targeting an OCI **Government** region or **Dedicated Region**.
>   - You will apply **STIG baselines**, CM, and ATO controls at the OS and
>     organizational levels.
> - Use this as architecture scaffolding in your ATO package, not as proof of
>   compliance.

## High-Level Design

- **Dedicated / Gov Region Selection**
  - `region` variable is expected to be a Gov or Dedicated region
    (e.g., `us-gov-phoenix-1`, or your Dedicated Region identifier).

- **VCN with Private Subnets**
  - No Internet Gateway.
  - Service Gateway for OCI service access (OCIR, Logging, Metrics).
  - NSG with deny-all baseline + explicit allow rules.

- **Confidential / Hardened Compute**
  - Use shapes that are compatible with:
    - Hardware-based isolation (e.g., SEV-SNP on supported shapes).
    - STIG-ready images or golden images from your hardening pipeline.
  - Example uses `VM.Standard.E4.Flex`; in real IL6 deployments, this must be
    replaced with **approved shapes and images**.

- **Containers or VMs per Component**
  - `lab`   – C-Lcone Lab workloads.
  - `agent` – MalignantAgent workloads.
  - `gao`   – GAO Orchestrator.

## Files

- `main.tf`          – provider, tags, module wiring.
- `variables.tf`     – region/compartment/shape/image configuration.
- `network.tf`       – VCN, subnets, Service Gateway, NSG.
- `compute_conf.tf`  – confidential/hardened VM instances per component.

You can choose to:
- Run Docker/podman inside each VM; or
- Treat the VM as the enclave boundary and run the Python services directly.

## Relation to IL6 / SAP

In a real IL6/SAP context, you would additionally:

- Use a Dedicated Region or specifically accredited Gov region.
- Apply STIGs to base images; track them via CMDB and CI/CD.
- Use Cloud Guard, Logging, and Security Zones for:
  - Continuous monitoring.
  - Policy enforcement (no public IPs, encryption at rest, etc.).
- Attach full ATO documentation:
  - Control narratives (NIST 800-53 / ISO / etc.).
  - Data flow diagrams showing enclave boundaries.
  - Evidence from automated scans and manual assessments.
