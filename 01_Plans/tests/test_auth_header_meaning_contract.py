from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
AUTH_CONTEXT = ROOT / '03_Implement/backend/src/kj_atlas_api/auth_context.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'
API_DOC = ROOT / '02_Architecture/api.md'

def _resolve_function() -> ast.FunctionDef:
    tree = ast.parse(AUTH_CONTEXT.read_text(encoding='utf-8'))
    return next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == 'resolve_identity_context')

class AuthHeaderMeaningContractTest(unittest.TestCase):
    def test_subject_precedes_legacy_user_header_for_external_uid(self) -> None:
        fn = _resolve_function()
        assignment = next(node for node in fn.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'external_uid' for target in node.targets))
        self.assertIsInstance(assignment.value, ast.BoolOp)
        self.assertIsInstance(assignment.value.op, ast.Or)
        attrs = []
        for value in assignment.value.values:
            self.assertIsInstance(value, ast.Call)
            header_arg = value.args[1]
            self.assertIsInstance(header_arg, ast.Attribute)
            attrs.append(header_arg.attr)
        self.assertEqual(['auth_subject_field', 'auth_user_field'], attrs)

    def test_provider_is_normalized_and_user_id_comes_from_identity_mapping(self) -> None:
        source = AUTH_CONTEXT.read_text(encoding='utf-8')
        self.assertIn('provider = _normalize_provider(_header(request, settings.auth_provider_field))', source)
        self.assertIn('return raw_provider.strip().lower() or "header"', source)
        self.assertIn('identity = _resolve_identity_row(db=db, provider=provider, external_uid=external_uid)', source)
        self.assertIn('user_id = identity.user_id', source)

    def test_email_and_name_are_only_loaded_into_new_user_row(self) -> None:
        fn = _resolve_function()
        jit_if = next(node for node in fn.body if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and isinstance(node.test.left, ast.Name) and node.test.left.id == 'identity' and any(isinstance(op, ast.Is) for op in node.test.ops))
        user_row_call = next(node for node in ast.walk(ast.Module(body=jit_if.body, type_ignores=[])) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'UserRow')
        keywords = {kw.arg: kw.value for kw in user_row_call.keywords}
        self.assertIsInstance(keywords['display_name'], ast.Name)
        self.assertEqual('display_name', keywords['display_name'].id)
        self.assertIsInstance(keywords['email'], ast.Name)
        self.assertEqual('email', keywords['email'].id)
        loads = [node.id for node in ast.walk(fn) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id in {'display_name', 'email'}]
        self.assertEqual(1, loads.count('display_name'))
        self.assertEqual(1, loads.count('email'))

    def test_public_surfaces_describe_runtime_meaning(self) -> None:
        config = CONFIG.read_text(encoding='utf-8')
        registry = REGISTRY.read_text(encoding='utf-8')
        api_doc = API_DOC.read_text(encoding='utf-8')
        self.assertIn('内部 `users.id` を直接指定しない', config)
        self.assertIn('JIT provisioning時に新規 `UserRow.email` を初期化', config)
        self.assertIn('JIT provisioning時に新規 `UserRow.display_name` を初期化', config)
        self.assertIn('内部 `users.id` はidentity mappingから解決', registry)
        self.assertIn('`AUTH_USER_FIELD` は内部 `users.id` の指定ではない', api_doc)
        self.assertIn('既存user属性をheaderで上書きしない', api_doc)

if __name__ == '__main__':
    unittest.main()
