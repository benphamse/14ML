---
description: Workflow for reviewing Terraform code in pull requests
trigger: on_pr
---

# Terraform Code Review Workflow

A systematic approach to reviewing Terraform code changes.

---

## Review Checklist

### 1. Structure & Organization

- [ ] **File Organization**: Code follows standard module structure
  - `main.tf` - Primary resources
  - `variables.tf` - Input variables
  - `outputs.tf` - Output values
  - `locals.tf` - Local values
  - `versions.tf` - Version constraints

- [ ] **Naming Conventions**: All identifiers use `snake_case`

  ```hcl
  # ✅ Good
  resource "aws_instance" "web_server" { }
  variable "instance_count" { }

  # ❌ Bad
  resource "aws_instance" "webServer" { }
  variable "instanceCount" { }
  ```

- [ ] **Module Structure**: Reusable modules have examples and tests

### 2. Variables & Outputs

- [ ] **Variable Definitions**: All variables have:

  ```hcl
  variable "example" {
    type        = string           # ✅ Type defined
    description = "Description"    # ✅ Description provided
    default     = "value"          # ✅ Default (if optional)
    sensitive   = true             # ✅ Marked if sensitive

    validation {                   # ✅ Validation (where applicable)
      condition     = length(var.example) > 0
      error_message = "Cannot be empty."
    }
  }
  ```

- [ ] **No `type = any`**: Specific types should be used

  ```hcl
  # ❌ Bad
  variable "config" { type = any }

  # ✅ Good
  variable "config" {
    type = object({
      name    = string
      enabled = bool
    })
  }
  ```

- [ ] **Output Descriptions**: All outputs have descriptions
  ```hcl
  output "instance_id" {
    description = "The ID of the EC2 instance"
    value       = aws_instance.main.id
  }
  ```

### 3. Security Review

- [ ] **No Hardcoded Secrets**:

  ```hcl
  # ❌ CRITICAL: Hardcoded credentials
  password = "MyPassword123"

  # ✅ Good: Using variables
  password = var.db_password

  # ✅ Better: Using Secrets Manager
  password = data.aws_secretsmanager_secret_version.db.secret_string
  ```

- [ ] **Encryption Enabled**:

  ```hcl
  # S3
  server_side_encryption_configuration { ... }

  # RDS
  storage_encrypted = true

  # EBS
  encrypted = true
  ```

- [ ] **IAM Least Privilege**: No wildcard permissions

  ```hcl
  # ❌ Bad
  actions   = ["*"]
  resources = ["*"]

  # ✅ Good
  actions   = ["s3:GetObject", "s3:PutObject"]
  resources = ["arn:aws:s3:::bucket-name/*"]
  ```

- [ ] **Network Security**: Security groups properly restricted

  ```hcl
  # ❌ Bad: Open to world
  cidr_blocks = ["0.0.0.0/0"]

  # ✅ Good: Restricted
  cidr_blocks = var.allowed_cidr_blocks
  ```

### 4. State & Backend

- [ ] **Remote Backend**: Configured for shared environments
- [ ] **State Locking**: DynamoDB table or equivalent configured
- [ ] **State Encryption**: Enabled in backend configuration

### 5. Resource Configuration

- [ ] **Tagging Strategy**: All resources properly tagged

  ```hcl
  tags = {
    Name        = "${var.project}-${var.environment}-resource"
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
    Owner       = var.owner
  }
  ```

- [ ] **Lifecycle Rules**: Critical resources protected

  ```hcl
  lifecycle {
    prevent_destroy = true  # For production databases, etc.
  }
  ```

- [ ] **Dependencies**: Explicit `depends_on` only when necessary

### 6. Testing & Documentation

- [ ] **Examples Provided**: At least one example in `/examples`
- [ ] **README Updated**: Generated via terraform-docs
- [ ] **Tests Exist**: Integration tests for critical functionality

---

## Review Comments Templates

### Security Issue

````markdown
🔴 **SECURITY**: [Brief description]

**Issue**: [Detailed explanation]

**Risk**: [Impact if not addressed]

**Recommendation**:

```hcl
// Suggested fix
```
````

````

### Best Practice Violation

```markdown
🟡 **BEST PRACTICE**: [Brief description]

**Current**:
```hcl
// Current code
````

**Suggested**:

```hcl
// Improved code
```

**Why**: [Explanation of benefits]

````

### Minor Suggestion

```markdown
💡 **SUGGESTION**: [Brief description]

[Explanation and suggested improvement]
````

### Approval

```markdown
✅ **LGTM**

- [x] Structure follows standards
- [x] Security scan passed
- [x] Variables properly documented
- [x] No hardcoded secrets
- [x] Encryption enabled
```

---

## Automated Checks

Ensure these pass before manual review:

```bash
# Format check
terraform fmt -check -recursive

# Validation
terraform validate

# Linting
tflint --recursive

# Security scan
checkov -d . --quiet

# Documentation current
terraform-docs markdown table . --output-check
```

---

## PR Requirements

### Must Have

- [ ] Terraform plan output attached
- [ ] All automated checks passing
- [ ] Description of changes
- [ ] Link to related ticket/issue

### Should Have

- [ ] Cost estimation (Infracost)
- [ ] Screenshots for UI-related changes
- [ ] Rollback procedure documented

### For Production Changes

- [ ] Change request approved
- [ ] Deployment window scheduled
- [ ] Rollback procedure tested
- [ ] Monitoring alerts verified
