from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from projection_request import (  # noqa: E402
    ProjectionRequestError,
    canonical_json,
    normalize_projection_request,
    selection_input_fingerprint,
)

REQUESTS_PATH = ROOT / "fixtures" / "projection_requests.json"


class ProjectionRequestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requests = json.loads(REQUESTS_PATH.read_text(encoding="utf-8"))

    def base(self) -> dict:
        return copy.deepcopy(self.requests["sameContrast"][0])

    def test_formal_request_is_closed_world(self) -> None:
        request = self.base()
        request["legacyField"] = True
        with self.assertRaisesRegex(ProjectionRequestError, "unknown keys"):
            normalize_projection_request(request)

    def test_permission_must_be_server_resolved(self) -> None:
        request = self.base()
        request["permission"]["resolutionSource"] = "requester_declared"
        with self.assertRaisesRegex(ProjectionRequestError, "server_resolved"):
            normalize_projection_request(request)

    def test_role_never_grants_permission(self) -> None:
        request = self.base()
        request["roles"] = ["approve", "publish"]
        request["permission"]["canApprove"] = False
        request["permission"]["canPublish"] = False
        normalized, _ = normalize_projection_request(request)
        self.assertEqual(normalized["roles"], ["approve", "publish"])
        self.assertFalse(normalized["permission"]["canApprove"])
        self.assertFalse(normalized["permission"]["canPublish"])

    def test_unreviewed_visibility_is_permission_and_safemode(self) -> None:
        request = copy.deepcopy(self.requests["unreviewedNeighborhood"])
        _, strict = normalize_projection_request(
            request, safe_mode_allows_unreviewed=False
        )
        _, allowed = normalize_projection_request(
            request, safe_mode_allows_unreviewed=True
        )
        self.assertEqual(strict, "reviewed_only")
        self.assertEqual(allowed, "include_unreviewed")

    def test_actor_kind_does_not_change_selection_fingerprint(self) -> None:
        human = self.base()
        sei = copy.deepcopy(human)
        sei["actor"] = {"actorRef": "sei:test", "kind": "sei_cognition"}
        sei["roles"] = ["explore"]
        h, _ = normalize_projection_request(human)
        s, _ = normalize_projection_request(sei)
        self.assertEqual(
            canonical_json(selection_input_fingerprint(h)),
            canonical_json(selection_input_fingerprint(s)),
        )

    def test_set_like_lists_are_normalized_deterministically(self) -> None:
        request = self.base()
        request["roles"] = ["explore", "compare", "explore"]
        request["interest"]["focusRefs"] = ["c5", "c1", "c5"]
        request["permission"]["readableScopes"] = [
            "network:working",
            "network:working",
        ]
        normalized, _ = normalize_projection_request(request)
        self.assertEqual(normalized["roles"], ["compare", "explore"])
        self.assertEqual(normalized["interest"]["focusRefs"], ["c1", "c5"])
        self.assertEqual(
            normalized["permission"]["readableScopes"], ["network:working"]
        )

    def test_legacy_document_scope_is_rejected(self) -> None:
        request = self.base()
        request["sourceScope"] = "document"
        with self.assertRaisesRegex(ProjectionRequestError, "unknown sourceScope"):
            normalize_projection_request(request)

    def test_unknown_actor_kind_fails_closed(self) -> None:
        request = self.base()
        request["actor"]["kind"] = "unknown_agent"
        with self.assertRaisesRegex(ProjectionRequestError, "unknown actor.kind"):
            normalize_projection_request(request)

    def test_empty_readable_scope_fails_closed(self) -> None:
        request = self.base()
        request["permission"]["readableScopes"] = []
        with self.assertRaisesRegex(ProjectionRequestError, "must not be empty"):
            normalize_projection_request(request)


if __name__ == "__main__":
    unittest.main()
