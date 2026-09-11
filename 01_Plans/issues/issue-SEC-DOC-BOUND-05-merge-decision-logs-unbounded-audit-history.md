# Issue: SEC-DOC-BOUND-05 merge-decision-logs系GETがpagination無しで無制限に増える監査履歴を返す

- Type: Security
- Status: In Progress
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/sui_sensemaking_api/routes/docs.py`, `03_Implement/backend/src/sui_sensemaking_api/document_repository.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-04-document-access-admin-list-no-pagination.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `GET /docs/{doc_id}/merge-decision-logs/by-group/{group_id}`と`GET /docs/{doc_id}/merge-decision-logs/restore/{snapshot_version}`は、それぞれ`document_repository.py`の`list_merge_decision_logs_by_group` / `list_merge_decision_logs_by_snapshot`を経由してappend-only監査ログを読むが、件数上限とpaginationが無い。
  - `MergeDecisionLogRow`の一意制約は`(tenant_id, doc_id, decision_id)`のみで、`group_id`/`snapshot_version`は一意制約に含まれない。同一グループ/スナップショットに対してマージ・取り消し・再マージのサイクルごとに新しい`decision_id`の行が積み上がる。
- 利用者または開発への影響: 長期間の編集で多数の判断イベントを蓄積すると、対象GETを呼ぶたびに全履歴を1レスポンスで返し続け、DB負荷とレスポンスサイズが無制限に増加する。

## 対応方針

- `SEC-DOC-BOUND-04` で確立済みのkeyset pagination規約を横展開する。
- `MergeDecisionLogRow.id` 昇順を安定したcursorとし、`cursor`は直前ページ末尾のrow id、`limit`は既定100・最大500とする。
- `limit + 1`件を取得して`has_more`を判定し、次ページがある場合だけ`X-Next-Cursor`へ最後に返したrow idを設定する。
- 既存レスポンスbodyの`list[MergeDecisionRecord]` shapeは維持し、pagination metadataはheaderに限定する。
- `by-group`と`restore/{snapshot_version}`へ同一規約を適用する。

## 受入条件

- [ ] 両GETが`cursor`/`limit`を受け取り、既定100・最大500の境界を持つ。
- [ ] 同一group/snapshotに複数イベントがある場合、`id`昇順でページ間の重複・欠落なく辿れる。
- [ ] 次ページが存在するときだけ`X-Next-Cursor`が返る。
- [ ] `limit=0` / `limit=501`等の範囲外入力を422で拒否する。
- [ ] 既存の非pagination利用（query無し）のappend orderとbody shapeを維持する。
- [ ] 宣言したintegration/backend regressionを実行する。

## 検証計画

- SQLite TestClient integrationで5件の判断イベントを作成し、`limit=2`で3ページを辿って順序・no overlap・終端header無しを確認する。
- `by-group`と`restore`の双方で同じcursor契約を確認する。
- 既存merge-decision-log contract regressionとbackend test suiteを実行する。

## 判断記録（2026-09-10）

`SEC-DOC-BOUND-04` が既に `DocumentRow.id` keyset、既定100/最大500、`X-Next-Cursor` を実装しDoneになったため、本issueで残っていた「pagination規約が無いので方式決定が必要」という阻害要因は解消した。同じ読み取り境界の規約を監査ログへ適用し、監査ログ固有の単調増加主キー`MergeDecisionLogRow.id`をcursorとする。offset paginationや「直近N件だけ」の別規約は導入しない。

## 補足

- 発見経緯: backend unbounded-query/resource-exhaustion観点監査で発見。
- `group_id`/`snapshot_version`はappend-only履歴の絞り込み軸であり一意ではないため、cursorはそれらではなく単調増加するrow `id`を使う。
