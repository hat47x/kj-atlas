# Issue: KJ-AB-CROSS-CHECK-01 ナラティブ検査が A/B 照合の方向と件数を落としている

- Type: Product Invariant / AI Integration
- Status: Done
- Source Issue: `01_Plans/direction-review-2026-08-13.md` 優先3-2
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `models_ai.py`, `routes/ai.py`, `03_Implement/frontend/src/domain/types.ts`, `validate.ts`, `inquiry_bundle_safe_mode.ts`, `App.tsx`, `api/client.ts`, `02_Architecture/schemas.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md`（§5 A/B照合・§6 失敗の徴候）, `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`
- Expected verification level: `integration`

## 課題

方法論の正本は A/B 照合を**双方向**で行い、結果を**件数で報告**することを要求している。

> `00_Prompt/kj_technique.md:180-186`
> 必ず双方向に照合する。
> - **B型にあってA型に無いもの** → 図に無いことを書いた。根拠がない。図に足すか、文から削る。
> - **A型にあってB型で落ちたもの** → 語れなかった束がある。なぜ語れないのかを問う。
> 照合の結果を件数で report する。ゼロ件なら照合していない疑いがある。

しかし `NarrativeCheckIssue`（`02_Architecture/schemas.md`・`03_Implement/frontend/src/domain/types.ts`）は `severity` / `message` / `references` のみで、**方向も件数も保持しない**。`_build_narrative_check_prompt`（`routes/ai.py:193`）も A/B 照合を要求せず、応答は LLM が自由に畳んでいた。検査結果が「ゼロ件なら照合していない疑いがある」を評価できない。

これは方向性レビューの**優先3「検査の実装（三要素で見て最大の不均衡）」**の一項目である。

## 対応方針

- 実施すること（D-a）:
  1. `NarrativeCheckIssue.direction?: "b_missing_in_a" | "a_missing_in_b"` を追加（各 issue の A/B 照合方向）。
  2. `NarrativeCheck.counts?: { bMissingInA: number; aMissingInB: number }` を追加（方向別件数。0 も有効な報告値 — `kj_technique.md:185` のゼロ=照合していない疑い）。
  3. `_build_narrative_check_prompt` に A/B 双方向照合の要求と direction/counts の schema を追加。
  4. frontend `types.ts` / `validate.ts` / `inquiry_bundle_safe_mode.ts` / `App.tsx` / `client.ts` を同期（optional で後方互換）。
  5. `schemas.md` と `test_ts_python_contract_drift.py` の TYPE_MAP を更新。
- 実施しないこと:
  1. 検査ロジック（severity/message/references）の削除 — 検査は方法論が要求している。方向・件数の付与のみ。
  2. A/B 照合を `generate_narrative` の警告へ統合する（本issueは check_narrative の出力契約のみを扱う）。

## 受入条件

- [x] AC-1: `NarrativeCheckIssue` が `direction` を、`NarrativeCheck` が `counts` を保持する（TS/Python/schemas 同期、drift test で固定）。
- [x] AC-2: プロンプトが A/B 双方向照合と direction/counts の報告を要求する（テストで固定）。
- [x] AC-3: SafeMode 投影が direction/counts（構造値）を保持する（本文 message は redact のまま）。
- [x] AC-4: frontend 検証が direction/counts を受け入れ、ラウンドトリップで保持する。

## 検証

- `python -m pytest tests/test_ai_prompt.py tests/test_ts_python_contract_drift.py -q`
- `cd 03_Implement/frontend && npm run test -- src/domain/validate.test.ts && npm run typecheck`
- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-14）

D-a を実装した。

- backend: `models.py`（`NarrativeCheckDirection` / `NarrativeCheckCounts` / `NarrativeCheckIssue.direction` / `NarrativeCheck.counts`）、`models_ai.py`（`NarrativeIssue.direction` / `CheckNarrativeResponse.counts`）、`routes/ai.py`（prompt に A/B 双方向照合＋direction/counts schema を追加）。
- frontend: `types.ts`・`validate.ts`（`parseNarrativeCheckDirection` / `parseNarrativeCheckCounts`）・`inquiry_bundle_safe_mode.ts`（direction/counts を preserve）・`client.ts`（`checkNarrative` 戻り値に counts）・`App.tsx`（`nextCheck` へ counts を反映）。
- `schemas.md` 更新、`test_ts_python_contract_drift.py` の TYPE_MAP に `NarrativeCheck` / `NarrativeCheckIssue` / `NarrativeCheckCounts` を追加。
- テスト: `test_ai_prompt.py`（prompt の双方向照合要求・parser の direction/counts 受理）、`validate.test.ts`（direction/counts のラウンドトリップ）。全 AC 完了。
