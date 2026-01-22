#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Terraform Skill Search - BM25 search engine for Terraform best practices
Usage: python search.py "<query>" [--domain <domain>] [--max-results 3]
       python search.py "<query>" --infra-design [-p "Project Name"]
       python search.py "<query>" --infra-design --persist [-p "Project Name"] [--env "production"]

Domains: provider, resource, module, pattern, security, state, best-practice

Persistence (Master + Overrides pattern):
  --persist    Save infrastructure design to infrastructure/MASTER.md
  --env        Also create an environment-specific override file
"""

import argparse
from core import CSV_CONFIG, AVAILABLE_DOMAINS, MAX_RESULTS, search, search_multi_domain
from infra_generator import generate_infra_design, persist_infra_design


def format_output(result):
    """Format results for Claude consumption (token-optimized)"""
    if "error" in result:
        return f"Error: {result['error']}"

    output = []
    output.append(f"## Terraform Skill Search Results")
    output.append(f"**Domain:** {result['domain']} | **Query:** {result['query']}")
    output.append(f"**Source:** {result['file']} | **Found:** {result['count']} results\n")

    for i, row in enumerate(result['results'], 1):
        output.append(f"### Result {i}")
        for key, value in row.items():
            value_str = str(value)
            if len(value_str) > 500:
                value_str = value_str[:500] + "..."
            output.append(f"- **{key}:** {value_str}")
        output.append("")

    return "\n".join(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Terraform Skill Search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--domain", "-d", choices=list(CSV_CONFIG.keys()), help="Search domain")
    parser.add_argument("--max-results", "-n", type=int, default=MAX_RESULTS, help="Max results (default: 3)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    # Infrastructure design generation
    parser.add_argument("--infra-design", "-id", action="store_true", help="Generate complete infrastructure design recommendation")
    parser.add_argument("--project-name", "-p", type=str, default=None, help="Project name for infrastructure design output")
    parser.add_argument("--format", "-f", choices=["ascii", "markdown"], default="markdown", help="Output format for infrastructure design")
    # Persistence (Master + Overrides pattern)
    parser.add_argument("--persist", action="store_true", help="Save infrastructure design to infrastructure/MASTER.md")
    parser.add_argument("--env", type=str, default=None, help="Create environment-specific override file")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Output directory for persisted files (default: current directory)")

    args = parser.parse_args()

    # Infrastructure design takes priority
    if args.infra_design:
        result = generate_infra_design(
            args.query, 
            args.project_name, 
            args.format,
            persist=args.persist,
            environment=args.env,
            output_dir=args.output_dir
        )
        print(result)
        
        # Print persistence confirmation
        if args.persist:
            project_slug = args.project_name.lower().replace(' ', '-') if args.project_name else "default"
            print("\n" + "=" * 60)
            print(f"✅ Infrastructure design persisted to infrastructure/{project_slug}/")
            print(f"   📄 infrastructure/{project_slug}/MASTER.md (Global Source of Truth)")
            if args.env:
                env_filename = args.env.lower().replace(' ', '-')
                print(f"   📄 infrastructure/{project_slug}/environments/{env_filename}.md (Environment Overrides)")
            print("")
            print(f"📖 Usage: When building for a specific environment, check infrastructure/{project_slug}/environments/[env].md first.")
            print(f"   If exists, its rules override MASTER.md. Otherwise, use MASTER.md.")
            print("=" * 60)
    # Domain search
    else:
        result = search(args.query, args.domain, args.max_results)
        if args.json:
            import json
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_output(result))
