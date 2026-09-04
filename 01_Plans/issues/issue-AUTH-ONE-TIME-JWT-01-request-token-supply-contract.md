# Issue: AUTH-ONE-TIME-JWT-01 Bearer access tokenのreplay防御方式が未決

- Type: Architecture / Security / Frontend
- Status: Open
- Source Issue: `SEC-AUTH-REPLAY-01`
- Priority: P1
- Owner: Maintainer
- Scope: auth edge, frontend auth client, Broker/BFF integration, `ADR-0064`
- Related ADR/Spec: `ADR-0064`, `ADR-0074`（Proposed）, `OPS-SAAS-SCALE-01`, `SEC-AUTH-REPLAY-01`
- Expected verification level: integration

## 課題

直前の実装はaccess token自身の`jti`を要求単位nonceとして消費し、同じBearer tokenの2回目以降を拒否した。しかしRFC 6750のBearer tokenは、所持者が有効期間中にresource serverへ提示するcredentialであり、現行frontendも同じ短命tokenを複数API要求へ使用する。RFC 7519の`jti`はJWTの一意識別子で、通常のBearer access tokenをone-time credentialへ変える規定ではない。

このため、access token `jti`だけをDBへ一度登録して再送を拒否する方式は、正規clientと窃取者を区別できず、通常操作、並列fetch、network retryを壊す。sender-constrained tokenなしに「窃取Bearer tokenの再利用だけを拒否する」ことはできない。誤ったone-time実装は撤回し、通常のtoken再利用を復元した。

## 三要素牽制

- 業務設計: 利用者は一度のlogin後に複数の閲覧・保存要求を行える必要がある。要求ごとの再認証やtoken交換を通常業務へ持ち込まない。
- データ設計: 生token、秘密鍵、生`jti`を永続化・log出力しない。sender constraintを採る場合も公開鍵thumbprintと短命proof replay stateだけを最小保持する。
- 機能設計: Bearer方式を維持する間は署名、issuer、audience、期限、TLS、module-memory保持で防御する。強いreplay防御が必要ならaccess tokenの`jti`ではなく、HTTP method/URI/token hashへ結び付く要求単位proofを検証する。

## 対応方針

- 候補A: RFC 9449 DPoP。client鍵へaccess tokenをsender-constrainし、要求ごとのDPoP proof `jti`、`htm`、`htu`、`ath`を検証する。
- 候補B: same-origin BFF session。Bearer tokenをbrowserへ渡さずBFFへ閉じ込め、browser要求はHttpOnly sessionとCSRF防御で扱う。
- 候補C: 現行Bearer方式を維持し、短い有効期限、TLS、module-memory保持、audience制限を保証範囲として明記する。
- 比較判断の正本は`ADR-0074`へ集約した。同ADRはactive tenant正本化とtoken replay露出縮小を同じserver-owned session境界で解く案Bを採用候補としている。DPoPを別系統で並行実装せず、ADRがAcceptedになるまで現行Bearer保証を超えて表明しない。

## 受入条件

- [x] 通常のBearer access tokenを連続API要求へ使用できる契約を回帰testで復元する。
- [x] `jti`欠損tokenをRFC 7519どおり通常Bearer JWTとして扱い、docstringとtestを一致させる。
- [x] DPoP、BFF、短命Bearer継続の業務・データ・機能trade-offを`ADR-0074`へ集約し、BFFを採用候補としてProposedにした。
- [ ] `ADR-0074`をMaintainerがAcceptedまたはRejectedにし、本issueの実装方式を確定する。
- [ ] 強いreplay防御を採る場合、別worker間でも要求proof再利用を拒否し、通常のaccess token再利用を壊さない。
- [ ] timeout、応答不明retryがfail-closedし、mutationを重複実行しない。
- [ ] refresh tokenをSPAへ渡さず、XSS時のcredential露出範囲を拡大しない。
- [ ] mock Broker、frontend統合、最低2 backend workerのE2Eで契約を固定する。

## 暫定運用

本issueと`SAAS-TENANT-SESSION-BINDING-01`の方式決定までは、PostgreSQLが共有するのはprincipal単位versionだけであり、認証session単位のactive tenantを伴う多worker本番運用は未保証とする。JWT replay防御済みとも表明しない。Bearer tokenの保証範囲は短命、署名検証、issuer/audience制限、TLS、browser storage不使用までとする。

## 依存関係

- `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（採択が前提。DPoP/BFFの並行実装を避ける）
- `01_Plans/issues/done/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md`（BFF採択時は同一session正本として実装・検証する）

## 根拠

- RFC 7519 §4.1.7: `jti`はJWTの一意識別子でありoptional。access tokenの一回使用を意味しない。
- RFC 6750 §1.2/1.3: Bearer tokenは所持者がresource serverへ提示するaccess credentialで、鍵所持証明を要求しない。
- RFC 9449 §4.2: replay防御対象の要求単位`jti`はaccess tokenではなく、`htm`/`htu`等へ結び付くDPoP proof JWTに置かれる。
