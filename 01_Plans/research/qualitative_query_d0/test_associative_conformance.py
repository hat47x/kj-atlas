from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from associative_channel import normalize_associative_response  # noqa: E402
from associative_process import invoke_associative_provider  # noqa: E402

FIXTURE_PATH = ROOT / "fixtures" / "associative_contract_conformance_v1.json"
PROVIDER_PATH = ROOT / "fixtures" / "synthetic_associative_provider.py"
EXPECTED_DIGEST = "a9a627e3ce3580dab010608efd30d11e84de2c66a39dcb6ff508d793c00260d2"


def canonical_request_bytes(request: dict) -> bytes:
    return json.dumps(
        request,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class AssociativeContractConformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.request = cls.fixture["request"]

    def test_fixture_identity_and_canonical_digest_are_frozen(self) -> None:
        self.assertEqual(
            self.fixture["schema"],
            "sui.associative-contract-conformance-fixture/v1alpha1",
        )
        self.assertEqual(
            self.fixture["fixtureId"], "sui-sei-associative-conformance-v1"
        )
        self.assertEqual(self.fixture["requestCanonicalSha256"], EXPECTED_DIGEST)
        actual = hashlib.sha256(canonical_request_bytes(self.request)).hexdigest()
        self.assertEqual(actual, EXPECTED_DIGEST)

    def test_fixture_is_exactly_formal_request_surface(self) -> None:
        self.assertEqual(
            set(self.request),
            {
                "schema",
                "requestId",
                "networkId",
                "intent",
                "anchorRefs",
                "items",
                "policy",
            },
        )
        serialized = canonical_request_bytes(self.request).decode("utf-8")
        for forbidden in (
            "reviewState",
            "permission",
            "credential",
            "score",
            "confidence",
            "activation",
            "similarity",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_fixture_round_trips_through_process_and_d2_normalizer(self) -> None:
        response = invoke_associative_provider(
            self.request,
            [sys.executable, str(PROVIDER_PATH), "valid"],
        )
        channel = normalize_associative_response(self.request, response)
        self.assertEqual(channel["channel"], "associative_sparse")
        self.assertEqual(channel["anchorRefs"], ["c1"])
        self.assertEqual(channel["candidateRefs"], ["c2", "c3"])
        self.assertFalse(channel["trace"]["semanticAuthority"])

    def test_fixture_canonicalization_is_whitespace_independent(self) -> None:
        compact = canonical_request_bytes(self.request)
        reparsed = json.loads(compact.decode("utf-8"))
        pretty = json.dumps(reparsed, ensure_ascii=False, indent=4)
        self.assertEqual(
            hashlib.sha256(canonical_request_bytes(json.loads(pretty))).hexdigest(),
            EXPECTED_DIGEST,
        )


if __name__ == "__main__":
    unittest.main()
