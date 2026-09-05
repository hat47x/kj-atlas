from pathlib import Path

path = Path("01_Plans/issues/issue-AI-IR-SCALE-01-preserve-large-round-evidence-under-token-budget.md")
text = path.read_text(encoding="utf-8")
old = "branch-only GitHub Actions run `33950682087` で、R32とR23〜R30関連を含む **54 test**、ruff、`git diff --check` が成功した。workflowは同run内で自己削除した。テストではprompt byte値をprovider token値と意図的に無関係な数へ崩し、差分計算が `provider_reported.input_tokens` のみを使うことも固定した。"
new = "branch-only GitHub Actions run `33950682087` で初期54 test、hardening後のrun `33950879266` でR32とR23〜R30関連を含む **56 test**、ruff、`git diff --check` が成功した。後者ではcanonicalなlocal-01〜30 + globalのexact setとroute task identityも固定し、31件という件数だけを満たす改変reportをfail-closedする。workflowは各run内で自己削除した。テストではprompt byte値をprovider token値と意図的に無関係な数へ崩し、差分計算が `provider_reported.input_tokens` のみを使うことも固定した。"
assert text.count(old) == 1
path.write_text(text.replace(old, new), encoding="utf-8")
