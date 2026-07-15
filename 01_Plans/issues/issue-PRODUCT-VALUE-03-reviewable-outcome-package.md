# Issue: PRODUCT-VALUE-03 レビュー可能な成果物パッケージ

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Product Value contributor
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/narratives.md`, `04_Documentation/data_handling.md`
- Related Backlog: `PRODUCT-VALUE-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `02_Architecture/review_attribution.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `e2e`

## 目的

整理結果を単なる見栄えのよい要約にせず、確定点、保留点、未レビュー情報、根拠、元データへの戻り方を読者が確認できる成果物として共有する。

## 実装した範囲

- NarrativeとReview Packにclaim type、review state、根拠、矛盾を含める。
- OverviewとDetailを選び、必要な粒度でtrace情報を確認できる。
- 共有前確認で未レビュー、保留、批評、根拠、矛盾の件数を表示する。
- SafeMode ONで未レビュー本文、機微情報、不要な主体情報を既定で抑制する。
- 読み取り専用の読者が元カード、島、関係、レビュー状態へ戻れる。
- 粒度選択をfieldset/legendで表し、キーボードと支援技術から理解できる。
- narrativesとdata handling文書を実装と同期する。

## 受入条件

- [x] 成果物に確定点、保留点、未レビュー情報、根拠への戻り方が含まれる。
- [x] 共有前確認で未レビュー情報と保留点の扱いを安全側に確認できる。
- [x] SafeMode ONで未レビュー本文や機微情報を既定抑制する。
- [x] 元カード、島、関係、レビュー状態へ戻る参照が残る。
- [x] narrativesとdata handlingが成果物の意味と確認観点を説明する。
- [x] E2Eで共有前確認から成果物生成、読み取り専用確認まで検証できる。
- [x] H-PV3代理受入でpackage、trace、SafeMode、read-only権限境界を確認した。

## 証跡

- Fixture: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` の `buildReviewPackTraceDocument()`。
- Export/trace: `03_Implement/frontend/e2e/review_pack_trace_export.spec.ts`。
- Narrative tests: `03_Implement/frontend/src/export/narrative_export.test.ts`。
- 公開説明: `04_Documentation/narratives.md`, `04_Documentation/data_handling.md`。

## 境界

- 成果物を正式承認、署名、組織決裁として表示しない。
- 自動公開しない。
- SafeModeと共有前確認を迂回しない。
- 正式なpackage public contractや署名機能を導入する場合は別issueで契約と権限を判断する。
- 物理キーボード、スクリーンリーダー、公開画像、最終出荷の確認は `MVP-EXIT-01` で扱う。

## 検証

- `cd 03_Implement/frontend && npm run typecheck`
- `cd 03_Implement/frontend && npm run test`
- `cd 03_Implement/frontend && npx playwright test e2e/review_pack_trace_export.spec.ts`

## 完了判断

成果物の最小構成、trace、SafeMode、共有前確認、read-only確認、文書、H-PV3受入が揃ったためDoneとする。詳細な反復実行ログと旧current-open summaryはGit履歴で参照する。

新ADRは不要である。本IssueはAccepted済みの `ADR-0032` を実装したもので、package契約や出荷権限を変更しない。
