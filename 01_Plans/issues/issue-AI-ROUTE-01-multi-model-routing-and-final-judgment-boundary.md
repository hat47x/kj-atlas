# Issue Draft: AI-ROUTE-01 Multi-Model Routing（MMR-01〜06）の実装要件

- Type: Feature request / AI capability
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a, `03_Implement/backend/src/kj_atlas_api/`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md` §7.1a（MMR-01〜06）, `02_Architecture/value_traceability.md` §2.1（V3）, `01_Plans/adr/ADR-0050-llm-provider-configuration-contract.md`
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

- [ ] intermediate と final_judgement の責務分離が契約（api.md/schemas.md）で固定される。
- [ ] intermediate の許可タスク・禁止タスクが強制される（MMR-02/03）。
- [ ] final_judgement が high-reasoning tier へルーティングされる（MMR-04）。
- [ ] 監査ログに MMR-05 の4項目が記録される。
- [ ] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。
- [ ] `provider=none` で中核操作が成立する。
- [ ] integration test でルーティング・監査・安全停止が検証される。

## 検証計画

- `cd 03_Implement/backend && python -m pytest`（ルーティング・監査・安全停止）
- `python 01_Plans/docs_check.py`

## 補足

- 本issueは要件・契約固定を目的とし、既存の ContextQuery/ContextBundle（CE1）と provider 契約（ADR-0050）を再利用する。
- `final_judgement` の high-reasoning tier 選定は、利用可能なモデルとコスト制約に依存するため、実装時に設定として決める。
