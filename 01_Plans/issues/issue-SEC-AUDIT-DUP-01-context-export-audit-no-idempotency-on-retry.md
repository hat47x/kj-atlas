# Issue: SEC-AUDIT-DUP-01 context-audit/export-auditが再送・二重クリックで重複した監査イベントを外部へ送出する

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/audit.py`
- Related ADR/Spec: `issue-DX-BACKEND-CE4-01-audit-tracker-unbounded-memory.md`, `issue-SEC-AUDIT-LOG-01-proposal-decision-reason-unmasked-in-server-log.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `POST /docs/{doc_id}/context-audit`（`routes/docs.py:582-661`）と`POST /docs/{doc_id}/export-audit`（`routes/docs.py:664-699`）は、認可・検証を通過すると無条件に`dispatcher.emit(build_event(...))`を呼ぶ。
  - `build_event()`（`audit.py:239-262`）は呼び出しごとに`eventId=f"audit-{uuid4()}"`で新しいIDを発行する。クライアント指定のidempotencyキーは無く、これらの監査イベントはこのサービスのDBに行として永続化されない（`AuditDispatcher`経由で外部HTTPシンクへfire-and-forgetされるのみ）ため、重複を検出できるユニーク制約や`IntegrityError`ベースのdedup経路も存在しない。
  - フロントエンドの`reportAgentTaskExportAudit`（`App.tsx:8606-8619`）は明示的に「fail-open by design (spec §3.4 / ADR-0049 D2)」として、送信失敗を無言で握りつぶす設計になっている。つまりクライアントがこの呼び出しを（ネットワークタイムアウト後の再試行、あるいはユーザーによるアクションの再実行によって）2回発火させても、サーバー側・クライアント側のいずれにも重複を防ぐ・検出する仕組みが無い。
- 利用者または開発への影響: 同一の論理的な監査事実（同一tenant/doc/操作種別/`equivalenceKey`/`bundleHash`、または同一tenant/doc/`exportKind`）に対して、ネットワーク再試行やユーザーの再操作により、相関する手段のない2つの異なる`eventId`を持つ監査イベントが外部監査シンクへ送出されうる。監査・コンプライアンス用途でエクスポート/操作件数を集計する場合、実際より多くカウントされる可能性がある。

## 対応方針

- 実施すること: 修正方針をMaintainerが決定する。候補:
  - (a) クライアント指定のidempotencyキー（例: 操作ごとに一度だけ生成される値）を`ContextAuditPayload`/`ExportAuditPayload`に追加し、サーバー側で短期間の重複排除を行う。
  - (b) `(tenant_id, doc_id, operation, equivalenceKey, bundleHash)`（context-audit）や`(tenant_id, doc_id, exportKind)`（export-audit）を鍵に、短時間ウィンドウでのサーバー側dedupを追加する。
  - (c) 現状の「at-least-once」送出を、ADR-0049 D2のfail-open設計思想と整合する意図的な仕様として受け入れ、その旨をドキュメントに明記するに留める。
  - いずれを採るか、また対象とする時間ウィンドウ/鍵の範囲はMaintainerの判断。
- 実施しないこと: 修正方針の選定なしにdedupロジックを追加すること。既存のDB行ベースのユニーク制約パターン（例: `MergeDecisionLogRow`）はこの経路（DB非永続・fire-and-forget）に適用できず、模倣できる既存の機械的パターンが無い。

## 受入条件

- [ ] 修正方針（idempotencyキー追加／サーバー側dedup／at-least-onceを意図的仕様として受容）が決定される。
- [ ] 実装する場合、同一の論理操作を2回送信しても外部シンクへは重複が送出されない（または明示的に許容されたものとして文書化される）ことを確認する。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認: 実装する場合、同一payloadで`POST /docs/{doc_id}/context-audit`（または`/export-audit`）を2回連続送信する統合テストで、ディスパッチされる監査イベント数を確認する。
- 期待結果: 採用した方針に応じた重複排除が機能する、またはat-least-once送出が仕様として明記される。

## 補足

- 発見経緯: 第34ラウンドの「backend duplicate-submission/idempotency」観点監査で発見。ワークフローの自動検証エージェントはセッション上限エラーで完了しなかったため、本記述はメイン会話で`routes/docs.py`・`audit.py`・`App.tsx`のコードを直接読んで再検証したもの。`issue-DX-BACKEND-CE4-01`は同じ`routes/docs.py`内の別懸念（`_ce4_audit_event_tracker`辞書のプロセス寿命全体でのメモリ蓄積）であり、本issueが指す「同一論理操作の重複送出」とは別種の問題。`issue-SEC-AUDIT-LOG-01`も別エンドポイント（`/ai/proposals/audit`）のPIIマスキングであり無関係。
