from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / '03_Implement/backend/src/sui_sensemaking_api/main.py'
GUEST_ROUTE = ROOT / '03_Implement/backend/src/sui_sensemaking_api/routes/guest_session.py'
GUEST_AUTH = ROOT / '03_Implement/backend/src/sui_sensemaking_api/guest_request_auth.py'
GUEST_REDEEM = ROOT / '03_Implement/backend/src/sui_sensemaking_api/guest_redeem.py'
CONFIG = ROOT / '04_Documentation/configuration.md'
REGISTRY = ROOT / '02_Architecture/runtime_parameter_registry.md'


class AuthSessionHashKeyScopeContractTest(unittest.TestCase):
    def test_one_runtime_key_is_wired_to_member_guest_and_redeem_consumers(self) -> None:
        main = MAIN.read_text(encoding='utf-8')
        self.assertIn('app.state.saas_auth_session_hash_key = _saas_auth_session_hash_key', main)
        self.assertIn('app.state.guest_auth_session_hash_key = _saas_auth_session_hash_key', main)
        self.assertIn('app.state.guest_redeem_state_hash_key = _saas_auth_session_hash_key', main)

        guest_route = GUEST_ROUTE.read_text(encoding='utf-8')
        self.assertIn('guest_redeem_state_hash_key', guest_route)
        self.assertIn('guest_auth_session_hash_key', guest_route)

        guest_auth = GUEST_AUTH.read_text(encoding='utf-8')
        self.assertIn('guest_auth_session_hash_key', guest_auth)
        self.assertIn('derive_session_key_hash(raw_session_id, key=hash_key)', guest_auth)

        redeem = GUEST_REDEEM.read_text(encoding='utf-8')
        self.assertIn('_REDEEM_STATE_DOMAIN = "guest-redeem-v1\\x00"', redeem)
        self.assertIn('derive_session_key_hash(_REDEEM_STATE_DOMAIN + raw_state, key=hash_key)', redeem)

    def test_public_contract_names_all_rotation_impacts(self) -> None:
        for path in (CONFIG, REGISTRY):
            text = path.read_text(encoding='utf-8')
            row = next(
                line for line in text.splitlines()
                if line.startswith('| `SUI_SAAS_AUTH_SESSION_HASH_KEY` |')
            )
            self.assertIn('member', row)
            self.assertIn('guest auth session', row)
            self.assertIn('guest redeem state', row)
            self.assertIn('未使用redeem state', row)
            self.assertIn('無効化', row)


if __name__ == '__main__':
    unittest.main()
