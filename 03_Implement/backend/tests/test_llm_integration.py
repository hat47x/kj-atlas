"""LLM integration tests — mock LLM (always available) + optional Ollama."""

import json
import subprocess
import sys
import time

import httpx
import pytest

MOCK_URL = "http://localhost:8001/generate"
OLLAMA_URL = "http://localhost:8002/generate"


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
         "/mnt/d/GIT/kj-atlas/03_Implement/deploy/tools/mock_local_llm.py",
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
        assert "summaryText" in data

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

    def test_all_six_tasks_non_empty(self):
        for task in ["re_layout", "suggest_merges", "suggest_island_summary",
                     "summarize_island_relation", "generate_narrative",
                     "check_narrative"]:
            assert len(_generate(MOCK_URL, task, "test")) > 0


@pytest.mark.ollama
class TestOllamaLLMIntegration:
    """Real LLM tests via Ollama adapter."""

    @pytest.fixture(autouse=True)
    def setup(self):
        try:
            httpx.get("http://localhost:11434/api/tags", timeout=3)
        except Exception:
            pytest.skip("Ollama not available")
        # Start adapter if needed
        for _ in range(3):
            try:
                httpx.get("http://localhost:8002/", timeout=1)
                return
            except Exception:
                pass
        pytest.skip("Ollama adapter not running on port 8002")

    def test_ollama_connectivity(self):
        r = httpx.get("http://localhost:8002/", timeout=5)
        assert r.status_code == 200

    def test_ollama_re_layout_non_empty(self):
        text = _generate(OLLAMA_URL, "re_layout",
                         "Place 3 cards in a grid. Return JSON only.",
                         model="deepseek-r1:7b", timeout=130)
        assert len(text) > 10

    def test_ollama_suggest_merges_non_empty(self):
        text = _generate(OLLAMA_URL, "suggest_merges",
                         "Find merge candidates. Return JSON only.",
                         model="deepseek-r1:7b", timeout=130)
        assert len(text) > 10
