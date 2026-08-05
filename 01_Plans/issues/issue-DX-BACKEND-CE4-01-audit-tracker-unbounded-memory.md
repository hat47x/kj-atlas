# Issue: DX-BACKEND-CE4-01 CE4監査追跡辞書がプロセス寿命全体で無制限に蓄積

- Type: Process
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`
- Related ADR/Spec: N/A
- Expected verification level: `integration`

## 課題

- 現在の問題: `routes/docs.py:518`のモジュールレベル辞書`_ce4_audit_event_tracker: dict[tuple[str, str, str, str], _Ce4AuditTrackerState] = {}`は、`query → bundle → proposal → apply`の一連のCE4監査イベントが揃っているかを`(tenant_id, doc_id, equivalenceKey, bundleHash)`単位で追跡する。この辞書をクリアする手段は`reset_ce4_audit_event_tracker()`（`docs.py:522-524`）だけで、リポジトリ全体を検索してもこの関数を呼ぶのはテストのセットアップ/ティアダウン（`tests/test_docs_audit_integration.py`）のみ。本番コードには一切クリア経路が無く、プロセスが処理したすべての一意なタプルがプロセス寿命全体にわたって辞書に残り続ける。`settings.py`の`ce4_audit_require_all_events`は既定`True`で、`validate_llm_provider_guards`によりすべての`runtime_profile`（`local-dev`/`evaluation`/`enterprise-production`）で無効化できないよう強制されている（無効化しようとすると`ValueError`）ため、これは常時有効な本番コードパスである。
- 利用者または開発への影響:
  1. **メモリの無制限増加**: 現在のDockerfileは`uvicorn`を`--workers`指定なし（単一プロセス）で起動しており、直ちに実害が出る構成ではないが、プロセスが長時間稼働するほど辞書サイズが増え続ける。
  2. **将来のマルチワーカー/マルチレプリカ化との非互換**: SaaS化（マルチテナント）の方向性を考えると、複数workerやレプリカで運用する可能性がある。その場合、`query`/`bundle`が一方のプロセス、`apply`が別のプロセスに届くと、正当なリクエスト列でも`409 missing_event`相当の誤検知拒否が起こる。プロセス再起動時も同様に追跡状態が失われる。
  - なお、追跡キーに`tenant_id`（サーバー側で解決された値、リクエストペイロードからの直接指定ではない）が含まれるため、tenant間のデータ越境は確認されなかった。
- 判断が必要な理由: この追跡state自体（4つの監査イベントが揃うまでapplyを許可しない）は意図した機能であり、単純に辞書を消すことは機能を壊す。正しい修正には、TTL/eviction方針の追加、または共有ストア（Redis/DB）への移行、あるいは単一プロセスデプロイを明示的な制約として文書化するという設計判断が必要。

## 対応方針

- 実施すること: 次のいずれかをMaintainerが決定する。(a) TTL/evictionポリシーを追加してプロセス内メモリのまま運用を続ける、(b) 追跡stateを共有ストア（Redis/DB）へ移行しマルチワーカー対応する、(c) 単一プロセスデプロイを明示的な制約として文書化し、現状を許容する。
- 実施しないこと: 辞書のクリア方法や蓄積ロジックの変更。監査完全性チェックという機能自体を壊すリスクがあるため、設計判断を経ずに変更しない。

## 受入条件

- [ ] 上記(a)〜(c)のいずれかの方針が決定される。
- [ ] 決定した方針に応じた実装またはデプロイ制約の文書化が行われる。

## 検証計画

- 実行する確認: 対応後、`python3 -m pytest tests/test_docs_audit_integration.py`（backend）。
- 期待結果: 既存のCE4監査完全性チェックの挙動を壊さないことを確認する。

## 補足

- 発見経緯: 第13ラウンドの棚卸し（Pydantic mutable default/共有state観点）で発見。同じ観点で確認したモジュールレベルのmutable Pydantic/dataclassデフォルト・関数のmutableデフォルト引数・`global`文・`app.state`書き込みはすべてクリーン（既存の`AuditDispatcher._queue`は境界付き`deque(maxlen=...)`であり本件とは異なる）。
