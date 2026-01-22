---
name: terraform-skill
description: "Terraform IaC intelligence. Cloud providers: AWS, Azure, GCP, Kubernetes, Docker. Actions: plan, apply, create, design, implement, review, fix, improve, optimize, validate, lint, migrate, refactor, import infrastructure. Resources: VPC, EC2, RDS, S3, Lambda, EKS, IAM, CloudFront, Route53, ALB, Security Groups. Patterns: multi-tier, microservices, serverless, data lake, disaster recovery, multi-region, hub-spoke. Topics: state management, modules, workspaces, remote backend, drift detection, cost optimization, security hardening, compliance, tagging strategy."
---

# Terraform Skill - Infrastructure as Code Intelligence

Comprehensive Terraform guide for cloud infrastructure. Contains 50+ providers, 200+ resources, 30+ architecture patterns, 100+ best practices, and security guidelines across AWS, Azure, GCP, and Kubernetes. Searchable database with priority-based recommendations.

## When to Apply

Reference these guidelines when:

- Designing new cloud infrastructure
- Creating Terraform modules
- Reviewing Terraform code for best practices
- Implementing security policies
- Setting up CI/CD for infrastructure
- Managing Terraform state
- Optimizing cloud costs

## Rule Categories by Priority

| Priority | Category               | Impact   | Domain     |
| -------- | ---------------------- | -------- | ---------- |
| 1        | Security               | CRITICAL | `security` |
| 2        | State Management       | CRITICAL | `state`    |
| 3        | Module Design          | HIGH     | `module`   |
| 4        | Resource Naming        | HIGH     | `naming`   |
| 5        | Cost Optimization      | MEDIUM   | `cost`     |
| 6        | Tagging Strategy       | MEDIUM   | `tagging`  |
| 7        | Architecture Patterns  | MEDIUM   | `pattern`  |
| 8        | Provider Configuration | LOW      | `provider` |

## Quick Reference

### 1. Security (CRITICAL)

- `no-hardcoded-secrets` - Never hardcode credentials, use variables or secrets manager
- `least-privilege-iam` - Use minimal IAM permissions required
- `encrypt-at-rest` - Enable encryption for all storage resources
- `encrypt-in-transit` - Use TLS/SSL for all network traffic
- `security-groups` - Restrict ingress/egress to required ports only
- `private-subnets` - Place sensitive resources in private subnets
- `enable-logging` - Enable CloudTrail, VPC Flow Logs, access logs

### 2. State Management (CRITICAL)

- `remote-backend` - Use S3/GCS/Azure Blob with state locking
- `state-encryption` - Enable encryption for state files
- `state-isolation` - Separate state per environment
- `state-locking` - Enable DynamoDB/Cloud Storage locking
- `no-local-state` - Never commit .tfstate to version control

### 3. Module Design (HIGH)

- `module-versioning` - Always pin module versions
- `module-inputs` - Use descriptive variable names with validation
- `module-outputs` - Export useful values for composition
- `module-documentation` - Include README with examples
- `module-scope` - Single responsibility per module

### 4. Resource Naming (HIGH)

- `consistent-naming` - Use consistent naming convention
- `include-environment` - Include env in resource names
- `include-region` - Include region code when multi-region
- `avoid-special-chars` - Use only alphanumeric and hyphens

### 5. Cost Optimization (MEDIUM)

- `right-sizing` - Use appropriate instance sizes
- `spot-instances` - Use spot/preemptible for non-critical
- `reserved-capacity` - Use reserved instances for steady workloads
- `lifecycle-policies` - Set S3/storage lifecycle rules
- `auto-scaling` - Implement auto-scaling policies

### 6. Tagging Strategy (MEDIUM)

- `mandatory-tags` - Environment, Project, Owner, CostCenter
- `consistent-tags` - Use consistent tag keys across resources
- `automation-tags` - Add terraform=true tag
- `compliance-tags` - Add compliance/security classification

### 7. Architecture Patterns (MEDIUM)

- `multi-tier` - Web/App/Data tier separation
- `microservices` - Container-based with service mesh
- `serverless` - Lambda/Functions with API Gateway
- `data-lake` - S3/GCS with Glue/BigQuery

### 8. Provider Configuration (LOW)

- `provider-versioning` - Pin provider versions
- `provider-aliases` - Use aliases for multi-region
- `assume-role` - Use assume role for cross-account

## How to Use

Search specific domains using the CLI tool below.

---

## Prerequisites

Check if Python is installed:

```bash
python3 --version || python --version
```

If Python is not installed, install it based on user's OS:

**macOS:**

```bash
brew install python3
```

**Ubuntu/Debian:**

```bash
sudo apt update && sudo apt install python3
```

**Windows:**

```powershell
winget install Python.Python.3.12
```

---

## How to Use This Skill

When user requests Terraform work (create, plan, apply, design, implement, review, fix, improve), follow this workflow:

### Step 1: Analyze User Requirements

Extract key information from user request:

- **Cloud provider**: AWS, Azure, GCP, Kubernetes, etc.
- **Architecture type**: multi-tier, microservices, serverless, data-lake, etc.
- **Environment**: production, staging, development
- **Compliance needs**: HIPAA, SOC2, PCI-DSS, etc.

### Step 2: Generate Infrastructure Design (REQUIRED)

**Always start with `--infra-design`** to get comprehensive recommendations with reasoning:

```bash
python3 scripts/search.py "<architecture_type> <cloud_provider> <keywords>" --infra-design [-p "Project Name"]
```

This command:

1. Searches 5 domains in parallel (provider, pattern, security, module, resource)
2. Applies reasoning rules from `terraform-reasoning.csv` to select best matches
3. Returns complete infrastructure design: architecture, modules, security, state config
4. Includes anti-patterns to avoid

**Example:**

```bash
python3 scripts/search.py "aws microservices eks production" --infra-design -p "MyProject"
```

### Step 2b: Persist Infrastructure Design (Master + Overrides Pattern)

To save the design for **hierarchical retrieval across sessions**, add `--persist`:

```bash
python3 scripts/search.py "<query>" --infra-design --persist -p "Project Name"
```

This creates:

- `infrastructure/MASTER.md` — Global Source of Truth with all infrastructure rules
- `infrastructure/environments/` — Folder for environment-specific overrides

**With environment-specific override:**

```bash
python3 scripts/search.py "<query>" --infra-design --persist -p "Project Name" --env "production"
```

This also creates:

- `infrastructure/environments/production.md` — Environment-specific deviations from Master

### Step 3: Supplement with Detailed Searches (as needed)

After getting the infrastructure design, use domain searches to get additional details:

```bash
python3 scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

**When to use detailed searches:**

| Need                  | Domain          | Example                                     |
| --------------------- | --------------- | ------------------------------------------- |
| Provider configs      | `provider`      | `--domain provider "aws multi-region"`      |
| Resource details      | `resource`      | `--domain resource "eks cluster"`           |
| Security hardening    | `security`      | `--domain security "iam encryption"`        |
| Module examples       | `module`        | `--domain module "vpc networking"`          |
| Architecture patterns | `pattern`       | `--domain pattern "microservices"`          |
| Best practices        | `best-practice` | `--domain best-practice "state management"` |
| State configuration   | `state`         | `--domain state "remote backend"`           |

### Step 4: Generate Terraform Code

After collecting design information, generate code following:

1. **File Structure:**

```
terraform/
├── main.tf           # Main resources
├── variables.tf      # Input variables
├── outputs.tf        # Output values
├── providers.tf      # Provider configuration
├── versions.tf       # Terraform/provider versions
├── locals.tf         # Local values
├── data.tf           # Data sources
├── backend.tf        # Backend configuration
└── modules/          # Custom modules
```

2. **Naming Convention:**

```hcl
# Pattern: {project}-{environment}-{resource}-{identifier}
resource "aws_instance" "myproject_prod_web_001" {
  # ...
}
```

3. **Variable Validation:**

```hcl
variable "environment" {
  type        = string
  description = "Environment name"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

---

## Available Domains

| Domain          | File                     | Description                       |
| --------------- | ------------------------ | --------------------------------- |
| `provider`      | `providers.csv`          | Cloud provider configurations     |
| `resource`      | `resources.csv`          | Resource types and best practices |
| `module`        | `modules.csv`            | Reusable module patterns          |
| `pattern`       | `patterns.csv`           | Architecture patterns             |
| `security`      | `security.csv`           | Security guidelines               |
| `state`         | `state-management.csv`   | State management strategies       |
| `best-practice` | `best-practices.csv`     | General best practices            |
| `naming`        | `naming-conventions.csv` | Naming conventions                |

## Available Cloud Providers

| Provider   | Alias        | Use Cases                   |
| ---------- | ------------ | --------------------------- |
| AWS        | `aws`        | General cloud, enterprise   |
| Azure      | `azurerm`    | Microsoft ecosystem, hybrid |
| GCP        | `google`     | Data/ML, Kubernetes         |
| Kubernetes | `kubernetes` | Container orchestration     |
| Docker     | `docker`     | Container images            |
| Helm       | `helm`       | Kubernetes packages         |
| GitHub     | `github`     | SCM, Actions                |
| Datadog    | `datadog`    | Monitoring                  |
| Cloudflare | `cloudflare` | CDN, DNS, security          |

---

## Common Commands

```bash
# Initialize Terraform
terraform init

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Show state
terraform state list

# Import existing resource
terraform import aws_instance.example i-1234567890abcdef0

# Destroy infrastructure
terraform destroy
```

---

## Integration with Terraform Tools

### Linting with tflint

```bash
tflint --init
tflint
```

### Security scanning with tfsec

```bash
tfsec .
```

### Cost estimation with Infracost

```bash
infracost breakdown --path .
```

### Documentation with terraform-docs

```bash
terraform-docs markdown table . > README.md
```
