#!/usr/bin/env python3
"""Classify changed repository paths for heavyweight application CI jobs."""
from __future__ import annotations

import sys
from dataclasses import dataclass

FRONTEND_PREFIX = "03_Implement/frontend/"
BACKEND_PREFIX = "03_Implement/backend/"
RUN_ALL_PATHS = {
    ".github/workflows/ci.yml",
    "01_Plans/ci_change_scope.py",
    "01_Plans/tests/test_ci_change_scope.py",
}


@dataclass(frozen=True)
class ChangeScope:
    frontend: bool
    backend: bool


def classify_changes(paths: list[str]) -> ChangeScope:
    normalized = {path.strip().replace("\\", "/") for path in paths if path.strip()}
    run_all = bool(normalized & RUN_ALL_PATHS)
    return ChangeScope(
        frontend=run_all or any(path.startswith(FRONTEND_PREFIX) for path in normalized),
        backend=run_all or any(path.startswith(BACKEND_PREFIX) for path in normalized),
    )


def main() -> int:
    scope = classify_changes(sys.stdin.readlines())
    print(f"frontend={str(scope.frontend).lower()}")
    print(f"backend={str(scope.backend).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
