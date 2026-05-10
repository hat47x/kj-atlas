# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P0
- Owner: Stream H（QA計画・検証境界）
- Scope: 本ファイルのみ（docs-only）
- Expected verification level: `e2e`

## Phase 1: テスト資産棚卸し

| Area | 現行 | 欠落 | 優先度 |
|---|---|---|---|
| Smoke | 起動/読込確認あり | 監査連携の根拠不足 | P2 |
| Core Journey | 部分的に存在 | 作成→編集→レビュー→安全共有の連結不足 | P0 |
| Boundary | SafeMode/readOnly一部あり | I18N境界と同時保証不足 | P0 |

## Phase 2: ADR（Context/Decision/Consequences）

### Decision
- 自動化対象: S1〜S3（Must）、S4（Should）をE2E自動化。
- 人間レビュー対象: 文言妥当性・業務受容性・監査判断。
- flaky許容ゼロ、再試行は最大3回、4回目相当は Stop。

## Phase 4: E2E現実シナリオ拡張（最小本数・高リスク優先）

| Scenario | Priority | Flow | Done判定 |
|---|---|---|---|
| S1 Authoring Continuity | P0 | 作成→編集→再読込 | 欠損ゼロ/整合維持 |
| S2 Review Governance | P0 | 差分記録→人手昇格 | 自動昇格なし |
| S3 Safe Sharing Gate | P0 | 共有試行→条件充足→許可 | fail-closed維持 |
| S4 Import-to-Safe-Export | P1 | sanitize→共有境界確認 | 悪性reject/正常allow |

## I18N境界（QA-PUB-01横断チェック）
- `?locale=en` でも S1〜S3 が同一判定で成立する。
- `?readOnly=1` と locale 切替を併用しても禁止操作境界が維持される。

## Phase 6: 完了判定
- AC: S1〜S3のMust判定軸が固定され、I18N境界が横断項目として組込済み。
- DoD: blocked時テンプレート・再開条件・3回上限停止条件が明示済み。
- 保留: 依存未解決時は `Execution: Hold`。
