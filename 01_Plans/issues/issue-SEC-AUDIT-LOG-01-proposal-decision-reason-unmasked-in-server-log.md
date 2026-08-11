# Issue: SEC-AUDIT-LOG-01 提案却下理由（自由記述）がサーバーログへ無加工で記録される

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`
- Related ADR/Spec: N/A
- Expected verification level: `unit`

## 課題

- 現在の問題: `POST /ai/proposals/audit`（`record_proposal_decision`、`routes/ai.py:620-635`）は、`payload.reason`（`ProposalDecisionAuditRequest.reason`、`models_ai.py`で長さ制約なしの任意自由記述）を`logger.info(..., extra={"reason": payload.reason or "", ...})`でサーバーログへそのまま記録する。同じ関数で`actor`は本ラウンドで`audit.py`の`sha256(...).hexdigest()[:24]`方式に合わせてハッシュ化したが、`reason`は自由記述本文であり、同じ機械的な変換では解決しない。
- 判断が必要な理由: `reason`は「却下・保留の理由」という監査上意味のある自由記述であり、単純にハッシュ化すると監査記録としての価値（なぜ却下したかを後から読める）が失われる。一方、無加工でログに残すと`security.md`が定める「未マスク本文…はログ、スクショ、exportに含めない」という方針に反する可能性がある。選択肢は複数あり（(a) ログへは記録せず既存の`AuditEvent`/`sanitize_metadata()`/`AuditDispatcher`経由の監査ストアへ回す、(b) 長さ上限を設けて切り詰める、(c) 現状どおりサーバーログのみに残すことを許容範囲と明記する）、どれを選ぶかは監査設計の方針判断であり機械的には決められない。
- 利用者または開発への影響: 現状は同梱SPAの5箇所の呼び出し元（`App.tsx`）がすべて`reason: undefined`を送るため実害はないが、`ProposalDecisionAuditRequest`はpublic REST契約であり、SPA以外のクライアントは任意の自由記述を送れる。その場合、機微な内容がサーバーログに無加工で残る。

## 対応方針

- 実施すること: `reason`をサーバーログへ記録する方針（記録する/しない、記録する場合の上限・マスク方法、既存`sanitize_metadata()`/`AuditDispatcher`パイプラインへの統合要否）をMaintainerが決定する。
- 実施しないこと: 方針が決まる前に、`reason`の扱いを機械的に変更すること（安易な切り詰めやハッシュ化は監査記録としての可読性を損なう可能性があるため、判断前に実施しない）。

## 受入条件

- [x] `reason`のログ記録方針（記録有無・上限・パイプライン統合）が決定される。
- [x] 決定に応じて`routes/ai.py`の実装が更新される。

## 検証計画

- 実行する確認: 変更する場合、`cd 03_Implement/backend && python -m pytest tests/test_ce2_proposal_api.py -q`。
- 期待結果: 決定した方針どおりに`reason`が扱われ、既存の`record_proposal_decision`契約（レスポンス形状・422検証）が壊れない。

## 補足

- 発見経緯: 第18ラウンドの「バックエンド機微データのログ漏洩」観点監査で発見。同ラウンドで発見した`actor`（アクター識別子）の無加工ログ記録は、`audit.py`の既存sha256ハッシュ化規約に合わせる機械的修正として本ラウンドで直接対応済み（`routes/ai.py`）。`reason`は自由記述本文であるため機械的な修正が成立せず、本issueとして切り出した。
- `CE2-AUDIT-CONTRACT-01`で方針を確定した。reasonは最大1000文字、通常logと監査DBの双方へ本文を保存せず、`reason_sha256`と`reason_utf8_bytes`だけを専用追記eventへ保存する。可読な理由本文を将来必要とする場合は、retention・閲覧権限・削除請求境界を持つ別の機微情報storeとして再設計する。
