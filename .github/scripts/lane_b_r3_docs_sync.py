from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    return text.replace(old, new, 1)


child_path = Path("01_Plans/issues/issue-AI-ROUTE-HELD-LINKAGE-01-link-final-judgement-failure-to-proposal-state.md")
child = child_path.read_text(encoding="utf-8")
child = replace_once(
    child,
    '- model-governance / routing上、eligible final-judgement modelを解決できない状態 — **R3 pending**。現行 `check_narrative` / `detect_contradiction` はtenant model-registry gate (`_assert_model_allowed`) を通らないため、未到達のfailure classをR2で実装済みとはみなさない。',
    '- model-governance / routing上、eligible final-judgement modelを解決できない状態 — **R3 verified on branch**。`check_narrative` / `detect_contradiction` の実LLM callをtenant model-registry gate (`_assert_model_allowed`) へ接続し、明示link時のみsystem holdへ遷移する。',
    "child R3 pending prose",
)
child = replace_once(
    child,
    '`provider_validation`、parse failure、policy rejection等を同じ「利用不能」に含めるかは、実装前にAPI/error contractと合わせて明示する。曖昧なcatch-allで全失敗をholdしない。R2では `provider_validation` と入力/policy/parse failureをhold対象外とした。',
    '`provider_validation`、入力・parse/output failureは引き続きsystem hold対象外とし、曖昧なcatch-allは導入しない。R3ではtenant policyにより選択済みfinal-judgement modelを実行できない `model_not_allowed` だけを `policy_rejected` として明示分類し、`model_not_registered` / `model_provider_unavailable` は `provider_unavailable` として区別する。HTTP status/detailは既存governance contractを維持する。',
    "child failure classification",
)
child = replace_once(
    child,
    '- [ ] model-governance / routing上、eligible final-judgement modelを解決できないfailureを、同じ明示link / system-held契約へ接続する。— R3。現行final-judgement routeは `_assert_model_allowed` を通らないため未実装。',
    '- [x] model-governance / routing上、eligible final-judgement modelを解決できないfailureを、同じ明示link / system-held契約へ接続する。— R3: 全actual final-judgement LLM callをtenant registry gateへ接続し、明示link時だけ `model_not_allowed` / `model_not_registered` / `model_provider_unavailable` をsystem `held` へ接続。成功時はselected modelと `RegisteredProviderConfig` を実requestへ固定する。',
    "child R3 AC",
)
child = replace_once(
    child,
    '- [ ] R3のmodel-governance / routing failure integration evidenceを追加する。',
    '- [x] R3のmodel-governance / routing failure integration evidenceを追加する。— GitHub Actions run `34018370431`: R3 + R2 system-hold + proposal-linkage + model-governance + AI eval pipelineのfocused/adjacent regression 51 passed、`compileall`、docs contract、Issue lifecycle 35 tests、`git diff --check` がsuccess。',
    "child R3 evidence AC",
)
child = replace_once(
    child,
    '- [ ] `AI-ROUTE-01` MMR-06はR2 + R3のintegration evidenceとcloseout同期が揃うまで未完了のままとする。',
    '- [ ] `AI-ROUTE-01` MMR-06の最終closeoutはR3のmain統合後に同期する。併せて、親MMR-05で不足しているlinked final-judgement telemetry（`sourceBundleHash` / `proposalId` の一貫した監査記録）を別残差として解消し、MMR-06安全停止とMMR-05追跡性を混同しない。',
    "child closeout residual",
)
child += '''\n\n## R3 実装・検証履歴（2026-09-06）\n\n- `check_narrative` と `detect_contradiction` のactual LLM callは、standalone / linkedを問わず `resolve_model_for_task()` → `_assert_model_allowed()` を通る。proposal state transitionだけは従来どおり明示的 `externalProposalRef` がある場合に限定する。\n- governance成功時は、選択済み `model_id` と `_assert_model_allowed()` が返した `RegisteredProviderConfig` を同じ `LLMRequest` へ渡し、registry確認後にglobal provider/fallbackへ迂回する経路を作らない。\n- `detect_contradiction` はhuman adjudication済みcontradictionを先にreturnし、LLM call自体が不要な場合にはgovernance gateやsystem holdを発火させない。\n- pre-provider governance failureは `model_not_allowed -> policy_rejected`、`model_not_registered` / `model_provider_unavailable -> provider_unavailable` としてsystem auditへ正規化する。外向きHTTP detailは既存contractのまま維持する。\n- provider dispatch前なので存在しないprovider/traceは監査へ捏造せず、`requestedModelId` / `governanceCode` / `failureCode` / `routingStage=final_judgement` を記録する。\n- verification: GitHub Actions run `34018370431` でfocused/adjacent regression **51 passed**、`python -m compileall -q src/kj_atlas_api`、non-test docs contract（`active_memos=43`, `tracked_markdown=787`）、Issue lifecycle **35 tests OK**、`git diff --check` がsuccess。one-shot patch/helper/workflowは同run内で自己削除済み。\n- R3はmodel-governance safety boundaryを閉じるが、親MMR-05のlinked telemetry completenessは別残差として扱う。R3の実装成功を理由に、未記録の `sourceBundleHash` / `proposalId` まで完了扱いしない。\n'''
child_path.write_text(child, encoding="utf-8")

parent_path = Path("01_Plans/issues/issue-AI-ROUTE-01-multi-model-routing-and-final-judgment-boundary.md")
parent = parent_path.read_text(encoding="utf-8")
parent = replace_once(
    parent,
    '- [x] 監査ログに MMR-05 の4項目が記録される。— `_audit_llm_trace` に `routingStage` 追加',
    '- [~] 監査ログに MMR-05 の4項目が記録される。— `_audit_llm_trace` で `routingStage` / provider/model は記録済み。一方、linked final-judgementの通常LLM auditとsystem-hold auditで `sourceBundleHash` / `proposalId` を一貫して保持する契約は未完了のため、完全達成とはみなさない。',
    "parent MMR-05 truth sync",
)
parent = replace_once(
    parent,
    '- [ ] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。— 未実装。現行 `check_narrative` / `detect_contradiction` はproposal識別子を持たず、対象proposalを安全に一意特定できないため、`AI-ROUTE-HELD-LINKAGE-01` でproposal identity / system hold / recovery契約を先に固定する。',
    '- [ ] final_judgement 利用不能時に held へ遷移し、auto-publish しない（MMR-06）。— R1/R2はmain統合済み、R3 model-governance boundaryはbranchでintegration verified。R3のmain統合とcloseout同期が完了するまで未完了扱いを維持する。',
    "parent MMR-06 progress",
)
parent = replace_once(
    parent,
    '- [~] integration test でルーティング・監査・安全停止が検証される。— **部分**: `test_ai_eval_pipeline.py::test_ai_route_emits_routing_audit_event` を追加 — /ai ルート実走行で `llm` 監査イベントが CE2-C5 項目（task/routingStage/provider/model/trace_id）で dispatcher へ出ることを固定（SEC-LLM-AUDIT-01 配線の e2e）。**安全停止（MMR-06）は未実装のため integration 未追加**。単体テスト44件＋本統合テストで pass。',
    '- [~] integration test でルーティング・監査・安全停止が検証される。— routing audit既存e2eに加え、R2 system-holdとR3 model-governance安全停止をintegrationで固定。R3 GitHub Actions run `34018370431` はfocused/adjacent 51 passed。ただしMMR-05のlinked `sourceBundleHash` / `proposalId` telemetry completenessが残るため全体は部分達成。',
    "parent integration evidence",
)
parent += '''\n\n## R3 model-governance進捗（2026-09-06）\n\n- branch `lane-b/final-judgement-model-governance-r3` で、actual final-judgement LLM callをtenant model registry / allowlistへ接続した。成功時はselected modelとregistered providerを同一 `LLMRequest` に固定する。\n- linked external proposalではgovernance/routing failureをprovider dispatch前にsystem `held` へ接続し、standalone callはproposal state-neutralを維持する。human adjudicationでLLM不要な `detect_contradiction` はgate前にreturnする。\n- Run `34018370431`: focused/adjacent regression 51 passed、compileall、docs contract、Issue lifecycle 35 tests、diff check success。\n- MMR-06はR3 main統合後にcloseout同期する。MMR-05については、従来の `[x]` が `routingStage` 追加だけを根拠に4項目全達成としていたため `[~]` へ補正した。`sourceBundleHash` / `proposalId` のlinked telemetry completenessは次残差として扱う。\n'''
parent_path.write_text(parent, encoding="utf-8")

print("R3 issue evidence synced without premature closeout")
