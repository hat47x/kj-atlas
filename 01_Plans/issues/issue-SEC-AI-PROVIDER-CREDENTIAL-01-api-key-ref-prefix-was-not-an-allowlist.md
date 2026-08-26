# Issue: SEC-AI-PROVIDER-CREDENTIAL-01 apiKeyRefのprefix判定が他用途secretを参照可能にする

- Type: Security / Credential boundary
- Status: Done
- Source Issue: `AI-MODEL-GOVERNANCE-03`動的provider dispatch実装時のモンキーテスト（2026-08-26）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/model_registry.py`, `03_Implement/backend/src/kj_atlas_api/llm/provider.py`, model registry tests
- Related ADR/Spec: `ADR-0065`, `AI-MODEL-GOVERNANCE-03`, `ADR-0035`
- Expected verification level: `integration`

## 課題

provider登録の`apiKeyRef`は「allowlist済み環境変数」と説明されていたが、実装は`KJ_ATLAS_` prefixへ一致する任意名を許可していた。registry駆動dispatchが参照を実際に解決すると、`KJ_ATLAS_ADMIN_API_KEY`や業務APIキー等を外部LLMのAuthorization headerへ誤送信できる。平文secretをDBへ保存しない対策だけでは、用途の異なるsecret間の境界を守れない。

## 対応方針

- 環境変数参照は既知のprovider credential名を列挙した明示allowlistに限定する。
- `secret:`参照は形式のみ保存可能とするが、secret-manager adapter未設定時は実行時にfail-closedとする。
- API検証に加え、DB直接投入を想定してruntime resolverでもallowlistを再検証する。
- エラー、API、監査へ参照名・secret値を露出しない。

## 受入条件

- [x] `KJ_ATLAS_DEEPSEEK_API_KEY`はDeepSeek provider参照として利用できる。
- [x] `KJ_ATLAS_ADMIN_API_KEY`および任意`KJ_ATLAS_*`名は登録時に422となる。
- [x] DBへ未許可参照が存在してもruntimeはcredentialを解決しない。
- [x] secret-manager adapter未設定の`secret:`参照はprovider unavailableとなる。
- [x] secret値をAPI応答・ログ・監査へ出さない。

## 対応結果（2026-08-26）

環境変数参照allowlistを`KJ_ATLAS_DEEPSEEK_API_KEY`へ限定し、登録validatorとruntime resolverの両方で適用した。将来providerを追加するときは、transport実装と同じ変更で参照名を明示追加する。prefixだけを広げる運用は認めない。
