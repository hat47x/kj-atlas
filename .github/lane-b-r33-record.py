from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
heading = "## R33 — provider usage と canonical prompt のfingerprint binding"
assert heading not in text
record = r'''

## R33 — provider usage と canonical prompt のfingerprint binding

R32で保存measurement JSONのroute/task/provider/model/usage整合はfail-closed化したが、そのusageが**現在のcanonical promptそのもの**を測った結果かは、route名だけでは後から証明できなかった。prompt実装が変わった後に古いusageを誤って再利用することを防ぐため、R33ではproviderへ送るexact UTF-8 promptにSHA-256 fingerprintを付与し、measurement harnessとresult analyzerを同じidentity contractで結んだ。

- `measure_ai_route_provider_tokens.py` は各routeの `prompt.sha256` と、top-level `prompt_fingerprint={algorithm: sha256, encoding: utf-8}` を記録する。hashはprompt identity専用でありtoken推定には使わない。
- `analyze_ai_route_provider_measurement.py` は保存reportのoptional A2/C構成を読み、同じmodel・canonical builderから現在のrequestを決定論的に再生成する。routeごとのSHA-256が一致しなければ `prompt-fingerprint-mismatch` でfail-closedする。
- fingerprint contract自体がない旧形式reportも `unsupported-or-missing-prompt-fingerprint` としてdecision-readyに昇格させない。prompt変更後は再測定が必要になる。
- canonical request集合にない余分なrouteも `unexpected-route` として拒否する。R32のexact task / exact C route-set検証と合わせ、route名・task・prompt本体の三層でmeasurement identityを固定する。
- SHA-256、UTF-8 byte数、文字数はいずれもtoken数へ変換しない。token値と差分は引き続きprovider-reported `input_tokens` のみを正本とする。

branch-only GitHub Actions run `33951131455` で、R23〜R33関連を含む **62 test**、ruff、`git diff --check` が成功した。38-request dry-runの全prompt fingerprint、1文字変更時のfingerprint変化、stale/legacy reportのfail-closedを回帰へ固定し、一時patch/workflowも同run内で自己削除した。

**非主張**: fingerprintはprovider responseの暗号学的署名ではなく、偶発的なstale/mismatched measurementを防ぐための再現可能なprompt identityである。外部providerは呼んでおらず、実token値・context余裕・cost・latency・品質、A2/B/C採択、production cap/routeは引き続き未変更である。
'''
path.write_text(text.rstrip() + record.rstrip() + "\n", encoding="utf-8")
