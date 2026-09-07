from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / '03_Implement/backend/src/kj_atlas_api/main.py'
RUNTIME = ROOT / '03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'

class SaasProviderStartupSemanticsContractTest(unittest.TestCase):
    def test_provider_check_is_post_db_and_non_throwing_diagnostic(self) -> None:
        main = MAIN.read_text(encoding='utf-8')
        self.assertLess(main.index('init_db()'), main.index('validate_saas_providers_exist()'))
        runtime_source = RUNTIME.read_text(encoding='utf-8')
        tree = ast.parse(runtime_source)
        fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'validate_saas_providers_exist')
        self.assertNotIn(ast.Raise, {type(node) for node in ast.walk(fn)})
        doc = ' '.join((ast.get_docstring(fn) or '').split())
        self.assertIn('warning rather than blocking startup', doc)
        source = ast.get_source_segment(runtime_source, fn) or ''
        self.assertIn('logger.warning(', source)
        self.assertIn('POST /admin/provision/identity-providers', source)

    def test_registry_distinguishes_hard_gate_from_provider_diagnostic(self) -> None:
        registry = REGISTRY.read_text(encoding='utf-8')
        self.assertNotIn('起動前preflightとprovider存在検査を通過できる。1つでも欠ける場合はfail-fast', registry)
        self.assertIn('active IdP存在検査はpost-DB-initのwarning診断', registry)
        self.assertIn('provider 0件自体はstartup拒否条件ではない', registry)
        self.assertIn('0件でもprocess startupは拒否せずwarningを出す', registry)
        self.assertIn('最初のproviderを登録でき', registry)

if __name__ == '__main__':
    unittest.main()
