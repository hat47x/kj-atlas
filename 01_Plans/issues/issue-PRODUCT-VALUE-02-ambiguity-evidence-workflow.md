# Issue: PRODUCT-VALUE-02 保留・違和感・根拠不足を扱う作業フロー

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer / Product Value contributor
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `02_Architecture/value_traceability.md`
- Related Backlog: `PRODUCT-VALUE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `00_Prompt/domain.md`, `02_Architecture/llm_input_ir_spec.md`
- Expected verification level: `e2e`

## 目的

保留、違和感、根拠不足、反対意見を、削除すべき不完全さではなく思考を深める作業状態として残す。未確定情報を見つけ、共有前に確認し、AIへ渡す場合も制約として保持できるようにする。

## 実装した範囲

- CardViewとSidePanelでclaim type、critique、review state、根拠、矛盾を表示する。
- HoldとShelfを第一級の作業状態として付与・解除・復元できる。
- 批評の種別、メモ、再提案差分、根拠・矛盾リンクを扱える。
- 文書全体の未整理、未レビュー、根拠不足を集約表示する。
- SafeMode共有前確認で保留、批評、根拠、矛盾、未レビュー状態を示す。
- ContextBundleへ未確定状態と制約を保持する。
- 保存値を変えずに日本語・英語の利用者向けラベルを表示する。

## 受入条件

- [x] カード、島、関係に保留または違和感を付けられる。
- [x] 根拠不足と反対意見を確定情報と区別して表示できる。
- [x] 状態表示と絞り込みで未整理、未レビュー、根拠不足を見つけられる。
- [x] 共有前確認で保留点、未レビュー情報、根拠不足を確認できる。
- [x] ContextBundleで未確定状態を制約または除外理由として追跡できる。
- [x] `human_reviewed`は人間操作でのみ昇格し、AI、worker、APIが自動昇格しない。
- [x] H-PV2代理受入でfixture、見つけやすさ、SafeMode、AI権限境界を確認した。

## 証跡

- Fixture: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts` の `buildDomainExpressionDocument()`。
- Keyboard: `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`。
- Share preflight: `03_Implement/frontend/e2e/pre_share_summary_gate.spec.ts`。
- Accessibility: `03_Implement/frontend/e2e/a11y_selection_and_share_gate.spec.ts`。
- 所有issue: `DOMAIN-EXPR-01`〜`DOMAIN-EXPR-04`、`CE1`はいずれもDone。

## 境界

- 少数意見や矛盾を自動削除・自動解決しない。
- 批評や根拠の量を品質スコアとして人の評価に使わない。
- AIは提案を作成できるが、レビュー状態を確定しない。
- 将来、永続状態の意味、AI権限、共有既定を変える場合だけissue/ADRで再判断する。

## 検証

- `cd 03_Implement/frontend && npm run typecheck`
- `cd 03_Implement/frontend && npm run test`
- `cd 03_Implement/frontend && npx playwright test e2e/domain_expression_keyboard_access.spec.ts e2e/pre_share_summary_gate.spec.ts e2e/a11y_selection_and_share_gate.spec.ts`

## 完了判断

DOMAIN-EXPR-01〜04とCE1がDoneで、UI、共有前確認、ContextBundle、レビュー権限境界、H-PV2受入が揃ったためDoneとする。詳細な反復実行ログと旧current-open summaryはGit履歴で参照する。

新ADRは不要である。本Issueは `ADR-0040` と `ADR-0032` の実装完了を反映するもので、schemaや安全境界を変更しない。
