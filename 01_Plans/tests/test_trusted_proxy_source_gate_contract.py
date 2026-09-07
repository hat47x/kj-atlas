from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
AUTH_CONTEXT = ROOT / '03_Implement/backend/src/kj_atlas_api/auth_context.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'


def _function_source(path: Path, name: str) -> str:
    source = path.read_text(encoding='utf-8')
    tree = ast.parse(source)
    fn = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )
    return ast.get_source_segment(source, fn) or ''


class TrustedProxySourceGateContractTest(unittest.TestCase):
    def test_source_gate_runs_before_any_forwarded_header_read(self) -> None:
        source = _function_source(AUTH_CONTEXT, 'resolve_identity_context')
        gate = source.index('_check_trusted_proxy(request)')
        first_header_read = source.index('_header(request, settings.auth_provider_field)')
        self.assertLess(gate, first_header_read)

    def test_configured_gate_uses_request_client_and_rejects_untrusted_source(self) -> None:
        source = _function_source(AUTH_CONTEXT, '_check_trusted_proxy')
        self.assertIn('request.client.host', source)
        self.assertIn('if not raw_cidrs:', source)
        self.assertIn('return  # Not configured', source)
        self.assertIn('"code": "untrusted_proxy"', source)
        self.assertIn('Request did not originate from a trusted proxy.', source)

    def test_public_rows_name_pre_header_source_gate_scope(self) -> None:
        for path in (CONFIG, REGISTRY):
            text = path.read_text(encoding='utf-8')
            row = next(
                line for line in text.splitlines()
                if line.startswith('| `KJ_ATLAS_TRUSTED_PROXIES` |')
            )
            self.assertIn('single-tenant', row)
            self.assertIn('request.client.host', row)
            self.assertIn('header', row)
            self.assertIn('403', row)
            self.assertIn('untrusted_proxy', row)
            self.assertIn('saas-multitenant', row)


if __name__ == '__main__':
    unittest.main()
