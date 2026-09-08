from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = ROOT / "03_Implement/deploy/docker-compose.yml"


def _service_section(compose_text: str, service_name: str) -> list[str]:
    lines = compose_text.splitlines()
    start = next(
        (index for index, line in enumerate(lines) if line == f"  {service_name}:"),
        None,
    )
    if start is None:
        raise AssertionError(f"compose service is missing: {service_name}")
    section: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^  [A-Za-z0-9_.-]+:\s*$", line):
            break
        section.append(line)
    return section


def _nested_block(lines: list[str], *, marker: str, indent: int) -> list[str]:
    prefix = " " * indent + marker
    start = next((index for index, line in enumerate(lines) if line == prefix), None)
    if start is None:
        raise AssertionError(f"compose block is missing: {marker}")
    block: list[str] = []
    for line in lines[start + 1 :]:
        if not line.strip():
            block.append(line)
            continue
        current_indent = len(line) - len(line.lstrip(" "))
        if current_indent <= indent:
            break
        block.append(line)
    return block


def _list_environment_keys(block: list[str]) -> list[str]:
    keys: list[str] = []
    for line in block:
        match = re.match(r"^\s*-\s*(KJ_ATLAS_[A-Z0-9_]+)(?:=|\s*$)", line)
        if match:
            keys.append(match.group(1))
    return keys


def _mapping_keys(block: list[str]) -> list[str]:
    keys: list[str] = []
    for line in block:
        match = re.match(r"^\s*(KJ_ATLAS_[A-Z0-9_]+):", line)
        if match:
            keys.append(match.group(1))
    return keys


class ComposeRuntimeDeliveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        compose_text = COMPOSE_PATH.read_text(encoding="utf-8")
        api = _service_section(compose_text, "api")
        web = _service_section(compose_text, "web")
        cls.api_environment_keys = _list_environment_keys(
            _nested_block(api, marker="environment:", indent=4)
        )
        web_build = _nested_block(web, marker="build:", indent=4)
        cls.web_build_arg_keys = _mapping_keys(
            _nested_block(web_build, marker="args:", indent=6)
        )

    def test_api_public_environment_keys_are_unique(self) -> None:
        duplicates = sorted(
            key for key, count in Counter(self.api_environment_keys).items() if count > 1
        )
        self.assertEqual(duplicates, [], f"duplicate api.environment public keys: {duplicates}")

    def test_app_revision_has_one_api_delivery_and_one_web_build_delivery(self) -> None:
        self.assertEqual(self.api_environment_keys.count("KJ_ATLAS_APP_REVISION"), 1)
        self.assertEqual(self.web_build_arg_keys.count("KJ_ATLAS_APP_REVISION"), 1)

    def test_web_build_public_args_are_unique(self) -> None:
        duplicates = sorted(
            key for key, count in Counter(self.web_build_arg_keys).items() if count > 1
        )
        self.assertEqual(duplicates, [], f"duplicate web build args: {duplicates}")


if __name__ == "__main__":
    unittest.main()
