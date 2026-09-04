# Issue: DX-FRONTEND-MERGE-METHOD-DRIFT-01 stale merge後のfrontend typecheckを正本へ戻す

> mergeMethod導入後の正本契約は変えず、後続のstale branch再マージで生じた二重挿入とfixture未同期だけを修復する。

- Type: Bug / DX / Contract Integrity
- Status: Done
- Source Issue: `AI-MERGE-METHOD-TRACE-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/domain/stream_b_contract_handoff.ts`, `03_Implement/frontend/src/domain/stream_b_contract_handoff.test.ts`, `03_Implement/frontend/src/domain/stream_b_mock_validation.test.ts`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.test.ts`, `03_Implement/frontend/src/import/agent_response_import.ts`, `03_Implement/frontend/src/ui/MergeSuggestionsPanel.test.ts`
- Related ADR/Spec: `AI-MERGE-METHOD-TRACE-01`, PR #2869, merge commit `c70a0433de213980b842c4286e4305c5c3574953`
- Expected verification level: `integration`

## 課題

PR #2869で `mergeMethod` のproposal→decision追跡契約は実装・typecheck済みだったが、その後に旧作業branchをmainへ再マージした履歴があり、現mainでは同じ変更の一部が二重に挿入されている。

確認できた例:

- `stream_b_contract_handoff.ts` の `MergeMethod` import、input field、検査条件が二重化している。
- `agent_response_import.ts` のimportと `content` 解析blockが二重化している。
- `App.tsx` とStream B test fixtureで `mergeMethod` propertyが二重化している。
- 一方で旧test fixtureには、新規入力で必須となった `mergeMethod` が反映されていない箇所が残る。

その結果、`tsc --noEmit` が重複identifier/propertyと必須field欠落で失敗する。これはmergeMethodの意味契約自体の不足ではなく、正本統合時の状態ドリフトである。

## 対応方針

- `mergeMethod` の二値語彙・必須/後方互換契約は変更しない。
- 二重に挿入された同一import・field・条件・解析blockだけを1件へ戻す。
- 新規decision/suggestion入力として扱うtest fixtureには `mergeMethod` を明示する。
- 旧保存済みdecisionを読む後方互換testでは、欠落値を推測補完しない既存契約を維持する。
- unrelatedなfrontend refactorや型重複一般問題へ範囲を広げない。

## 受入条件

- [x] `npm run typecheck` がcurrent main相当のtreeで成功する。
- [x] mergeMethod関連の対象unit testが成功する。
- [x] mergeMethodの語彙・fail-closed・旧decision後方互換契約を変更しない。
- [x] planning tests / active memo validator / docs-check / triageが成功する。
- [x] 一時検証workflow/scriptを最終差分へ残さない。
- [x] 内容確定後、意味を変えず自然な日本語として全文を読み直す。


## 検証結果

current main `528d05956dd96fc9880cd800dce3c714acef9909` から切ったbranchで、正本契約を変えずに状態ドリフトを修復した。

- `npm run typecheck`: success
- mergeMethod / Stream B / external-agent / decision / UIの対象Vitest: 59件成功
- planning unit tests: 130件成功、1件skip
- Active issue memo validator: success
- docs-check: success
- triage: `errors: []`
- `git -c core.whitespace=cr-at-eol diff --check`: success
- 実装差分は対象frontend 7ファイルだけ、追加15行・削除14行相当の局所差分として検証した

## 原因整理

PR #2869で `mergeMethod` のproposal→decision追跡契約はtypecheckを含めて検証済みだった。その後、旧作業branch由来の変更がmainへ再マージされ、同じimport・field・property・parser blockが一部経路へ二重に入った。一方、別系統の古いfixtureは新規入力で必須となった `mergeMethod` やpartial時の明示 `selectedCardIds` を持たないまま残った。

このため、同じ正本内に「新契約の二重挿入」と「旧fixtureの未同期」が同時に存在し、TypeScript型検査とStream B回帰が破綻していた。

## 完了境界

- `mergeMethod` の二値語彙とremote/commonのfail-closed契約は変更していない。
- 旧保存済みdecisionで `mergeMethod` 欠落を許容し、推測補完しない後方互換境界も変更していない。
- partialの明示選択契約は緩めず、Stream B handoff側が `selectedCardIds` を運べるように同期した。
- unrelatedなfrontend refactor、依存パッケージ更新、npm audit警告の解消は本Issueへ含めていない。
