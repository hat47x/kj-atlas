from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUTH_CONTEXT = ROOT / '03_Implement/backend/src/kj_atlas_api/auth_context.py'
TRUSTED_AUTH_EDGE = ROOT / '03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py'
SAAS_REQUEST_CONTEXT = ROOT / '03_Implement/backend/src/kj_atlas_api/saas_request_context.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'
API_DOC = ROOT / '02_Architecture/api.md'

FIELDS = {
    'KJ_ATLAS_AUTH_PROVIDER_FIELD': 'auth_provider_field',
    'KJ_ATLAS_AUTH_USER_FIELD': 'auth_user_field',
    'KJ_ATLAS_AUTH_EMAIL_FIELD': 'auth_email_field',
    'KJ_ATLAS_AUTH_NAME_FIELD': 'auth_name_field',
    'KJ_ATLAS_AUTH_SUBJECT_FIELD': 'auth_subject_field',
}


class AuthHeaderFieldScopeContractTest(unittest.TestCase):
    def test_settings_fields_are_consumed_by_forwarded_header_resolver(self) -> None:
        source = AUTH_CONTEXT.read_text(encoding='utf-8')
        self.assertIn('Only applies to single-tenant header-based auth.', source)
        self.assertIn('def resolve_identity_context(*, db: Session, request: Request)', source)
        for attr in FIELDS.values():
            self.assertIn(f'settings.{attr}', source)

    def test_saas_jwt_cookie_resolver_does_not_consume_header_name_settings(self) -> None:
        saas_sources = (
            TRUSTED_AUTH_EDGE.read_text(encoding='utf-8')
            + SAAS_REQUEST_CONTEXT.read_text(encoding='utf-8')
        )
        self.assertIn('class JwtSaasIdentityContextResolver', saas_sources)
        for attr in FIELDS.values():
            self.assertNotIn(f'settings.{attr}', saas_sources)

    def test_public_surfaces_state_single_tenant_only_scope(self) -> None:
        config = CONFIG.read_text(encoding='utf-8')
        registry = REGISTRY.read_text(encoding='utf-8')
        api_doc = API_DOC.read_text(encoding='utf-8')
        scope = 'single-tenant の forwarded-header identity path'
        exclusion = '`saas-multitenant` の trusted JWT/cookie path では使用しない'
        for key in FIELDS:
            config_row = next(line for line in config.splitlines() if line.startswith(f'| `{key}` |'))
            registry_row = next(line for line in registry.splitlines() if line.startswith(f'| `{key}` |'))
            self.assertIn(scope, config_row)
            self.assertIn(exclusion, config_row)
            self.assertIn(scope, registry_row)
            self.assertIn(exclusion, registry_row)
        self.assertIn(scope + ' の入力ヘッダ', api_doc)
        self.assertIn(exclusion, api_doc)


if __name__ == '__main__':
    unittest.main()
