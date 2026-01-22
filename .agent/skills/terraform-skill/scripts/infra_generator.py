#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infrastructure Design Generator - Aggregates search results and applies reasoning
to generate comprehensive Terraform infrastructure design recommendations.

Usage:
    from infra_generator import generate_infra_design
    result = generate_infra_design("aws microservices eks", "My Project")
    
    # With persistence (Master + Overrides pattern)
    result = generate_infra_design("aws microservices eks", "My Project", persist=True)
    result = generate_infra_design("aws microservices eks", "My Project", persist=True, environment="production")
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from core import search, DATA_DIR


# ============ CONFIGURATION ============
REASONING_FILE = "terraform-reasoning.csv"

SEARCH_CONFIG = {
    "reasoning": {"max_results": 1},
    "pattern": {"max_results": 2},
    "provider": {"max_results": 2},
    "module": {"max_results": 3},
    "security": {"max_results": 5},
    "state": {"max_results": 2},
    "best-practice": {"max_results": 3}
}


# ============ INFRASTRUCTURE DESIGN GENERATOR ============
class InfraDesignGenerator:
    """Generates infrastructure design recommendations from aggregated searches."""

    def __init__(self):
        self.reasoning_data = self._load_reasoning()

    def _load_reasoning(self) -> list:
        """Load reasoning rules from CSV."""
        filepath = DATA_DIR / REASONING_FILE
        if not filepath.exists():
            return []
        with open(filepath, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _multi_domain_search(self, query: str) -> dict:
        """Execute searches across multiple domains."""
        results = {}
        for domain, config in SEARCH_CONFIG.items():
            results[domain] = search(query, domain, config["max_results"])
        return results

    def _find_reasoning_rule(self, query: str) -> dict:
        """Find matching reasoning rule for the query."""
        query_lower = query.lower()

        # Try keyword match
        best_match = None
        best_score = 0

        for rule in self.reasoning_data:
            keywords = rule.get("Keywords", "").lower().split(",")
            score = sum(1 for kw in keywords if kw.strip() in query_lower)
            if score > best_score:
                best_score = score
                best_match = rule

        if best_match:
            return best_match

        # Default rule
        return {
            "Architecture Type": "General",
            "Recommended Provider": "aws",
            "Recommended Pattern": "Three-Tier Web Application",
            "Module Priority": "terraform-aws-vpc, terraform-aws-rds",
            "Security Priority": "encrypt-at-rest, restrict-security-groups",
            "State Strategy": "isolate-state-per-env",
            "Cost Strategy": "right-sizing, auto-scaling",
            "Complexity": "Medium",
            "Decision Rules": "{}"
        }

    def _extract_results(self, search_result: dict) -> list:
        """Extract results list from search result dict."""
        return search_result.get("results", [])

    def generate(self, query: str, project_name: str = None) -> dict:
        """Generate complete infrastructure design recommendation."""
        # Step 1: Get reasoning rules for this query
        reasoning = self._find_reasoning_rule(query)

        # Step 2: Multi-domain search
        search_results = self._multi_domain_search(query)

        # Step 3: Extract best matches from each domain
        pattern_results = self._extract_results(search_results.get("pattern", {}))
        provider_results = self._extract_results(search_results.get("provider", {}))
        module_results = self._extract_results(search_results.get("module", {}))
        security_results = self._extract_results(search_results.get("security", {}))
        state_results = self._extract_results(search_results.get("state", {}))
        best_practice_results = self._extract_results(search_results.get("best-practice", {}))

        best_pattern = pattern_results[0] if pattern_results else {}
        best_provider = provider_results[0] if provider_results else {}

        # Parse decision rules
        decision_rules = {}
        try:
            decision_rules = json.loads(reasoning.get("Decision Rules", "{}"))
        except json.JSONDecodeError:
            pass

        return {
            "project_name": project_name or query.upper(),
            "architecture_type": reasoning.get("Architecture Type", "General"),
            "pattern": {
                "name": best_pattern.get("Pattern Name", reasoning.get("Recommended Pattern", "")),
                "category": best_pattern.get("Category", ""),
                "description": best_pattern.get("Description", ""),
                "components": best_pattern.get("Components", ""),
                "terraform_structure": best_pattern.get("Terraform Structure", ""),
                "complexity": best_pattern.get("Complexity", reasoning.get("Complexity", "Medium"))
            },
            "provider": {
                "name": best_provider.get("Provider Name", reasoning.get("Recommended Provider", "aws")),
                "registry": best_provider.get("Registry Name", ""),
                "version": best_provider.get("Version Constraint", ""),
                "authentication": best_provider.get("Authentication Method", ""),
                "config_example": best_provider.get("Configuration Example", "")
            },
            "modules": [
                {
                    "name": m.get("Module Name", ""),
                    "source": m.get("Source", ""),
                    "description": m.get("Description", ""),
                    "example": m.get("Example Usage", "")
                }
                for m in module_results[:3]
            ],
            "security": {
                "priority_rules": reasoning.get("Security Priority", "").split(", "),
                "rules": [
                    {
                        "rule_id": s.get("Rule ID", ""),
                        "severity": s.get("Severity", ""),
                        "description": s.get("Description", ""),
                        "do": s.get("Do", ""),
                        "dont": s.get("Don't", ""),
                        "compliance": s.get("Compliance", "")
                    }
                    for s in security_results[:5]
                ]
            },
            "state_management": {
                "strategy": reasoning.get("State Strategy", "isolate-state-per-env"),
                "rules": [
                    {
                        "rule_id": st.get("Rule ID", ""),
                        "severity": st.get("Severity", ""),
                        "description": st.get("Description", ""),
                        "do": st.get("Do", "")
                    }
                    for st in state_results[:2]
                ]
            },
            "best_practices": [
                {
                    "rule_id": bp.get("Rule ID", ""),
                    "category": bp.get("Category", ""),
                    "description": bp.get("Description", ""),
                    "do": bp.get("Do", "")
                }
                for bp in best_practice_results[:3]
            ],
            "cost_strategy": reasoning.get("Cost Strategy", "right-sizing"),
            "decision_rules": decision_rules,
            "generated_at": datetime.now().isoformat()
        }


def generate_infra_design(query: str, project_name: str = None, format: str = "markdown",
                          persist: bool = False, environment: str = None, output_dir: str = None) -> str:
    """Generate infrastructure design and optionally persist it."""
    generator = InfraDesignGenerator()
    design = generator.generate(query, project_name)

    output = format_design_output(design, format)

    if persist:
        persist_infra_design(design, output_dir, environment)

    return output


def format_design_output(design: dict, format: str = "markdown") -> str:
    """Format design output for display."""
    if format == "markdown":
        return _format_markdown(design)
    else:
        return _format_ascii(design)


def _format_markdown(design: dict) -> str:
    """Format as markdown."""
    lines = []
    lines.append(f"# Infrastructure Design: {design['project_name']}")
    lines.append(f"\n**Architecture Type:** {design['architecture_type']}")
    lines.append(f"**Generated:** {design['generated_at']}")

    # Pattern
    lines.append("\n## Architecture Pattern")
    pattern = design['pattern']
    lines.append(f"**Pattern:** {pattern['name']}")
    lines.append(f"**Category:** {pattern['category']}")
    lines.append(f"**Description:** {pattern['description']}")
    lines.append(f"**Components:** {pattern['components']}")
    lines.append(f"**Terraform Structure:** `{pattern['terraform_structure']}`")
    lines.append(f"**Complexity:** {pattern['complexity']}")

    # Provider
    lines.append("\n## Provider Configuration")
    provider = design['provider']
    lines.append(f"**Provider:** {provider['name']}")
    lines.append(f"**Registry:** {provider['registry']}")
    lines.append(f"**Version:** {provider['version']}")
    lines.append(f"**Authentication:** {provider['authentication']}")
    lines.append(f"\n```hcl\n{provider['config_example']}\n```")

    # Modules
    lines.append("\n## Recommended Modules")
    for m in design['modules']:
        lines.append(f"\n### {m['name']}")
        lines.append(f"**Source:** `{m['source']}`")
        lines.append(f"**Description:** {m['description']}")
        if m['example']:
            lines.append(f"\n```hcl\n{m['example']}\n```")

    # Security
    lines.append("\n## Security Guidelines")
    security = design['security']
    lines.append(f"**Priority Rules:** {', '.join(security['priority_rules'])}")
    lines.append("\n| Rule ID | Severity | Description | Compliance |")
    lines.append("|---------|----------|-------------|------------|")
    for rule in security['rules']:
        lines.append(f"| {rule['rule_id']} | {rule['severity']} | {rule['description'][:50]}... | {rule['compliance']} |")

    # State Management
    lines.append("\n## State Management")
    state = design['state_management']
    lines.append(f"**Strategy:** {state['strategy']}")
    for rule in state['rules']:
        lines.append(f"\n- **{rule['rule_id']}** ({rule['severity']}): {rule['description']}")
        lines.append(f"  - Do: {rule['do']}")

    # Best Practices
    lines.append("\n## Best Practices")
    for bp in design['best_practices']:
        lines.append(f"\n### {bp['rule_id']} ({bp['category']})")
        lines.append(f"{bp['description']}")
        lines.append(f"- **Do:** {bp['do']}")

    # Cost Strategy
    lines.append("\n## Cost Optimization")
    lines.append(f"**Strategy:** {design['cost_strategy']}")

    # Decision Rules
    if design['decision_rules']:
        lines.append("\n## Decision Rules")
        for key, value in design['decision_rules'].items():
            lines.append(f"- **{key}:** {value}")

    return "\n".join(lines)


def _format_ascii(design: dict) -> str:
    """Format as ASCII box."""
    lines = []
    width = 80

    def box_line(text, char="─"):
        return f"│ {text:<{width-4}} │"

    def separator(char="─"):
        return f"├{'─' * (width-2)}┤"

    lines.append(f"┌{'─' * (width-2)}┐")
    lines.append(box_line(f"INFRASTRUCTURE DESIGN: {design['project_name']}"))
    lines.append(separator())
    lines.append(box_line(f"Architecture: {design['architecture_type']}"))
    lines.append(box_line(f"Pattern: {design['pattern']['name']}"))
    lines.append(box_line(f"Provider: {design['provider']['name']} ({design['provider']['version']})"))
    lines.append(separator())
    lines.append(box_line("MODULES:"))
    for m in design['modules']:
        lines.append(box_line(f"  • {m['name']}"))
    lines.append(separator())
    lines.append(box_line("SECURITY RULES:"))
    for rule in design['security']['rules'][:3]:
        lines.append(box_line(f"  • [{rule['severity']}] {rule['rule_id']}"))
    lines.append(separator())
    lines.append(box_line(f"State Strategy: {design['state_management']['strategy']}"))
    lines.append(box_line(f"Cost Strategy: {design['cost_strategy']}"))
    lines.append(f"└{'─' * (width-2)}┘")

    return "\n".join(lines)


def persist_infra_design(design: dict, output_dir: str = None, environment: str = None):
    """Persist infrastructure design to files."""
    base_dir = Path(output_dir) if output_dir else Path.cwd()
    project_slug = design['project_name'].lower().replace(' ', '-')
    project_dir = base_dir / "infrastructure" / project_slug

    # Create directories
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "environments").mkdir(exist_ok=True)

    # Write MASTER.md
    master_content = _format_markdown(design)
    master_content = f"""---
project: {design['project_name']}
architecture: {design['architecture_type']}
provider: {design['provider']['name']}
generated: {design['generated_at']}
---

{master_content}

---

## File Structure

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
    ├── networking/
    ├── compute/
    ├── database/
    └── security/
```

## Usage

```bash
# Initialize
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan
```
"""
    (project_dir / "MASTER.md").write_text(master_content, encoding='utf-8')

    # Write environment-specific file if requested
    if environment:
        env_slug = environment.lower().replace(' ', '-')
        env_content = f"""---
environment: {environment}
inherits: ../MASTER.md
---

# Environment: {environment}

This file contains environment-specific overrides for {design['project_name']}.

## Overrides from Master

### Variables

```hcl
# Environment-specific variable values
environment = "{env_slug}"

# Adjust based on environment
instance_type = "{'t3.large' if env_slug == 'production' else 't3.micro'}"
min_capacity  = {'3' if env_slug == 'production' else '1'}
max_capacity  = {'10' if env_slug == 'production' else '3'}
```

### State Backend

```hcl
terraform {{
  backend "s3" {{
    bucket         = "tf-state-{project_slug}"
    key            = "{env_slug}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "tf-locks-{project_slug}"
  }}
}}
```

### Security Considerations

{f'- Enable all security features' if env_slug == 'production' else '- Relaxed security for development'}
{f'- Multi-AZ deployment required' if env_slug == 'production' else '- Single AZ acceptable'}
{f'- Enable detailed monitoring' if env_slug == 'production' else '- Basic monitoring sufficient'}

### Cost Considerations

{f'- Use reserved instances' if env_slug == 'production' else '- Use spot instances where possible'}
{f'- Enable auto-scaling with conservative limits' if env_slug == 'production' else '- Minimal resources, scale down at night'}
"""
        (project_dir / "environments" / f"{env_slug}.md").write_text(env_content, encoding='utf-8')


# ============ MAIN ============
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = generate_infra_design(query, format="markdown")
        print(result)
