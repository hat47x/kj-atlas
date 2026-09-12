from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from associative_channel import (  # noqa: E402
    D2AssociativeError,
    MAX_ANCHORS,
    MAX_CANDIDATES,
    MAX_SCOPE_ITEMS,
    REQUEST_SCHEMA,
    RESPONSE_SCHEMA,
    build_associative_request,
    normalize_associative_response,
)
from query_engine import D0Network  # noqa: E402

NETWORK_PATH = ROOT / "fixtures" / "network.json"


class D2AssociativeChannelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = json.loads(NETWORK_PATH.read_text(encoding="utf-8"))
        self.network = D0Network(self.snapshot)
        self.request = build_associative_request(
            self.network,
            request_id="assoc-1",
            intent="bridge",
            anchor_refs=["c1"],
            scope_refs=["c1", "c2", "c3", "c4", "c5"],
            candidate_limit=3,
        )

    def response(self, **overrides) -> dict:
        value = {
            "schema": RESPONSE_SCHEMA,
            "requestId": self.request["requestId"],
            "provider": {
                "providerId": "sei-cognition-sacs",
                "implementationVersion": "evaluation-v1",
            },
            "outcome": "candidates",
            "candidateRefs": ["c3", "c2"],
            "evidence": [
                {
                    "ref": "c2",
                    "matchedChannelRefs": [
                        "channel:text",
                        "graph:relationType:related",
                        "graph:neighborKind:card",
                        "provenance:source:s1",
                        "provenance:actor:human:a",
                        "grouping:island:i1",
                    ],
                },
                {
                    "ref": "c3",
                    "matchedChannelRefs": [
                        "channel:text",
                        "graph:relationType:related",
                        "graph:neighborKind:card",
                    ],
                },
            ],
            "noveltyCue": "none",
        }
        value.update(overrides)
        return value

    def test_request_uses_formal_schema_and_bounded_channels(self) -> None:
        self.assertEqual(self.request["schema"], REQUEST_SCHEMA)
        self.assertEqual(self.request["anchorRefs"], ["c1"])
        self.assertEqual(
            [item["ref"] for item in self.request["items"]],
            ["c1", "c2", "c3", "c4", "c5"],
        )
        c1 = next(item for item in self.request["items"] if item["ref"] == "c1")
        self.assertIn("text", c1["channels"])
        self.assertEqual(
            c1["channels"]["graph"],
            {"relationTypes": ["related"], "neighborKinds": ["card"]},
        )
        self.assertEqual(
            c1["channels"]["provenance"],
            {"sourceRefs": ["s1"], "actorRefs": ["human:a"]},
        )
        self.assertEqual(c1["channels"]["grouping"], {"islandRef": "i1"})

    def test_request_does_not_send_review_state_permission_or_credentials(self) -> None:
        rendered = json.dumps(self.request, ensure_ascii=False, sort_keys=True)
        self.assertNotIn("reviewState", rendered)
        self.assertNotIn("permission", rendered.lower())
        self.assertNotIn("credential", rendered.lower())
        self.assertNotIn("observedAt", rendered)

    def test_scope_is_explicitly_bounded(self) -> None:
        request = build_associative_request(
            self.network,
            request_id="bounded",
            intent="affinity",
            anchor_refs=["c1"],
            scope_refs=["c1", "c2"],
            candidate_limit=1,
        )
        self.assertEqual([item["ref"] for item in request["items"]], ["c1", "c2"])

    def test_unknown_anchor_fails_closed(self) -> None:
        with self.assertRaisesRegex(D2AssociativeError, "unknown refs"):
            build_associative_request(
                self.network,
                request_id="bad",
                intent="bridge",
                anchor_refs=["missing"],
            )

    def test_anchor_must_be_in_scope(self) -> None:
        with self.assertRaisesRegex(D2AssociativeError, "contained in scopeRefs"):
            build_associative_request(
                self.network,
                request_id="bad",
                intent="bridge",
                anchor_refs=["c1"],
                scope_refs=["c2", "c3"],
            )

    def test_candidate_limit_is_bounded_and_bool_is_not_integer(self) -> None:
        for invalid in (0, MAX_CANDIDATES + 1, True):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(D2AssociativeError, "candidateLimit"):
                    build_associative_request(
                        self.network,
                        request_id="bad-limit",
                        intent="bridge",
                        anchor_refs=["c1"],
                        candidate_limit=invalid,
                    )

    def test_anchor_count_limit_is_fail_closed(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        for index in range(MAX_ANCHORS + 1 - len(snapshot["nodes"])):
            snapshot["nodes"].append(
                {
                    "id": f"extra-a-{index}",
                    "kind": "card",
                    "text": "追加",
                    "reviewState": "human_reviewed",
                    "sourceRefs": [],
                    "actorRefs": [],
                }
            )
        network = D0Network(snapshot)
        anchors = sorted(network.nodes)[: MAX_ANCHORS + 1]
        with self.assertRaisesRegex(D2AssociativeError, "anchorRefs exceeds"):
            build_associative_request(
                network,
                request_id="too-many-anchors",
                intent="affinity",
                anchor_refs=anchors,
            )

    def test_scope_count_limit_is_fail_closed(self) -> None:
        snapshot = copy.deepcopy(self.snapshot)
        needed = MAX_SCOPE_ITEMS + 1 - len(snapshot["nodes"])
        for index in range(needed):
            snapshot["nodes"].append(
                {
                    "id": f"extra-s-{index}",
                    "kind": "card",
                    "text": "追加",
                    "reviewState": "human_reviewed",
                    "sourceRefs": [],
                    "actorRefs": [],
                }
            )
        network = D0Network(snapshot)
        with self.assertRaisesRegex(D2AssociativeError, "scopeRefs exceeds"):
            build_associative_request(
                network,
                request_id="too-wide",
                intent="affinity",
                anchor_refs=["c1"],
            )

    def test_response_is_stable_ref_order_not_provider_order(self) -> None:
        normalized = normalize_associative_response(self.request, self.response())
        self.assertEqual(normalized["candidateRefs"], ["c2", "c3"])
        self.assertEqual([item["ref"] for item in normalized["items"]], ["c2", "c3"])
        self.assertFalse(normalized["trace"]["semanticAuthority"])

    def test_provider_internal_numeric_signals_are_rejected(self) -> None:
        for key in (
            "activation",
            "score",
            "confidence",
            "importance",
            "rank",
            "similarity",
            "novelty_signal",
        ):
            with self.subTest(key=key):
                response = self.response()
                response["evidence"][0][key] = 0.9
                with self.assertRaisesRegex(D2AssociativeError, "forbidden signals"):
                    normalize_associative_response(self.request, response)

    def test_unknown_top_level_response_key_is_rejected(self) -> None:
        response = self.response(debug="internal")
        with self.assertRaisesRegex(D2AssociativeError, "unknown keys"):
            normalize_associative_response(self.request, response)

    def test_provider_metadata_is_closed_world(self) -> None:
        response = self.response()
        response["provider"]["model"] = "hidden"
        with self.assertRaisesRegex(D2AssociativeError, "provider must contain exactly"):
            normalize_associative_response(self.request, response)

    def test_request_id_mismatch_is_rejected(self) -> None:
        response = self.response(requestId="other")
        with self.assertRaisesRegex(D2AssociativeError, "requestId mismatch"):
            normalize_associative_response(self.request, response)

    def test_candidate_outside_scope_is_rejected(self) -> None:
        response = self.response(candidateRefs=["c8"], evidence=[])
        with self.assertRaisesRegex(D2AssociativeError, "outside request scope"):
            normalize_associative_response(self.request, response)

    def test_anchor_cannot_be_returned_as_candidate(self) -> None:
        response = self.response(candidateRefs=["c1"], evidence=[])
        with self.assertRaisesRegex(D2AssociativeError, "must not be returned"):
            normalize_associative_response(self.request, response)

    def test_duplicate_candidate_is_rejected(self) -> None:
        response = self.response(candidateRefs=["c2", "c2"], evidence=[])
        with self.assertRaisesRegex(D2AssociativeError, "must not contain duplicates"):
            normalize_associative_response(self.request, response)

    def test_candidate_limit_is_enforced_on_response(self) -> None:
        request = copy.deepcopy(self.request)
        request["policy"]["candidateLimit"] = 1
        with self.assertRaisesRegex(D2AssociativeError, "exceeds candidateLimit"):
            normalize_associative_response(request, self.response())

    def test_abstain_requires_empty_candidates_and_abstain_cue(self) -> None:
        valid = self.response(
            outcome="abstain",
            candidateRefs=[],
            evidence=[],
            noveltyCue="abstain",
        )
        normalized = normalize_associative_response(self.request, valid)
        self.assertEqual(normalized["candidateRefs"], [])
        self.assertEqual(normalized["noveltyCue"], "abstain")

        invalid = self.response(
            outcome="abstain",
            candidateRefs=["c2"],
            evidence=[],
            noveltyCue="abstain",
        )
        with self.assertRaisesRegex(D2AssociativeError, "abstain requires"):
            normalize_associative_response(self.request, invalid)

    def test_candidate_outcome_requires_none_novelty_cue(self) -> None:
        response = self.response(noveltyCue="abstain")
        with self.assertRaisesRegex(D2AssociativeError, "candidate outcome"):
            normalize_associative_response(self.request, response)

    def test_evidence_ref_must_be_candidate(self) -> None:
        response = self.response()
        response["evidence"].append({"ref": "c4", "matchedChannelRefs": []})
        with self.assertRaisesRegex(D2AssociativeError, "must be a candidateRef"):
            normalize_associative_response(self.request, response)

    def test_duplicate_evidence_ref_is_rejected(self) -> None:
        response = self.response()
        response["evidence"].append(copy.deepcopy(response["evidence"][0]))
        with self.assertRaisesRegex(D2AssociativeError, "duplicate evidence.ref"):
            normalize_associative_response(self.request, response)

    def test_invented_channel_provenance_is_rejected(self) -> None:
        response = self.response()
        response["evidence"][0]["matchedChannelRefs"].append("provenance:source:not-real")
        with self.assertRaisesRegex(D2AssociativeError, "not present on both"):
            normalize_associative_response(self.request, response)

    def test_grounded_channel_provenance_is_accepted_but_not_semantic_proof(self) -> None:
        normalized = normalize_associative_response(self.request, self.response())
        c2 = next(item for item in normalized["items"] if item["ref"] == "c2")
        self.assertIn("channel:text", c2["evidence"]["matchedChannelRefs"])
        self.assertIn("provenance:source:s1", c2["evidence"]["matchedChannelRefs"])
        rendered = json.dumps(normalized, ensure_ascii=False)
        for forbidden in ("activation", "confidence", "similarity", "score", "rank"):
            self.assertNotIn(f'"{forbidden}"', rendered)

    def test_empty_channel_provenance_is_allowed_without_invention(self) -> None:
        response = self.response(evidence=[])
        normalized = normalize_associative_response(self.request, response)
        self.assertEqual(
            [item["evidence"]["matchedChannelRefs"] for item in normalized["items"]],
            [[], []],
        )

    def test_adapter_does_not_mutate_network_or_provider_response(self) -> None:
        snapshot_before = copy.deepcopy(self.snapshot)
        response = self.response()
        response_before = copy.deepcopy(response)
        normalize_associative_response(self.request, response)
        self.assertEqual(self.snapshot, snapshot_before)
        self.assertEqual(response, response_before)


if __name__ == "__main__":
    unittest.main()
