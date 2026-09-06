from __future__ import annotations

import os
from pathlib import Path


def main() -> None:
    test_path = Path("03_Implement/backend/tests/test_llm_provider.py")
    text = test_path.read_text()
    marker = "\ndef test_deepseek_task_model_map_override("
    assert text.count(marker) == 1
    addition = r'''


def test_deepseek_provider_maps_official_v4_usage_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_key = settings.deepseek_api_key
    original_url = settings.deepseek_base_url
    original_model = settings.deepseek_model
    settings.deepseek_api_key = "sk-test-key"
    settings.deepseek_base_url = "https://api.deepseek.com"
    settings.deepseek_model = "deepseek-v4-flash"

    def _fake_urlopen(req, timeout_seconds=120):
        response = {
            "choices": [{"message": {"content": "ok"}}],
            "usage": {
                "prompt_tokens": 321,
                "completion_tokens": 1,
                "prompt_cache_hit_tokens": 100,
                "prompt_cache_miss_tokens": 221,
                "total_tokens": 322,
            },
        }
        return _StubHTTPResponse(json.dumps(response))

    monkeypatch.setattr("kj_atlas_api.llm.provider.open_trusted_http", _fake_urlopen)

    try:
        response = DeepSeekProvider().generate(
            LLMRequest(
                task="suggest_document_title",
                prompt="test prompt",
                max_tokens=1,
            )
        )
        # DeepSeek V4 Chat Completions reports input/output usage using the
        # OpenAI-compatible prompt_tokens/completion_tokens fields. Cache split
        # fields are diagnostics; the provider-reported prompt total is the
        # measurement source of truth.
        assert response.input_tokens == 321
        assert response.output_tokens == 1
    finally:
        settings.deepseek_api_key = original_key
        settings.deepseek_base_url = original_url
        settings.deepseek_model = original_model
'''
    test_path.write_text(text.replace(marker, addition + marker, 1))

    issue_path = Path(
        "01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md"
    )
    issue = issue_path.read_text()
    heading = "## R52 — DeepSeek V4公式usage shapeをtransport回帰へ固定"
    assert heading not in issue
    run_id = os.environ["R52_RUN_ID"]
    issue += f'''\n\n{heading}\n\nR50/R51の事前整備完了境界後、外部実測直前のtransport契約を現行DeepSeek V4公式Chat Completions APIと再照合した。公式APIは引き続き `usage.prompt_tokens` / `usage.completion_tokens` を返し、Token Usage資料も実際のtoken数はAPIが返すusageを正本とする。production parserはこのshapeを既に読んでいたが、既存DeepSeek成功テストはpayload/model/thinking/contentまででusage mappingを直接固定しておらず、R20系fake providerはtransport parserを通らないため、parser driftが外部実測時まで潜伏する具体的な回帰穴があった。\n\nR52ではproduction実装やmeasurement schemaを変更せず、DeepSeek V4相当responseに `prompt_tokens` / `completion_tokens` とcache splitを含め、`LLMResponse.input_tokens` / `output_tokens` がprovider-reported totalをそのまま保持するdirect transport regressionを追加した。cache splitやbytes/charsからtokenを再計算しない。\n\nGitHub Actions run `{run_id}` でDeepSeek provider近接回帰、R20/R48/R51 measurement系回帰、ruff、`git diff --check`、active issue validator、issue tests、full docs checkを検証した。one-shot workflowは同run内で自己削除する。\n\n**非主張**: R52でも外部DeepSeek APIは呼んでおらず、実provider-reported token値は未取得である。新しいprovenance層や方式候補は追加せず、A2/B/C採択、production cap/route、十分な余裕policy、未完了ACは変更しない。R50の停止境界を維持し、次の本質的ゲートは明示的に許可されたnamed provider/model外部実測のままである。\n'''
    issue_path.write_text(issue.rstrip() + "\n")


if __name__ == "__main__":
    main()
