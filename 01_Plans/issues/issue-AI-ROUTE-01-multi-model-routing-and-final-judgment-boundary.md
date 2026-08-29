# Issue Draft: AI-ROUTE-01 Multi-Model Routing（MMR-01〜06）の実装要件

- Type: Feature request / AI capability
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a, `03_Implement/backend/src/kj_atlas_api/`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a（MMR-01〜06）, `02_Architecture/value_traceability.md` §2.1（V3）, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`
- Expected verification level: `integration`

## 課題

`00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a は、モデル責務分担（intermediate 処理と final_judgement 判断）を固定する Multi-Model Routing 要件 MMR-01〜06 を定義している。しかしこれを実装する専用issueが存在しない。

- MMR-01: `intermediate` と `final_judgement` を論理的に分離する。
- MMR-02: `intermediate` は `classify/summarize/format_transform/branch_resolve` に限定する。
- MMR-03: `intermediate` は `accept/reject/merge/finalize/publish` を実行してはならない。
- MMR-04: `final_judgement` は high-reasoning tier へルーティングする。
- MMR-05: 監査ログに `routingStage` / `provider/model` / `sourceBundleHash` / `proposalId` を必須記録する。
- MMR-06: `final_judgement` 利用不能時は auto-publish へフォールバックせず `held` へ遷移する。

この能力は `value_traceability.md` V3（レビュー）の価値、「AI候補や要約を人間が採否判断できる」ことを、モデル責務の安全境界として支える。プロダクト価値実現の高価値要件であり、単独issueとして要件・契約・検証を固定する必要がある。

## 要件

- intermediate と final_judgement の責務を分離し、許可タスク・禁止タスクを契約で固定する。
- final_judgement のルーティング先（high-reasoning tier）を設定契約（ADR-0050）と整合させる。
- 監査ログに routingStage / provider/model / sourceBundleHash / proposalId を記録する。
- final_judgement 利用不能時は held へ遷移し、auto-publish へフォールバックしない。
- `provider=none` では中核操作が成立する（AIルーティング不要）。

## 受入条件

- [x] intermediate と final_judgement の責務分離が契約（api.md/schemas.md）で固定される。— `routing_stage_for_task()`（provider.py）で分類
- [x] intermediate の許可タスク・禁止タスクが強制される（MMR-02/03）。— 分類で構造的に強制（変換系タスクのallowlist）
- [x] final_judgement が high-reasoning tier へルーティングされる（MMR-04）。— `resolve_model_for_task()` + `KJ_ATLAS_LLM_HIGH_REASONING_MODEL`
- [x] 監査ログに MMR-05 の4項目が記録される。— `_audit_llm_trace` に `routingStage` 追加
- [ ] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。— 未実装（外部エージェント連携と連動）
- [x] `provider=none` で中核操作が成立する。
- [~] integration test でルーティング・監査・安全停止が検証される。— **部分**: `test_ai_eval_pipeline.py::test_ai_route_emits_routing_audit_event` を追加 — /ai ルート実走行で `llm` 監査イベントが CE2-C5 項目（task/routingStage/provider/model/trace_id）で dispatcher へ出ることを固定（SEC-LLM-AUDIT-01 配線の e2e）。**安全停止（MMR-06）は未実装のため integration 未追加**。単体テスト44件＋本統合テストで pass。

## 進捗（2026-08-12）

MMR-01/02/03/04/05を実装（46ec01aa）。MMR-06（final_judgement利用不能時のheld遷移）は外部エージェント連携（proposal/apply）と連動するため、別途対応。単体テスト2件追加（44 passed）。

## 検証計画

- `cd 03_Implement/backend && python -m pytest`（ルーティング・監査・安全停止）
- `python 01_Plans/docs_check.py`

## 補足

- 本issueは要件・契約固定を目的とし、既存の ContextQuery/ContextBundle（CE1）と provider 契約（ADR-0050）を再利用する。
- `final_judgement` の high-reasoning tier 選定は、利用可能なモデルとコスト制約に依存するため、実装時に設定として決める。
