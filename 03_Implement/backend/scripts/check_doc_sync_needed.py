#!/usr/bin/env python3
"""Detect when code changes require corresponding documentation updates.

ADR-0067: Three-Element Constraint Design Method — doc sync automation.

This script checks whether recent code changes touch areas that have
mandatory documentation counterparts. When a change is detected in one
of these areas, the script emits a reminder to update the corresponding doc.

Mappings (code → mandatory doc update):
  settings.py (new KJ_ATLAS_*) → runtime_parameter_registry.md
  models_ai.py (new class) → api.md (if new endpoint) + schemas.md
  routes/*.py (new endpoint) → api.md
  domain/types.ts (new type/field) → schemas.md
  ui/*.tsx (new component) → ui_catalog.md
  App.tsx (new screen/panel) → ui_catalog.md + non-canvas-ui-flow-design.html
  alembic/versions/*.py (new migration) → data_model_operations_overview.html

Exit code 0 = no sync needed or only reminders.
Exit code 1 = mandatory sync missing (CI should warn but not block).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Mapping: changed file pattern → doc files that should be reviewed
DOC_SYNC_MAP: dict[str, list[str]] = {
    "03_Implement/backend/src/kj_atlas_api/settings.py": [
        "02_Architecture/runtime_parameter_registry.md",
    ],
    "03_Implement/backend/src/kj_atlas_api/models_ai.py": [
        "02_Architecture/api.md",
        "02_Architecture/schemas.md",
    ],
    "03_Implement/backend/src/kj_atlas_api/models.py": [
        "02_Architecture/schemas.md",
        "02_Architecture/data_model_operations_overview.html",
    ],
    "03_Implement/backend/src/kj_atlas_api/routes/": [
        "02_Architecture/api.md",
    ],
    "03_Implement/frontend/src/domain/types.ts": [
        "02_Architecture/schemas.md",
    ],
    "03_Implement/frontend/src/ui/": [
        "04_Documentation/ui_catalog.md",
    ],
    "03_Implement/frontend/src/App.tsx": [
        "04_Documentation/ui_catalog.md",
        "02_Architecture/non-canvas-ui-flow-design.html",
    ],
    "03_Implement/backend/alembic/versions/": [
        "02_Architecture/data_model_operations_overview.html",
    ],
    "00_Prompt/": [
        "AGENTS.md",
    ],
    "01_Plans/adr/": [
        "02_Architecture/",
    ],
}


def get_changed_files(base_ref: str = "HEAD") -> list[str]:
    """Get list of changed files compared to base."""
    # Try multiple strategies to find a base commit
    for base_cmd in [
        ["git", "merge-base", "HEAD", "main"],
        ["git", "merge-base", "HEAD", "origin/main"],
        ["git", "rev-parse", "HEAD~5"],
    ]:
        try:
            result = subprocess.run(
                base_cmd, capture_output=True, text=True, cwd=REPO_ROOT,
            )
            if result.returncode == 0 and result.stdout.strip():
                base = result.stdout.strip()
                break
        except Exception:
            continue
    else:
        # Fallback: diff against HEAD (working tree changes)
        base = "HEAD"

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base, "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            files = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            if files:
                return files
        # If no files from commit diff, try working tree diff
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.split("\n") if line.strip()]
    except Exception:
        pass

    return []


def check_doc_sync(changed_files: list[str]) -> tuple[list[str], list[str]]:
    """Check which doc files need updates based on changed code files."""
    reminders: list[str] = []
    missing: list[str] = []

    for changed in changed_files:
        for pattern, docs in DOC_SYNC_MAP.items():
            if changed.startswith(pattern) or (pattern.endswith("/") and pattern[:-1] in changed):
                for doc in docs:
                    doc_path = REPO_ROOT / doc
                    reminder = f"  Code '{changed}' changed → review doc '{doc}'"
                    if reminder not in reminders:
                        reminders.append(reminder)
                    if not doc_path.exists():
                        missing.append(f"  MISSING: doc '{doc}' referenced but does not exist")

    return reminders, missing


def main() -> int:
    print("=== Document Sync Check (ADR-0067) ===")

    changed_files = get_changed_files()
    if not changed_files:
        print("  No changed files detected (or git not available)")
        return 0

    print(f"  Checking {len(changed_files)} changed files...")

    reminders, missing = check_doc_sync(changed_files)

    if reminders:
        print(f"\n  Sync reminders ({len(reminders)}):")
        for r in reminders:
            print(r)

    if missing:
        print(f"\n  MISSING docs ({len(missing)}):")
        for m in missing:
            print(m)
        print("\n  WARNING: Some referenced doc files do not exist.")
        return 1

    if reminders:
        print(f"\n  {len(reminders)} sync reminders — review the listed docs.")
    else:
        print("  No sync needed for changed files.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
