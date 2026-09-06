from pathlib import Path

path = Path('01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md')
text = path.read_text(encoding='utf-8')

replacements = [
    ('- Status: Draft\n', '- Status: Open\n', 1),
    ('- Scope: 本ファイルのみ（docs-only）\n', '- Scope: 本ファイル, `03_Implement/frontend/e2e/`（テスト資産のみ。製品実装は対象外）\n', 1),
    ('### Draft理由（現状）\n', '### Draft理由（当時。2026-07-18までに解消済み）\n', 1),
    ('### Execution Hold理由（現状）\n', '### Execution Hold理由（当時。2026-07-18までに解消済み）\n', 1),
    (
        '3. **Scope Gate**: 本Issueは docs-only であり、実装変更要求を含めない。\n',
        '3. **Scope Gate**: Draft→Open同期は docs-only で行い、Open後の実行は `03_Implement/frontend/e2e/` のテスト資産に限る。製品実装変更は含めない。\n',
        1,
    ),
    (
        '- DoD-O1: 実装非実施（docs-only）が明示され、対象外変更を含まない。\n',
        '- DoD-O1: Draft→Open同期は docs-only とし、Open後の実行でも変更対象はE2Eテスト資産に限定して製品実装を含めない。\n',
        1,
    ),
    ('### Hold条件の扱い\n', '### Hold条件の扱い（当時。2026-07-18までに解消済み）\n', 1),
]

for old, new, expected in replacements:
    actual = text.count(old)
    if actual != expected:
        raise SystemExit(f'unexpected replacement count for {old!r}: {actual} != {expected}')
    text = text.replace(old, new, expected)

section = '''\n\n## 2026-09-07 Open化同期 — 承認済みゲートを現在状態へ反映\n\n2026-07-16〜18に成立していた解除条件を、triageが読む現在状態へ同期する。前節までのうち、各rerun時点で「Draft / Execution: Hold」と記録した箇所は**その時点の歴史証拠**として保持し、現在状態の主張には使わない。\n\n- Pending-1（実運用E2E環境での実行承認）とPending-2（I18N境界最終レビュー）は、2026-07-16にMaintainer承認済み。\n- B-USE-03（G1/G2/G3のentry/exit証跡欄）とO-USE-02（ADR-0019準拠の実行経路）は、2026-07-18に解消済み。標準経路はDocker Compose、SQLite/mockは差分リスクを記録する例外経路とする。\n- したがって `Open Readiness: Prepared` / `Execution: Ready` と整合させ、`Status` を `Open` とする。Draft gateだけを理由にtriageから除外し続けない。\n- 本同期は**S1〜S4の完了、release承認、実環境での全E2E合格を主張しない**。Openは「実行して証拠を作れる状態」を意味する。\n- Draft→Open同期自体はdocs-only。Open後の最初の実行バッチは、既存E2E資産をS1〜S4へ棚卸しし、実際に不足するjourneyがある場合だけ `03_Implement/frontend/e2e/` にテストを追加する。製品実装、SafeMode契約、公開挙動は変更しない。既存specで十分な場合は重複テストを作らず、実行証跡の同期を優先する。\n'''

if '## 2026-09-07 Open化同期' in text:
    raise SystemExit('Open sync section already exists')
text = text.rstrip() + section + '\n'
path.write_text(text, encoding='utf-8')
print('normalized QA-E2E-USE-01 to Open execution-ready state')
