"""Comprehensive KJ-method session E2E test — full business flow.

Simulates a complete KJ-method session using the mock LLM across all
10 AI tasks in realistic business flow order. Uses the same pattern
as test_llm_integration.py (direct mock calls, no backend startup).

Business flows:
  1. Card Creation  → refine_card_text (individual cards)
  2. Grouping       → suggest_card_groups (bulk grouping)
  3. Review         → detect_contradiction (conflict detection)
  4. Prioritization → assess_card_importance (importance ranking)
  5. Layout         → re_layout (spatial arrangement)
  6. Merge          → suggest_merges (consolidation)
  7. Island Summary → suggest_island_summary
  8. Island Relation→ summarize_island_relation
  9. Narrative Gen  → generate_narrative
 10. Narrative Check→ check_narrative
"""

from __future__ import annotations

import json
import subprocess
import sys
import time

import httpx
import pytest

MOCK_URL = "http://localhost:8001/generate"
EXTERNAL_LLM_URL = "http://localhost:8001/generate"

_mock_proc = None


def _ensure_mock():
    global _mock_proc
    if _mock_proc is not None and _mock_proc.poll() is None:
        return
    _mock_proc = subprocess.Popen(
        [sys.executable,
         "/mnt/d/GIT/kj-atlas/03_Implement/deploy/tools/mock_local_llm.py",
         "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        time.sleep(0.1)
        try:
            httpx.get("http://localhost:8001/", timeout=0.5)
            return
        except Exception:
            pass


def pytest_sessionfinish():
    global _mock_proc
    if _mock_proc and _mock_proc.poll() is None:
        _mock_proc.kill()


def _call(task: str, prompt: str) -> dict:
    r = httpx.post(MOCK_URL, json={
        "task": task, "prompt": prompt,
        "temperature": 0.2, "max_tokens": 500, "model": "mock",
    }, timeout=10)
    r.raise_for_status()
    return json.loads(r.json()["text"])


# ============================================================================
# KJ Session: Complete Business Flow
# ============================================================================


class TestKJSessionBusinessFlow:
    """Full KJ-method session: all 10 tasks in 6 business phases."""

    @pytest.fixture(autouse=True)
    def setup(self):
        _ensure_mock()

    def test_phase1_card_refinement_all_cards(self):
        """Phase 1: Refine 6 raw KJ cards."""
        cards = [
            "The system should save data automatically when user closes",
            "Export to PDF is needed for sharing with external people",
            "Undo function is important for editing safety",
            "Search across all documents is required for finding info",
            "Dark mode would help users working at night",
            "Real-time collaboration is essential for team work",
        ]
        refined = []
        for i, text in enumerate(cards):
            data = _call("refine_card_text",
                         f"Card text: {text}\nContext: product requirements KJ session.\nReturn JSON.")
            assert "refinedText" in data, f"Card {i}: {data}"
            assert len(data["refinedText"]) > 0
            refined.append(data["refinedText"])
        assert len(refined) == 6

    def test_phase2_card_grouping_eight_cards(self):
        """Phase 2: Group 8 cards into thematic islands."""
        cards = [
            ("c0", "Auto-save on close"), ("c1", "Export to PDF"),
            ("c2", "Undo functionality"), ("c3", "Full-text search"),
            ("c4", "Dark mode support"), ("c5", "Real-time collab"),
            ("c6", "Version history"), ("c7", "Keyboard shortcuts"),
        ]
        prompt = "\n".join(f'- id="{i}", text="{t}"' for i, t in cards)
        data = _call("suggest_card_groups", prompt)
        assert "groups" in data
        assert len(data["groups"]) >= 1
        for g in data["groups"]:
            assert "label" in g and "cardIds" in g

    def test_phase3_contradiction_detection_pairs(self):
        """Phase 3: Detect contradictions between reviewer pairs."""
        pairs = [
            ("Data must be server-only", "Data must work offline"),
            ("All users need SSO", "Guest access without login"),
        ]
        for a, b in pairs:
            data = _call("detect_contradiction",
                         f"Card A: {a}\nCard B: {b}\nReturn JSON.")
            assert "hasContradiction" in data
            assert "explanation" in data

    def test_phase4_importance_assessment_prioritization(self):
        """Phase 4: Rate 5 cards by importance."""
        cards = [
            ("p1", "Security audit log for all data access"),
            ("p2", "Dark mode color scheme"),
            ("p3", "Real-time sync between devices"),
            ("p4", "Export to PNG format"),
            ("p5", "Two-factor authentication"),
        ]
        prompt = "\n".join(f'- id="{i}", text="{t}"' for i, t in cards)
        data = _call("assess_card_importance", prompt)
        assert "assessments" in data
        assert len(data["assessments"]) == 5
        for a in data["assessments"]:
            assert a["importance"] in ("high", "medium", "low")

    def test_phase5_layout_and_merges(self):
        """Phase 5: Layout 4 cards and find merges."""
        prompt = (
            '- id="a", text="Auto-save"\n'
            '- id="b", text="Auto-save on close"\n'
            '- id="c", text="Export PDF"\n'
            '- id="d", text="Export PNG"'
        )
        layout = _call("re_layout", prompt)
        assert "cards" in layout
        assert len(layout["cards"]) == 4

        merges = _call("suggest_merges", prompt + "Return JSON.")
        assert "suggestions" in merges

    def test_phase6_island_summary_relation_narrative(self):
        """Phase 6: Island summary, relation, narrative generation + check."""
        island_prompt = (
            '- id="a", text="Auto-save prevents data loss"\n'
            '- id="b", text="Export enables sharing"'
        )
        summary = _call("suggest_island_summary", island_prompt)
        assert "summaryText" in summary

        rel = _call("summarize_island_relation", "Relation between A and B. Return JSON.")
        assert "text" in rel

        narrative = _call("generate_narrative",
                          'Reading order:\n  - 1. card id="a"\n  - 2. card id="b"\nReturn JSON.')
        assert "text" in narrative

        check = _call("check_narrative",
                      f'Narrative: {narrative["text"]}\nCards: a, b\nReturn JSON.')
        assert "issues" in check

    def test_complete_kj_session_all_ten_tasks(self):
        """One test: all 10 AI tasks in order with correct prompt format."""
        tasks = [
            ("refine_card_text", "Card: Auto-save when closing. Return JSON."),
            ("suggest_card_groups", '- id="a", text="A"\n- id="b", text="B"'),
            ("detect_contradiction", "Card A: X is true.\nCard B: X is false.\nReturn JSON."),
            ("assess_card_importance", '- id="a", text="Critical"\n- id="b", text="Minor"'),
            ("re_layout", '- id="a", text="A"'),
            ("suggest_merges", '- id="a", text="A"'),
            ("suggest_island_summary", '- id="a", text="A"'),
            ("summarize_island_relation", "Relation: A to B. Return JSON."),
            ("generate_narrative", '- 1. card id="a"\nReturn JSON.'),
            ("check_narrative", "Narrative: Test. Cards: a. Return JSON."),
        ]
        for task, prompt in tasks:
            data = _call(task, prompt)
            assert isinstance(data, dict), f"{task}: got {type(data)}"
            assert len(data) > 0, f"{task}: empty response"


# ============================================================================
# Ollama E2E: Real LLM verification
# ============================================================================


@pytest.mark.external_llm
class TestKJSessionExternalLLM:
    """Real LLM verification via any OpenAI-compatible adapter on port 8001."""

    @pytest.fixture(autouse=True)
    def setup(self):
        try:
            httpx.get("http://localhost:8001/", timeout=3)
        except Exception:
            pytest.skip("OpenAI-compatible adapter not running on port 8001")

    def _call_external(self, task, prompt):
        r = httpx.post(EXTERNAL_LLM_URL, json={
            "task": task, "prompt": prompt,
            "temperature": 0.1, "max_tokens": 300, "model": "any",
        }, timeout=130)
        r.raise_for_status()
        return r.json()["text"]

    def test_external_refine_card_text(self):
        text = self._call_external("refine_card_text",
                                   "Card: Auto-save when closing document. Return JSON only.")
        assert len(text) > 10

    def test_external_suggest_card_groups(self):
        text = self._call_external("suggest_card_groups",
                                   '- id="a", text="Auto-save"\n- id="b", text="Export"\n'
                                   '- id="c", text="Dark mode"\n- id="d", text="Night theme"')
        assert len(text) > 10

    def test_external_detect_contradiction(self):
        text = self._call_external("detect_contradiction",
                                   "Card A: Data must be encrypted.\nCard B: Data stored as plain text.\nReturn JSON only.")
        assert len(text) > 10

    def test_external_assess_card_importance(self):
        text = self._call_external("assess_card_importance",
                                   '- id="a", text="Security"\n- id="b", text="Theme"')
        assert len(text) > 10

    def test_external_full_four_card_tasks(self):
        results = {}
        for task, prompt in [
            ("refine_card_text", "Card: Auto-save on close. Return JSON only."),
            ("suggest_card_groups", '- id="a", text="A"\n- id="b", text="B"'),
            ("detect_contradiction", "Card A: X\nCard B: not X\nReturn JSON only."),
            ("assess_card_importance", '- id="x", text="Important"'),
        ]:
            text = self._call_external(task, prompt)
            assert len(text) > 10, f"Empty for {task}"
            results[task] = len(text)
        assert len(results) == 4
