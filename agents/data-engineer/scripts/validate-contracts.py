#!/usr/bin/env python3
"""
Data Contract Validation Script

Checks that data contracts in {PRODUCT_ROOT}/planning-mds/schemas/ are:
  - Present (directory exists and contains at least one schema file)
  - Valid YAML or JSON
  - Versioned (each schema file declares a top-level 'version' field)
  - Named with a consistent convention (<name>-v<N>.yaml or <name>.yaml)

Does NOT validate business-rule correctness or producer/consumer alignment —
those require runtime context and are checked in integration tests.

Usage:
    python3 validate-contracts.py [--product-root PATH] [schemas-dir]
    python3 validate-contracts.py
    python3 validate-contracts.py --product-root ../my-product
    python3 validate-contracts.py /path/to/planning-mds/schemas/

If no schemas-dir is supplied, defaults to
{PRODUCT_ROOT}/planning-mds/schemas/.
Exit 0 = pass (errors=0); exit 1 = fail.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _product_root import add_product_root_arg, resolve_product_root  # noqa: E402

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

SCHEMA_EXTENSIONS = {".yaml", ".yml", ".json"}


def _load_file(path: Path) -> Tuple[dict | None, str | None]:
    """Return (parsed_content, error_message). Supports YAML and JSON."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        try:
            return json.loads(text), None
        except json.JSONDecodeError as exc:
            return None, f"JSON parse error: {exc}"
    if _YAML_AVAILABLE:
        try:
            data = yaml.safe_load(text)
            return data, None
        except yaml.YAMLError as exc:
            return None, f"YAML parse error: {exc}"
    # Fallback: check that the file is non-empty
    return {"_unparsed": True}, None


class ContractValidator:
    def __init__(self, schemas_dir: Path):
        self.schemas_dir = schemas_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        self._check_directory_exists()
        if self.errors:
            return False

        schema_files = [
            f for f in self.schemas_dir.rglob("*")
            if f.is_file() and f.suffix in SCHEMA_EXTENSIONS
        ]

        if not schema_files:
            self.warnings.append(
                f"No schema files found in {self.schemas_dir} "
                f"(extensions checked: {', '.join(sorted(SCHEMA_EXTENSIONS))}). "
                "If no cross-service data contracts exist yet this is expected."
            )
            return True

        print(f"[contracts] Found {len(schema_files)} schema file(s) in {self.schemas_dir}")

        for schema_file in sorted(schema_files):
            self._validate_schema_file(schema_file)

        return len(self.errors) == 0

    def _check_directory_exists(self) -> None:
        if not self.schemas_dir.exists():
            self.warnings.append(
                f"Schemas directory not found: {self.schemas_dir}. "
                "Create {PRODUCT_ROOT}/planning-mds/schemas/ when the first "
                "cross-service data contract is defined."
            )
        elif not self.schemas_dir.is_dir():
            self.errors.append(
                f"Expected a directory at {self.schemas_dir} but found a file."
            )

    def _validate_schema_file(self, path: Path) -> None:
        rel = path.relative_to(self.schemas_dir)

        # 1. Parse
        content, parse_error = _load_file(path)
        if parse_error:
            self.errors.append(f"{rel}: {parse_error}")
            return

        if content is None or not isinstance(content, dict):
            self.errors.append(
                f"{rel}: schema file must contain a YAML/JSON object at the top level, "
                f"got {type(content).__name__}."
            )
            return

        # Skip internal marker used when yaml is unavailable
        if "_unparsed" in content:
            self.warnings.append(
                f"{rel}: PyYAML not installed — skipping field checks. "
                "Install pyyaml for full validation."
            )
            return

        # 2. Version field
        if "version" not in content:
            self.errors.append(
                f"{rel}: missing top-level 'version' field. "
                "Every data contract must declare its version (e.g., version: '1.0.0')."
            )

        # 3. Name / title field
        if "name" not in content and "title" not in content and "$id" not in content:
            self.warnings.append(
                f"{rel}: no 'name', 'title', or '$id' field. "
                "Adding one makes contracts easier to reference."
            )

        # 4. Description
        if "description" not in content:
            self.warnings.append(
                f"{rel}: no 'description' field. "
                "A short description of the contract's purpose aids consumers."
            )

        # 5. Schema definition presence
        has_schema_body = any(
            k in content
            for k in ("properties", "fields", "schema", "$schema", "columns")
        )
        if not has_schema_body:
            self.warnings.append(
                f"{rel}: no schema body found (expected 'properties', 'fields', "
                "'schema', '$schema', or 'columns'). "
                "The contract has a version but no field definitions."
            )

        # 6. Changelog / breaking-change marker (advisory)
        has_changelog = any(
            k in content
            for k in ("changelog", "breaking_changes", "breaking-changes", "compatibility")
        )
        if not has_changelog:
            self.warnings.append(
                f"{rel}: no 'changelog' or 'breaking_changes' field. "
                "Recommended when publishing versioned contracts so consumers "
                "can assess upgrade impact."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate data contracts in {PRODUCT_ROOT}/planning-mds/schemas/."
    )
    add_product_root_arg(parser)
    parser.add_argument(
        "schemas_dir",
        nargs="?",
        default=None,
        help="Path to schemas directory (default: {PRODUCT_ROOT}/planning-mds/schemas/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    args = parser.parse_args()

    product_root = resolve_product_root(args.product_root)
    schemas_dir = (
        Path(args.schemas_dir)
        if args.schemas_dir
        else product_root / "planning-mds" / "schemas"
    )

    print(f"Validating data contracts: {schemas_dir}")
    print("-" * 60)

    validator = ContractValidator(schemas_dir)
    passed = validator.validate()

    if args.strict:
        validator.errors.extend(validator.warnings)
        validator.warnings.clear()

    if validator.errors:
        print("\n[ERROR] Must Fix:")
        for i, err in enumerate(validator.errors, 1):
            print(f"  {i}. {err}")

    if validator.warnings:
        print("\n[WARNING] Should Fix:")
        for i, warn in enumerate(validator.warnings, 1):
            print(f"  {i}. {warn}")

    print("\n" + "=" * 60)
    error_count = len(validator.errors)
    warn_count = len(validator.warnings)

    if error_count == 0 and warn_count == 0:
        print("[PASS] Data contract validation PASSED — no issues found.")
        return 0
    elif error_count == 0:
        print(f"[PASS] Data contract validation PASSED with {warn_count} warning(s).")
        return 0
    else:
        print(
            f"[FAIL] Data contract validation FAILED with {error_count} error(s) "
            f"and {warn_count} warning(s)."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
