# Issue Draft: PROV-CONTRACT-01 llm_provider_spec.md §4 の実装整合修正

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `02_Architecture/llm_provider_spec.md`
- Related Backlog: `PROV-CONTRACT-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D3）, `02_Architecture/llm_input_ir_spec.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: PROV-CONTRACT-01
- RequirementStatement: `llm_provider_spec.md` §4 が「正規形に固定」と記載する `LLMRequest`/`LLMResponse` を、実装（`provider.py` の `LLMRequest{task,prompt,temperature,max_tokens}` → `LLMResponse{raw_text,metadata}`）と一致する「現在実装済みの最小契約」として記述し直し、`inputs`/`output_schema`/`usage`/構造化`output`は Phase-2（未配線）として明示的に分離する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`llm_provider_spec.md` を読む実装者 / 操作=§4 を参照して LocalProvider/LargeScaleProvider の実装差分を確認 / 期待結果=文書の記載どおりに実装されていることが確認でき、未配線の項目は「Phase-2」と明記されているため実装漏れと誤認しない / 除外=IR配線の実装そのもの（本Issueはドキュメント修正のみ）。
- SecurityGateImpact: N/A

## 1) 課題 / Problem statement

- `llm_provider_spec.md` §4.1/4.2 は `LLMRequest`（`inputs`・`output_schema`・`options.timeout_ms`/`seed`・`context.trace_id`/`safe_mode`）と `LLMResponse`（`usage`・構造化`output`・`provider_meta`）を凍結済みの正規形として記載するが、`03_Implement/backend/src/kj_atlas_api/llm/provider.py:16-27` の実装は `LLMRequest{task, prompt, temperature, max_tokens}` → `LLMResponse{raw_text, metadata}` という大幅に単純化された形のみである。
- 「正本」を名乗る凍結文書が実装済みでない内容を確定事項のように記載しているため、実装者・監査者が実態を誤認するリスクがある。

## 2) 背景 / Context

- ADR-0050 D3 で是正方針を確定済み。本Issueはその実施（ドキュメントのみ・コード変更なし）。

## 3) 判断基準による優先度評価

- 価値: 「正本」文書の信頼性はプロジェクト全体のガバナンスの基盤。乖離放置は他の判断（IR配線の要否判断等）を誤らせる。
- 安全: N/A（ドキュメントのみ）。
- 規模拡大: N/A。
- 後方互換: 実装への影響なし。

## 3.2 非目標 / Non-goals

- `inputs`/`output_schema`/`usage`/構造化`output` の実装（将来の別Issue・別ADR判断）。

## 4) 提案する解決策 / Proposed solution

- §4.1 を「現在実装済みの最小契約（`provider.py` 準拠）」と明記し、フィールドを `task`/`prompt`/`temperature`/`max_tokens` のみに修正。
- §4.2 を `raw_text`/`metadata`（`provider_kind`/`provider_name`/`model_id`/`transport`/`requested_at`/`trace_id`/`fallback_to_none`）に修正。
- `inputs`/`output_schema`/`usage`/構造化`output`/`context.safe_mode` は「Phase-2（未配線・Pending）」という節を新設して移動し、`02_Architecture/llm_input_ir_spec.md` との関係（IR仕様は存在するが `LLMRequest.inputs` への実配線はまだ無い）を明記する。
- 既存の CE1 Contract Handoff Boundary・監査データ契約（§5）等、実装済みで正確な記載はそのまま維持する。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: §4.1/4.2 の記載が `provider.py` の実装（`LLMRequest{task,prompt,temperature,max_tokens}`／`LLMResponse{raw_text,metadata}`）と一致する。
- [x] AC-2: 未配線項目（`inputs`/`output_schema`/`options.timeout_ms`/`seed`/`context.trace_id`/`safe_mode`/`usage`/構造化`output`）を新設 §4.4「Phase-2（未配線・Pending）」へ分離し、「正規形に固定」という表現を除去。
- [x] AC-3: `llm_input_ir_spec.md` との関係（IR仕様は存在するが `LLMRequest.inputs` への実配線はまだ無い）を §4.4 に明記。
- [x] AC-4: 他章との矛盾を解消（§1系の `provider_meta.trace_id`×3箇所を `LLMResponse.metadata.trace_id` へ統一、§2 の `fixture` が実行時受理値でないことを注記、§6 の `LLMRequest.inputs` 参照を実装済みフィールドへ修正）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 §4.1/4.2 の書き換え。
- [x] T2 Phase-2 節の新設。
- [x] T3 全体の整合レビュー（他章との矛盾チェック）。

## 7) 検証計画 / Validation plan

- `grep -n "LLMRequest\|LLMResponse" 02_Architecture/llm_provider_spec.md 03_Implement/backend/src/kj_atlas_api/llm/provider.py` で記載とコードの用語一致を目視確認。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 該当なし（ドキュメントのみ）

## Traceability

- Related: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`（D3）
- Related: `02_Architecture/llm_input_ir_spec.md`
- Related: `01_Plans/issues/done/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane B: LLMProvider経路）, `02_Architecture/value_traceability.md` §2.9
- Derived-from: `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`

## 完了記録 2026-07-06（Claude Code）

- §4 を「実装済み最小契約」（`task`/`prompt`/`temperature`/`max_tokens` → `raw_text`/`metadata`）として書き直し、新設 §4.4「Phase-2（未配線・Pending）」に `inputs`/`output_schema`/`options.timeout_ms`・`seed`/`context.trace_id`・`safe_mode`/`usage`/構造化`output` を分離。
- 修正過程で副次的に発見した2件の軽微な乖離も同ドキュメント内で解消（スコープ外への拡大は避け、同一ファイル内の直接関連箇所のみ）: (1) §2 Provider enum の `fixture` が `KJ_ATLAS_LLM_PROVIDER` の実行時受理値でない（テスト専用）ことを注記、(2) §6 Attachments 制約の `LLMRequest.inputs` 参照を実装済みの `LLMRequest.prompt` へ修正。
- 検証: `grep` によるドキュメント内表記統一確認のみ（コード変更なし・typecheck/vitest対象外）。
