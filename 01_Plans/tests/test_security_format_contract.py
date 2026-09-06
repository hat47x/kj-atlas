from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _public_row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith(prefix)
    ]
    if len(rows) != 1:
        raise AssertionError(f"expected one public row for {key} in {path}, got {len(rows)}")
    return rows[0]


def _hex_key_pattern() -> str:
    tree = ast.parse(SETTINGS_PATH.read_text(encoding="utf-8"))
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "_HEX_KEY_PATTERN"
            for target in node.targets
        )
    )
    if not isinstance(assignment.value, ast.Call) or not assignment.value.args:
        raise AssertionError("_HEX_KEY_PATTERN is not a static re.compile call")
    value = ast.literal_eval(assignment.value.args[0])
    if not isinstance(value, str):
        raise AssertionError("_HEX_KEY_PATTERN is not a static string")
    return value


def _settings_validator_source() -> str:
    text = SETTINGS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(text)
    settings_class = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"
    )
    validator = next(
        node
        for node in settings_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "validate_llm_provider_guards"
    )
    if validator.end_lineno is None:
        raise AssertionError("Settings validator source range is unavailable")
    return "\n".join(text.splitlines()[validator.lineno - 1 : validator.end_lineno])


class SecurityFormatContractTests(unittest.TestCase):
    def test_saas_session_hash_key_lowercase_hex_contract_matches_public_docs(self) -> None:
        self.assertEqual(_hex_key_pattern(), r"^[0-9a-f]{64}$")

        registry_row = _public_row(REGISTRY_PATH, "KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY")
        configuration_row = _public_row(CONFIG_PATH, "KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY")

        for row in (registry_row, configuration_row):
            self.assertIn("64", row)
            self.assertIn("lowercase", row)
            self.assertIn("32", row)

    def test_oauth_redirect_uri_fixed_callback_path_matches_public_docs(self) -> None:
        validator = _settings_validator_source()
        self.assertIn(
            'urlsplit(self.saas_oauth_broker_http_redirect_uri).path != "/session/callback"',
            validator,
        )

        for row in (
            _public_row(REGISTRY_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI"),
            _public_row(CONFIG_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI"),
        ):
            self.assertIn("`/session/callback`", row)

    def test_oauth_endpoint_trusted_url_contract_matches_public_docs(self) -> None:
        validator = _settings_validator_source()
        endpoints = (
            (
                "self.saas_oauth_broker_http_authorize_endpoint",
                "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT",
            ),
            (
                "self.saas_oauth_broker_http_token_endpoint",
                "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT",
            ),
            (
                "self.saas_oauth_broker_http_redirect_uri",
                "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI",
            ),
        )

        for field, key in endpoints:
            self.assertIn(
                f'endpoint={field}',
                validator,
            )
            self.assertIn(
                f'endpoint_key="{key}"',
                validator,
            )
            for row in (
                _public_row(REGISTRY_PATH, key),
                _public_row(CONFIG_PATH, key),
            ):
                for term in ("HTTPS", "loopback", "credential", "query", "fragment"):
                    self.assertIn(term, row)

    def test_jwt_public_policy_keeps_default_and_hmac_none_rejection(self) -> None:
        tree = ast.parse(SETTINGS_PATH.read_text(encoding="utf-8"))
        settings_class = next(
            node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"
        )

        jwt_default = None
        for node in settings_class.body:
            if not isinstance(node, ast.AnnAssign) or not isinstance(node.value, ast.Call):
                continue
            kwargs = {kw.arg: kw.value for kw in node.value.keywords if kw.arg is not None}
            alias_node = kwargs.get("validation_alias")
            default_node = kwargs.get("default")
            if alias_node is None or default_node is None:
                continue
            try:
                alias = ast.literal_eval(alias_node)
            except Exception:
                continue
            if alias == "KJ_ATLAS_JWT_ALGORITHMS":
                jwt_default = ast.literal_eval(default_node)
                break
        self.assertEqual(jwt_default, "RS256,ES256")

        for row in (
            _public_row(REGISTRY_PATH, "KJ_ATLAS_JWT_ALGORITHMS"),
            _public_row(CONFIG_PATH, "KJ_ATLAS_JWT_ALGORITHMS"),
        ):
            self.assertIn("RS256,ES256", row)
            self.assertIn("HMAC", row)
            self.assertIn("`none`", row)


if __name__ == "__main__":
    unittest.main()
