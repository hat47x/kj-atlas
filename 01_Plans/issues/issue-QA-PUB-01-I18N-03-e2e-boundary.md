# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification boundary plan
- Status: Draft (Open-Readiness Prepared / Execution Hold)
- Priority: P0
- Owner: Stream H（QA P0 Hold解除準備）
- Scope: `01_Plans/issues/`（docs-only）
- Related backlog: `PUB-01`, `I18N-03`, `QA-E2E-USE-01`
- Policy reference: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## Phase 1: Read Gate（Draft/Hold理由と依存抽出）

### Draft理由
- 境界3軸（公開互換/I18N等価/安全境界）はあるが、Open判定時に必要な承認証跡欄が不足。
- どの境界逸脱が即Holdか（重大度閾値）が記述されていない。

### Execution Hold理由
- PUB-01 と I18N-03 の最終承認IDが未確定。
- `ADR-0019` に基づく実行経路の事前選択が未完了。

### 依存ブロッカー
| Blocker ID | 内容 | 計測条件 | 解消責務 |
|---|---|---|---|
| B-PUB-01 | 公開境界承認未了 | `Pending-1` に承認ID/日付追記 | Product/Reviewer |
| B-I18N-01 | I18N-03承認未了 | `Pending-2` に承認ID/日付追記 | Localization reviewer |
| B-ENV-01 | 実行経路未固定 | Compose/SQLite/例外のいずれか選択済み | QA lead |

## Phase 2: ADR C/D/C（簡易）
### Context
P0境界Issueだが、実行前提と承認証跡が欠け、Open化判断が担当者依存になる。

### Decision
Open化ゲートを「3軸境界 + 承認証跡 + 実行経路固定」で定義する。

### Consequences
- 境界Issueの着手可否が再現可能。
- 承認未了状態での先行実装を予防。

## Phase 3: Plan（Open化条件・責務・最小検証セット）

### Open化条件
- O-PUB-01: 公開互換/ I18N等価/ 安全境界の3軸が明文化済み。
- O-PUB-02: 承認ID（PUB/I18N）が Pending欄に記録済み。
- O-PUB-03: `Execution: Hold` 解除条件が1行で判定可能。

### 責務
- Stream H: 境界定義と停止条件の維持。
- Stream F: Open後の実行シナリオ実装。
- Reviewer: 承認ID付与と解除判断。

### 最小検証セット
1. 3軸定義が曖昧語なく記載。
2. 自動化/人間レビュー責務が混在しない。
3. Hold解除条件が measurable。

## Phase 4: Execute（具体化）

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

## Phase 5: Verify（測定可能性チェック）

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
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|O-PUB-01|O-PUB-02|O-PUB-03|Pending|Execution: Hold|ADR-0019" 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `git diff --check -- 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`

## Phase 6: Proceed（3区分）
- **Open化可能**: O-PUB-01〜03充足。
- **追加判断必要**: 承認IDが一部未記入。
- **保留継続**: B-PUB-01/B-I18N-01/B-ENV-01のいずれか未解消。

### Pending approvals（未承認は保持）
- Pending-1: 公開境界（PUB-01）最終承認。
- Pending-2: I18N-03 の外部公開判定承認。

### Execution
- `Execution: Hold`（Pending解消まで維持）
