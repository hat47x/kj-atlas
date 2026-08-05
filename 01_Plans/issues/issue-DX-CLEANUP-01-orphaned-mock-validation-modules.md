# Issue: DX-CLEANUP-01 P2A/P2B系mock-validationモジュールが未参照

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/domain/merge/p2b_decision_log_mock.ts`, `03_Implement/frontend/src/domain/p2a_stream_d/mock_validation_stream_d.ts`
- Related ADR/Spec: `01_Plans/issues/issue-FB-P2A-02-a2-mock-validation.md`, `01_Plans/issues/issue-FB-P2B-02-a2-mock-validation.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: 次の2モジュールが、自身の定義fileと自身のtestファイル以外のどこからも参照されていないことを`git grep`で確認した。
  - `03_Implement/frontend/src/domain/merge/p2b_decision_log_mock.ts`（export: `P2BDecisionLogMockStore`）— 参照元は`p2b_decision_log_mock.test.ts`のみ。
  - `03_Implement/frontend/src/domain/p2a_stream_d/mock_validation_stream_d.ts`（export: `runMockValidationStreamD`, `HIERARCHY_FIXTURES_STREAM_D`, `VISIBILITY_FIXTURES_STREAM_D`, `projectContractStubStreamD`, `evaluateInvariantStubStreamD`）— 参照元は自身のtestファイルと、実装ログ`03_Implement/frontend/tests/stream_b_a2_a3_validation_log_2026-05-08.md`のみ。
  - 関連する`issue-FB-P2A-02-a2-mock-validation.md`/`issue-FB-P2B-02-a2-mock-validation.md`はいずれも`Status: Done`だが、`Scope: 01_Plans/issues/ only`（計画文書のみが対象）と記載されており、これらのソースファイル自体を追跡対象にしていない。
- 利用者または開発への影響: 実害はない（未使用コードが残っているだけ）。ただし、これがA3（実実装）フェーズ移行前の一時的なmock検証スキャフォールディングとして意図的に残されているのか、それとも本当に不要になった残骸なのかが、この棚卸しだけでは判断できない。
- 判断結果: 両モジュールはA2のmock-first handoff成果であり、現在はP2Bの実監査モジュール群とP2A Stream Dの実階層・可視性検証および近接テストが存在する。現行`api.md`も旧mock validation planを形成履歴へ分離しており、実装から自己テスト以外の参照がないため、A3移行後の残骸と判断した。

## 対応方針

- 実施したこと: 2つのmockモジュールと、それらだけを検証していた2つのtestファイルを削除した。
- 実施しないこと: 現行P2A/P2B実装、実契約テスト、形成履歴に記録された過去の検証コマンドの改変。

## 受入条件

- [x] 両モジュールをA3移行後のmock残骸として削除する方針を確定する。
- [x] 対応するtestファイルも削除し、frontend testと型検査がgreenであることを確認する。

## 検証計画

- 実行する確認: 方針決定後、`git grep -l "P2BDecisionLogMockStore\|mock_validation_stream_d"`で参照先が意図通りになっていることを確認する。
- 期待結果: 削除する場合は参照が完全に消え、`npx vitest run`・`npx tsc --noEmit`がgreenのまま。

## Validation

- `node node_modules/vitest/vitest.mjs run src/domain/merge src/domain/p2a_stream_d`
- `node node_modules/typescript/bin/tsc --noEmit`
- `python 01_Plans/docs_check.py --root .`

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸しで発見。
