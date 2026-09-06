from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
SAAS_POLICY = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"
MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"


def _profile_row(registry: str, profile: str) -> list[str]:
    section = registry.split("## Runtime profiles", 1)[1].split(
        "### Profile default vs recommendation", 1
    )[0]
    prefix = f"| `{profile}` |"
    rows = [line for line in section.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {profile}, got {len(rows)}")
    return [cell.strip() for cell in rows[0].strip().strip("|").split("|")]


class ProductionProfileRequiredSettingsContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")
        self.settings = SETTINGS.read_text(encoding="utf-8")
        self.saas_policy = SAAS_POLICY.read_text(encoding="utf-8")
        self.main = MAIN.read_text(encoding="utf-8")

    def test_enterprise_profile_exposes_settings_fail_fast_credentials(self) -> None:
        required = _profile_row(self.registry, "enterprise-production")[2]
        self.assertIn("`KJ_ATLAS_ADMIN_API_KEY=<secret>`", required)
        self.assertIn("`KJ_ATLAS_API_KEY=<secret>`", required)
        self.assertIn('if self.admin_api_key is None:', self.settings)
        self.assertIn(
            'if profile == "enterprise-production" and self.api_key is None:',
            self.settings,
        )
        summary = next(
            line
            for line in self.configuration.splitlines()
            if line.startswith("- `enterprise-production`:")
        )
        self.assertIn("`KJ_ATLAS_ADMIN_API_KEY`", summary)
        self.assertIn("`KJ_ATLAS_API_KEY`", summary)

    def test_saas_profile_exposes_startup_hard_gate_without_promoting_callback_only_fields(self) -> None:
        row = _profile_row(self.registry, "saas-multitenant")
        required, notes = row[2], row[3]
        required_tokens = (
            "`KJ_ATLAS_ADMIN_API_KEY=<secret>`",
            "`KJ_ATLAS_DATABASE_URL=<PostgreSQL URL>`",
            "`KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`",
            "`KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`",
            "`KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT=<HTTPS URL>`",
            "`KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny`",
            "`KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER=external_http`",
            "`KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT=<HTTPS URL>`",
            "`KJ_ATLAS_TENANT_CAPABILITY_RESOLVER=external_http`",
            "`KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT=<HTTPS URL>`",
            "`KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT=<HTTPS URL>`",
            "`KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY=<64 lowercase hex>`",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, required)

        hard_gate_fragments = (
            'self.database_backend == "postgresql"',
            'not self.allow_jit_provisioning',
            'self.access_control_adapter == "external_http"',
            'self.access_control_fail_safe_mode == "deny"',
            'self.document_policy_binding_resolver == "external_http"',
            'self.tenant_capability_resolver == "external_http"',
            'self.saas_oauth_broker_http_authorize_endpoint is not None',
            'self.saas_auth_session_hash_key is not None',
        )
        for fragment in hard_gate_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.saas_policy)

        for endpoint_key in (
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
            "KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT",
            "KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT",
        ):
            self.assertIn(endpoint_key, self.settings)

        self.assertIn("token endpoint / redirect URI / client ID / client secret", notes)
        self.assertIn("503", notes)
        callback_guard = (
            "if token_endpoint is None or redirect_uri is None or client_id is None "
            "or client_secret is None:"
        )
        self.assertIn(callback_guard, self.main)
        self.assertIn(
            "return None",
            self.main.split(callback_guard, 1)[1].split(
                "return ExternalOauthBrokerConfig", 1
            )[0],
        )

        summary = next(
            line
            for line in self.configuration.splitlines()
            if line.startswith("- `saas-multitenant`:")
        )
        for fragment in (
            "`KJ_ATLAS_ADMIN_API_KEY`",
            "PostgreSQL",
            "OAuth authorize endpoint",
            "auth-session hash key",
        ):
            self.assertIn(fragment, summary)


if __name__ == "__main__":
    unittest.main()
