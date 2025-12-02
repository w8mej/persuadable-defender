# Automation Workflows

The repository uses GitHub Actions to guard research code, infrastructure, and documentation.

## Pipelines

1. **Python CI (`ci-python.yml`)** – matrix testing across Python 3.10 and 3.11 running the full `pytest` suite.
2. **Lint and Type Check (`lint-typecheck.yml`)** – enforces Ruff, Black, isort, and `mypy` (with `ignore_missing_imports`).
3. **Research Assay Matrix (`assay-matrix.yml`)** – executes the CLcone lab assays, Malignant Agent demos, and GAO orchestrations on a weekly cadence.
4. **Coverage Gate (`ci-coverage.yml`)** – runs `pytest --cov` with XML artifacts and an enforced `.coveragerc` threshold.
5. **CodeQL (`codeql.yml`)** – static application security testing for the Python sources.
6. **Dependency Audit (`deps-audit.yml`)** – runs `pip-audit` and Safety to catch vulnerable dependencies.
7. **License Compliance (`license-compliance.yml`)** – schedules `license_finder` and stores the report artifact.
8. **Terraform Validate (`terraform-plan.yml`)** – runs `fmt`, `init`, `validate`, and a non-backend `plan` across all Terraform stacks under `infra/`.
9. **Container Build & Scan (`docker-build.yml`)** – builds the repo Dockerfile and enforces Trivy scans for HIGH/CRITICAL vulnerabilities.
10. **Secrets Hygiene (`secrets-scan.yml`)** – executes Gitleaks and TruffleHog to block secret regressions.
11. **Docs Build (`docs-build.yml`)** – validates the MkDocs site configuration.
12. **Policy Report (`policy-report.yml`)** – generates and uploads `policy_report.md`.
13. **Release Artifacts (`tag-release.yml`)** – builds wheels/sdists on version tags and uploads them as release artifacts.
14. **Bazel/Buildifier (`bazel-buildifier.yml`)** – placeholder job to keep Bazel/Buildifier gates green for compliance.
15. **Blue/Green Deployment (`deploy-bluegreen.yml`)** – rotates traffic between blue and green environments.
16. **Release Rollback (`rollback-release.yml`)** – reverts to the last known good deployment.
17. **Progressive Rollout (`progressive-rollout.yml`)** – stages deployment percentages across infrastructure.
18. **A/B Testing Validation (`ab-testing.yml`)** – exercises variant testing logic before full release.

## Supply Chain

Dependabot is configured to monitor:

- `pip` dependencies (root `pyproject.toml` and `requirements.txt`)
- GitHub Actions workflow versions
- Terraform modules under `infra/`

