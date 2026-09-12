from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lexical_sparse import lexical_expand  # noqa: E402
from query_engine import D0Network  # noqa: E402
from query_envelope import QueryEnvelopeError, compose_query_envelope  # noqa: E402

NETWORK_PATH = ROOT / "fixtures" / "network.json"


class MultiChannelQueryEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = json.loads(NETWORK_PATH.read_text(encoding="utf-8"))
        self.network = D0Network(self.snapshot)
        self.selection = self.network.neighborhood(["c1"], depth=0)
        self.lexical = lexical_expand(self.network, ["c1"])
        self.associative = {
            "channel": "associative_sparse",
            "anchorRefs": ["c1"],
            "candidateRefs": ["c5", "c8"],
            "items": [
                {"ref": "c5", "evidence": {"matchedChannelRefs": ["channel:text"]}},
                {"ref": "c8", "evidence": {"matchedChannelRefs": []}},
            ],
            "noveltyCue": "none",
            "trace": {
                "networkId": self.network.network_id,
                "providerId": "synthetic-provider",
                "implementationVersion": "test-v1",
                "semanticAuthority": False,
                "sourceNetworkMutated": False,
            },
        }

    def compose(self, channels=None):
        return compose_query_envelope(
            self.network,
            request_id="req-envelope-1",
            intent="neighborhood",
            deterministic_selection=self.selection,
            candidate_channels=[self.lexical, self.associative] if channels is None else channels,
        )

    def test_candidate_channels_never_expand_d0_selection(self) -> None:
        result = self.compose()
        self.assertEqual(result["deterministicSelection"]["selectedNodeRefs"], ["c1"])
        candidate_refs = {
            ref
            for channel in result["candidateChannels"]
            for ref in channel["candidateRefs"]
        }
        self.assertTrue(candidate_refs - {"c1"})
        self.assertEqual(result["trace"]["selectionAuthority"], "d0_deterministic_only")
        self.assertFalse(result["trace"]["candidateAutoPromotion"])

    def test_cross_channel_presence_is_descriptive_not_vote(self) -> None:
        result = self.compose()
        c8 = next(item for item in result["channelPresence"] if item["ref"] == "c8")
        self.assertEqual(c8["channels"], ["associative_sparse", "lexical_sparse"])
        self.assertNotIn("count", c8)
        self.assertNotIn("score", c8)
        self.assertFalse(result["trace"]["crossChannelPresenceIsVote"])

    def test_candidate_channels_are_stably_ordered_by_channel_name(self) -> None:
        result = self.compose([self.lexical, self.associative])
        self.assertEqual(
            [channel["channel"] for channel in result["candidateChannels"]],
            ["associative_sparse", "lexical_sparse"],
        )

    def test_duplicate_channel_name_fails_closed(self) -> None:
        duplicate = copy.deepcopy(self.lexical)
        with self.assertRaisesRegex(QueryEnvelopeError, "channel names must be unique"):
            self.compose([self.lexical, duplicate])

    def test_unsupported_channel_fails_closed(self) -> None:
        channel = copy.deepcopy(self.lexical)
        channel["channel"] = "semantic_dense"
        with self.assertRaisesRegex(QueryEnvelopeError, "unsupported candidate channel"):
            self.compose([channel])

    def test_candidate_outside_snapshot_fails_closed(self) -> None:
        channel = copy.deepcopy(self.associative)
        channel["candidateRefs"] = ["missing"]
        with self.assertRaisesRegex(QueryEnvelopeError, "outside snapshot"):
            self.compose([channel])

    def test_candidate_channel_network_mismatch_fails_closed(self) -> None:
        channel = copy.deepcopy(self.associative)
        channel["trace"]["networkId"] = "other-network"
        with self.assertRaisesRegex(QueryEnvelopeError, "same network"):
            self.compose([channel])

    def test_provider_numeric_signal_cannot_reenter_through_envelope(self) -> None:
        channel = copy.deepcopy(self.associative)
        channel["items"][0]["activation"] = 0.91
        with self.assertRaisesRegex(QueryEnvelopeError, "forbidden ranking/provider signals"):
            self.compose([channel])

    def test_deterministic_selection_network_mismatch_fails_closed(self) -> None:
        selection = copy.deepcopy(self.selection)
        selection["trace"]["networkId"] = "other-network"
        with self.assertRaisesRegex(QueryEnvelopeError, "same network"):
            compose_query_envelope(
                self.network,
                request_id="req-envelope-1",
                intent="neighborhood",
                deterministic_selection=selection,
                candidate_channels=[],
            )

    def test_intent_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(QueryEnvelopeError, "intent must match"):
            compose_query_envelope(
                self.network,
                request_id="req-envelope-1",
                intent="contrast",
                deterministic_selection=self.selection,
                candidate_channels=[],
            )

    def test_candidate_may_also_be_d0_selected_without_changing_authority(self) -> None:
        selection = self.network.neighborhood(["c1"], depth=1)
        result = compose_query_envelope(
            self.network,
            request_id="req-envelope-overlap",
            intent="neighborhood",
            deterministic_selection=selection,
            candidate_channels=[self.lexical],
        )
        overlap = set(selection["selectedNodeRefs"]) & set(self.lexical["candidateRefs"])
        self.assertTrue(overlap)
        self.assertEqual(
            result["deterministicSelection"]["selectedNodeRefs"],
            selection["selectedNodeRefs"],
        )
        self.assertFalse(result["trace"]["candidateAutoPromotion"])

    def test_abstaining_associative_channel_adds_no_presence(self) -> None:
        channel = copy.deepcopy(self.associative)
        channel["candidateRefs"] = []
        channel["items"] = []
        channel["noveltyCue"] = "abstain"
        result = self.compose([channel])
        self.assertEqual(result["channelPresence"], [])
        self.assertEqual(result["candidateChannels"][0]["noveltyCue"], "abstain")

    def test_composition_is_read_only_for_all_inputs(self) -> None:
        before_snapshot = copy.deepcopy(self.snapshot)
        before_selection = copy.deepcopy(self.selection)
        before_lexical = copy.deepcopy(self.lexical)
        before_associative = copy.deepcopy(self.associative)
        self.compose()
        self.assertEqual(self.snapshot, before_snapshot)
        self.assertEqual(self.selection, before_selection)
        self.assertEqual(self.lexical, before_lexical)
        self.assertEqual(self.associative, before_associative)


if __name__ == "__main__":
    unittest.main()
