# Issue: DX-CLEANUP-01 P2A/P2B系mock-validationモジュールが未参照

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
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

## 対応方針

- 実施すること: これらのモジュールが今後のA3実装フェーズで使われる予定のスキャフォールディングか、削除してよい残骸かをMaintainerが判断する。
- 実施しないこと: 本issueでは削除を実行しない。P2A/P2B系の実装計画の全体像を把握していないコーディングエージェントが独断で削除すると、意図した将来利用を破壊するリスクがある。

## 受入条件

- [ ] 両モジュールについて「維持する（将来利用予定）」または「削除する」の方針が決定される。
- [ ] 削除する場合、対応するtestファイルも合わせて削除し、`npx vitest run`がgreenであることを確認する。

## 検証計画

- 実行する確認: 方針決定後、`git grep -l "P2BDecisionLogMockStore\|mock_validation_stream_d"`で参照先が意図通りになっていることを確認する。
- 期待結果: 削除する場合は参照が完全に消え、`npx vitest run`・`npx tsc --noEmit`がgreenのまま。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸しで発見。
