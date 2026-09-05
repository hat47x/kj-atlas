from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R35 — provider usage に call provenance を結び付ける"
assert heading not in text
record = r'''

## R35 — provider usage に call provenance を結び付ける

R33まででprovider-reported usageをcanonical promptへSHA-256で結び付けたが、成功responseが**いつ・どのtransport・どのtrace・どのexecution pathで得られたか**という既存 `LLMCallMetadata` の監査情報はmeasurement reportへ保存していなかった。R35ではprovider実測時に `response.metadata.as_audit_fields()` を各routeへ保存し、usage値とcall provenanceを同じrowで追跡できるようにした。

- measurement reportはtop-level `provider_call_provenance={version: 1}` と、各routeの `provider_call` を持つ。dry-runでは `provider_call=null` のままであり、実測証拠へ昇格しない。
- measured routeでは `provider` / `provider_kind` / `model_id` / `transport` / `requested_at` / `trace_id` / `fallback_to_none` / `execution_path` を既存audit metadataからそのまま保存する。
- analyzerはprovider/model/kindの整合、非空のtransport/requested_at/trace_id、`fallback_to_none=false`、`execution_path=primary` を要求する。fallback・non-primary・trace欠落・provenance契約欠落はfail-closedする。
- prompt fingerprintとcall provenanceは役割を分ける。前者は「何を送ったか」、後者は「どのcallとして実行されたか」のローカル監査証跡であり、token値は引き続きprovider-reported `input_tokens` だけを正本とする。

branch-only GitHub Actions run `33952594490` で、R23〜R35関連を含む **68 test**、ruff、`git diff --check` が成功した。provider-call provenanceの保存、primary pathの正常系、fallback/non-primary、trace欠落、旧provenance契約欠落、dry-run非昇格を回帰へ固定し、一時patch/workflowも同run内で自己削除した。

**非主張**: `provider_call` はproviderが署名したreceiptではなく、KJ Atlas側の既存 `LLMCallMetadata` に基づく監査情報である。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは未変更である。本Issueは引き続きIn Progressであり、未完了ACは完了扱いにしない。
'''
path.write_text(text.rstrip() + record.rstrip() + "\n", encoding="utf-8")
