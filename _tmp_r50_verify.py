from __future__ import annotations

import json
from pathlib import Path


def load(path: str) -> dict[str, object]:
    return json.loads(Path(path).read_text())


dry = load("/tmp/ai-ir-scale-dry-run.json")
assert dry["executed"] is False
assert dry["measurement_complete"] is False
assert dry["expected_provider"] == "deepseek"
assert dry["expected_model"] == "deepseek-v4-flash"
assert dry["expected_deepseek_thinking_mode"] == "disabled"
routes = dry["routes"]
assert isinstance(routes, dict)
assert len(routes) == 6
assert all(row["status"] == "dry-run" for row in routes.values())
assert all(row["provider_call"] is None for row in routes.values())

blocked = load("/tmp/ai-ir-scale-no-opt-in.json")
assert blocked["measurement_complete"] is False
assert blocked["status"] == "external-execution-not-opted-in"
assert blocked["required_env"] == "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"
