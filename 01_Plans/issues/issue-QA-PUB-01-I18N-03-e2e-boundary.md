# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification boundary plan
- Status: Draft (Boundary-Refined / Execution Hold)
- Priority: P0
- Owner: Stream H（QA計画・検証境界）
- Scope: `01_Plans/issues/`（docs-only）
- Related backlog: `PUB-01`, `I18N-03`, `QA-E2E-USE-01`
- Policy reference: `ADR-0019`

## 検証境界（Doneの定義）

| 境界軸 | Done判定 |
|---|---|
| 公開互換 | visibility変更が保存・再読込後も保持される |
| I18N等価 | `ja/en` で同一ユーザージャーニーが同一結果 |
| 安全境界 | readOnly + SafeMode で禁止操作が常に遮断 |

## 自動化と人間レビュー分離
- 自動化: 操作結果・状態遷移・境界遮断の可否。
- 人間レビュー: 翻訳品質、説明文妥当性、監査判断文。

## 再試行/停止ルール
- flaky許容ゼロ。
- 自己修復（再実行/待機調整/fixture確認）は最大3回。
- 4回目相当は Stop、保留理由と再開条件を記録。

## 保留条件
- 依存未解決、E2E環境不足、または上流承認待ちの場合は `Execution: Hold`。


## Open readiness pack（AC/DoD/Validation plan 固定）

### AC（Open化判定用）
- AC-O1: 公開互換 / I18N等価 / 安全境界 の3軸が維持される。
- AC-O2: 自動化と人間レビューの責務分離が崩れていない。
- AC-O3: flakyゼロ + 自己修復3回上限 + 4回目相当Stop が維持される。
- AC-O4: 未解決依存がある場合は `Execution: Hold` を維持する。

### DoD（Open公開品質）
- DoD-O1: `ADR-0019` 参照境界と本Issueの役割が単体再読で判定可能。
- DoD-O2: Validation手順が再実行可能で、境界逸脱時の停止条件が明示済み。
- DoD-O3: 承認未了項目は `Pending` として保持され、確定語へ昇格しない。

### Validation plan（docs-check）
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|Pending|Execution: Hold|ADR-0019" 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `git diff --check -- 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`

### Pending approvals（未承認は保持）
- Pending-1: 公開境界（PUB-01）最終承認。
- Pending-2: I18N-03 の外部公開判定承認。
