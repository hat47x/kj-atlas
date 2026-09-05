from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R41 — context-window hard-fitへ資料source provenanceを必須化"
assert heading not in text
record = r'''

## R41 — context-window hard-fitへ資料source provenanceを必須化

R39でoperatorがnamed model/providerのcontext-window値を明示した場合だけhard-fitを算出できるようにしたが、その数値が**どのprovider/model資料を根拠にしたか**は結果へ残っておらず、後から値だけが独り歩きする余地があった。R41ではcontext-window値と資料sourceを対にして扱い、hard-fit判断の来歴を監査可能にした。

- `analyze_ai_route_provider_measurement.py` の `analyze(...)` / context budget summaryへ `context_window_source` を追加した。
- `context_window_tokens` を渡す場合、空でない `context_window_source` を必須とする。sourceなしの数値入力はfail-closedし、逆にtoken値なしでsourceだけを渡す組合せも拒否する。
- CLIに `--context-window-source` を追加し、provider/modelの公式ドキュメントURL、文書ID、版・日付を識別できる参照等を記録できるようにした。
- 出力ではsource文字列を正規化して保持し、`context_window_source_kind=operator-supplied-document-reference` と明示する。R39のhard-fit算術、production output reserve、layout Cのmax-single semantics、`sufficient_headroom_policy=null` は変更しない。
- sourceは**監査用provenance**であり、analyzer自身がURL先を取得して真正性・最新性・記載内容を自動検証するものではない。このため、sourceを添えただけでcontext-window値がproviderにより保証されたとは主張しない。
- CLIの引数不整合はstructured `context-window-argument-error:*` として非decision-readyで返す。measurement report自体のroute/task/provider/model/usage/prompt/provider-input/call provenance検証は従来どおりである。

branch-only GitHub Actions run `33955296602` でR23〜R41関連を含む **80 test**、ruff、`git diff --check` が成功した。一時patch/workflowは同run内で自己削除した。

**非主張**: R41は実modelのcontext-window値を取得・固定せず、外部providerを呼ばず、資料sourceの真正性を自動検証せず、安全余裕policy・A2/B/C採択・production cap/routeを決定しない。未完了ACとSafeMode・防PII・structured-text-only・proposal-only境界は未変更である。
'''
path.write_text(text.rstrip() + record.rstrip() + "\n", encoding="utf-8")
