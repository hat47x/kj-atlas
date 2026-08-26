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

なお、この時点の`KJ_ATLAS_*` prefix許可は、実際に参照を解決するAC-5実装時に用途外secretへ到達し得ると判明した。最終仕様では`SEC-AI-PROVIDER-CREDENTIAL-01`により明示allowlistへ置き換えている。

## 対応記録4（2026-08-26・AC-5完了）

modelの`providerId`からactive provider rowを解決し、request単位でlocal／DeepSeek／large-scale transportを構築する動的dispatchを実装した。`/ai/available-models`と実行前gateは同じregistry設定（lifecycle、tenant allowlist、base URL、credential参照、large-scale policy）から利用可否を判定する。process-wide `KJ_ATLAS_LLM_PROVIDER`はenv seedと後方互換の既定経路に残るが、registry modelの配送先選択には使わない。

統合testではprocess既定を`none`にしたままlocalとDeepSeekを同時登録し、両modelが一覧へ現れ、local modelだけがloopback `/generate`へ、DeepSeek modelだけがOpenAI互換 `/v1/chat/completions`へ送られることを固定した。別providerのmodel ID・credentialが混線しないこともrequest payload／Authorization headerで確認した。

実装中に検出した配送先登録境界とcredential参照allowlistの不備は、`SEC-AI-PROVIDER-DEST-01`および`SEC-AI-PROVIDER-CREDENTIAL-01`として別起票し、同時に修正した。
