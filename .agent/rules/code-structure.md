---
trigger: always_on
description: Terraform code structure and quality rules for production-grade infrastructure
---

# Terraform Code Structure & Quality Rules

This document defines the standard rules for code structure, quality, and security for production-grade Terraform infrastructure.

---

## 1. Directory Structure

### 1.1 Standard Module Structure

```text
terraform-<provider>-<name>/
├── .github/
│   └── workflows/           # CI/CD pipelines
│       ├── ci.yml           # PR validation
│       ├── release.yml      # Semantic versioning
│       └── security.yml     # Weekly security scans
├── examples/                # REQUIRED: Usage examples
│   ├── basic/               # Minimal viable configuration
│   ├── complete/            # All features enabled
│   └── multi-region/        # Complex/Advanced scenarios
├── modules/                 # Internal sub-modules (if needed)
│   └── <sub-module>/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── tests/                   # Integration tests
│   ├── basic.tftest.hcl     # Basic functionality tests
│   └── complete.tftest.hcl  # Full feature tests
├── .gitignore               # TF-specific ignores
├── .pre-commit-config.yaml  # Local development hooks
├── .tflint.hcl              # Linting rules
├── .terraform-docs.yml      # Documentation generation
├── .trivyignore             # Security scan exceptions
├── CHANGELOG.md             # Version history (auto-generated)
├── README.md                # Documentation (auto-generated)
├── main.tf                  # Primary resource definitions
├── variables.tf             # Input variables with validation
├── outputs.tf               # Exported values
├── locals.tf                # Computed local values
├── data.tf                  # Data sources
├── providers.tf             # Provider requirements ONLY (no config)
└── versions.tf              # Version constraints
```

### 1.2 Root Configuration Structure (Live Infrastructure)

```text
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── backend.tf       # Dev state backend
│   │   ├── main.tf          # Module calls
│   │   ├── variables.tf     # Environment-specific vars
│   │   ├── terraform.tfvars # Variable values (NEVER commit secrets)
│   │   └── outputs.tf
│   ├── staging/
│   └── prod/
├── modules/                 # Shared internal modules
│   ├── networking/
│   ├── compute/
│   ├── database/
│   └── security/
├── .github/workflows/       # CI/CD for infrastructure
└── README.md
```

---

## 2. Automated Quality Configurations

### 2.1 Linting Rules (`.tflint.hcl`)

```hcl
plugin "terraform" {
  enabled = true
  preset  = "recommended"
}

# AWS-specific rules (if using AWS)
plugin "aws" {
  enabled = true
  version = "0.31.0"
  source  = "github.com/terraform-linters/tflint-ruleset-aws"
}

# Documentation
rule "terraform_documented_variables" {
  enabled = true
}

rule "terraform_documented_outputs" {
  enabled = true
}

# Naming conventions
rule "terraform_naming_convention" {
  enabled = true
  format  = "snake_case"
}

# Module sources must be pinned
rule "terraform_module_pinned_source" {
  enabled = true
  style   = "semver"
}

# No deprecated interpolation
rule "terraform_deprecated_interpolation" {
  enabled = true
}

# Required providers must have versions
rule "terraform_required_providers" {
  enabled = true
}

# Required Terraform version
rule "terraform_required_version" {
  enabled = true
}

# No unused declarations
rule "terraform_unused_declarations" {
  enabled = true
}

# Standard file structure
rule "terraform_standard_module_structure" {
  enabled = true
}
```

### 2.2 Pre-commit Hooks (`.pre-commit-config.yaml`)

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ["--maxkb=1000"]
      - id: detect-private-key
      - id: check-merge-conflict

  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.96.1
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
        args:
          - --hook-config=--retry-once-with-cleanup=true
      - id: terraform_tflint
        args:
          - --args=--config=__GIT_WORKING_DIR__/.tflint.hcl
      - id: terraform_docs
        args:
          - --hook-config=--path-to-file=README.md
          - --hook-config=--add-to-existing-file=true
          - --hook-config=--create-file-if-not-exist=true
      - id: terraform_checkov
        args:
          - --args=--quiet
          - --args=--compact
      - id: terraform_trivy
        args:
          - --args=--severity=HIGH,CRITICAL
          - --args=--skip-dirs=.terraform

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks
```

### 2.3 Documentation Rules (`.terraform-docs.yml`)

````yaml
formatter: "markdown table"
version: "0.17"

header-from: docs/header.md
footer-from: docs/footer.md

sections:
  hide: []
  show: []

content: |-
  {{ .Header }}

  ## Requirements

  | Name | Version |
  |------|---------|
  {{ range .Requirements }}| {{ .Name }} | {{ .Version }} |
  {{ end }}

  ## Providers

  {{ .Providers }}

  ## Usage

  ```hcl
  module "{{ .Name }}" {
    source  = "<registry>/<namespace>/{{ .Name }}"
    version = "x.x.x"

    # Required variables
    {{ range .Inputs }}{{ if .Required }}{{ .Name }} = {{ .Type }}
    {{ end }}{{ end }}
  }
````

Examples

[Basic](./examples/basic)
[Complete](./examples/complete)

{{ .Inputs }}

{{ .Outputs }}

{{ .Resources }}

{{ .Footer }}

output:
file: README.md
mode: inject
template: |-

<!-- BEGIN_TF_DOCS -->

{{ .Content }}

<!-- END_TF_DOCS -->

settings:
anchor: true
color: true
default: true
description: true
escape: true
hide-empty: false
html: true
indent: 2
lockfile: true
read-comments: true
required: true
sensitive: true
type: true

````

### 2.4 Git Ignore (`.gitignore`)

```gitignore
# Terraform
.terraform/
.terraform.lock.hcl
*.tfstate
*.tfstate.*
*.tfvars
!*.tfvars.example
crash.log
crash.*.log
override.tf
override.tf.json
*_override.tf
*_override.tf.json

# IDE
.idea/
*.swp
*.swo
.vscode/

# OS
.DS_Store
Thumbs.db

# Secrets (NEVER commit these)
*.pem
*.key
secrets.tf
````

---

## 3. Coding Standards

### 3.1 Variable Best Practices

```hcl
# ✅ GOOD: Fully documented with validation
variable "environment" {
  type        = string
  description = "Environment name (dev, staging, prod)"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for the application servers"
  default     = "t3.micro"

  validation {
    condition     = can(regex("^t[23]\\.", var.instance_type))
    error_message = "Only t2 and t3 instance types are allowed."
  }
}

# ❌ BAD: No description, no validation, uses 'any'
variable "config" {
  type = any
}
```

### 3.2 Output Best Practices

```hcl
# ✅ GOOD: Descriptive with sensitive marking
output "database_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = aws_db_instance.main.endpoint
}

output "database_password" {
  description = "The master password for the RDS instance"
  value       = aws_db_instance.main.password
  sensitive   = true
}

# ❌ BAD: No description
output "vpc_id" {
  value = aws_vpc.main.id
}
```

### 3.3 Resource Naming Convention

```hcl
# Pattern: {project}_{environment}_{resource}_{identifier}
resource "aws_instance" "myapp_prod_web_001" {
  # ...

  tags = {
    Name        = "myapp-prod-web-001"
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
  }
}
```

### 3.4 Locals for DRY Code

```hcl
locals {
  # Common tags applied to all resources
  common_tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
    Owner       = var.owner
    CostCenter  = var.cost_center
  }

  # Computed values
  name_prefix = "${var.project}-${var.environment}"

  # Conditional logic
  is_production = var.environment == "prod"
  instance_type = local.is_production ? "t3.large" : "t3.micro"
}
```

### 3.5 Version Constraints (`versions.tf`)

```hcl
terraform {
  required_version = ">= 1.5.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}
```

### 3.6 Provider Configuration (`providers.tf`)

```hcl
# For MODULES: Only declare requirements, no configuration
# providers.tf in a module should be EMPTY or contain only:
# (Provider configuration is done in the root module)

# For ROOT CONFIGURATIONS:
provider "aws" {
  region = var.region

  default_tags {
    tags = local.common_tags
  }

  # Assume role for cross-account access
  assume_role {
    role_arn = var.assume_role_arn
  }
}

# Multi-region with alias
provider "aws" {
  alias  = "us_west_2"
  region = "us-west-2"

  default_tags {
    tags = local.common_tags
  }
}
```

---

## 4. Security Rules

### 4.1 Never Hardcode Secrets

```hcl
# ❌ BAD: Hardcoded credentials
resource "aws_db_instance" "main" {
  password = "MyP@ssw0rd123!"  # NEVER DO THIS
}

# ✅ GOOD: Use variables with sensitive flag
variable "db_password" {
  type        = string
  description = "Database master password"
  sensitive   = true
}

resource "aws_db_instance" "main" {
  password = var.db_password
}

# ✅ BETTER: Use Secrets Manager
data "aws_secretsmanager_secret_version" "db" {
  secret_id = aws_secretsmanager_secret.db.id
}

resource "aws_db_instance" "main" {
  password = jsondecode(data.aws_secretsmanager_secret_version.db.secret_string)["password"]
}
```

### 4.2 Enable Encryption

```hcl
# S3 Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

# RDS encryption
resource "aws_db_instance" "main" {
  storage_encrypted = true
  kms_key_id        = aws_kms_key.main.arn
}
```

### 4.3 Least Privilege IAM

```hcl
# ✅ GOOD: Specific permissions
data "aws_iam_policy_document" "lambda" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = [
      "${aws_s3_bucket.data.arn}/*"
    ]
  }
}

# ❌ BAD: Overly permissive
data "aws_iam_policy_document" "bad" {
  statement {
    effect    = "Allow"
    actions   = ["*"]
    resources = ["*"]
  }
}
```

---

## 5. State Management Rules

### 5.1 Remote Backend Configuration

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "project/environment/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-locks"

    # Use assume role for cross-account
    role_arn = "arn:aws:iam::123456789012:role/TerraformStateAccess"
  }
}
```

### 5.2 State Isolation

```text
# Separate state files per environment
s3://terraform-state/
├── project-a/
│   ├── dev/terraform.tfstate
│   ├── staging/terraform.tfstate
│   └── prod/terraform.tfstate
└── project-b/
    ├── dev/terraform.tfstate
    └── prod/terraform.tfstate
```

---

## 6. CI/CD Pipeline Rules

### 6.1 GitHub Actions Workflow

```yaml
name: Terraform CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.0"

      - name: Terraform Format
        run: terraform fmt -check -recursive

      - name: Terraform Init
        run: terraform init -backend=false

      - name: Terraform Validate
        run: terraform validate

      - name: TFLint
        uses: terraform-linters/setup-tflint@v4
      - run: |
          tflint --init
          tflint --recursive

      - name: Checkov Security Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform
          quiet: true

      - name: Trivy Security Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: "config"
          scan-ref: "."
          severity: "HIGH,CRITICAL"

  plan:
    needs: validate
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v3

      - name: Terraform Init
        run: terraform init

      - name: Terraform Plan
        run: terraform plan -out=tfplan

      - name: Post Plan to PR
        uses: actions/github-script@v7
        with:
          script: |
            // Post plan output as PR comment
```

---

## 7. Implementation Checklist

### Code Quality

- [ ] All resources use `snake_case` naming
- [ ] No hardcoded values (use variables)
- [ ] Every variable has `type` and `description`
- [ ] Every output has `description`
- [ ] Sensitive values marked with `sensitive = true`
- [ ] `terraform fmt` passes
- [ ] `terraform validate` passes
- [ ] `tflint` passes with no errors

### Security

- [ ] No secrets in code (use Secrets Manager/Vault)
- [ ] Encryption enabled for storage resources
- [ ] IAM policies follow least privilege
- [ ] Security groups restrict ingress/egress

- [ ] `checkov` or `tfsec` scan passes

### Documentation

- [ ] README auto-generated via terraform-docs

- [ ] Examples exist in `/examples` directory
- [ ] CHANGELOG updated for releases

### Testing

- [ ] Basic integration test exists
- [ ] Tests pass in CI/CD pipeline

### State

- [ ] Remote backend configured
- [ ] State encryption enabled
- [ ] State locking enabled
- [ ] State file per environment
