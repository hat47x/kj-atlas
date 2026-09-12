from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compile_projection_request import (  # noqa: E402
    CONTEXT_QUERY_V1_KEYS,
    ProjectionCompileError,
    canonical_json,
    compile_projection_request,
)

FIXTURE_DIR = ROOT / "fixtures"


class ContextProjectionR0CompilerTests(unittest.TestCase):
    def load(self, name: str) -> dict:
        return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))

    def test_human_and_sei_compile_to_same_closed_world_top_level(self) -> None:
        human = compile_projection_request(self.load("human_contrast.json"))
        sei = compile_projection_request(self.load("sei_contrast.json"))
        self.assertEqual(set(human), CONTEXT_QUERY_V1_KEYS)
        self.assertEqual(set(sei), CONTEXT_QUERY_V1_KEYS)
        self.assertEqual(human["safeModePolicy"], "strict")
        self.assertEqual(sei["safeModePolicy"], "strict")

    def test_actor_ref_does_not_enter_downstream_context_query(self) -> None:
        request = self.load("sei_contrast.json")
        query = compile_projection_request(request)
        rendered = canonical_json(query)
        self.assertNotIn(request["actor"]["actorRef"], rendered)

    def test_role_does_not_grant_approval_permission(self) -> None:
        request = self.load("human_contrast.json")
        request["roles"] = ["approve"]
        request["permission"]["canApprove"] = False
        query = compile_projection_request(request)
        self.assertEqual(query["outputMode"], "summary")
        self.assertNotIn("canApprove", canonical_json(query))

    def test_proposal_mode_requires_permission(self) -> None:
        request = self.load("generative_ai_proposal.json")
        request["permission"]["canCreateProposal"] = False
        query = compile_projection_request(request)
        self.assertEqual(query["outputMode"], "candidate")

    def test_permission_must_be_server_resolved(self) -> None:
        request = self.load("sei_contrast.json")
        request["permission"]["resolutionSource"] = "requester_declared"
        with self.assertRaisesRegex(ProjectionCompileError, "server_resolved"):
            compile_projection_request(request)

    def test_unreviewed_requires_both_permission_and_safe_mode_allowance(self) -> None:
        request = self.load("human_contrast.json")
        request["permission"]["canSeeUnreviewed"] = True
        strict = compile_projection_request(request, safe_mode_allows_unreviewed=False)
        allowed = compile_projection_request(request, safe_mode_allows_unreviewed=True)
        self.assertEqual(strict["reviewFilter"], "reviewedOnly")
        self.assertEqual(allowed["reviewFilter"], "includeUnreviewed")

    def test_permission_shrink_changes_constraints_deterministically(self) -> None:
        request = self.load("sei_contrast.json")
        broad = compile_projection_request(request)
        narrow_request = copy.deepcopy(request)
        narrow_request["permission"]["readableScopes"] = ["document:public"]
        narrow = compile_projection_request(narrow_request)
        self.assertNotEqual(canonical_json(broad), canonical_json(narrow))
        self.assertEqual(
            narrow["constraints"]["projectionResearchR0"]["readableScopes"],
            ["document:public"],
        )

    def test_compilation_is_deterministic_under_input_list_order(self) -> None:
        request = self.load("sei_contrast.json")
        a = compile_projection_request(request)
        reordered = copy.deepcopy(request)
        reordered["roles"] = list(reversed(reordered["roles"]))
        reordered["interest"]["seek"] = list(reversed(reordered["interest"]["seek"]))
        reordered["permission"]["readableScopes"] = list(
            reversed(reordered["permission"]["readableScopes"])
        )
        b = compile_projection_request(reordered)
        self.assertEqual(canonical_json(a), canonical_json(b))

    def test_unknown_actor_kind_fails_closed(self) -> None:
        request = self.load("sei_contrast.json")
        request["actor"]["kind"] = "unknown_agent"
        with self.assertRaises(ProjectionCompileError):
            compile_projection_request(request)

    def test_empty_readable_scope_fails_closed(self) -> None:
        request = self.load("sei_contrast.json")
        request["permission"]["readableScopes"] = []
        with self.assertRaisesRegex(ProjectionCompileError, "must not be empty"):
            compile_projection_request(request)


if __name__ == "__main__":
    unittest.main()
