---
description: Complete Terraform development workflow from code to deployment
trigger: manual
---

# Terraform Development Workflow

A comprehensive workflow for developing, validating, and deploying Terraform infrastructure.

---

## Phase 1: Pre-Development Setup

### 1.1 Environment Preparation

```bash
# Verify required tools are installed
terraform version    # >= 1.5.0 required
tflint --version     # For linting
checkov --version    # For security scanning
terraform-docs --version  # For documentation

# Install pre-commit hooks
pre-commit install
pre-commit install --hook-type commit-msg
```

### 1.2 Workspace Initialization

```bash
# Clone or create repository
git clone <repository-url>
cd <project>

# Initialize Terraform
terraform init

# Select workspace (if using workspaces)
terraform workspace select dev || terraform workspace new dev
```

### 1.3 Authentication Setup

```bash
# AWS (choose one method)
# Method 1: AWS Profile
export AWS_PROFILE=my-profile

# Method 2: Environment Variables (CI/CD)
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx

# Method 3: AWS SSO
aws sso login --profile my-sso-profile

# Verify authentication
aws sts get-caller-identity
```

---

## Phase 2: Development

### 2.1 Code Writing Checklist

Before writing code, verify:

- [ ] **File Structure**: Follows standard module structure
- [ ] **Naming Convention**: Uses `snake_case` for all identifiers
- [ ] **Variables**: All have `type`, `description`, and `validation` (where applicable)
- [ ] **Outputs**: All have `description`, sensitive values marked
- [ ] **Providers**: Version constraints defined in `versions.tf`
- [ ] **Backend**: Remote backend configured (not in modules)

### 2.2 Writing Resources

```hcl
# Follow this pattern for every resource:

# 1. Use locals for computed values
locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
  }
}

# 2. Reference data sources for existing resources
data "aws_vpc" "selected" {
  id = var.vpc_id
}

# 3. Create resources with consistent naming and tagging
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = var.subnet_id

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-web"
    Role = "webserver"
  })

  # Use lifecycle for critical resources
  lifecycle {
    prevent_destroy = var.environment == "prod"
  }
}

# 4. Export useful values
output "instance_id" {
  description = "ID of the web server instance"
  value       = aws_instance.web.id
}
```

### 2.3 Security Best Practices During Development

```hcl
# ✅ DO: Use variables for sensitive values
variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database master password"
}

# ✅ DO: Enable encryption by default
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ✅ DO: Restrict security group access
resource "aws_security_group" "web" {
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks  # NOT 0.0.0.0/0
  }
}

# ❌ DON'T: Hardcode secrets
resource "aws_db_instance" "bad" {
  password = "hardcoded-password"  # NEVER DO THIS
}
```

---

## Phase 3: Local Validation

### 3.1 Format and Validate

```bash
# Step 1: Format code
terraform fmt -recursive

# Step 2: Validate syntax
terraform validate

# Step 3: Run linting
tflint --recursive

# Step 4: Security scan
checkov -d . --quiet --compact

# Or use tfsec
tfsec . --minimum-severity HIGH
```

### 3.2 Pre-commit Validation

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Expected output:
# terraform_fmt............Passed
# terraform_validate.......Passed
# terraform_tflint.........Passed
# terraform_docs...........Passed
# terraform_checkov........Passed
# gitleaks.................Passed
```

### 3.3 Generate Documentation

```bash
# Auto-generate README from code
terraform-docs markdown table . > README.md

# Or with config file
terraform-docs -c .terraform-docs.yml .
```

---

## Phase 4: Planning

### 4.1 Create Execution Plan

```bash
# Generate plan with output file
terraform plan -out=tfplan

# For specific environment
terraform plan -var-file=environments/dev.tfvars -out=tfplan

# Target specific resources (use sparingly)
terraform plan -target=aws_instance.web -out=tfplan
```

### 4.2 Plan Review Checklist

Review the plan output for:

- [ ] **No Unexpected Destroys**: Check for resources being destroyed
- [ ] **Correct Resource Count**: Verify adds/changes/destroys match expectations
- [ ] **No Sensitive Data Exposed**: Sensitive values should show `(sensitive value)`
- [ ] **Tags Applied**: All resources have required tags
- [ ] **Naming Correct**: Resource names follow convention
- [ ] **Dependencies Correct**: Resources created in proper order

### 4.3 Cost Estimation

```bash
# Use Infracost for cost estimation
infracost breakdown --path .

# Compare with previous
infracost diff --path . --compare-to infracost-base.json
```

---

## Phase 5: Deployment

### 5.1 Pre-Deployment Checklist

- [ ] Plan reviewed and approved
- [ ] No security scan failures
- [ ] Documentation updated
- [ ] Change request approved (for prod)
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

### 5.2 Apply Changes

```bash
# Apply the saved plan
terraform apply tfplan

# Or apply with auto-approve (CI/CD only, NEVER for prod)
terraform apply -auto-approve  # Only for dev/staging

# Apply with confirmation
terraform apply
```

### 5.3 Apply Best Practices

```bash
# For production deployments:

# 1. Use saved plan file (prevents drift between plan and apply)
terraform plan -out=tfplan
terraform apply tfplan

# 2. Lock state during apply
# (Automatic with DynamoDB lock table)

# 3. Enable detailed logging for debugging
export TF_LOG=INFO
terraform apply tfplan

# 4. Use -parallelism for large infrastructures
terraform apply -parallelism=5 tfplan
```

---

## Phase 6: Post-Deployment Verification

### 6.1 Infrastructure Verification

```bash
# Verify state
terraform state list

# Show specific resource details
terraform state show aws_instance.web

# Verify outputs
terraform output

# Check for drift
terraform plan  # Should show "No changes"
```

### 6.2 Application Verification

```bash
# Health checks
curl -s https://app.example.com/health | jq .

# DNS resolution
dig app.example.com

# SSL certificate
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null | openssl x509 -noout -dates

# Load balancer targets
aws elbv2 describe-target-health --target-group-arn <arn>
```

### 6.3 Monitoring Setup Verification

- [ ] CloudWatch alarms configured
- [ ] Log groups created
- [ ] Metrics dashboards updated
- [ ] Alerting rules active

---

## Phase 7: Git Workflow

### 7.1 Commit Changes

```bash
# Stage changes
git add .

# Commit with conventional commit message
git commit -m "feat(vpc): add multi-az subnet configuration

- Add private subnets in 3 AZs
- Configure NAT gateway per AZ
- Add VPC flow logs

Refs: JIRA-123"
```

### 7.2 Commit Message Format

```text
<type>(<scope>): <description>

[optional body]

[optional footer]

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- style: Formatting
- refactor: Code refactoring
- test: Adding tests
- chore: Maintenance

Examples:
- feat(eks): add managed node group support
- fix(rds): correct backup retention period
- docs(readme): update usage examples
- refactor(vpc): simplify subnet calculation
```

### 7.3 Pull Request Process

```bash
# Create feature branch
git checkout -b feature/add-eks-cluster

# Push and create PR
git push -u origin feature/add-eks-cluster

# PR should include:
# - Description of changes
# - Link to ticket/issue
# - terraform plan output
# - Screenshots (if UI changes)
```

---

## Phase 8: Rollback Procedures

### 8.1 Quick Rollback (State)

```bash
# View state history (if versioning enabled)
aws s3api list-object-versions \
  --bucket terraform-state \
  --prefix project/env/terraform.tfstate

# Download previous state version
aws s3api get-object \
  --bucket terraform-state \
  --key project/env/terraform.tfstate \
  --version-id <version-id> \
  previous.tfstate

# Apply previous state (DANGEROUS - use with caution)
terraform state push previous.tfstate
```

### 8.2 Code Rollback

```bash
# Revert to previous commit
git revert HEAD

# Or checkout previous version
git checkout <commit-hash> -- .

# Then apply
terraform plan -out=tfplan
terraform apply tfplan
```

### 8.3 Resource-Level Rollback

```bash
# Taint resource to force recreation
terraform taint aws_instance.web

# Remove from state (resource still exists in cloud)
terraform state rm aws_instance.web

# Import existing resource
terraform import aws_instance.web i-1234567890abcdef0
```

---

## Phase 9: Maintenance

### 9.1 Regular Tasks

| Task                      | Frequency | Command                  |
| ------------------------- | --------- | ------------------------ |
| Drift detection           | Daily     | `terraform plan`         |
| Security scan             | Weekly    | `checkov -d .`           |
| Dependency updates        | Monthly   | Update provider versions |
| State backup verification | Monthly   | Check S3 versioning      |
| Access review             | Quarterly | Review IAM policies      |

### 9.2 Upgrade Terraform Version

```bash
# 1. Read upgrade guide
# https://developer.hashicorp.com/terraform/language/upgrade-guides

# 2. Update version constraint
# versions.tf: required_version = ">= 1.6.0"

# 3. Upgrade state (if needed)
terraform init -upgrade

# 4. Run validation
terraform validate
terraform plan
```

### 9.3 Upgrade Provider Versions

```bash
# View current versions
terraform providers

# Update version constraints in versions.tf
# Then:
terraform init -upgrade

# Verify no breaking changes
terraform plan
```

---

## Quick Reference Commands

```bash
# Initialize
terraform init
terraform init -upgrade
terraform init -reconfigure

# Validate
terraform fmt -check -recursive
terraform validate
tflint --recursive
checkov -d .

# Plan
terraform plan
terraform plan -out=tfplan
terraform plan -var-file=prod.tfvars

# Apply
terraform apply
terraform apply tfplan
terraform apply -auto-approve  # DANGER: dev only

# State
terraform state list
terraform state show <resource>
terraform state mv <source> <dest>
terraform state rm <resource>
terraform import <resource> <id>

# Output
terraform output
terraform output -json

# Destroy
terraform destroy
terraform destroy -target=<resource>

# Workspace
terraform workspace list
terraform workspace select <name>
terraform workspace new <name>
```
