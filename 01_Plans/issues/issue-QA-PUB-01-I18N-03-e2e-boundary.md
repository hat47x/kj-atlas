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
