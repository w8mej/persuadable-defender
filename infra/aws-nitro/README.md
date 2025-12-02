# AWS Nitro Enclaves Stack (Conceptual IL6/SAP Enclave Pattern)

This directory contains a **reference Terraform configuration** that provisions
**Nitro Enclave–capable EC2 instances** in a highly isolated VPC, intended as a
*design pattern* for DoD IL6 / SAP-style environments.

> ⚠️ **Critical Compliance Note**
>
> - This code is **not** a complete or certified IL6 / SAP deployment.
> - It is a **blueprint** that:
>   - Uses enclave-capable instances (Nitro).
>   - Restricts networking to private subnets with no Internet Gateway.
>   - Encourages ATO-ready practices (tagging, logging, region/partition choice).
> - Actual IL6/SAP systems must be deployed inside the correct AWS partition
>   (e.g., AWS GovCloud, AWS Secret, Top Secret / DoD regions) and go through:
>   - Full **STIG baseline application** on AMIs and OS.
>   - **Configuration Management (CM)**, change control, and inventory.
>   - **Boundary controls** and any required **Cross Domain Solutions (CDS)**.
>   - **ATO documentation**, **continuous monitoring**, and audits.

## High-Level Design

- **Partition / Region Aware**
  - Variables let you describe the intended partition (`aws-us-gov`, etc.).
  - For code portability, provider still uses the standard `aws` provider; in
    real IL6/SAP environments, you would use the appropriate isolated partition.

- **VPC + Private Subnets**
  - No Internet Gateway.
  - Security groups that allow only intra-VPC traffic.

- **Nitro Enclave–Capable EC2**
  - Example uses `m5.xlarge`-class instances (Nitro-based family) with:
    - `enclave_options { enabled = true }`
  - User data is left intentionally minimal with comments indicating where
    enclave initialization and container-to-enclave handoff would live.

- **One Instance per Logical Role**
  - `lab`   – enclave for the C-Lcone Lab workloads.
  - `agent` – enclave for MalignantAgent workloads.
  - `gao`   – enclave for GAO / orchestration workloads.

## Files

- `main.tf`      – provider, tags, and module wiring.
- `network.tf`   – VPC, subnets, security group.
- `ec2_nitro.tf` – three Nitro-capable EC2 instances with enclave options.
- `variables.tf` – partition/region/AMI/instance settings and tags.

## How This Relates to IL6 / SAP

This stack is designed for **discussion and extension**, not as a drop-in
accredited system. In an ATO package, you would:

- Replace the AMI IDs with:
  - STIG-hardened, IL6-approved base images.
  - Possibly golden images from your CM pipeline.
- Layer in:
  - AWS Systems Manager (SSM) for CM and patching (with VPC endpoints only).
  - CloudWatch / CloudTrail logging with central aggregation and retention.
  - GuardDuty / Security Hub as part of continuous monitoring (if permitted).
- Attach the relevant:
  - POA&Ms
  - SSPs
  - Control narratives

The goal here is to show that the **architecture** (Nitro Enclaves inside a
locked-down VPC) is compatible with those expectations.
