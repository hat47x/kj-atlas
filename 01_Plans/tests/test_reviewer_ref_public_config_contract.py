from __future__ import annotations

import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / '03_Implement/backend/src/kj_atlas_api/settings.py'
REVIEWER_REF = ROOT / '03_Implement/backend/src/kj_atlas_api/reviewer_ref.py'
API_DOC = ROOT / '02_Architecture/api.md'


def _settings_allowed_values() -> set[str]:
    tree = ast.parse(SETTINGS.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
            continue
        test = node.test
        if not (
            isinstance(test.left, ast.Name)
            and test.left.id == 'normalized_reviewer_ref_adapter'
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.NotIn)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Set)
        ):
            continue
        values = {
            element.value
            for element in test.comparators[0].elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        }
        return values
    raise AssertionError('reviewer-ref Settings allowlist was not found')


class ReviewerRefPublicConfigContractTest(unittest.TestCase):
    def test_public_config_rejects_unknown_adapter_instead_of_falling_back(self) -> None:
        self.assertEqual({'user_id', 'sso_subject'}, _settings_allowed_values())
        settings_text = SETTINGS.read_text(encoding='utf-8')
        self.assertIn(
            'KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER must be one of user_id|sso_subject',
            settings_text,
        )

        api_doc = API_DOC.read_text(encoding='utf-8')
        self.assertIn('不正値は Settings validation で起動時に拒否', api_doc)
        self.assertIn('公開設定経路ではフォールバックしない', api_doc)
        self.assertNotIn(
            'adapter未設定/不正値時は `user_id` フォールバック',
            api_doc,
        )

    def test_factory_unknown_name_fallback_remains_internal_defence(self) -> None:
        source = REVIEWER_REF.read_text(encoding='utf-8')
        self.assertIn(
            'def build_reviewer_ref_resolver_adapter(*, adapter_name: str)',
            source,
        )
        self.assertIn('factory 内部の未知 adapter 名への `user_id` フォールバックは防御的実装', API_DOC.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
