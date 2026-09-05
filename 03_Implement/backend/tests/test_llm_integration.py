"""LLM integration tests — mock LLM (always available) + optional Ollama."""

import json
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

MOCK_URL = "http://localhost:8001/generate"
OLLAMA_URL = "http://localhost:8002/generate"
# Resolved from this file, not hardcoded: an absolute developer-machine path
# breaks the mock server startup on every other checkout, including CI.
# tests -> backend -> 03_Implement -> repository root
MOCK_SERVER = (
    Path(__file__).resolve().parents[3] / "03_Implement" / "deploy" / "tools" / "mock_local_llm.py"
)


def _generate(url, task, prompt, model="mock", timeout=130):
    r = httpx.post(url, json={"task": task, "prompt": prompt,
                   "temperature": 0.2, "max_tokens": 500, "model": model},
                   timeout=timeout)
    r.raise_for_status()
    return r.json()["text"]


# Module-level mock server — started once for all mock tests
_mock_proc = None


def _ensure_mock():
    global _mock_proc
    if _mock_proc is not None and _mock_proc.poll() is None:
        return  # Already running
    _mock_proc = subprocess.Popen(
        [sys.executable,
         str(MOCK_SERVER),
         "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Wait for server to be ready
    for _ in range(20):
        time.sleep(0.1)
        try:
            httpx.get("http://localhost:8001/", timeout=0.5)
            return
        except Exception:
            pass
    raise RuntimeError("Mock server failed to start")


def pytest_sessionfinish():
    global _mock_proc
    if _mock_proc and _mock_proc.poll() is None:
        _mock_proc.kill()


class TestMockLLMIntegration:
    """All 6 AI tasks produce valid JSON via the mock LLM."""

    @pytest.fixture(autouse=True)
    def setup(self):
        _ensure_mock()

    def test_mock_re_layout_valid_json(self):
        data = json.loads(_generate(MOCK_URL, "re_layout", "layout test"))
        assert "transform" in data and "cards" in data

    def test_mock_suggest_merges_valid_json(self):
        data = json.loads(_generate(MOCK_URL, "suggest_merges", "merge test"))
        assert "suggestions" in data

    def test_mock_island_summary_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "suggest_island_summary", "island test"))
        assert "candidates" in data
        assert all("summaryText" in c and "groundingIds" in c for c in data["candidates"])

    def test_mock_island_relation_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "summarize_island_relation", "rel test"))
        assert "text" in data

    def test_mock_generate_narrative_valid_json(self):
        assert "text" in json.loads(
            _generate(MOCK_URL, "generate_narrative", "narrative test"))

    def test_mock_check_narrative_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "check_narrative", "check test"))
        assert "issues" in data

    def test_all_nine_tasks_non_empty(self):
        for task in ["re_layout", "suggest_merges", "suggest_island_summary",
                     "summarize_island_relation", "generate_narrative",
                     "check_narrative", "refine_card_text",
                     "suggest_card_groups", "detect_contradiction"]:
            assert len(_generate(MOCK_URL, task, "test")) > 0, f"Empty for {task}"

    # ADR-0064: KJ-method card-level tests
    def test_refine_card_text_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "refine_card_text",
                      'Card text: test card. Return JSON.'))
        assert "refinedText" in data

    def test_suggest_card_groups_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "suggest_card_groups",
                      'Cards:\n  - id="a", text="A"\n  - id="b", text="B"'))
        assert "groups" in data

    def test_detect_contradiction_valid_json(self):
        data = json.loads(
            _generate(MOCK_URL, "detect_contradiction",
                      'Card A: X\nCard B: Y'))
        assert "hasContradiction" in data

EXTERNAL_LLM_URL = "http://localhost:8001/generate"


@pytest.mark.external_llm
class TestExternalLLMIntegration:
    """Tests against any OpenAI-compatible adapter (unified).

    The unified adapter (openai_compatible_adapter.py) works with:
    - Ollama:       python3 openai_compatible_adapter.py --port 8001
    - DeepSeek:     LLM_API_KEY=sk-... python3 openai_compatible_adapter.py
                    --port 8001 --base-url https://api.deepseek.com/v1
                    --model deepseek-v4-flash
    - OpenAI:       LLM_API_KEY=sk-... python3 openai_compatible_adapter.py
                    --port 8001 --base-url https://api.openai.com/v1
                    --model gpt-4o-mini

    Run with: pytest tests/test_llm_integration.py -v -m external_llm
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        try:
            httpx.get(EXTERNAL_LLM_URL.replace("/generate", "/"), timeout=3)
        except Exception:
            pytest.skip("OpenAI-compatible adapter not running on port 8001")

    def test_external_llm_connectivity(self):
        r = httpx.get(EXTERNAL_LLM_URL.replace("/generate", "/"), timeout=5)
        assert r.status_code == 200

    def test_external_refine_card_text(self):
        text = _generate(EXTERNAL_LLM_URL, "refine_card_text",
                         "Card: Auto-save when closing document. Return JSON only.",
                         timeout=130)
        assert len(text) > 10

    def test_external_detect_contradiction(self):
        text = _generate(EXTERNAL_LLM_URL, "detect_contradiction",
                         "Card A: Data must be encrypted.\n"
                         "Card B: Data stored as plain text. Return JSON only.",
                         timeout=130)
        assert len(text) > 10

    def test_external_suggest_card_groups(self):
        text = _generate(EXTERNAL_LLM_URL, "suggest_card_groups",
                         '- id="a", text="Auto-save"\n'
                         '- id="b", text="Export PDF"\n'
                         '- id="c", text="Dark mode"\n'
                         '- id="d", text="Night theme"\nReturn JSON only.',
                         timeout=130)
        assert len(text) > 10
