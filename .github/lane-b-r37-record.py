from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R37 — DeepSeek usage を exact chat input message content に結び付ける"
assert heading not in text
record = r'''
## R37 — DeepSeek usage を exact chat input message content に結び付ける

R33のcanonical prompt SHA-256とR35のcall provenanceにより、provider-reported usageを「現在のuser prompt」と「primary callの監査情報」へ結び付けられるようになった。一方、DeepSeek/OpenAI-compatible chat transportが入力tokenとして実際に送るのはuser prompt単体ではなく、task由来のsystem messageとuser messageの組である。system message templateが将来変わった場合、R33だけでは古いusageを現在と同じtransport inputの観測として誤利用する余地が残るため、R37でこの境界を閉じた。

- `kj_atlas_api.llm.provider._openai_chat_messages()` を、DeepSeek/OpenAI-compatible transportが送るsystem+user message contentの単一source of truthとして切り出し、実transport自身が同helperを使う。
- DeepSeek実測responseでは、measurement reportに `provider_input={kind: openai-chat-messages-v1, sha256: ...}` を各routeへ保存する。SHA-256対象は同helperが返すmessage配列のcanonical JSON / UTF-8である。
- top-level `provider_input_provenance` はversion / kind / algorithm / encodingを固定する。dry-runではrouteの `provider_input=null` のままであり、provider実測証拠へ昇格しない。
- analyzerは `actual_provider_kind=deepseek` のrouteがある場合だけprovider-input provenance契約と、現在のcanonical requestから再生成したsystem+user message SHA-256との一致を要求する。missing / kind mismatch / stale hashはfail-closedする。
- generic providerのmeasurementにはDeepSeek固有のmessage契約を強制しない。R35までのprovider/model/prompt/call-provenance検証をそのまま維持する。
- 同一user promptでもtaskが異なればsystem messageが変わり、message fingerprintも変わることを回帰で固定した。

branch-only GitHub Actions run `33953053815` で、R23〜R37関連を含む **73 test**、ruff、`git diff --check` が成功した。一時patch/helper/workflowも同run内で自己削除した。

**非主張**: provider-input fingerprintはprovider署名receiptではなくKJ Atlas側の入力同一性証跡であり、tokenizerやtoken数を推定するものではない。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは未変更である。本Issueは引き続きIn Progressであり、未完了ACは完了扱いにしない。
'''
path.write_text(text.rstrip() + "\n\n" + record.strip() + "\n", encoding="utf-8")
