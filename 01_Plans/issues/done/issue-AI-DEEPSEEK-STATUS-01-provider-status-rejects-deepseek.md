# Issue: AI-DEEPSEEK-STATUS-01 DeepSeek有効時にprovider statusが500になる

- Type: Bug / Contract / Documentation
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16の管理CLI・MCP・生成AI連動モンキーテストで発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/tests/test_ai_provider_status_route.py`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/export/diagnostics_bundle.ts`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/ai_provider_status.spec.ts`, `01_Plans/adr/ADR-0053-support-diagnostics-bundle-boundary.md`, `02_Architecture/llm_provider_spec.md`, `03_Implement/backend/README.md`
- Related Backlog: `AI-DEEPSEEK-STATUS-01`
- Related ADR/Spec: `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/llm_provider_spec.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `e2e`

## 課題

Settingsとprovider registryは`KJ_ATLAS_LLM_PROVIDER=deepseek`を正式に受理するが、`ProviderStatusResponse.providerKind`とfrontendの`ProviderKind`は`none/local/large-scale`だけを許可していた。そのためDeepSeek有効時の`GET /ai/provider-status`は応答検証で500となり、View panelの設定表示も取得不能になる。主要provider仕様とbackend READMEの受理値もDeepSeekを欠き、環境変数正本と矛盾していた。

## 対応方針

- backend/frontendのprovider kind契約へ`deepseek`を追加する。
- 日英UIへDeepSeek表示を追加し、call count/token usageを同じread-only面で表示する。
- DeepSeek設定時のAPI 200と実ブラウザ表示を固定回帰にする。
- provider仕様とbackend READMEを環境変数正本へ同期する。

三要素牽制: 業務上は運用者が外部AI利用状態と使用量を確認できる必要がある。データ上は既存のprovider kind文字列を正しく通すだけで、秘密値は応答しない。機能上はread-only表示契約の欠落を補い、provider切替やAI提案の自動適用は導入しない。安全不変条件は不変でADR不要。

## 受入条件

- [x] DeepSeek設定時に`GET /ai/provider-status`が200で`providerKind=deepseek`を返す。
- [x] View panelが日英でDeepSeekを表示できる。
- [x] DeepSeekのcall count/token usageを既存形式で表示できる。
- [x] `none/local/large-scale`の既存表示が回帰しない。
- [x] provider仕様・README・環境変数正本の受理値が一致する。

## 対応結果（2026-08-16）

- backend response、frontend type、日英表示、診断bundle許可リストを`deepseek`へ同期した。診断bundleはprovider種別だけを含み、API key・endpoint・modelを含めない。
- backend近接14件、frontend近接112件、provider status実Edge 3件、typecheck、docs-checkを通過した。
- Git管理外のlocal credentialを用いた隔離環境で実DeepSeek生成を実施し、カード改善・島要約・タイトル提案の200応答とprovider statusのcall count/token usage反映を確認した。資格情報の値は出力・記録・コミットしていない。

## 検証計画

- backend provider status近接テスト、frontend typecheck/i18n、Playwright `ai_provider_status.spec.ts`を実行する。
- docs-checkとactive issue validatorを実行する。


## 配置の整理（2026-09-05）

- 本Issueは受入条件を満たし、実装・回帰確認・実API確認まで完了して `Done` となっていた一方、R18以前からの経緯により、完了済みのまま作業中Issueと同じルートへ残るlegacy集合に含まれていた。
- 既存のライフサイクル契約は、このlegacy集合を恒久的に残すための例外ではない。完了済みIssueを `01_Plans/issues/done/` へ移すたびに `LEGACY_DONE_AT_ROOT_BASELINE` も同じ変更で下げる、単調減少のラチェットである。
- 本変更ではDeepSeek対応の完了済みIssue 2件を正規配置へ移し、baselineを54から52へ縮小した。R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
