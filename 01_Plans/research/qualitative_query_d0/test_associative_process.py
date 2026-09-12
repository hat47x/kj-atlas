from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from associative_channel import build_associative_request  # noqa: E402
from associative_process import (  # noqa: E402
    AssociativeProviderProcessError,
    execute_associative_channel_via_process,
    invoke_associative_provider,
)
from query_engine import D0Network  # noqa: E402

NETWORK_PATH = ROOT / "fixtures" / "network.json"
PROVIDER_PATH = ROOT / "fixtures" / "synthetic_associative_provider.py"


class AssociativeProviderProcessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = json.loads(NETWORK_PATH.read_text(encoding="utf-8"))
        self.network = D0Network(self.source)

    def command(self, mode: str = "valid") -> list[str]:
        return [sys.executable, str(PROVIDER_PATH), mode]

    def request(self) -> dict:
        return build_associative_request(
            self.network,
            request_id="process-1",
            intent="neighborhood",
            anchor_refs=["c1"],
            scope_refs=["c1", "c2", "c3"],
            candidate_limit=2,
        )

    def test_formal_request_process_response_normalization_e2e(self) -> None:
        before = copy.deepcopy(self.source)
        result = execute_associative_channel_via_process(
            self.network,
            self.command(),
            request_id="process-1",
            intent="neighborhood",
            anchor_refs=["c1"],
            scope_refs=["c1", "c2", "c3"],
            candidate_limit=2,
        )
        self.assertEqual(result["channel"], "associative_sparse")
        self.assertEqual(result["anchorRefs"], ["c1"])
        self.assertEqual(result["candidateRefs"], ["c2", "c3"])
        self.assertEqual(result["trace"]["providerId"], "synthetic-process-provider")
        self.assertFalse(result["trace"]["semanticAuthority"])
        self.assertEqual(self.source, before)

    def test_nonzero_exit_keeps_diagnostic_out_of_response(self) -> None:
        with self.assertRaisesRegex(
            AssociativeProviderProcessError,
            "exited with code 7: synthetic provider failure",
        ):
            invoke_associative_provider(self.request(), self.command("fail"))

    def test_timeout_kills_provider(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "timed out"):
            invoke_associative_provider(
                self.request(), self.command("sleep"), timeout_seconds=0.05
            )

    def test_invalid_json_stdout_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            AssociativeProviderProcessError, "not one valid UTF-8 JSON value"
        ):
            invoke_associative_provider(self.request(), self.command("invalid-json"))

    def test_duplicate_json_key_fails_closed(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "duplicate JSON key"):
            invoke_associative_provider(self.request(), self.command("duplicate-key"))

    def test_contract_invalid_response_fails_before_d2_channel(self) -> None:
        with self.assertRaisesRegex(
            AssociativeProviderProcessError,
            "violates associative contract",
        ):
            execute_associative_channel_via_process(
                self.network,
                self.command("contract-invalid"),
                request_id="process-invalid",
                intent="neighborhood",
                anchor_refs=["c1"],
                scope_refs=["c1", "c2"],
                candidate_limit=1,
            )

    def test_request_size_limit_is_checked_before_spawn(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "request exceeds"):
            invoke_associative_provider(
                self.request(), self.command(), max_request_bytes=16
            )

    def test_response_size_limit_is_checked_before_reading_json(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "response exceeds"):
            invoke_associative_provider(
                self.request(), self.command(), max_response_bytes=32
            )

    def test_argv_must_be_explicit_sequence_not_shell_string(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "sequence of strings"):
            invoke_associative_provider(self.request(), "python provider.py")

    def test_missing_executable_fails_closed(self) -> None:
        with self.assertRaisesRegex(AssociativeProviderProcessError, "could not start"):
            invoke_associative_provider(
                self.request(), ["/definitely/not/a/provider/binary"]
            )

    def test_invalid_limits_fail_before_spawn(self) -> None:
        for kwargs in (
            {"timeout_seconds": 0},
            {"max_request_bytes": True},
            {"max_response_bytes": 0},
            {"max_diagnostic_bytes": -1},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(AssociativeProviderProcessError):
                    invoke_associative_provider(self.request(), self.command(), **kwargs)


if __name__ == "__main__":
    unittest.main()
