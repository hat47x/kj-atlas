# Issue: AI-MODEL-UX-01 利用可能modelが空の理由を利用者画面で判別できない

- Type: UX / Operability
- Status: Done
- Source Issue: 管理UI・API・MCP協調モンキーテスト（2026-08-16）
- Priority: P2
- Owner: Maintainer
- Scope: `/ai/available-models`, frontend `ModelSelector`, admin model/provider status UI
- Related Issue: `AI-MODEL-GOVERNANCE-03`
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-01`, `02_Architecture/api.md` §2.11
- Expected verification level: `e2e`

## 課題

`/ai/available-models`は実効集合だけを返すため、空配列が「active modelなし」「tenant allowlistで全除外」「実行provider transport不一致」「provider設定不足」のどれによるものか利用者画面で判別できない。今回、空状態に管理設定・AI接続設定を確認する案内を追加したが、利用者は管理者へ伝えるべき原因や復旧操作を特定できない。

## 対応方針

- 秘密情報や他tenantのmodel名を漏らさない、列挙型の`unavailableReason`または集約診断をAPI契約へ追加する。
- 利用者画面は権限に応じて「管理者へ連絡」と「管理画面で確認」を出し分ける。
- 管理画面はprovider lifecycle、runtime transport、tenant allowlistの交差結果を、実行可否と同じresolverから説明表示する。
- API応答と表示文言は、model/providerの状態変更後にも同一session・tenant条件で整合させる。

## 受入条件

- [x] 空集合の主要原因を、情報漏えいしない安定したreason codeで区別できる。
- [x] 一般利用者には管理権限を前提としない次の行動が表示される。
- [x] 管理者には原因に対応する設定箇所が表示される。
- [x] provider不一致、allowlist空、active modelなしをAPI・Edge E2Eで固定する。— 2026-08-25、`03_Implement/frontend/e2e/ai_model_ux_available_models_reason.spec.ts`。page.routeでは固定せず、実backend（fresh SQLite、`KJ_ATLAS_LLM_PROVIDER=none`）へ`/admin/provision/models/**`管理APIで直接registry/allowlistを変更し、実Chromiumで確認した。(1) `no_active_models`: registryが空の状態。(2) `provider_unavailable`: 有効なmodelを登録するがそのproviderKind（`deepseek`）が実行runtime（`none`）と一致しない状態。(3) `tenant_policy_excludes_all`: runtimeと一致するproviderKind（`none`）のmodelを別途登録した上で、tenant allowlistを(2)の到達不能modelのみに絞り、到達可能modelを除外した状態。3reasonそれぞれでModelSelectorの案内文言（`model_selector.reason.*`）が一致することを確認し、続けて同一session・tenantでallowlistをクリアするとreasonが解消しmodelが選択可能になることも確認した（対応方針の「同一session・tenant条件での整合」）。第4のreason `no_user_selectable_models` はこのAC自身が名指しする3件に含まれないため対象外（未着手のまま明記）。ModelSelectorが管理権限で文言を出し分けるコードパスは存在しない（`ModelSelector.tsx`は`unavailableReason`のみで分岐し、admin/非adminの分岐なし）ことをコード確認済みのため、admin/非adminでの差分検証は行っていない。

## 検出記録（2026-08-16）

Edge実画面でprovider `none`・利用可能model空を再現し、selectorのdisabled状態と汎用案内は確認できた。一方、現行APIには原因情報がなく、UIだけではこれ以上具体化できないため継続課題として起票した。

## 対応記録（2026-08-16）

`/ai/available-models`へ、秘密値・他tenant情報・内部provider IDを含まない集約reason codeを追加した。

- `no_active_models`
- `provider_unavailable`
- `tenant_policy_excludes_all`
- `no_user_selectable_models`

利用者画面は各理由に応じて「モデル登録・有効化」「AI接続」「tenant allowlist」「model capabilities」のどれを管理者へ確認すべきか表示する。backendの各分岐test、API client契約、selector表示test、型検査は成功した。実ブラウザで4理由すべてを固定するE2Eが残るため`In Progress`とする。

## 対応記録2（2026-08-25）

第4のACに従い、`provider_unavailable`・`tenant_policy_excludes_all`・`no_active_models`の3reasonを実backend + 実Chromiumの E2E（`03_Implement/frontend/e2e/ai_model_ux_available_models_reason.spec.ts`）で固定した。詳細は上記ACの注記を参照。`no_user_selectable_models`（4番目のreason）は本ACが名指ししないため対象外。

検証:

- 新規spec: 実backend起動（fresh SQLite、`alembic upgrade head`、`KJ_ATLAS_LLM_PROVIDER=none`）に対し `KJ_ATLAS_E2E_REAL_BACKEND=1 npx playwright test e2e/ai_model_ux_available_models_reason.spec.ts --workers=1` で2件pass。`KJ_ATLAS_E2E_REAL_BACKEND`未設定では2件ともskip（既定の`npm run e2e`はbackend不要のまま）。
- backend回帰: `pytest tests/test_llm_provider.py tests/test_ai_provider_error_contract.py tests/test_model_governance.py` で65 passed（reason-code契約のdriftなし）。
- frontend単体: `vitest run src/ui/ModelSelector.test.ts src/api/client.test.ts` で50 passed。
- frontend E2E全件（回帰確認）: 223件中200 passed・10 skipped（うち2件は本specの自己skip）・13 failed。failedの内訳を`--workers=1`・実backend停止済みの条件で再実行して切り分けた: (a) 2件（`recent_documents_dialog.spec.ts`全件・`header_toolbar_layout.spec.ts`390x720）は、本検証で使った実backend fixtureを停止せずに全件走らせたことによる汚染で、backend停止後は成功（本PRのtest hygiene issueであり回帰ではない。`01_Plans/agent_failure_log.md`に記録した）。(b) 残り11件・8ファイル（`agent_response_import.spec.ts`×2、`agent_task_export.spec.ts`×1、`ce3_patch_workspace.spec.ts`×1、`diagnostics_structural_metrics.spec.ts`×1、`first_meaningful_map_mouse_flow.spec.ts`×2、`large_document_operability.spec.ts`×1、`public_pack_visibility_compat.spec.ts`×2、`representative_visual_cue_capacity_budget.spec.ts`×1）は、本ブランチの分岐元であるmain最新（直前の`perf(UX-PERF-01)`コミット a8f37a39）で既に発生しており、本変更（新規spec 1件 + doc 2件の追加のみ、production codeへの変更なし）とは無関係と判断した。うち3件（`agent_response_import`×2・`ce3_patch_workspace`×1）はUX-PERF-01自身の検証記録が「backend未起動由来・変更前でも同一に失敗」と既に確認済み。残り8件（`agent_task_export`・`diagnostics_structural_metrics`・`first_meaningful_map_mouse_flow`×2・`large_document_operability`・`public_pack_visibility_compat`×2・`representative_visual_cue_capacity_budget`）はUX-PERF-01の検証対象リストに含まれておらず新たに判明したため、別途フォローアップを起票した（本issueのscope外）。
- `01_Plans/docs_check.py`: 新規env var `KJ_ATLAS_E2E_REAL_BACKEND`・`KJ_ATLAS_E2E_BACKEND_URL`を`02_Architecture/runtime_parameter_registry.md`へ追加し、pass確認。

4件のAC全てが完了したため`Status`を`Done`とし、`01_Plans/issues/done/`へ移動する。
