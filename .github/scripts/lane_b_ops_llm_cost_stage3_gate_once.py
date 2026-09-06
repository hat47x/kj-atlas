from pathlib import Path

path = Path("01_Plans/issues/issue-OPS-LLM-COST-01-cost-control-contract-unimplemented.md")
text = path.read_text(encoding="utf-8")
anchor = "- この変更は観測契約だけを閉じる。共有予算reserve/settle、hard/soft limit、自動降格、複数worker共有store（AC-3/5/6）は引き続き未実装で、本IssueはOpenを維持する。"
if text.count(anchor) != 1:
    raise SystemExit(f"stage3 gate anchor changed: {text.count(anchor)} matches")
addition = anchor + """

## 進捗（2026-09-06）: 段階3 implementation gate の再確認

- **DB実装能力は阻害要因ではない。** 現行 `generation_repository.py` には、`UPDATE ... WHERE head_version = expected` + `rowcount` によるcompare-and-swapと、`SELECT ... FOR UPDATE` によるrow lockの両方があり、同一DBを共有する複数worker間のatomic reserveを構成できる既存パターンがある。共有予算storeを実装する場合は、process-local lockではなくこのDB transaction境界を再利用する。
- 一方、`llm_escalation_policy.html` §03 は段階3を「月次／環境別の予算上限」「上限到達時のlocal-only降格」「複数worker共有store」とだけ定め、設定値・共有store・降格時挙動を決定してから実装すると明記している。したがって次の契約はまだ一意でない。
  1. 月次budgetの境界時刻・timezoneと、環境別scopeの識別方法。
  2. 外部call前にreserveするtoken量。現行はprovider自己申告usageのみでlocal tokenizer推定を行わず、入力tokenは呼出し前に確定できない。`LLMRequest.max_tokens` は出力上限だけである。
  3. providerがusageを欠損／部分報告した場合のsettle。AC-4では欠損を0と同一視しないため、予算台帳で0消費として扱うことはできない。
  4. budget deny／共有store不達時の遷移先。AC-6は外部providerを許可するfallbackを禁止するが、local再試行・`none`・`held` のどれを正本とするかは未決である。
- よってAC-3/5/6は未完のまま維持する。上記4点を決めずに単一process counterや楽観的な外部call後settleだけを追加しても、複数workerで上限超過を防ぐAC-6を満たさない。長期的な運用契約を固定する判断になる場合は、実装前に補足ADRの要否を判断する。
"""
path.write_text(text.replace(anchor, addition, 1), encoding="utf-8")
print("OPS-LLM-COST-01 stage3 implementation gate documented")
