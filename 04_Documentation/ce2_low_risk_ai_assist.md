# CE2 Low-risk AI Assist（proposal-only運用）

## 概要

CE2では AI の出力を**即時適用せず**、`proposalId + diff + sourceBundleHash` を持つ提案として扱います。

- API: `POST /ai/proposals/island-summary`
- 監査記録: `POST /ai/proposals/audit`
- UI: 提案は `Adopt / Hold / Reject` で人間が確定

## 安全境界

- 自動適用（auto-apply）は実装しません。
- `adopt` は明示的な人間操作でのみ実行します。
- 監査ログ（採用/保留/却下）は proposalId 単位で残します。

## 最低運用フロー

1. 提案生成（proposed）
2. 人間レビュー（内容確認）
3. `adopt` / `hold` / `reject`
4. 監査イベント確認（proposalIdベース）
