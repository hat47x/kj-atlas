# Issue: SEC-DOC-BOUND-05 merge-decision-logs系GETがpagination無しで無制限に増える監査履歴を返す

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/document_repository.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-04-document-access-admin-list-no-pagination.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `GET /docs/{doc_id}/merge-decision-logs/by-group/{group_id}`（`routes/docs.py:744`）と`GET /docs/{doc_id}/merge-decision-logs/restore/{snapshot_version}`（`routes/docs.py:770`）は、それぞれ`document_repository.py`の`list_merge_decision_logs_by_group`（L41-55）/`list_merge_decision_logs_by_snapshot`（L58-73）を呼び出すが、いずれも`.limit(...)`が無い:
    ```python
    return db.scalars(
        select(MergeDecisionLogRow)
        .where(MergeDecisionLogRow.tenant_id == tenant.tenant_id)
        .where(MergeDecisionLogRow.doc_id == doc_id)
        .where(MergeDecisionLogRow.group_id == group_id)
        .order_by(MergeDecisionLogRow.id.asc())
    ).all()
    ```
  - `MergeDecisionLogRow`（`models.py:216-256`）の一意制約は`(tenant_id, doc_id, decision_id)`のみで、`group_id`/`snapshot_version`は一意制約に含まれない。つまり同一グループ/スナップショットに対して、マージ・取り消し・再マージのサイクルごとに新しい`decision_id`の行が積み上がる、正真正銘のappend-onlyな監査ログテーブルである。
  - `03_Implement/backend/src/kj_atlas_api`内の既存の`.limit(...)`使用箇所（`identity_binding.py`、`tenant_context.py`の`MAX_SESSION_TENANT_COUNT=256`）はいずれも無関係な固定用途（存在確認、セッションあたりのテナント数上限）向けの小さな定数であり、監査ログ件数に模倣できる規約ではない。
- 利用者または開発への影響: ドキュメントの候補グループ（またはスナップショット）が長期間の編集で多数のマージ判断イベントを蓄積すると、これらのGETエンドポイントを呼ぶたびに無制限に増え続ける全履歴を1レスポンスで返し続ける。`api.md:131-137`はこの2エンドポイントを「append order」の応答として公開文書化しており、`test_docs_roundtrip.py`等の既存テストでも到達可能な経路であることを確認済み。

## 対応方針

- 実施すること: 監査履歴として1回のレスポンスでどこまで返すべきかという妥当な上限（ページサイズのデフォルト/最大値）と、上限を超えた場合にクライアントが過去分を辿る手段（pagination/cursor、または「直近N件のみ」で十分と判断するか）をMaintainerが決定する。
- 実施しないこと: 監査履歴を返す範囲・件数の決定そのもの。模倣できる既存のpagination規約が無く、「監査ログとしてどこまでの履歴を1回のAPI呼び出しで見せるべきか」は製品判断が必要なため機械的には対応しない。

## 受入条件

- [ ] レスポンスの上限件数（デフォルト/最大）と、上限超過時の扱い（pagination提供か、直近N件のみで仕様上十分と明記するか）が決定される。
- [ ] 実装した場合、大量の判断イベントを持つグループ/スナップショットに対する統合テストでレスポンス件数が上限内に収まることを確認する。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認: 実装後、多数のマージ判断イベントを持つ候補グループ/スナップショットに対する統合テストで、レスポンス件数が指定した上限を超えないことを確認する。
- 期待結果: レスポンスサイズが常に上限内に収まる、またはドキュメントで明示的に許容範囲として規定される。

## 補足

- 発見経緯: 第31ラウンドの「backend unbounded-query/resource-exhaustion」観点監査で発見。独立検証者が`models.py`の一意制約（`group_id`/`snapshot_version`は一意制約対象外）を確認し、実際に行が積み上がりうることを裏付けた。`01_Plans/issues/`内の関連issue（`issue-FB-RM-MID-03`はフロントエンド側の監査JSONエクスポート生成器で無関係、直近コミット`13d68ec5`の「proposal audit trail上限」もフロントエンドのメモリ内配列（`App.tsx`の`proposalAuditTrail`）であり本issueが指すbackendの読み取り経路とは別）を確認し、本ギャップを扱う既存issueが無いことを確認済み。`SEC-DOC-BOUND-04`と同種（読み取り経路のレスポンスpagination欠如）だが対象テーブル・エンドポイントが異なるため別issueとして分離。
