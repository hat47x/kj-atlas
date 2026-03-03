from __future__ import annotations

import json
import os
from pathlib import Path


def profiles_dir() -> Path:
    override = os.getenv("AUTH_PROVIDER_PROFILE_DIR")
    if override:
        return Path(override)
    return Path(__file__).parent / "profiles"


def load_profile(profile_name: str) -> dict:
    path = profiles_dir() / f"{profile_name}.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def profile_names() -> list[str]:
    return sorted(path.stem for path in profiles_dir().glob("*.json"))
