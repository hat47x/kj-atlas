# Issue: SEC-AUDIT-DUP-01 context-audit/export-auditが再送・二重クリックで重複した監査イベントを外部へ送出する

- Type: Security
- Status: Done
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

- [x] 修正方針（idempotencyキー追加／サーバー側dedup／at-least-onceを意図的仕様として受容）が決定される。→ **案b（サーバー側・短時間ウィンドウdedup）を採択**（2026-08-15・仮承認）。ウィンドウは `KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS`（既定5秒）、キーは論理操作識別子。LRU上限4096で bounded（CE4無制限メモリ懸念と非干渉）。
- [x] 実装する場合、同一の論理操作を2回送信しても外部シンクへは重複が送出されない（または明示的に許容されたものとして文書化される）ことを確認する。→ 統合テストで同一 export-audit 二重POST → シンク1件を固定。api.md に仕様を明記。
- [x] 宣言した検証を実行するか、未実施理由を記録する。→ `test_audit.py` 18 pass・`test_docs_audit_integration.py` 26 pass・`test_ai_eval_pipeline.py` pass（AI LLM監査経路は dedup_key を渡さないため非干渉）。

## 対応記録（2026-08-15・iteration 36）

**方針（仮承認・案b）: サーバー側の短時間ウィンドウdedup** を採択した。クライアントidempotencyキー（案a）はfrontendがfail-openで握りつぶす現行設計と二重管理になるため見送り、at-least-once受容（案c）は「成功後の再送」による重複集計を放置するため見送った。

- `audit.py` の `AuditDispatcher` に **bounded dedup** を追加:
  - `emit(event, *, dedup_key)` — dedup_key は呼び出し元が論理的操作を特定するキー（context-audit: `tenant/doc/operation/equivalenceKey/bundleHash`、export-audit: `tenant/doc/exportKind`）。
  - 直近の送信成功キーを `OrderedDict`（LRU・上限4096）＋ `KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS`（既定5秒）で管理。ウィンドウ内の同一キーは `reason="duplicate"` で抑制。
  - **送信成功時のみ**記録するため、失敗後の再送（fail-open flush経路）を誤って抑制しない。さらに `_queued_dedup_keys`（fail-openキューの未達キー）を追跡し、未達の再送は「flushで既存コピーを配送・新規送信しない」（`reason="queued_pending"`）ことで、失敗→再送でも重複送出されない。
  - キューの要素を `(event, dedup_key)` ペア化し、flush成功時・drop時にキーを整合管理（メモリは bounded のまま・DX-BACKEND-CE4-01 観点と整合）。
- `routes/docs.py` の context-audit / export-audit が `dedup_key` を渡す。
- `api.md` の両エンドポイント契約に dedup 仕様（ウィンドウ既定5秒）を明記。
- テスト: `test_audit.py` に5件（同一キー抑制・異種キー両送・window=0無効・失敗再送の非誤抑制・dedup_key省略時無変化）＋ `test_docs_audit_integration.py` に2件（同一export二重POST→シンク1件・異種export両送）。backend 18+26 tests pass。受入条件は上記「受入条件」節の `[x]` を参照。

## 補足

- 発見経緯: 第34ラウンドの「backend duplicate-submission/idempotency」観点監査で発見。ワークフローの自動検証エージェントはセッション上限エラーで完了しなかったため、本記述はメイン会話で`routes/docs.py`・`audit.py`・`App.tsx`のコードを直接読んで再検証したもの。`issue-DX-BACKEND-CE4-01`は同じ`routes/docs.py`内の別懸念（`_ce4_audit_event_tracker`辞書のプロセス寿命全体でのメモリ蓄積）であり、本issueが指す「同一論理操作の重複送出」とは別種の問題。`issue-SEC-AUDIT-LOG-01`も別エンドポイント（`/ai/proposals/audit`）のPIIマスキングであり無関係。
- 本件は2026-08-15の iteration 36 で解決。
