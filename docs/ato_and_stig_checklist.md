# ATO & STIG Checklist (AWS + OCI)

This repository includes Terraform blueprints for **enclave-style deployments**
on AWS (Nitro Enclaves) and OCI (confidential / Dedicated Region patterns).
These are **not** full IL6 / SAP implementations but are designed to align with
how an ATO package might look.

Use this checklist as a conversation anchor with security / accreditation teams.

---

## 1. Region / Partition Selection

### AWS

- [ ] Use the correct **partition**:
  - `aws-us-gov` (GovCloud)
  - or AWS Secret / Top Secret / DoD regions as appropriate.
- [ ] Confirm that:
  - VPCs and subnets are created in the authorized regions only.
  - Cross-region connectivity is explicitly reviewed and approved.

### OCI

- [ ] Use a **Government region** or **Dedicated Region** explicitly accredited for IL6/SAP workloads.
- [ ] Verify that tenancy / compartments are scoped to the correct security domain.

---

## 2. STIG Baselines & Hardened Images

### Common

- [ ] Maintain a **golden image pipeline** that:
  - Applies relevant DISA STIGs and organizational hardening.
  - Produces versioned, immutable images for:
    - Nitro-capable EC2 instances.
    - OCI VMs used as enclaves.

### AWS Nitro

- [ ] Replace `ami_id` in `infra/aws-nitro/variables.tf` with:
  - The OCID of your STIG-hardened AMI.
  - Document its STIG ID and associated baselines.

### OCI Confidential

- [ ] Replace `image_ocid` in `infra/oci-confidential/variables.tf` with:
  - The OCID of your hardened image.
  - Attach STIG compliance reports in the ATO documentation.

---

## 3. Configuration Management (CM)

- [ ] Integrate EC2/VM instances with:
  - AWS Systems Manager (SSM) or OCI equivalent for:
    - Patch management.
    - Inventory.
    - State tracking.
- [ ] Ensure that any CM agent traffic:
  - Stays inside your enclave or over approved endpoints (VPC/Service Gateways).
- [ ] Track instance state and configuration in a **CMDB**:
  - Tags in Terraform (`tags`/`freeform_tags`) should match CMDB entries.

---

## 4. Boundary Controls & Networking

### AWS

- [ ] Verify **no Internet Gateway** in enclave VPCs.
- [ ] Use **VPC Endpoints** for required AWS APIs.
- [ ] Security Groups:
  - [ ] Deny-all inbound by default.
  - [ ] Restrict egress to:
    - VPC CIDR.
    - VPC endpoint ENIs (CloudWatch, SSM, KMS, etc.).
- [ ] Document any cross-VPC or cross-region links as part of boundary controls.

### OCI

- [ ] Verify **no Internet Gateway** for enclave VCNs.
- [ ] Use **Service Gateway** for OCI services (OCIR, Logging, Metrics).
- [ ] NSG rules:
  - [ ] Deny-all baseline.
  - [ ] Explicitly allow only necessary intra-VCN traffic.

---

## 5. Cross-Domain Solutions (CDS)

- [ ] Identify all data flows **into and out of** the security enclave:
  - Telemetry / logs.
  - Model artifacts, code, or configuration.
  - Human operator interfaces.
- [ ] For each cross-domain flow:
  - [ ] Specify the CDS technology or process used.
  - [ ] Document:
    - Classification levels.
    - Sanitization / filtering steps.
    - Monitoring / auditing controls.

This repo intentionally keeps CDS out of Terraform; most CDS systems are
specialized appliances or services integrated at the network boundary.

---

## 6. ATO Documentation

For each environment (AWS Nitro, OCI Confidential):

- [ ] System Security Plan (SSP)
  - Architectural diagrams (VPC/VCN, enclaves, CDS, data flows).
  - Control implementations referencing Terraform modules (network, compute, etc.).
- [ ] Security Assessment Plan & Report
  - Evidence from automated scanning.
  - Pen test findings and mitigations.
- [ ] Plan of Action & Milestones (POA&M)
  - Known gaps and remediation schedule.

This repository can be cited in the SSP as:

> "Terraform-based infrastructure-as-code defining the Cognitive Light Cone
> research enclave, including network isolation, Nitro Enclave hosts (AWS), and
> confidential VM enclaves (OCI)."

---

## 7. Continuous Monitoring

### AWS

- [ ] Enable CloudTrail for all Nitro-hosting accounts.
- [ ] Use CloudWatch Logs and Metrics:
  - ECS/EC2/Enclave logs.
  - VPC Flow Logs for enclave subnets.
- [ ] Consider GuardDuty, Security Hub if permitted by the classification.

### OCI

- [ ] Use OCI Logging and Monitoring:
  - VM logs and metrics.
  - VCN Flow Logs (if enabled in your tenancy).
- [ ] Configure Cloud Guard or equivalent for continuous posture mgmt.

---

## 8. Mapping to This Repo

- `infra/aws-nitro/*` – Nitro Enclave host provisioning and enclave VPC pattern.
- `infra/oci-confidential/*` – Confidential VM / Dedicated Region enclave pattern.
- `infra/aws/*` and `infra/oci/*` – Non-Nitro/container-based enclaves that can be
  used for lower-classification experimentation or as stepping stones.

These IaC artefacts are deliberately small and well-commented so they can be
embedded into a larger, formally controlled IL6/SAP architecture.
