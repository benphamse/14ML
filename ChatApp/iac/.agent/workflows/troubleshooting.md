---
description: Workflow for troubleshooting and debugging Terraform issues
trigger: on_error
---

# Terraform Troubleshooting Workflow

A systematic approach to diagnosing and resolving Terraform issues.

---

## Phase 1: Identify the Problem

### 1.1 Error Categories

| Category       | Symptoms                      | Common Causes                  |
| -------------- | ----------------------------- | ------------------------------ |
| **Syntax**     | `Error: Invalid...`           | HCL syntax errors              |
| **Validation** | `Error: Reference...`         | Missing resources, wrong types |
| **Provider**   | `Error: error configuring...` | Auth, API issues               |
| **State**      | `Error: state...`             | Lock, corruption, drift        |
| **Apply**      | `Error: creating/updating...` | Cloud API limits, permissions  |

### 1.2 Enable Debug Logging

```bash
# Set log level (TRACE, DEBUG, INFO, WARN, ERROR)
export TF_LOG=DEBUG

# Log to file
export TF_LOG_PATH=./terraform.log

# Provider-specific logging
export TF_LOG_PROVIDER=DEBUG

# Run command
terraform plan 2>&1 | tee debug.log
```

---

## Phase 2: Common Issues & Solutions

### 2.1 Authentication Errors

**Symptoms:**

```
Error: error configuring Terraform AWS Provider: no valid credential sources
```

**Solutions:**

```bash
# Verify credentials
aws sts get-caller-identity

# Check profile
export AWS_PROFILE=correct-profile

# Check environment variables
env | grep AWS

# For SSO
aws sso login --profile my-profile

# Verify provider config
cat providers.tf
```

### 2.2 State Lock Errors

**Symptoms:**

```
Error: Error acquiring the state lock
Error: state lock was lost
```

**Solutions:**

```bash
# View lock info
terraform force-unlock <LOCK_ID>

# Check DynamoDB table
aws dynamodb scan --table-name terraform-locks

# Manual unlock (DANGER - ensure no other operations)
terraform force-unlock -force <LOCK_ID>
```

### 2.3 State Drift

**Symptoms:**

```
# Plan shows unexpected changes
~ resource "aws_instance" "web" {
    # Changes detected that weren't made by Terraform
}
```

**Solutions:**

```bash
# Refresh state from actual infrastructure
terraform refresh

# Import missing resource
terraform import aws_instance.web i-1234567890

# Remove resource from state (keeps actual resource)
terraform state rm aws_instance.web

# View state details
terraform state show aws_instance.web
```

### 2.4 Dependency Errors

**Symptoms:**

```
Error: Reference to undeclared resource
Error: Cycle detected
```

**Solutions:**

```hcl
# Fix missing dependency
resource "aws_instance" "web" {
  # Add explicit dependency if needed
  depends_on = [aws_iam_role.web]
}

# Break cycles by using data sources or separating resources
data "aws_instance" "existing" {
  instance_id = var.existing_instance_id
}
```

### 2.5 Provider Version Issues

**Symptoms:**

```
Error: Unsupported attribute
Error: Invalid resource type
```

**Solutions:**

```bash
# Check current providers
terraform providers

# Upgrade providers
terraform init -upgrade

# Lock specific version
terraform providers lock -platform=linux_amd64

# View available versions
terraform version -json
```

### 2.6 Resource Limit Errors

**Symptoms:**

```
Error: LimitExceededException
Error: QuotaExceeded
```

**Solutions:**

```bash
# Check current limits (AWS example)
aws service-quotas list-service-quotas --service-code ec2

# Request increase
aws service-quotas request-service-quota-increase \
  --service-code ec2 \
  --quota-code L-1216C47A \
  --desired-value 100

# Deploy in batches
terraform apply -parallelism=2
```

### 2.7 Timeout Errors

**Symptoms:**

```
Error: timeout while waiting for state
Error: deadline exceeded
```

**Solutions:**

```hcl
# Increase timeouts
resource "aws_db_instance" "main" {
  timeouts {
    create = "60m"
    update = "60m"
    delete = "60m"
  }
}

# Or use lifecycle
resource "aws_eks_cluster" "main" {
  lifecycle {
    create_before_destroy = true
  }
}
```

---

## Phase 3: State Recovery

### 3.1 Corrupted State

```bash
# Download state backup (S3 versioning)
aws s3api list-object-versions \
  --bucket terraform-state \
  --prefix project/terraform.tfstate

# Restore previous version
aws s3api get-object \
  --bucket terraform-state \
  --key project/terraform.tfstate \
  --version-id "previous-version-id" \
  restored.tfstate

# Push restored state
terraform state push restored.tfstate
```

### 3.2 State Migration

```bash
# Move resource in state
terraform state mv aws_instance.old aws_instance.new

# Move to different state file
terraform state mv -state-out=other.tfstate aws_instance.web

# Rename resource
terraform state mv \
  module.old_name.aws_instance.web \
  module.new_name.aws_instance.web
```

### 3.3 Import Existing Resources

```bash
# Find resource ID
aws ec2 describe-instances --filters "Name=tag:Name,Values=my-instance"

# Import
terraform import aws_instance.web i-1234567890abcdef0

# Import module resource
terraform import module.vpc.aws_vpc.main vpc-12345678

# Generate config (Terraform 1.5+)
terraform plan -generate-config-out=generated.tf
```

---

## Phase 4: Debugging Tools

### 4.1 Terraform Console

```bash
# Interactive console for testing expressions
terraform console

> var.environment
"prod"

> local.name_prefix
"myapp-prod"

> aws_instance.web.id
"i-1234567890"

> length(var.subnets)
3

> cidrsubnet("10.0.0.0/16", 8, 1)
"10.0.1.0/24"
```

### 4.2 Graph Visualization

```bash
# Generate dependency graph
terraform graph | dot -Tpng > graph.png

# Filter by type
terraform graph -type=plan | dot -Tpng > plan-graph.png
```

### 4.3 State Inspection

```bash
# List all resources
terraform state list

# Show resource details
terraform state show aws_instance.web

# Pull entire state
terraform state pull > current-state.json

# Inspect JSON
jq '.resources[] | select(.type == "aws_instance")' current-state.json
```

---

## Phase 5: Prevention

### 5.1 Pre-commit Checks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    hooks:
      - id: terraform_validate
      - id: terraform_tflint
      - id: terraform_checkov
```

### 5.2 CI/CD Validation

```yaml
# GitHub Actions
- name: Terraform Validate
  run: |
    terraform init -backend=false
    terraform validate

- name: TFLint
  run: tflint --recursive
```

### 5.3 Monitoring & Alerting

```hcl
# Drift detection alarm
resource "aws_cloudwatch_event_rule" "drift_detection" {
  name                = "terraform-drift-detection"
  schedule_expression = "rate(1 day)"
}
```

---

## Quick Reference

### Common Commands

```bash
# Validate
terraform validate

# Format check
terraform fmt -check -recursive

# Refresh state
terraform refresh

# Force unlock
terraform force-unlock <LOCK_ID>

# Import resource
terraform import <resource> <id>

# State operations
terraform state list
terraform state show <resource>
terraform state mv <source> <dest>
terraform state rm <resource>
terraform state pull
terraform state push <file>

# Debug
TF_LOG=DEBUG terraform plan
terraform console
terraform graph
```

### Useful Environment Variables

```bash
# Logging
export TF_LOG=DEBUG
export TF_LOG_PATH=./terraform.log

# Input
export TF_INPUT=0  # Disable interactive input

# Parallelism
export TF_CLI_ARGS_apply="-parallelism=5"

# Auto-approve (CI only)
export TF_CLI_ARGS_apply="-auto-approve"
```
