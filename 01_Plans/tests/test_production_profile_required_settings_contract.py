from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"
SETTINGS = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
SAAS_POLICY = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"
MAIN = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
OAUTH_BFF = ROOT / "03_Implement/backend/src/kj_atlas_api/oauth_bff.py"


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
        self.oauth_bff = OAUTH_BFF.read_text(encoding="utf-8")

    def test_nonproduction_profiles_keep_recommendations_out_of_startup_required(self) -> None:
        self.assertIn("Startup-required conditions", self.registry)
        self.assertIn("Recommended / conditional settings", self.registry)
        local = _profile_row(self.registry, "local-dev")
        evaluation = _profile_row(self.registry, "evaluation")
        self.assertEqual(local[2], "なし（追加のprofile固有hard gateなし）")
        self.assertEqual(evaluation[2], "なし（追加のprofile固有hard gateなし）")
        for token in ("KJ_ATLAS_DATABASE_URL", "KJ_ATLAS_LLM_PROVIDER", "KJ_ATLAS_ALLOW_JIT_PROVISIONING"):
            self.assertIn(token, local[3])
        for token in ("KJ_ATLAS_DATABASE_URL", "KJ_ATLAS_LLM_PROVIDER", "KJ_ATLAS_AUDIT_TRANSPORT", "KJ_ATLAS_ACCESS_CONTROL_ADAPTER"):
            self.assertIn(token, evaluation[3])

    def test_enterprise_profile_exposes_settings_fail_fast_credentials(self) -> None:
        row = _profile_row(self.registry, "enterprise-production")
        required, operating = row[2], row[3]
        self.assertIn("`KJ_ATLAS_ADMIN_API_KEY=<secret>`", required)
        self.assertIn("`KJ_ATLAS_API_KEY=<secret>`", required)
        for token in (
            "KJ_ATLAS_ALLOW_JIT_PROVISIONING",
            "KJ_ATLAS_LLM_PROVIDER",
            "KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE",
        ):
            self.assertNotIn(token, required)
            self.assertIn(token, operating)
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

    def test_oauth_bff_conditional_rows_expose_request_phase_requiredness(self) -> None:
        backend = self.registry.split("## Backend settings", 1)[1].split(
            "## Compose and frontend build keys", 1
        )[0]
        token_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT"
        redirect_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI"
        client_id_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID"
        secret_key = "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET"
        keys = (token_key, redirect_key, client_id_key, secret_key)
        registry_rows = {
            key: next(line for line in backend.splitlines() if line.startswith(f"| `{key}` |"))
            for key in keys
        }
        config_rows = {
            key: next(line for line in self.configuration.splitlines() if line.startswith(f"| `{key}` |"))
            for key in keys
        }
        for key in (redirect_key, client_id_key):
            self.assertIn("login", registry_rows[key])
            self.assertIn("login", config_rows[key])
        for key in keys:
            self.assertIn("callback", registry_rows[key])
            self.assertIn("503", registry_rows[key])
            self.assertIn("callback", config_rows[key])
            self.assertIn("503", config_rows[key])
        self.assertIn(
            "if not authorize_endpoint or not client_id or not redirect_uri:",
            self.oauth_bff,
        )
        self.assertIn('503, "oauth_login_unavailable"', self.oauth_bff)
        self.assertIn('503, "oauth_broker_unavailable"', self.oauth_bff)

    def test_saas_profile_separates_startup_hard_gate_from_bff_request_conditions(self) -> None:
        row = _profile_row(self.registry, "saas-multitenant")
        required, conditional, notes = row[2], row[3], row[4]
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

        callback_only = (
            "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT",
            "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI",
            "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID",
            "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET",
        )
        for key in callback_only:
            self.assertNotIn(key, required)
            self.assertIn(key, conditional)
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
