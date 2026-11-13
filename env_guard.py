#!/usr/bin/env python3
"""
Env Vault Guard
Zero-dependency validator for .env files against .env.example templates.
Author: Rahul Buriya (rny0007)
License: MIT
"""

import sys
import os
import re
import argparse
import json
from typing import Dict, Set, Tuple


def parse_env_file(filepath: str) -> Dict[str, str]:
    """Parse a standard dotenv file into key-value pairs."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Environment file not found: {filepath}")

    env_vars = {}
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for idx, line in enumerate(f, start=1):
            line = line.strip()
            # Skip empty lines and full comments
            if not line or line.startswith("#"):
                continue
            # Match standard KEY=VALUE format
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
            if match:
                key = match.group(1)
                val = match.group(2)
                # Strip inline comments if not inside quotes
                if val.startswith('"') and val.endswith('"') and len(val) >= 2:
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'") and len(val) >= 2:
                    val = val[1:-1]
                else:
                    # Strip trailing comment
                    val = re.sub(r"\s+#.*$", "", val).strip()
                env_vars[key] = val
    return env_vars


def audit_env(template_path: str, actual_path: str, allow_empty: bool = False, strict: bool = False) -> Dict:
    """Compare actual .env against template .env.example."""
    template_vars = parse_env_file(template_path)
    actual_vars = parse_env_file(actual_path)

    template_keys = set(template_vars.keys())
    actual_keys = set(actual_vars.keys())

    missing_keys = sorted(list(template_keys - actual_keys))
    extra_keys = sorted(list(actual_keys - template_keys))

    empty_keys = []
    if not allow_empty:
        for k in template_keys.intersection(actual_keys):
            if not actual_vars[k].strip():
                empty_keys.append(k)

    passed = (len(missing_keys) == 0 and len(empty_keys) == 0)
    if strict and len(extra_keys) > 0:
        passed = False

    return {
        "template_file": template_path,
        "target_file": actual_path,
        "total_required": len(template_keys),
        "total_provided": len(actual_keys),
        "missing_keys": missing_keys,
        "empty_keys": empty_keys,
        "extra_keys": extra_keys,
        "passed": passed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Env Vault Guard: Validate .env files against .env.example templates"
    )
    parser.add_argument("--template", "-t", default=".env.example", help="Path to example template file")
    parser.add_argument("--env", "-e", default=".env", help="Path to target .env file")
    parser.add_argument("--allow-empty", action="store_true", help="Allow keys with blank/empty values")
    parser.add_argument("--strict", action="store_true", help="Fail if target contains undeclared extra keys")
    parser.add_argument("--json", action="store_true", help="Output audit report in JSON format")
    args = parser.parse_args()

    try:
        report = audit_env(args.template, args.env, args.allow_empty, args.strict)
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["passed"] else 1)

    print("=" * 65)
    print(" 🛡️  ENV VAULT GUARD - ENVIRONMENT AUDIT REPORT")
    print("=" * 65)
    print(f"Template File (.example): {report['template_file']} ({report['total_required']} keys required)")
    print(f"Target Environment File : {report['target_file']} ({report['total_provided']} keys provided)")
    print("-" * 65)

    if report["missing_keys"]:
        print(f"❌ Missing Required Variables ({len(report['missing_keys'])}):")
        for k in report["missing_keys"]:
            print(f"   - {k}")
        print()

    if report["empty_keys"]:
        print(f"⚠️  Blank/Empty Variables ({len(report['empty_keys'])}):")
        for k in report["empty_keys"]:
            print(f"   - {k}")
        print()

    if report["extra_keys"]:
        status = "⚠️  Extra Variables (Undeclared in Template)" if not args.strict else "❌ Disallowed Extra Variables (--strict)"
        print(f"{status} ({len(report['extra_keys'])}):")
        for k in report["extra_keys"]:
            print(f"   - {k}")
        print()

    print("-" * 65)
    if report["passed"]:
        print("✅ PASS: All required environment variables are present and configured.")
        print("=" * 65)
        sys.exit(0)
    else:
        print("❌ FAIL: Environment validation failed. Update environment before deploying.")
        print("=" * 65)
        sys.exit(1)


if __name__ == "__main__":
    main()
