from pathlib import Path

ISSUE = Path("01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md")
text = ISSUE.read_text(encoding="utf-8")

replacements = [
    ("- Status: Draft\n", "- Status: Open\n"),
    ("- Owner: Stream H（QA P0 Hold解除準備）\n", "- Owner: Stream H（QA E2E）\n"),
    ("- Scope: `01_Plans/issues/`（docs-only）\n", "- Scope: 本ファイル, `03_Implement/frontend/e2e/`（Open後の追加検証はテスト資産のみ。製品実装変更は別Issue）\n"),
    ("### Draft理由\n", "### Draft理由（当時。2026-07-18までに解消済み）\n"),
    ("### Execution Hold理由\n", "### Execution Hold理由（当時。2026-07-18までに解消済み）\n"),
]
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one occurrence: {old!r}; found {text.count(old)}")
    text = text.replace(old, new, 1)

if "## 2026-09-07 Open化同期 — 承認済みゲートを現在状態へ反映" in text:
    raise SystemExit("Open sync already present")

text = text.rstrip() + """

## 2026-09-07 Open化同期 — 承認済みゲートを現在状態へ反映

2026-07-16〜18に成立していた解除条件と、その後に積み上がったE2E証跡を、triageが読む現在状態へ同期する。前節までの各時点で「Draft / Execution: Hold」と記録した箇所は**その時点の歴史証拠**として保持し、現在状態の主張には使わない。

- Pending-1（PUB-01公開境界）とPending-2（I18N-03外部公開判定）は、2026-07-16にMaintainer承認済み。
- B-ENV-01（ADR-0019準拠の実行経路）は、2026-07-18にDocker Compose標準経路として固定済み。SQLite/mockはDockerを実行できない場合の例外経路であり、標準経路と混同しない。
- その後、公開互換 / I18N等価 / readOnly + SafeMode の3軸に対するE2E資産と回帰証跡が追加され、readOnlyのカードdrag欠落など実際に見つかった境界逸脱も隠さず是正・回帰固定されている。
- したがって `Open Readiness: Prepared` / `Execution: Ready` と整合させ、`Status` を `Open` とする。古いDraft gateだけを理由にtriageから除外し続けない。
- この同期は**3軸のcurrent-main再検証完了、release承認、翻訳品質の人間レビュー完了を主張しない**。Openは「標準経路で実行して証拠を現在化できる状態」を意味する。
- Draft→Open同期自体はdocs-only。Open後の追加変更はE2Eテスト資産に限定し、製品実装の新規変更が必要な欠落を見つけた場合は、本Issueへ抱え込まず別Issueとして切り出す。既存specで3軸を十分に覆える場合は重複テストを作らず、Compose-backed再実行と証跡同期を優先する。
"""

ISSUE.write_text(text, encoding="utf-8")
print("QA-PUB-01-I18N-03 current state synchronized: Draft -> Open")
