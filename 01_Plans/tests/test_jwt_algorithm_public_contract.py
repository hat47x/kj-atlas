from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / '03_Implement/backend/src/kj_atlas_api/settings.py'
AUTH_EDGE = ROOT / '03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'
API_DOC = ROOT / '02_Architecture/api.md'

def _known_algorithms() -> set[str]:
    tree = ast.parse(SETTINGS.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == '_KNOWN_JWT_ALGORITHMS' for target in node.targets):
            continue
        value = node.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id == 'frozenset':
            value = value.args[0]
        if isinstance(value, (ast.Set, ast.List, ast.Tuple)):
            return {e.value for e in value.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)}
    raise AssertionError('_KNOWN_JWT_ALGORITHMS not found')

def _row(text: str, key: str) -> str:
    matches = [line for line in text.splitlines() if line.startswith(f'| `{key}` |')]
    if len(matches) != 1:
        raise AssertionError(f'{key}: expected one row, got {len(matches)}')
    return matches[0]

def _documented_algorithms(row: str) -> set[str]:
    return set(re.findall(r'`((?:RS|ES|PS)\d{3})`', row))

class JwtAlgorithmPublicContractTest(unittest.TestCase):
    def test_public_rows_name_exact_settings_allowlist(self) -> None:
        expected = _known_algorithms()
        self.assertEqual(expected, _documented_algorithms(_row(CONFIG.read_text(encoding='utf-8'), 'KJ_ATLAS_JWT_ALGORITHMS')))
        self.assertEqual(expected, _documented_algorithms(_row(REGISTRY.read_text(encoding='utf-8'), 'KJ_ATLAS_JWT_ALGORITHMS')))

    def test_settings_and_auth_edge_enforce_configured_allowlist(self) -> None:
        settings_source = SETTINGS.read_text(encoding='utf-8')
        self.assertIn('must contain at least one algorithm', settings_source)
        self.assertIn('must not contain HMAC algorithms', settings_source)
        self.assertIn('contains unknown algorithms', settings_source)
        self.assertNotIn('HS256', _known_algorithms())
        self.assertNotIn('none', _known_algorithms())
        edge_source = AUTH_EDGE.read_text(encoding='utf-8')
        self.assertIn('settings.jwt_algorithms.split(",")', edge_source)
        self.assertNotIn('Algorithm allowlist: RS256, ES256 only', edge_source)

    def test_profile_and_api_distinguish_default_from_requirement(self) -> None:
        registry = REGISTRY.read_text(encoding='utf-8')
        self.assertNotIn('`KJ_ATLAS_JWT_ALGORITHMS=RS256,ES256`', registry)
        self.assertIn('未指定は既定 `RS256,ES256`', registry)
        self.assertIn('既知の非HMAC asymmetric algorithm', registry)
        api_doc = API_DOC.read_text(encoding='utf-8')
        self.assertIn('`KJ_ATLAS_JWT_ALGORITHMS` の検証済みallowlist', api_doc)
        self.assertIn('HMAC/`none`/未知algorithmは受理しない', api_doc)

if __name__ == '__main__':
    unittest.main()
