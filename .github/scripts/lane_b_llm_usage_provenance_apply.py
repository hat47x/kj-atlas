from __future__ import annotations

from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


provider_path = Path("03_Implement/backend/src/kj_atlas_api/llm/provider.py")
provider = provider_path.read_text(encoding="utf-8")
provider = replace_once(
    provider,
    '''# OPS-LLM-COST-01 (段階2): in-process input/output token totals, keyed by the
# same provider kind + "total". Filled from provider-reported usage; providers
# that do not report usage contribute 0 tokens.
_LLM_TOKEN_USAGE: dict[str, dict[str, int]] = {}
''',
    '''# OPS-LLM-COST-01 (段階2): in-process input/output token totals, keyed by the
# same provider kind + "total". Filled only from provider-reported usage. A
# missing/partial provider report still contributes 0 for the absent side to
# preserve the historical numeric totals, while _LLM_TOKEN_USAGE_COVERAGE makes
# that absence distinguishable from a genuine provider-reported zero.
_LLM_TOKEN_USAGE: dict[str, dict[str, int]] = {}
_LLM_TOKEN_USAGE_COVERAGE: dict[str, dict[str, int]] = {}
''',
    "declare usage coverage metrics",
)
provider = replace_once(
    provider,
    '''def _record_llm_usage(
    provider_kind: str,
    *,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> None:
    """Accumulate provider-reported token usage WITHOUT touching the call count
    (the count is recorded once per attempt by _record_llm_call)."""
    used_input = max(int(input_tokens or 0), 0)
    used_output = max(int(output_tokens or 0), 0)
    for key in (provider_kind, "total"):
        bucket = _LLM_TOKEN_USAGE.setdefault(key, {"input": 0, "output": 0})
        bucket["input"] += used_input
        bucket["output"] += used_output
''',
    '''def _record_llm_usage(
    provider_kind: str,
    *,
    input_tokens: int | None = None,
    output_tokens: int | None = None,
) -> None:
    """Accumulate provider-reported usage and its reporting completeness.

    Call counting remains separate because failed provider attempts have no
    successful response to settle. Numeric totals remain backward-compatible:
    an absent side contributes 0, but coverage records whether that 0 was a
    complete provider report, a partial report, or no usage report at all.
    """
    used_input = max(int(input_tokens or 0), 0)
    used_output = max(int(output_tokens or 0), 0)
    if input_tokens is None and output_tokens is None:
        coverage_key = "missingCalls"
    elif input_tokens is None or output_tokens is None:
        coverage_key = "partialCalls"
    else:
        coverage_key = "completeCalls"

    for key in (provider_kind, "total"):
        bucket = _LLM_TOKEN_USAGE.setdefault(key, {"input": 0, "output": 0})
        bucket["input"] += used_input
        bucket["output"] += used_output
        coverage = _LLM_TOKEN_USAGE_COVERAGE.setdefault(
            key,
            {"completeCalls": 0, "partialCalls": 0, "missingCalls": 0},
        )
        coverage[coverage_key] += 1
''',
    "record usage coverage",
)
provider = replace_once(
    provider,
    '''def llm_token_usage() -> dict[str, dict[str, int]]:
    """Snapshot of the in-process token usage totals (copied, never the live dict)."""
    return {key: dict(value) for key, value in _LLM_TOKEN_USAGE.items()}


def reset_llm_call_counts() -> None:
    """Clear the counters. Ops/tests only — a reset is not a runtime event."""
    _LLM_CALL_COUNTS.clear()
    _LLM_TOKEN_USAGE.clear()
''',
    '''def llm_token_usage() -> dict[str, dict[str, int]]:
    """Snapshot of provider-reported token totals for the current process."""
    return {key: dict(value) for key, value in _LLM_TOKEN_USAGE.items()}


def llm_token_usage_coverage() -> dict[str, dict[str, int]]:
    """Snapshot of complete/partial/missing provider usage reports.

    This deliberately carries no prompt/response content, raw tokens, model,
    task, tenant, or user identity. The aggregation key remains provider kind
    plus total in the current process.
    """
    return {key: dict(value) for key, value in _LLM_TOKEN_USAGE_COVERAGE.items()}


def reset_llm_call_counts() -> None:
    """Clear the process-local observability counters. Ops/tests only."""
    _LLM_CALL_COUNTS.clear()
    _LLM_TOKEN_USAGE.clear()
    _LLM_TOKEN_USAGE_COVERAGE.clear()
''',
    "expose/reset usage coverage",
)
provider = replace_once(
    provider,
    '''    # OPS-LLM-COST-01 (段階2): provider-reported token usage, when available
    # (OpenAI chat-completions `usage`). None means the provider did not report
    # it; the call counter treats None as 0 tokens.
''',
    '''    # OPS-LLM-COST-01: provider-reported token usage, when available.
    # None means that side was not reported; numeric aggregation preserves the
    # historical 0 contribution while tokenUsageCoverage records the absence.
''',
    "clarify response usage semantics",
)
provider = replace_once(
    provider,
    '''    # (before any provider error) is what cost control needs. Token usage is
    # recorded after a successful generate (providers that do not report usage
    # contribute 0 tokens).
''',
    '''    # (before any provider error) is what cost control needs. Token usage is
    # recorded after a successful generate; reporting coverage distinguishes a
    # genuine provider-reported zero from partial/missing usage metadata.
''',
    "clarify generate usage accounting",
)
provider_path.write_text(provider, encoding="utf-8")

models_path = Path("03_Implement/backend/src/kj_atlas_api/models_ai.py")
models = models_path.read_text(encoding="utf-8")
models = replace_once(
    models,
    '''class ProviderStatusResponse(BaseModel):
''',
    '''class TokenUsageCoverage(BaseModel):
    """Content-free completeness counters for provider token usage reports."""

    model_config = ConfigDict(extra="forbid")

    completeCalls: int = Field(default=0, ge=0)
    partialCalls: int = Field(default=0, ge=0)
    missingCalls: int = Field(default=0, ge=0)


class ProviderStatusResponse(BaseModel):
''',
    "add token usage coverage model",
)
models = replace_once(
    models,
    '''    # OPS-LLM-COST-01 (段階2): in-process input/output token totals per provider
    # kind (plus "total"). Populated from provider-reported usage (DeepSeek /
    # OpenAI chat completions `usage`); providers that do not report usage
    # contribute 0 tokens. Empty until the first LLM call.
    tokenUsage: dict[str, dict[str, int]] = Field(default_factory=dict)
''',
    '''    # OPS-LLM-COST-01: process-local input/output totals per provider kind
    # (plus "total"). Values come only from provider-reported usage. Missing
    # sides retain the historical numeric 0 contribution; tokenUsageCoverage
    # distinguishes that from a genuine reported zero.
    tokenUsage: dict[str, dict[str, int]] = Field(default_factory=dict)
    tokenUsageCoverage: dict[str, TokenUsageCoverage] = Field(default_factory=dict)
    tokenUsageSource: Literal["provider_reported_only"] = "provider_reported_only"
    tokenUsageAggregationScope: Literal["current_process_by_provider_kind"] = (
        "current_process_by_provider_kind"
    )
''',
    "extend provider status usage contract",
)
models_path.write_text(models, encoding="utf-8")

ai_path = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
ai = ai_path.read_text(encoding="utf-8")
ai = replace_once(
    ai,
    '''    OPS-LLM-COST-01 (段階2): also reports the in-process LLM call counts."""
    from kj_atlas_api.llm.provider import llm_call_counts, llm_token_usage

    return ProviderStatusResponse(
        providerKind=get_provider().provider_kind,
        callCounts=llm_call_counts(),
        tokenUsage=llm_token_usage(),
    )
''',
    '''    OPS-LLM-COST-01: also reports process-local call/token observability,
    including whether provider usage metadata was complete, partial, or missing."""
    from kj_atlas_api.llm.provider import (
        llm_call_counts,
        llm_token_usage,
        llm_token_usage_coverage,
    )

    return ProviderStatusResponse(
        providerKind=get_provider().provider_kind,
        callCounts=llm_call_counts(),
        tokenUsage=llm_token_usage(),
        tokenUsageCoverage=llm_token_usage_coverage(),
    )
''',
    "wire provider status usage coverage",
)
ai_path.write_text(ai, encoding="utf-8")

test_path = Path("03_Implement/backend/tests/test_ai_provider_status_route.py")
test = test_path.read_text(encoding="utf-8")
static_old = '{"providerKind": "none", "callCounts": {}, "tokenUsage": {}}'
static_new = '''{
            "providerKind": "none",
            "callCounts": {},
            "tokenUsage": {},
            "tokenUsageCoverage": {},
            "tokenUsageSource": "provider_reported_only",
            "tokenUsageAggregationScope": "current_process_by_provider_kind",
        }'''
test = replace_once(test, static_old, static_new, "update none provider status contract")
test = replace_once(
    test,
    '{"providerKind": "local", "callCounts": {}, "tokenUsage": {}}',
    '''{
            "providerKind": "local",
            "callCounts": {},
            "tokenUsage": {},
            "tokenUsageCoverage": {},
            "tokenUsageSource": "provider_reported_only",
            "tokenUsageAggregationScope": "current_process_by_provider_kind",
        }''',
    "update local alias provider status contract",
)
test = replace_once(
    test,
    '{"providerKind": "deepseek", "callCounts": {}, "tokenUsage": {}}',
    '''{
            "providerKind": "deepseek",
            "callCounts": {},
            "tokenUsage": {},
            "tokenUsageCoverage": {},
            "tokenUsageSource": "provider_reported_only",
            "tokenUsageAggregationScope": "current_process_by_provider_kind",
        }''',
    "update deepseek provider status contract",
)
test = replace_once(
    test,
    '{"providerKind": "local", "callCounts": {}, "tokenUsage": {}}',
    '''{
            "providerKind": "local",
            "callCounts": {},
            "tokenUsage": {},
            "tokenUsageCoverage": {},
            "tokenUsageSource": "provider_reported_only",
            "tokenUsageAggregationScope": "current_process_by_provider_kind",
        }''',
    "update static local provider status contract",
)
test = replace_once(
    test,
    '''    # No provider-reported usage -> 0 tokens recorded for the call.
    assert body["tokenUsage"] == {
        "large-scale": {"input": 0, "output": 0},
        "total": {"input": 0, "output": 0},
    }
''',
    '''    # Numeric totals remain backward-compatible, but missing usage is no
    # longer observationally identical to a provider-reported zero.
    assert body["tokenUsage"] == {
        "large-scale": {"input": 0, "output": 0},
        "total": {"input": 0, "output": 0},
    }
    assert body["tokenUsageCoverage"] == {
        "large-scale": {"completeCalls": 0, "partialCalls": 0, "missingCalls": 1},
        "total": {"completeCalls": 0, "partialCalls": 0, "missingCalls": 1},
    }
    assert body["tokenUsageSource"] == "provider_reported_only"
    assert body["tokenUsageAggregationScope"] == "current_process_by_provider_kind"
''',
    "assert missing usage coverage",
)
test = replace_once(
    test,
    '''    assert body["tokenUsage"]["large-scale"] == {"input": 240, "output": 74}
    assert body["tokenUsage"]["total"] == {"input": 240, "output": 74}
''',
    '''    assert body["tokenUsage"]["large-scale"] == {"input": 240, "output": 74}
    assert body["tokenUsage"]["total"] == {"input": 240, "output": 74}
    assert body["tokenUsageCoverage"]["large-scale"] == {
        "completeCalls": 2,
        "partialCalls": 0,
        "missingCalls": 0,
    }
    assert body["tokenUsageCoverage"]["total"] == {
        "completeCalls": 2,
        "partialCalls": 0,
        "missingCalls": 0,
    }
''',
    "assert complete usage coverage",
)
test += '''\n\ndef test_provider_status_distinguishes_partial_provider_usage(monkeypatch) -> None:\n    from kj_atlas_api.llm import provider as llm_provider\n    from kj_atlas_api.routes import ai as ai_routes\n\n    class _StubResponse:\n        raw_text = '{"refinedText": "（モック）改善案", "reasoning": "r"}'\n        input_tokens = 11\n        output_tokens = None\n\n    class _StubProvider:\n        provider_kind = "large-scale"\n        provider_name = "stub"\n\n        def generate(self, _req):\n            return _StubResponse()\n\n    monkeypatch.setattr(llm_provider, "get_provider", lambda: _StubProvider())\n    monkeypatch.setattr(ai_routes, "get_provider", lambda: _StubProvider())\n    monkeypatch.setattr(ai_routes, "_assert_model_allowed", lambda *a, **k: None)\n    reset_llm_call_counts()\n\n    with TestClient(app) as client:\n        response = client.post(\n            "/ai/refine-card-text",\n            json={"cardText": "partial", "textReviewed": True},\n        )\n        assert response.status_code == 200, response.text\n        body = client.get("/ai/provider-status").json()\n\n    assert body["tokenUsage"]["large-scale"] == {"input": 11, "output": 0}\n    assert body["tokenUsageCoverage"]["large-scale"] == {\n        "completeCalls": 0,\n        "partialCalls": 1,\n        "missingCalls": 0,\n    }\n'''
test_path.write_text(test, encoding="utf-8")

frontend_path = Path("03_Implement/frontend/src/api/client.ts")
frontend = frontend_path.read_text(encoding="utf-8")
frontend = replace_once(
    frontend,
    '''export type ProviderStatusSnapshot = {
  providerKind: ProviderKind;
  callCounts: Record<string, number>;
  tokenUsage: Record<string, { input: number; output: number }>;
};
''',
    '''export type ProviderStatusSnapshot = {
  providerKind: ProviderKind;
  callCounts: Record<string, number>;
  tokenUsage: Record<string, { input: number; output: number }>;
  tokenUsageCoverage: Record<string, {
    completeCalls: number;
    partialCalls: number;
    missingCalls: number;
  }>;
  tokenUsageSource: "provider_reported_only";
  tokenUsageAggregationScope: "current_process_by_provider_kind";
};
''',
    "sync frontend provider status contract",
)
frontend_path.write_text(frontend, encoding="utf-8")

issue_path = Path("01_Plans/issues/issue-OPS-LLM-COST-01-cost-control-contract-unimplemented.md")
issue = issue_path.read_text(encoding="utf-8")
issue = replace_once(
    issue,
    '''- [x] AC-2（段階2・完了）: **呼び出し回数**は計測・参照可能（OPS-LLM-COST-01 段階2・iteration 54）— `llm/provider.py` にプロセス内カウンタ（provider種別別＋total）を追加し `generate_with_fallback` で計上。`GET /ai/provider-status` の `callCounts` から参照可能。**トークン数**も計上完了（2026-08-16）— `LLMResponse` に `input_tokens`/`output_tokens` を追加し、OpenAI互換 `usage`（DeepSeek等）を解析してプロセス内で蓄積、`GET /ai/provider-status` の `tokenUsage`（provider種別別＋total）から参照可能。usage未報告providerは0計上。単一プロセス前提。欠損時の区別（AC-4）と共有store（AC-6）は段階3へ繰り越し。
''',
    '''- [x] AC-2（段階2・完了）: **呼び出し回数**は計測・参照可能（OPS-LLM-COST-01 段階2・iteration 54）— `llm/provider.py` にプロセス内カウンタ（provider種別別＋total）を追加し `generate_with_fallback` で計上。`GET /ai/provider-status` の `callCounts` から参照可能。**トークン数**も計上完了（2026-08-16）— `LLMResponse` に `input_tokens`/`output_tokens` を追加し、OpenAI互換 `usage`（DeepSeek等）を解析してプロセス内で蓄積、`GET /ai/provider-status` の `tokenUsage`（provider種別別＋total）から参照可能。数値合計は互換上、未報告側を0として保持するが、AC-4の `tokenUsageCoverage` によりprovider報告0・部分報告・未報告を区別する。単一プロセス前提。共有store（AC-6）は段階3へ繰り越し。
''',
    "sync AC2 missing usage wording",
)
issue = replace_once(
    issue,
    '''- [ ] AC-4: 計測値がprovider自己申告値かlocal tokenizer推定値かを区別し、provider／model／task／tenant等の集計scopeと欠損時挙動が一意である。prompt／response本文、生token、個人識別子をmetricへ保存しない。
''',
    '''- [x] AC-4: 計測値がprovider自己申告値かlocal tokenizer推定値かを区別し、provider／model／task／tenant等の集計scopeと欠損時挙動が一意である。— `GET /ai/provider-status` は `tokenUsageSource=provider_reported_only` と `tokenUsageAggregationScope=current_process_by_provider_kind` を明示し、現行集計がcurrent process × provider kind（＋total）のみでmodel/task/tenant別ではなくlocal tokenizer推定も行わないことを機械可読に固定した。`tokenUsageCoverage` は `completeCalls` / `partialCalls` / `missingCalls` を分離し、provider報告0とusage欠損を区別する。prompt／response本文、生token、個人識別子はmetricへ保存しない。
''',
    "complete AC4 observability contract",
)
issue += '''\n\n## 進捗（2026-09-06）: AC-4 usage provenance / 欠損契約\n\n- 既存 `tokenUsage` の数値互換性は維持し、providerが返さない側は従来どおり0加算する。一方で `tokenUsageCoverage` を追加し、complete / partial / missingを別カウンタとして保持するため、実際に0と報告された場合とusage自体が不明な場合を混同しない。\n- token算定sourceは現時点でprovider自己申告値だけであり、local tokenizerによる推定値を暗黙に混ぜない。`tokenUsageSource=provider_reported_only` としてAPI契約へ固定した。\n- 集計scopeは `current_process_by_provider_kind`。`total` は同一process内のprovider kind横断合計であり、model / task / tenant / user別の台帳ではない。これらの識別子やprompt/response本文、生token列をmetricへ保存しない。\n- この変更は観測契約だけを閉じる。共有予算reserve/settle、hard/soft limit、自動降格、複数worker共有store（AC-3/5/6）は引き続き未実装で、本IssueはOpenを維持する。\n'''
issue_path.write_text(issue, encoding="utf-8")

print("OPS-LLM-COST-01 AC-4 usage provenance patch applied")
