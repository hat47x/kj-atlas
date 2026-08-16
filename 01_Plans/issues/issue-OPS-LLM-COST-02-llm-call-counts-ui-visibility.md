# Issue: OPS-LLM-COST-02 LLM呼び出し量のUI可視化（provider-status の callCounts を画面表示）

- Type: Feature request / Operations (OPS-LLM-COST-01 の後続)
- Status: Done
- Source Issue: ドッグフーディング iteration 113（scenario 49 実装時の観察）。`GET /ai/provider-status` を業務フローE2Eとして固定する過程で、**backend は LLM呼び出し回数（callCounts）を返すのに frontend は providerKind しか表示・保持していない**ことを確認。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/ViewControlsPanel.tsx`, `03_Implement/frontend/src/i18n/locales/{en,ja}.json`, `03_Implement/frontend/e2e/ai_provider_status.spec.ts`
- Related ADR/Spec: `01_Plans/issues/issue-OPS-LLM-COST-01-cost-control-contract-unimplemented.md`（段階2: callCounts を「運用者が参照できる」形で公開）, `02_Architecture/llm_provider_spec.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `e2e`

## 課題

`GET /ai/provider-status` は `ProviderStatusResponse` として `providerKind` と **`callCounts`**（OPS-LLM-COST-01 段階2・プロバイダ種別ごとの LLM 呼び出し回数＋total）を返す。しかし frontend の `getProviderStatus()` は **`providerKind` のみを返し、`callCounts` を破棄**している:

```ts
// client.ts（現状）
export async function getProviderStatus(): Promise<ProviderKind> {
  ...
  const body = (await response.json()) as { providerKind: ProviderKind };
  return body.providerKind; // callCounts が落ちる
}
```

UI（ViewControlsPanel）は provider 種別バッジのみ表示し、**LLM呼び出し量・外部モデル（large-scale）の呼び出しボリュームを運用者が画面で確認できない**。cost 監視の指標が backend で計算されるだけで、運用面で参照できない状態。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | AI運用担当は「外部モデル呼び出し量」を**運用画面で監視**したい（コスト・課金の可視化）。provider 種別バッジだけでは料金リスクを追えない | 表示は**read-only**（ADR-0050 D1・切替スイッチなし）のまま。呼び出し回数は**指標表示**であって操作対象にしない |
| **データ設計** | backend の `callCounts`（`{providerKind: n, total: n}`）をそのまま UI に渡す。`total` と種別別の両方を表示 | 空 dict の場合は表示を省略（LLM未呼び出し）。`providerKind=none` では counts は空 |
| **機能設計** | `getProviderStatus()` を `{providerKind, callCounts}` を返す形へ変更し、App が保持 → ViewControlsPanel が表示。i18n キー追加。E2E で表示を固定 | 戻り値の型変更は `App.tsx` の1呼び出し箇所と E2E モックの応答にのみ影響（client.test.ts はルート情報のみ・非後退） |

## 要件

- `getProviderStatus()` は `{providerKind, callCounts}` を返す（`callCounts` は `Record<string, number>`・無ければ `{}`）。
- App は `providerKind` に加えて `llmCallCounts` を保持し、ViewControlsPanel へ渡す。
- ViewControlsPanel の AI プロバイダ節に**LLM呼び出し回数**（total と種別別）を read-only 表示する。
- `providerKind=none` / counts 空 のときは counts 表示を出さない（既存の none 表示と干渉しない）。
- E2E で provider=local のとき `callCounts` が画面表示されることを固定。

## 受入条件

- [x] `getProviderStatus()` が `callCounts` を含むスナップショットを返す。→ `ProviderStatusSnapshot` 型を追加し `{providerKind, callCounts: callCounts ?? {}}` を返す。
- [x] ViewControlsPanel が LLM呼び出し回数を表示する。→ `llmCallCounts` プロップを追加し、AI プロバイダ節に「LLM calls: N (local: n, ...)」を表示。i18n キー `view_controls.ai_provider.call_counts` を en/ja に追加。
- [x] counts 空 / provider=none では counts 表示が出ない（非後退）。→ 表示は `Object.keys(callCounts).length > 0` のときのみ。
- [x] E2E で表示を固定。→ `ai_provider_status.spec.ts` のモック応答に `callCounts` を追加し、表示アサーションを追加。

## 検証計画

- `cd 03_Implement/frontend && npx vitest run`（client / ViewControlsPanel 回帰）
- `npx playwright test e2e/ai_provider_status.spec.ts`
- backend 側は非変更（`provider-status` は既存のまま）

## 補足

- 本issueは **backend は一切変更しない**。`provider-status` の応答は scenario 49 で既に凍結済み（273/273）。
- 表示は read-only の指標であり、計数リセット等の操作は含めない（`reset_llm_call_counts` は ops/tests 専用）。
