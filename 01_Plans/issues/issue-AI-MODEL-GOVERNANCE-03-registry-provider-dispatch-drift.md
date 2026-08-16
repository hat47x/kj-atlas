# Issue: AI-MODEL-GOVERNANCE-03 モデルregistryのproviderIdが実行transport選択に使われない

- Type: Correctness / Security
- Status: Open
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

- [ ] modelの`providerId`と異なるtransportへrequestを送らない。
- [ ] 利用者画面に表示されたmodelは、同一session・同一tenant条件で実行前gateを通る。
- [ ] `none`または設定不足provider配下のmodelは実行操作を有効化しない。
- [ ] `apiKeyRef`の秘密値をDB・API・ログ・監査へ出さない。
- [ ] DeepSeek/localの2providerを同時登録した統合testで正しいtransport選択と不一致拒否を固定する。

## 検出記録（2026-08-16）

管理APIでprovider/modelを動的登録し、利用者APIとEdge画面への反映を横断確認した際、registry repositoryの説明と実行provider選択の実装が一致しないことを静的・実動作の両面で確認した。
