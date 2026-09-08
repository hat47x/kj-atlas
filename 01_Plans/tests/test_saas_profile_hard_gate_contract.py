from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNTIME_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _policy_validate_source() -> str:
    text = RUNTIME_PATH.read_text(encoding="utf-8")
    tree = ast.parse(text)
    policy = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "TrustedSaasRuntimePolicy"
    )
    validate = next(
        node
        for node in policy.body
        if isinstance(node, ast.FunctionDef) and node.name == "validate"
    )
    return ast.get_source_segment(text, validate) or ""


class SaasProfileHardGateContractTests(unittest.TestCase):
    def test_oauth_authorize_and_session_hash_are_startup_hard_gates(self) -> None:
        source = _policy_validate_source()
        self.assertIn(
            "self.saas_oauth_broker_http_authorize_endpoint is not None",
            source,
        )
        self.assertIn("self.saas_auth_session_hash_key is not None", source)

        registry_profile = REGISTRY_PATH.read_text(encoding="utf-8").split(
            "## Profile selection criteria", 1
        )[1].split("### SaaS profile implementation gate", 1)[0]
        self.assertIn("SaaS OAuth broker authorize endpoint", registry_profile)
        self.assertIn("auth-session hash key", registry_profile)

        config_profile = CONFIG_PATH.read_text(encoding="utf-8").split(
            "## Runtime profiles（推奨プロファイル）", 1
        )[1].split("## 最小設定", 1)[0]
        self.assertIn("OAuth authorize endpoint", config_profile)
        self.assertIn("auth-session hash key", config_profile)

    def test_registry_implementation_gate_matches_trusted_saas_runtime_policy(self) -> None:
        source = _policy_validate_source()
        self.assertIn("self.saas_oauth_broker_http_authorize_endpoint is not None", source)
        self.assertIn("self.saas_auth_session_hash_key is not None", source)

        implementation_gate = REGISTRY_PATH.read_text(encoding="utf-8").split(
            "### SaaS profile implementation gate", 1
        )[1].split("### Drift check gates", 1)[0]
        self.assertIn("SaaS OAuth broker authorize endpoint", implementation_gate)
        self.assertIn("auth-session hash key", implementation_gate)

    def test_saas_profile_requires_admin_api_key_across_public_profile_docs(self) -> None:
        settings = (ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py").read_text(encoding="utf-8")
        self.assertIn("if self.admin_api_key is None:", settings)
        self.assertIn('missing.append("KJ_ATLAS_ADMIN_API_KEY")', settings)
        self.assertIn('_AUTH_REQUIRED_PROFILES = ("enterprise-production", "saas-multitenant")', settings)

        registry_profile = REGISTRY_PATH.read_text(encoding="utf-8").split(
            "## Profile selection criteria", 1
        )[1].split("### SaaS profile implementation gate", 1)[0]
        config_profile = CONFIG_PATH.read_text(encoding="utf-8").split(
            "## Runtime profiles（推奨プロファイル）", 1
        )[1].split("## 最小設定", 1)[0]
        self.assertIn("`KJ_ATLAS_ADMIN_API_KEY`", registry_profile)
        self.assertIn("`KJ_ATLAS_ADMIN_API_KEY`", config_profile)

    def test_request_time_oauth_completeness_is_not_promoted_to_startup_gate(self) -> None:
        source = _policy_validate_source()
        for field in (
            "self.saas_oauth_broker_http_token_endpoint is not None",
            "self.saas_oauth_broker_http_redirect_uri is not None",
            "self.saas_oauth_broker_http_client_id is not None",
            "self.saas_oauth_broker_http_client_secret is not None",
        ):
            self.assertNotIn(field, source)

        config_profile = CONFIG_PATH.read_text(encoding="utf-8").split(
            "## Runtime profiles（推奨プロファイル）", 1
        )[1].split("## 最小設定", 1)[0]
        self.assertIn("起動hard gateではなく", config_profile)
        self.assertIn("redirect URI + client ID", config_profile)
        self.assertIn(
            "token endpoint + redirect URI + client ID + client secret",
            config_profile,
        )


if __name__ == "__main__":
    unittest.main()
