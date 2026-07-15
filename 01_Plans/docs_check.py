#!/usr/bin/env python3
"""Run the repository documentation checks through one local/CI entrypoint."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def check_commands(root: Path = ROOT) -> list[list[str]]:
    python = sys.executable
    plans = root / "01_Plans"
    return [
        [python, "-m", "unittest", "discover", "-s", str(plans / "tests"), "-p", "test_*.py"],
        [python, "-m", "unittest", "discover", "-s", str(plans / "issues" / "tests"), "-p", "test_*.py"],
        [python, str(plans / "issues" / "validate_active_issue_memos.py"), "--root", str(plans / "issues")],
        [python, str(plans / "docs_contract_checks.py"), "--root", str(root)],
    ]


def main() -> int:
    for command in check_commands():
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode:
            return result.returncode
    print("docs-check: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
