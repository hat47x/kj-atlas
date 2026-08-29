# Issue Draft: PROV-ERROR-01 LLMプロバイダ構造化エラーの忠実な伝播

- Type: Bug fix / Feature request
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Claude Code
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/src/**/*.test.ts`
- Related Backlog: `PROV-ERROR-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D2）
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PROV-ERROR-01
- RequirementStatement: バックエンドの `ProviderError.to_contract()`（`code`: `provider_unavailable`|`provider_timeout`|`provider_validation`、`ProviderDisabledError.disabled_reason`）を HTTP エラーレスポンスの構造化フィールドとしてフロントエンドまで欠落なく伝播し、`App.tsx` の正規表現による文字列一致判定を廃止して `code` を直接参照する形へ置き換える。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`provider=local` かつ接続先が停止している / 操作=AI提案を実行 / 期待結果=ユーザーには「AI機能に接続できません」という**未翻訳の生例外文を含まない**ローカライズ済みメッセージが表示され、`provider=none`（意図的無効）のメッセージとは異なる文言になる / 除外=リトライの自動化、エラーからの自動フォールバック挙動の変更（`02_Architecture/llm_escalation_policy.html` の既定を変えない）。
- SecurityGateImpact: N/A（`trace_id`・生例外文はエンドユーザー画面へ出さず開発者ログのみに残す方針を維持）

## 1) 課題 / Problem statement

- バックエンド（`03_Implement/backend/src/kj_atlas_api/llm/provider.py:81-135`）は `provider_unavailable`/`provider_timeout`/`provider_validation`/`disabled_reason` という構造化エラー種別を用意しているが、フロントエンドの `ApiError`（`03_Implement/frontend/src/api/client.ts:17-42`）は `status: number` と平文 `message: string` のみを保持し、構造化フィールドを受け取れない。
- `App.tsx:2510` は受け取った平文メッセージに対し正規表現 `/AI is disabled|provider.*disabled/i` で一致判定しており、`provider=local` が設定済みで単に接続先が落ちている場合（実際の例外文は `"local request failed: Connection refused"` 等）はこの正規表現に一致せず、**未翻訳の英語例外文がそのまま** `suggestionError`/`statusMessage` としてユーザーに表示される。

## 2) 背景 / Context

- ルート実装が現在 `HTTPException(detail=str(exc))` のように平文へ潰しているか、`to_contract()` の dict をそのまま返しているかは実装調査で確定させる（T1）。いずれにせよフロントの `ApiError`/`parseErrorMessage` が `code` を読み取れる形になっていないため、経路のどこかで確実に失われている。

## 3) 判断基準による優先度評価

- 価値: 「意図的無効」と「設定ミス/障害」の区別はユーザー体験の基本的な誠実さ（ADR-0001 の透明性原則）。
- 安全: 生例外文・`trace_id` はエンドユーザー画面に出さず、開発者コンソール/ログにのみ残す（情報漏えい面でも改善）。
- 規模拡大: 運用形態が増えるほど「なぜAIが動かないか」の問い合わせが増える。構造化エラーはサポート負荷を下げる。
- 後方互換: `detail` フィールドは文字列のまま維持し、`code`/`disabledReason` をトップレベルに追加する形で後方互換を保つ。

## 3.2 非目標 / Non-goals

- リトライ戦略・エスカレーション既定の変更（`02_Architecture/llm_escalation_policy.html` は不変）。provider のランタイム切替（PROV-VIS-01 の非目標と同じ）。

## 4) 提案する解決策 / Proposed solution

- バックエンド `/ai/*` ルートで `ProviderError` を捕捉した際、`HTTPException(status_code=..., detail={"message": str(exc), "code": exc.to_contract()["code"], "disabledReason": exc.to_contract().get("disabled_reason")})` の形で構造化 detail を返す。
- フロントエンド `ApiError` に `code?: string` `disabledReason?: string` を追加。`parseErrorMessage` 相当を拡張し、`body.detail` がオブジェクトの場合はそこから `message`/`code`/`disabledReason` を取り出す（文字列 `detail` の場合は従来どおり message のみ）。
- `App.tsx` の判定を `error instanceof ApiError && error.code === "provider_unavailable" ...` 等へ置き換え、正規表現を削除。
- `code` 別の i18n メッセージを用意（`provider_disabled`＝既存文言を維持、`provider_unavailable`/`provider_timeout`＝新規の運用者連絡を促す文言、`provider_validation`＝新規）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: `provider=local` かつ接続断のとき、未翻訳の生例外文がユーザー向け表示に含まれない（`resolveAiProviderErrorMessage` が `code` 別の i18n メッセージへ差し替える。生メッセージは `error.message` に残るが呼び出し元4箇所すべてで表示に使われなくなった）。
- [x] AC-2: `provider=none`（`disabledReason` あり）と `provider=local` 接続断（`disabledReason` なし・`code=provider_unavailable`）で異なる分類・メッセージになることを `client.test.ts`/`ai_provider_error.test.ts` で固定。
- [x] AC-3: `code`/`disabledReason` が `ApiError` から読み取れることを unit で固定（`client.test.ts` 新規3件）。
- [x] AC-4: 既存の `provider=none` 表示（`side_panel.critique.provider_disabled`）は判定条件を正規表現→`classifyAiProviderError(error) === "disabled"` へ置き換えたのみで表示自体は非回帰。
- [x] AC-5: `trace_id`・生例外文はユーザー向け4箇所（layout提案・島サマリ・ナラティブ整合性チェック・ナラティブ生成）いずれも `resolveAiProviderErrorMessage` 経由の定型文へ差し替え済み。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 バックエンドルートの現状確認（detail が文字列か dict か）＋構造化 detail への変更。
- [x] T2 `ApiError` 拡張＋`parseErrorMessage` 拡張。
- [x] T3 `App.tsx` の判定置き換え（正規表現削除）。
- [x] T4 i18n（code別メッセージ）追加。
- [x] T5 integration/unit テスト一式。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/backend && ruff check src tests && pytest`
- `cd 03_Implement/frontend && npm run typecheck && npm test`

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（エラー時のみ表示変化） / 保留操作の距離=不変 / 取り消し導線=N/A（エラー表示は状態表示であり操作ではない）

## Traceability

- Related: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D2）
- Related: `01_Plans/issues/done/issue-PROV-VIS-01-llm-provider-visibility-badge.md`
- Derived-from: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`

## 完了記録 2026-07-06（Claude Code）

- **バックエンドは無変更**: 調査の結果、`03_Implement/backend/src/kj_atlas_api/routes/ai.py:_raise_llm_http_error` は既に `HTTPException(detail=exc.to_contract())` で構造化 dict を返していた（ADR-0050 起票時点の想定より健全）。欠落は**フロントエンドのみ**で発生していた。
- `src/api/client.ts`: `ApiError` に `code?`/`disabledReason?` を追加。`parseErrorMessage`（`detail` が文字列の場合しか読めず dict は握りつぶして `response.statusText` にフォールバックしていた）を `parseErrorDetail` に置き換え、`detail` がオブジェクトの場合は `code`/`disabled_reason`/`message` を取り出す。10箇所の呼び出し元をすべて更新。
- `src/domain/ai_provider_error.ts`（新規）: `classifyAiProviderError(error)` — `disabledReason` の有無と `code` から `disabled|timeout|validation|unavailable|unknown` を判定。正規表現を一切使わない。
- `src/App.tsx`: `resolveAiProviderErrorMessage` ヘルパーを追加し、レイアウト提案・島サマリ提案・ナラティブ整合性チェック・ナラティブ生成の**4箇所すべて**で生 `error.message` の直接表示をやめ、`code` 別の i18n メッセージへ統一。`provider=none` 判定も正規表現 `/AI is disabled|provider.*disabled/i` から `classifyAiProviderError(error) === "disabled"` へ置き換え。
- i18n: `ai.provider_error.{disabled,timeout,validation,unavailable}` を ja/en に追加。既存の `side_panel.critique.provider_disabled` は文言・表示条件（トリガー元のみ変更）ともに非回帰。
- 検証: typecheck 0 / vitest **881 passed**（180 files。新規 `ai_provider_error.test.ts` 7件・`client.test.ts` 構造化エラー伝播3件を含む）。
