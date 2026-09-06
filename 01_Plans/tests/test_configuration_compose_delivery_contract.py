from __future__ import annotations

import re
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
COMPOSE_PATH = ROOT / "03_Implement/deploy/docker-compose.yml"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _service_section(text: str, service: str) -> str:
    match = re.search(
        rf"(?ms)^  {re.escape(service)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_.-]+:\s*$|\Z)",
        text,
    )
    if match is None:
        raise AssertionError(f"compose service is missing: {service}")
    return match.group("body")


def _api_environment_keys(compose_text: str) -> list[str]:
    api = _service_section(compose_text, "api")
    block = re.search(r"(?ms)^    environment:\n(?P<body>.*?)(?=^    \S|\Z)", api)
    if block is None:
        raise AssertionError("api.environment is missing")
    return re.findall(r"^      - (KJ_ATLAS_[A-Z0-9_]+)(?:=|\s*$)", block.group("body"), re.M)


def _web_build_arg_keys(compose_text: str) -> list[str]:
    web = _service_section(compose_text, "web")
    block = re.search(r"(?ms)^      args:\n(?P<body>.*?)(?=^      \S|^    \S|\Z)", web)
    if block is None:
        raise AssertionError("web.build.args is missing")
    return re.findall(r"^        (KJ_ATLAS_[A-Z0-9_]+):", block.group("body"), re.M)


def _documented_surface_keys(config_text: str, surface: str) -> list[str]:
    row = next(
        (line for line in config_text.splitlines() if line.startswith(f"| `{surface}` |")),
        None,
    )
    if row is None:
        raise AssertionError(f"configuration delivery row is missing: {surface}")
    return re.findall(r"`(KJ_ATLAS_[A-Z0-9_]+)`", row)


def _first_bash_block(section: str) -> str:
    return section.split("```bash", 1)[1].split("```", 1)[0]


class ConfigurationComposeDeliveryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.compose_text = COMPOSE_PATH.read_text(encoding="utf-8")
        cls.config_text = CONFIG_PATH.read_text(encoding="utf-8")

    def _assert_same_unique_keys(self, actual: list[str], documented: list[str], surface: str) -> None:
        duplicates = sorted(key for key, count in Counter(documented).items() if count > 1)
        self.assertEqual(duplicates, [], f"duplicate documented keys for {surface}: {duplicates}")
        self.assertEqual(set(documented), set(actual), f"configuration drift for {surface}")

    def test_api_environment_delivery_matches_configuration(self) -> None:
        self._assert_same_unique_keys(
            _api_environment_keys(self.compose_text),
            _documented_surface_keys(self.config_text, "api.environment"),
            "api.environment",
        )

    def test_web_build_args_delivery_matches_configuration(self) -> None:
        self._assert_same_unique_keys(
            _web_build_arg_keys(self.compose_text),
            _documented_surface_keys(self.config_text, "web.build.args"),
            "web.build.args",
        )

    def test_stale_two_key_compose_claim_is_absent(self) -> None:
        self.assertNotIn(
            "`KJ_ATLAS_DATABASE_URL` と `KJ_ATLAS_LLM_PROVIDER` の2キーだけ",
            self.config_text,
        )

    def test_standard_compose_minimal_example_does_not_claim_api_base_passthrough(self) -> None:
        section = self.config_text.split("## 最小設定", 1)[1].split("## Backend 環境変数", 1)[0]
        self.assertNotIn("KJ_ATLAS_FRONTEND_API_BASE", _first_bash_block(section))

    def test_standard_compose_evaluation_example_does_not_claim_api_base_passthrough(self) -> None:
        section = self.config_text.split("### Docker Compose 評価", 1)[1].split("### API key 付き検証", 1)[0]
        self.assertNotIn("KJ_ATLAS_FRONTEND_API_BASE", _first_bash_block(section))

    def test_direct_frontend_build_keeps_api_base_as_public_build_input(self) -> None:
        section = self.config_text.split("直接frontend buildを実行する場合", 1)[1].split("## API キーを有効にする", 1)[0]
        self.assertIn("export KJ_ATLAS_FRONTEND_API_BASE=/api", _first_bash_block(section))


if __name__ == "__main__":
    unittest.main()
