# Issue: OPS-LLM-COST-03 AI利用量表示が生成後も起動時の値を示す

- Type: Bug / Operations / UX
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（2026-08-16のDeepSeek実ブラウザモンキーテストで発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `OPS-LLM-COST-03`
- Related ADR/Spec: `02_Architecture/llm_provider_spec.md`, `01_Plans/adr/ADR-0050-llm-provider-and-user-freedom-boundary.md`
- Expected verification level: `e2e`

## 課題

View panelのprovider call countとtoken usageはアプリ起動時に一度だけ取得されていた。起動後にAI生成が成功しても、利用者がView panelを開いた時点では古い0件表示のままで、再読込するまで実利用量を確認できなかった。

## 対応方針

- View panelを開くたび、read-onlyの`GET /ai/provider-status`を再取得する。
- 取得失敗時は操作を遮断せず、直前の表示値を保持する。
- provider切替UI、利用上限、自動停止は追加しない。

三要素牽制: 業務上は運用者が確認操作をした時点の利用量を把握できる必要がある。データ上は秘密情報を含まない既存集計だけを再取得する。機能上は表示パネルopenをrefresh契機とし、生成・採否・文書状態は変更しない。既存read-only契約内の修正でありADR追加は不要。

## 受入条件

- [x] 起動後にAI生成し、View panelを開くと最新call countが表示される。
- [x] provider-reported input/output token usageが同時に更新される。
- [x] refresh失敗がView panelや編集操作を遮断しない。
- [x] providerのruntime切替UIを追加しない。

## 対応結果（2026-08-16）

- View panel open時にprovider statusを再取得し、kind、call count、token usageを同時更新するよう修正した。
- refresh失敗時はlast-known snapshotを保持する。
- 実DeepSeek生成後のWindows Edgeで、`deepseek: 1`とtoken usageが再読込なしで表示されることを確認した。

## 検証計画

- View panelの静的契約testとtypecheckを実行する。
- 実DeepSeekタイトル提案後にView panelを開き、call count/token usage更新をWindows Edgeで確認する。
