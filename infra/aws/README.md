# AWS Terraform Stack (Enclaved Fargate Deployment)

This directory contains a **reference Terraform configuration** that deploys the
three Cognitive Light Cone projects as **independent Docker-based services** on
AWS, using a highly restricted network architecture intended to *approximate* an
enclave-style environment.

> ⚠️ **Important Compliance Disclaimer**
>
> - This code is **not** a formal DoD IL6 or SAP-compliant implementation.
> - It is a *starting point* that:
>   - Avoids public internet access.
>   - Uses private subnets with no Internet Gateway.
>   - Uses VPC endpoints for required AWS APIs.
>   - Separates duties and simplifies auditing.
> - Actual IL6/SAP systems must go through your organization’s formal
>   **Authorization to Operate (ATO)** process, including:
>   - Region/partition selection (e.g., AWS Top Secret / Secret, GovCloud).
>   - STIG hardening, CM traceability, and boundary protections.
>   - Continuous monitoring and formal documentation.

## High-Level Design

- **VPC + Private Subnets**
  - No Internet Gateway.
  - Optional NAT Gateway *disabled by default*.
  - Interface VPC Endpoints for:
    - ECR (pull images)
    - CloudWatch Logs
    - SSM (optional, for management)
- **ECR Repositories**
  - One repo per project:
    - `persuadable-defender-lab`
    - `persuadable-defender-malignant-agent`
    - `persuadable-defender-gao`
- **ECS Fargate Services**
  - One task definition + service per project.
  - Each service runs in the private subnets only.
  - No public IPs.
- **Security Groups**
  - Deny-all by default.
  - Optional internal-only communication (e.g., GAO can reach MalignantAgent).

## Files

- `main.tf` – root module wiring providers, networking, ECS, and ECR.
- `network.tf` – VPC, subnets, security groups, endpoints.
- `ecr.tf` – ECR repositories for container images.
- `ecs.tf` – ECS cluster, task definitions, and services.
- `variables.tf` – configurable parameters (CIDRs, image URIs, etc.).
- `outputs.tf` – useful IDs/ARNs for integration with CI/CD.

## Usage (Outline)

1. Build and push images (outside of Terraform), for example:

   ```bash
   # example: Lab image
   docker build -t <account>.dkr.ecr.<region>.amazonaws.com/persuadable-defender-lab:latest \
       -f docker/Dockerfile.lab .

   # repeat for malignant-agent and gao
   ```

2. Configure Terraform:

   ```bash
   cd infra/aws
   terraform init
   terraform apply \
       -var "aws_region=us-gov-west-1" \
       -var "lab_image=ACCOUNT_ID.dkr.ecr.us-gov-west-1.amazonaws.com/persuadable-defender-lab:latest" \
       -var "malignant_image=..." \
       -var "gao_image=..."
   ```

3. Integrate with your existing IL6/SAP boundary controls and ATO process.

This configuration is intentionally small and heavily commented for use in
design reviews, and early-stage experiments.
