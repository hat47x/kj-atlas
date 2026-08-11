# Issue: AUTH-ONE-TIME-JWT-01 one-time JWTの要求単位供給契約が未実装

- Type: Architecture / Security / Frontend
- Status: Open
- Source Issue: `SEC-AUTH-REPLAY-01`
- Priority: P1
- Owner: Unassigned
- Scope: frontend auth client, Broker/BFF integration, retry coordinator, `ADR-0064`
- Related ADR/Spec: `ADR-0064`, `OPS-SAAS-SCALE-01`, `SEC-AUTH-REPLAY-01`
- Expected verification level: integration

## 課題

cluster-wide JWT replay拒否は、同じ`jti`のBearer tokenを2回目以降拒否する。backendとmock Brokerの契約は固定できたが、現行frontendは短命access tokenをmodule memoryへ保持する設計であり、API要求ごとに新しいtokenを取得・消費する供給経路がまだない。通常のOAuth access tokenを再利用する実装のままSaaS frontendを接続すると、2要求目が`token_replayed`になる。

## 対応方針

- Brokerまたはsame-origin BFFが、要求ごとに一意な`jti`を持つ短命tokenを供給する境界を設計する。
- token取得、API送信、消費済み破棄を1つのcoordinatorへ閉じ込め、並列fetchへ同じtokenを配らない。
- network応答不明時は同じtokenをretryせず、新tokenとidempotency contractを使う。mutationの二重実行防止はJWT replay防御へ依存させない。
- browser storage、log、diagnostic、error responseへtokenまたは生`jti`を残さない。

## 受入条件

- [ ] 連続・並列API要求がそれぞれ異なる`jti`で成功する。
- [ ] 同じtokenの意図的再送は、別workerへ到達しても`token_replayed`となる。
- [ ] token供給失敗、timeout、応答不明retryがfail-closedし、mutationを重複実行しない。
- [ ] refresh tokenをSPAへ渡さず、XSS時のcredential露出範囲を拡大しない。
- [ ] mock Broker、frontend統合、最低2 backend workerのE2Eで契約を固定する。

## 暫定運用

本issue解消までは、`saas-multitenant`のbackend多worker保証は成立するが、現行frontendを本番SaaSの認証clientとして解禁しない。Broker/BFFが要求単位token供給を担う構成だけを対象とする。
