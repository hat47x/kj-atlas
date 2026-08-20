# Issue: PRODUCT-VALUE-01 初回価値実感と最初の意味ある配置

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Product Value contributor
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `04_Documentation/installation.md`, `04_Documentation/operations.md`
- Related Backlog: `PRODUCT-VALUE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`, `02_Architecture/value_traceability.md`
- Expected verification level: `e2e`

## 目的

初回利用者が、説明を読み込まなくても短い入力からカードを作り、最初のまとまりまたは保留点へ到達できるようにする。完成度を要求するのではなく、「考え始められた」と分かる最小成功を支援する。

## 実装した範囲

- StartPanelで製品価値と開始方法を日本語・英語で案内する。
- 文書全体のカード状態と最初の意味ある配置への進捗を表示する。
- カードにclaim type、critique、review stateを表示する。
- SidePanelで批評、根拠、矛盾、レビュー状態を確認できる。
- マウス、キーボード、初回起動、共有前確認の代表経路をPlaywrightで検証する。
- installation、operations、public index、acceptance checkを初回経路と同期する。

## 受入条件

- [x] サンプルまたは短いメモ入力からカードを作れる。
- [x] 少なくとも1つのまとまり、関係、または保留点を作る操作が分かる。
- [x] まだ決めていないことを、失敗ではなく作業状態として確認できる。
- [x] SafeModeと取り込み検証状態を初回経路で確認できる。
- [x] `Tab`、`Enter`、`Space`で主要操作へ到達できる。
- [x] 公開文書の導入手順が初回成功経路と一致する。
- [x] H-PV1代理受入で、fixture、代表操作、証跡packetの妥当性を確認した。

## 証跡

- Fixture: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` の `buildFirstMeaningfulMapDocument()`。
- Mouse: `03_Implement/frontend/e2e/first_meaningful_map_mouse_flow.spec.ts`。
- Keyboard: `03_Implement/frontend/e2e/keyboard_release_candidate_flow.spec.ts`。
- First run: `03_Implement/frontend/e2e/first_run_document_entry.spec.ts`。
- Share preflight: `03_Implement/frontend/e2e/first_value_share_preflight.spec.ts`。
- 受入確認: `04_Documentation/acceptance_check.md`。

## 境界

- 自動的に「良い配置」を採点しない。
- AI提案を自動適用せず、`human_reviewed`をAIが設定しない。
- 物理キーボード、スクリーンリーダー、公開画像、最終出荷の確認は `MVP-EXIT-01` で扱う。

## 検証

- `cd 03_Implement/frontend && npm run typecheck`
- `cd 03_Implement/frontend && npm run test`
- `cd 03_Implement/frontend && npx playwright test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/keyboard_release_candidate_flow.spec.ts e2e/first_value_share_preflight.spec.ts`

## 完了判断

最小成功のUI、マウス・キーボード経路、SafeMode確認、公開文書、再利用可能fixture、H-PV1受入が揃ったためDoneとする。詳細な反復実行ログと旧current-open summaryはGit履歴で参照する。

新ADRは不要である。本IssueはAccepted済みの `ADR-0032` を実装したもので、価値定義や安全境界を変更しない。
