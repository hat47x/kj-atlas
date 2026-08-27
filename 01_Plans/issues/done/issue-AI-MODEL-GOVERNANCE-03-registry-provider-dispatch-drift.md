# Issue: AI-MODEL-GOVERNANCE-03 モデルregistryのproviderIdが実行transport選択に使われない

- Type: Correctness / Security
- Status: Done
- Source Issue: `AI-MODEL-GOVERNANCE-01`横断モンキーテスト（2026-08-16）
- Priority: P1
- Owner: Maintainer
- Scope: `backend/src/kj_atlas_api/llm/provider.py`, `routes/ai.py`, model registry, provider status, frontend model selector
- Related Issue: `AI-MODEL-GOVERNANCE-01`
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-01`
- Expected verification level: `e2e`

## 課題

管理面で登録するmodelは`providerId`を持ち、provider registryは`providerKind`、`baseUrl`、`apiKeyRef`を保持する。しかし実行時の`get_provider()`はprocess-wideな`KJ_ATLAS_LLM_PROVIDER`だけでtransportを決め、requestのmodelが参照する`providerId`を使わない。したがって、DeepSeekで起動したprocessにlocal provider配下のmodelを登録・許可すると、画面と`/ai/available-models`にはそのmodelが出る一方、実行はDeepSeek transportへmodel IDを送る。`none`起動でもregistry model一覧は返り得る。

今回のUI修正ではregistry状態を表示しても、runtime providerが`none`ならAI実行ボタンを有効化しないようにした。ただし異なるactive provider間の不一致はbackendでfail-closedにする必要がある。

## 対応方針

- 短期: `/ai/available-models`と実行前gateで、現在利用可能なtransportに結び付かないmodelを除外・拒否する。
- 本実装: model IDからprovider rowを解決し、既存transport（local / large-scale / deepseek）のfactoryへ安全にdispatchする。`apiKeyRef`はallowlist済み環境変数／secret-manager参照のみ解決し、任意環境変数名や平文secretを許可しない。
- provider/model lifecycle、tenant allowlist、task tierの交差を1つのresolver結果にまとめ、表示と実行で同じ結果を使う。
- provider statusはprocess-wide設定だけでなく、実効provider/modelの利用可否を説明できる形にする。

## 受入条件

- [x] modelの`providerId`と異なるtransportへrequestを送らない（短期fail-closed gate）。
- [x] 利用者画面に表示されたmodelは、同一session・同一tenant条件で実行前gateを通る。
- [x] `none`または設定不足provider配下のmodelは実行操作を有効化しない。
- [x] `apiKeyRef`の秘密値をDB・API・ログ・監査へ出さない。
- [x] DeepSeek/localの2providerを同時登録した統合testで正しいtransport選択と不一致拒否を固定する。

## 検出記録（2026-08-16）

管理APIでprovider/modelを動的登録し、利用者APIとEdge画面への反映を横断確認した際、registry repositoryの説明と実行provider選択の実装が一致しないことを静的・実動作の両面で確認した。

## 対応記録（2026-08-16）

短期対策として、利用可能モデル一覧とAI実行前gateの双方で、登録provider kindとprocessの実行transportが一致するmodelだけを許可するようにした。不一致modelは一覧から除外し、IDを直接指定しても`model_provider_unavailable`（503）でLLM送信前に拒否する。本issueは複数providerへの動的dispatchとsecret参照解決が残るためOpenを維持する。

## 対応記録2（iteration 197・AC-4の一部進捗）

**AC-4（apiKeyRef非露呈）のAPI・監査側をテストで凍結**した（`test_model_governance.py` に `test_provider_api_key_ref_never_exposed_to_api_or_audit` を追加・15/15 pass）:

- レジストリ一覧応答（`GET /admin/provision/models`）に `apiKeyRef` キーも値も**含まれない**ことを固定（`ProviderItem` は id/providerKind/displayName/lifecycleState のみ・現行実装どおり）。
- control-plane監査（`record_admin_plane_audit`）が**メタデータのみ**（route/operation/result/status_code/request_id/actor_ref_hash/occurred_at）で、登録ペイロード（apiKeyRef値）を記録しないことを固定。
- ログについても監査・登録経路でボディを出力しないことを実地確認。

**残るAC-4のDB側**: 登録時 `apiKeyRef` は任意文字列を受理（`max_length=256` のみ）で、平文secretをそのまま `api_key_ref` 列へ格納し得る。**登録時に allowlist済み環境変数名（`KJ_ATLAS_*_API_KEY`）／secret-managerキー参照パターンだけを受理する検証**を追加するのが残作業（並行編集者＝モデルガバナンス当事者との整合を要する）。AC-5（DeepSeek/local 2-provider統合test）も残。

## 対応記録3（iteration 199・AC-4完了）

**AC-4を完了**した（API・監査側は対応記録2、DB側を本対応で追加）:

- **登録時参照検証**（`RegisterProviderRequest._api_key_ref_must_be_a_reference`）: `apiKeyRef` は **allowlist済み `KJ_ATLAS_[A-Z][A-Z0-9_]*` 環境変数名** または **`secret:` プレフィックスのsecret-managerキー参照**のみ受理。**平文secret（`sk-...`）や任意環境変数名は 422** で拒否し、`api_key_ref` 列へ平文が格納されるのを防ぐ（fail-closed・API境界）。
- **テスト**: `test_provider_api_key_ref_rejects_plaintext_at_registration` を追加 — 平文secret 422・任意env名 422・`KJ_ATLAS_*` 201・`secret:...` 201 を固定。`test_model_governance.py` **16/16 pass**・admin ops E2E **20/20 pass**（CLI provider登録の非後退を確認）。

**残るAC-5**: DeepSeek/local 2-providerの同時登録で正しいtransport選択と不一致拒否を固定する統合テスト。動的dispatchの本実装（registry providerId → transport factory）と併せて並行編集者（モデルガバナンス当事者）との整合を要する。

## 対応記録4（2026-08-27・AC-5完了・本issue Done）

**AC-5（動的dispatch本実装 + 2-provider統合test）を完了**した。着手前に並行編集者の有無を確認し、この領域を触っている他セッションは無かった（Playwright関連の無関係セッションのみ稼働中）。

### 実装

- `03_Implement/backend/src/kj_atlas_api/settings.py`: `validate_llm_provider_guards()`のprovider別readiness検査（deepseek: api_key必須、large-scale: opt_in+escalation+base_url+model+allowlist必須）を`provider_kind_readiness_errors(kind, cfg)`へ抽出した。startup fail-fast（`self.llm_provider`のみ検査）とrequest-time per-model dispatch（任意のkindを検査）が同一関数を共用するため、両者の「設定済み」の定義がドリフトしない。あわせて、`KJ_ATLAS_DEEPSEEK_BASE_URL`のtrusted-endpoint検証を`if provider == "deepseek":`の外へ出し、local/large-scaleのbase URLと同様に無条件化した（deepseekがprimaryでなくてもper-model dispatchで到達し得るため、起動時fail-fastの対象から漏れていたSSRF関連の穴を閉じた）。
- `03_Implement/backend/src/kj_atlas_api/llm/provider.py`: `LLMRequest`に`provider_kind: str | None`フィールドを追加（`model`と同じ「requestレベルの明示指定が最優先」パターン）。`get_provider(provider_kind: str | None = None)`は指定時にそのkindを`ProviderRegistry.resolve()`し、未指定時は従来どおり`settings.llm_provider`を使う。`generate_with_fallback(req)`は`req.provider_kind`が設定されていれば`get_provider(req.provider_kind)`、そうでなければ`get_provider()`（引数なし）を呼ぶ形にした——既存テストが`get_provider`を引数なしのlambdaでmonkeypatchしているケース（`test_ai_provider_status_route.py`等）との互換性を壊さないための意図的な分岐。`ProviderRegistry.is_registered()`/`is_supported_provider_kind()`を追加し、未対応kindの検出をgate側で行えるようにした。
- `03_Implement/backend/src/kj_atlas_api/routes/ai.py`: `_assert_model_allowed()`をmodelの`providerId`→provider row→`providerKind`まで解決し、そのkind**自身**のreadiness（`_provider_kind_dispatch_errors`、内部で`provider_kind_readiness_errors`を呼ぶ）を検査するよう変更。判定に成功したら`provider_kind`を返し、呼び出し元6エンドポイント（suggest-island-summary / propose-opposing-viewpoint / generate-narrative / refine-card-text / suggest-card-groups / suggest-document-title）は`generate_with_fallback(LLMRequest(..., provider_kind=provider_kind))`でその結果を実際のdispatchへ渡す。`GET /ai/available-models`の一覧フィルタも同じ`_provider_kind_dispatch_errors`を使うよう統一し（旧`_provider_matches_runtime`は削除）、一覧と実行gateが同一判定関数を共有するため乖離しない（AC-2を維持）。
- `apiKeyRef`（AC-4）: 新しいdispatch機構は`ProviderRegistry.resolve(providerKind)`が返す既存のtransport（`DeepSeekProvider`/`LocalProvider`/`LargeScaleProvider`）をそのまま呼ぶだけで、registry行の`api_key_ref`列を読む経路を新設していない。各transportは従来どおり`KJ_ATLAS_*_API_KEY`環境変数を直接読む。したがって、AC-4の参照専用バリデーション（`RegisterProviderRequest._api_key_ref_must_be_a_reference`）をバイパスする新しい資格情報読み出し経路は存在しない。

### `KJ_ATLAS_LLM_PROVIDER`の以後の意味（設計判断）

タスク説明が要求した「requests that don't specify a model-specific providerに対する変更を最小にする解釈」を採用した。

1. **起動時fail-fastの対象**は従来どおりこの値のみ（`validate_llm_provider_guards()`は`self.llm_provider`が指すkindだけを起動時に検証する。他のkindは動的データのため起動時に全件検証できない——これはタスク説明が明示的に想定していた制約）。
2. **`model`を指定しない4エンドポイント**（suggest-layout / suggest-merges / check-narrative / detect-contradiction）の既定/フォールバックtransport。これらの呼び出しは一切変更していない。
3. **`model`を指定する6エンドポイント**は、その`model`のregistry上の`providerKind`へ動的dispatchする。`KJ_ATLAS_LLM_PROVIDER`と一致するかではなく、そのkind自身の設定完全性（起動時検査と同一関数）で判定する。
4. **`none`は無条件のkill switch**として維持する。`KJ_ATLAS_LLM_PROVIDER=none`のときは、registryに他のkindが設定済み（例: `KJ_ATLAS_DEEPSEEK_API_KEY`が偶然設定されている）であっても、動的dispatchを含め一切のAI呼び出しを行わない。これはAGENTS.md §7の安全不変条件「`KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する」を、per-model dispatch導入後も文字通り維持するための設計判断であり、`test_dynamic_dispatch_disabled_by_none_kill_switch`で固定した。

`02_Architecture/api.md`・`02_Architecture/runtime_parameter_registry.md`・`02_Architecture/llm_provider_spec.md`（§3.1として追記）を上記の意味に合わせて更新した。

### 検証

- `test_model_governance.py`に`test_dynamic_dispatch_local_and_deepseek_simultaneously`（DeepSeek/local同時登録 → 各modelが自分のtransportへ正しくdispatchすることをfake HTTP endpointで実証 → deepseekのAPI keyを外すと`model_provider_unavailable`503でLLM呼び出し前に拒否されることを確認）と`test_dynamic_dispatch_disabled_by_none_kill_switch`（`KJ_ATLAS_LLM_PROVIDER=none`はdeepseek設定済みでも一切dispatchしない）を追加。21/21 pass。
- **Mutation test**: `generate_with_fallback`の`get_provider(req.provider_kind)`呼び出しを一時的に`get_provider()`（引数なし、常にprocess-wide設定を使う）へ書き換え、`test_dynamic_dispatch_local_and_deepseek_simultaneously`が実際に失敗する（deepseek-modelへのリクエストがlocal transportへ誤ってdispatchされ、応答テキストが不一致になる）ことを確認した上で復元し、再度green（21/21 pass）を確認した。
- 関連backendテスト（`test_llm_provider.py`・`test_model_governance.py`・`test_ai_provider_status_route.py`・`test_ai_provider_error_contract.py`・`test_ai_oppose.py`・`test_ce2_proposal_api.py`・`test_ai_safemode.py`・`test_ai_eval_pipeline.py`・`test_ai_relations_route.py`）: 120/120 pass。
- backend全体`pytest`（`python -m pytest`）を初回実行した際、`test_llm_settings.py::test_large_scale_provider_requires_complete_destination_settings`（3 parametrize全件）が失敗した。`provider_kind_readiness_errors()`への抽出でlarge-scaleの「base URL/model/allowlist不足」メッセージ文言を変えてしまったため（テストは元の文言`"requires its base URL, model, and allowlist"`に一致することを固定していた）。`settings.py`のメッセージを元の文言へ戻して修正し、`test_llm_settings.py`32/32・`test_llm_provider.py`+`test_model_governance.py`+`test_llm_settings.py`97/97 pass、backend全体1290+97 pass 0 failedを確認した（正確な最終件数はPR本文に記載）。
- `01_Plans/docs_check.py`の実チェック（`run_docs_check(run_tests=False)`）: 680 markdown、errors 0（api.md/runtime_parameter_registry.md/llm_provider_spec.mdの更新を含めて既存契約違反なし）。埋め込みunittestスイート（`01_Plans/tests`・`01_Plans/issues/tests`）も個別実行でOK（本セッションの検証環境固有のgit-worktree制約により、`docs_check.py`のワンショット実行では無関係なfixtureテストが誤爆したため、原因を切り分けた上で個別実行に切り替えた。詳細は`01_Plans/agent_failure_log.md`）。

上記により受入条件は全項目達成し、本issueをDoneとする。
