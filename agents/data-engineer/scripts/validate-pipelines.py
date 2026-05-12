#!/usr/bin/env python3
"""
Data Pipeline Validation Script

Checks the data layer directory declared in {PRODUCT_ROOT}/planning-mds/BLUEPRINT.md
(or a supplied path) for:
  - Migrations directory present and non-empty
  - Pipeline definitions directory present (warns if absent, not an error when no
    pipelines have been declared yet)
  - Each migration file follows the naming convention: a leading numeric prefix
    (e.g. 001_, 0001_, or a timestamp prefix) so ordering is unambiguous
  - No duplicate migration version prefixes
  - Pipeline files contain at least one idempotency keyword
    (idempotent, upsert, on conflict, merge into, insert or ignore,
    insert or replace, dedupl, deduplicate)
  - Quality rules directory present when stories declared quality scope
  - No hardcoded credential patterns in any data-layer file

Usage:
    python3 validate-pipelines.py [--product-root PATH] [data-layer-dir]
    python3 validate-pipelines.py
    python3 validate-pipelines.py --product-root ../my-product
    python3 validate-pipelines.py /path/to/data-layer/

If no data-layer-dir is supplied, the script looks for a 'data-layer' key in
BLUEPRINT.md, then falls back to common directory names
(data/, data-layer/, pipelines/, etl/).
Exit 0 = pass (errors=0); exit 1 = fail.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _product_root import add_product_root_arg, resolve_product_root  # noqa: E402

# Migration file naming: must start with digits (version prefix)
MIGRATION_VERSION_RE = re.compile(r"^(\d+)[_\-]")

# Idempotency signal words searched case-insensitively in pipeline source files
IDEMPOTENCY_KEYWORDS = [
    "idempotent",
    "upsert",
    "on conflict",
    "merge into",
    "insert or ignore",
    "insert or replace",
    "deduplic",   # covers deduplicate / deduplication
    "if not exists",
    "insert_or_update",
    "replace into",
]

# Credential patterns that must not appear in data-layer files
CREDENTIAL_PATTERNS = [
    (re.compile(r"password\s*=\s*['\"][^'\"]{3,}['\"]", re.IGNORECASE), "hardcoded password"),
    (re.compile(r"(secret|api_key|apikey|token)\s*=\s*['\"][A-Za-z0-9+/=_\-]{8,}['\"]",
                re.IGNORECASE), "hardcoded secret/key/token"),
    (re.compile(r"(host|server)\s*=\s*['\"][a-z0-9\-\.]{4,}['\"]",
                re.IGNORECASE), "hardcoded host/server"),
]

# Common data-layer root directory names to probe when BLUEPRINT.md is absent
FALLBACK_LAYER_NAMES = ["data", "data-layer", "pipelines", "etl", "dbt"]

CODE_EXTENSIONS = {
    ".py", ".sql", ".yaml", ".yml", ".json",
    ".sh", ".hql", ".scala", ".java", ".ts", ".js",
}


def _find_data_layer(product_root: Path) -> Optional[Path]:
    """Probe BLUEPRINT.md for a data-layer declaration, then fall back."""
    blueprint = product_root / "planning-mds" / "BLUEPRINT.md"
    if blueprint.exists():
        text = blueprint.read_text(encoding="utf-8")
        match = re.search(
            r"data[_\-\s]?layer[_\-\s]?(?:directory|dir|path|root)?\s*[:=]\s*`?([^\s`\n]+)`?",
            text,
            re.IGNORECASE,
        )
        if match:
            candidate = product_root / match.group(1).strip("/")
            if candidate.exists():
                return candidate

    for name in FALLBACK_LAYER_NAMES:
        candidate = product_root / name
        if candidate.is_dir():
            return candidate

    return None


class PipelineValidator:
    def __init__(self, data_layer: Path, product_root: Path):
        self.data_layer = data_layer
        self.product_root = product_root
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> bool:
        if not self.data_layer.exists():
            self.warnings.append(
                f"Data layer directory not found: {self.data_layer}. "
                "Create it when the first data artifact is introduced by a story."
            )
            return True  # not an error when no data scope yet

        self._check_migrations()
        self._check_pipelines()
        self._check_quality()
        self._check_credentials()

        return len(self.errors) == 0

    # ------------------------------------------------------------------ #
    # Migrations
    # ------------------------------------------------------------------ #

    def _check_migrations(self) -> None:
        migrations_dir = self.data_layer / "migrations"
        if not migrations_dir.exists():
            self.warnings.append(
                f"No 'migrations/' subdirectory in {self.data_layer}. "
                "Expected when stories declare schema changes."
            )
            return

        migration_files = sorted(
            f for f in migrations_dir.iterdir()
            if f.is_file() and not f.name.startswith(".")
        )

        if not migration_files:
            self.warnings.append(
                f"{migrations_dir.relative_to(self.product_root)}: "
                "directory exists but contains no migration files."
            )
            return

        print(f"[migrations] Found {len(migration_files)} migration file(s).")

        version_prefixes: List[Tuple[str, str]] = []
        for mf in migration_files:
            match = MIGRATION_VERSION_RE.match(mf.name)
            if not match:
                self.errors.append(
                    f"Migration file '{mf.name}' does not start with a numeric version "
                    "prefix (e.g., '001_', '20260101_'). Migrations must be unambiguously "
                    "ordered by filename."
                )
            else:
                version_prefixes.append((match.group(1), mf.name))

        # Duplicate version prefix check
        seen: dict[str, str] = {}
        for prefix, fname in version_prefixes:
            if prefix in seen:
                self.errors.append(
                    f"Duplicate migration version prefix '{prefix}': "
                    f"'{seen[prefix]}' and '{fname}'. "
                    "Each migration must have a unique version prefix."
                )
            else:
                seen[prefix] = fname

    # ------------------------------------------------------------------ #
    # Pipelines
    # ------------------------------------------------------------------ #

    def _check_pipelines(self) -> None:
        pipelines_dir = self.data_layer / "pipelines"
        if not pipelines_dir.exists():
            self.warnings.append(
                f"No 'pipelines/' subdirectory in {self.data_layer}. "
                "Expected when stories declare ETL/ELT pipeline scope."
            )
            return

        pipeline_files = [
            f for f in pipelines_dir.rglob("*")
            if f.is_file() and f.suffix in CODE_EXTENSIONS
        ]

        if not pipeline_files:
            self.warnings.append(
                f"{pipelines_dir.relative_to(self.product_root)}: "
                "directory exists but contains no pipeline source files."
            )
            return

        print(f"[pipelines] Found {len(pipeline_files)} pipeline file(s).")

        no_idempotency: List[str] = []
        for pf in pipeline_files:
            try:
                text = pf.read_text(encoding="utf-8", errors="replace").lower()
            except OSError:
                continue
            if not any(kw in text for kw in IDEMPOTENCY_KEYWORDS):
                no_idempotency.append(
                    str(pf.relative_to(self.data_layer))
                )

        if no_idempotency:
            self.errors.append(
                f"The following pipeline file(s) contain no recognizable idempotency "
                f"mechanism ({', '.join(IDEMPOTENCY_KEYWORDS[:4])}, ...):\n"
                + "\n".join(f"    - {p}" for p in no_idempotency)
            )

    # ------------------------------------------------------------------ #
    # Quality rules
    # ------------------------------------------------------------------ #

    def _check_quality(self) -> None:
        quality_dir = self.data_layer / "quality"
        if not quality_dir.exists():
            self.warnings.append(
                f"No 'quality/' subdirectory in {self.data_layer}. "
                "Expected when stories declare data quality validation scope."
            )
            return

        quality_files = [
            f for f in quality_dir.rglob("*")
            if f.is_file() and f.suffix in CODE_EXTENSIONS
        ]
        if not quality_files:
            self.warnings.append(
                f"{quality_dir.relative_to(self.product_root)}: "
                "quality/ directory exists but contains no rule files."
            )
        else:
            print(f"[quality]    Found {len(quality_files)} quality rule file(s).")

    # ------------------------------------------------------------------ #
    # Credential leak detection
    # ------------------------------------------------------------------ #

    def _check_credentials(self) -> None:
        all_data_files = [
            f for f in self.data_layer.rglob("*")
            if f.is_file() and f.suffix in CODE_EXTENSIONS
        ]

        hits: List[str] = []
        for df in all_data_files:
            try:
                text = df.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern, label in CREDENTIAL_PATTERNS:
                if pattern.search(text):
                    hits.append(
                        f"{df.relative_to(self.data_layer)}: {label} pattern detected"
                    )

        if hits:
            self.errors.append(
                "Possible hardcoded credentials found in data-layer files:\n"
                + "\n".join(f"    - {h}" for h in hits)
                + "\nUse environment variables or a secrets manager instead."
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate data pipeline artifacts in the project data layer."
    )
    add_product_root_arg(parser)
    parser.add_argument(
        "data_layer_dir",
        nargs="?",
        default=None,
        help=(
            "Path to the data-layer root directory "
            "(default: auto-detected from BLUEPRINT.md or common names)"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors.",
    )
    args = parser.parse_args()

    product_root = resolve_product_root(args.product_root)

    if args.data_layer_dir:
        data_layer = Path(args.data_layer_dir)
    else:
        data_layer = _find_data_layer(product_root)
        if data_layer is None:
            print(
                "[WARNING] Could not locate data layer directory. "
                "Checked BLUEPRINT.md and common names: "
                + ", ".join(FALLBACK_LAYER_NAMES)
            )
            print(
                "Pass the path explicitly: "
                "python3 validate-pipelines.py /path/to/data-layer/"
            )
            print("\n" + "=" * 60)
            print("[PASS] Data pipeline validation PASSED — no data layer found (skipped).")
            return 0

    print(f"Validating data pipeline artifacts: {data_layer}")
    print("-" * 60)

    validator = PipelineValidator(data_layer, product_root)
    validator.validate()

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
        print("[PASS] Data pipeline validation PASSED — no issues found.")
        return 0
    elif error_count == 0:
        print(f"[PASS] Data pipeline validation PASSED with {warn_count} warning(s).")
        return 0
    else:
        print(
            f"[FAIL] Data pipeline validation FAILED with {error_count} error(s) "
            f"and {warn_count} warning(s)."
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
