from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")

replacements = {
    "R33 run `33951131455` ではR23〜R33関連を含む62 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33でroute/task/provider/model/usageとcanonical prompt fingerprintのfail-closed検証を固定した。":
    "R35 run `33952594490` ではR23〜R35関連を含む68 test・ruff・`git diff --check` が成功した。provider実測reportについてもR32/R33/R35でroute/task/provider/model/usage、canonical prompt fingerprint、primary call provenanceのfail-closed検証を固定した。",
    "  - `tests/test_ai_route_provider_prompt_fingerprint.py`\n":
    "  - `tests/test_ai_route_provider_prompt_fingerprint.py`\n  - `tests/test_ai_route_provider_call_provenance.py`\n",
    "  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usageとcanonical prompt SHA-256を含むmeasurement reportを保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/fingerprintが現在のcanonical builderと一致した場合だけ方式比較の入力にする。":
    "  - 明示的に選んだnamed model/providerで1回以上の代表規模requestを行い、provider-reported usage、canonical prompt SHA-256、primary call provenanceを含むmeasurement reportを保存する。保存reportは `scripts/analyze_ai_route_provider_measurement.py` を通し、route/task/provider/model/usage/fingerprintに加えてtransport/requested_at/trace_id、fallbackなし、primary execution pathが整合した場合だけ方式比較の入力にする。",
    "1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33 analyzerへ通す。** R33まで拡張したR20ハーネスを使う。":
    "1. **named provider/modelの実入力tokenを測り、保存reportをR32/R33/R35 analyzerへ通す。** R35まで拡張したR20ハーネスを使う。",
    "R33以降のreportにはexact UTF-8 promptのSHA-256を含め、現在のcanonical builderと一致しないstale/legacy reportは比較根拠へ使わない。":
    "R35以降のreportにはexact UTF-8 promptのSHA-256とprovider call provenanceを含め、現在のcanonical builderと一致しないstale/legacy report、fallback/non-primary call、trace欠落reportは比較根拠へ使わない。",
}
for old, new in replacements.items():
    assert text.count(old) == 1, old
    text = text.replace(old, new, 1)

heading = "## R36 — R35後のprovider実測readiness同期"
assert heading not in text
record = r'''

## R36 — R35後のprovider実測readiness同期

R35でfuture provider measurementへcall provenance検証を追加したため、Issue前半の受入条件注記・検証計画・実使用確認・次の判断順序を現行実装へ同期した。今後のnamed provider/model実測reportは、provider-reported usageだけでなく、canonical prompt SHA-256とprimary call provenance（transport / requested_at / trace_id、fallbackなし、primary execution path）までanalyzerで整合した場合だけR21の方式比較入力にする。

本同期はdocs-onlyであり、外部provider実測・A2/B/C採択・production cap/route変更を行わず、未完了ACを完了へ変更しない。
'''
text = text.rstrip() + record.rstrip() + "\n"
path.write_text(text, encoding="utf-8")
