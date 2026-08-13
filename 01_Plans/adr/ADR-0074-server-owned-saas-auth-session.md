# ADR-0074: SaaS active tenantをserver-owned認証sessionへ束縛する

- Status: Accepted
- Date: 2026-08-11
- Accepted: 2026-08-13（**案2 server-owned BFF session を採用**。保守者による明示承認。仮承認ではない）
- Deciders: Project Maintainer
- Source Issue: `SAAS-TENANT-SESSION-BINDING-01`
- Scope: `03_Implement/backend/`, `03_Implement/frontend/`, Identity Broker連携、SaaS session persistence

## Context

`ADR-0061`はactive tenantと`tenantSessionVersion`を認証session単位で原子的に解決・更新すると決めた。しかし現行実装は`principal_id`を共有DBの主キーとし、versionだけを保存する。選択tenantは保存されず、同じprincipalの別sessionも分離できない。version cookieもDB lookupやanti-forgery検証に使われない。

単なる列追加では解決しない。requestから「同じブラウザ認証session」をserver-trustedに識別する入力が必要である。access tokenの`jti`はtoken識別子であり、通常の連続requestやrefresh後も続くlogin sessionの識別子ではないため流用しない。

比較対象は次の3案である。

1. BrokerのOIDC `sid`相当claimをBearer access tokenへ含め、`issuer + sid`をsession keyにする。OP sessionを表すopaque IDという意味は適合するが、標準の`sid`提供先は主にID Token／Logout Tokenであり、access token搭載はBroker固有契約になる。token更新時の継続性、session fixation、logout通知もBrokerごとに検証が必要である。
2. BFFがOAuth clientとtokenを保持し、browserにはHttpOnly・Secure cookieでserver-owned session IDだけを渡す。API request、active tenant、version、logoutを同じserver sessionへ束縛できるが、現行の「SPAがBearer tokenをメモリ保持しAPIへ直接送る」方針を変更する。
3. tenant切替ごとにBrokerからtenant別tokenを再発行する。DB session正本は減るが、切替UIが認証redirectへ依存し、複数Brokerのclaim更新と失敗時状態が複雑になる。

参考仕様: OpenID Connect Back-Channel Logout 1.0は`sid`をissuer内で一意なUser Agent/deviceのopaque session IDとして定義する。OAuth 2.0 for Browser-Based Applicationsの現行IETF draftはBFFを、browserからtokenを隠し全API requestをbackend経由にする最も強い構成として整理している。

## 採択記録（2026-08-13）

保守者の明示承認により Proposed → Accepted。**案2 の server-owned BFF session を採用**する。下記 Decision の7項目がそのまま実装要件になる。

### 実装の解禁

本ADR採択により、**1つの判断で3本の Open P1 が同時に着手可能**になる。

| issue | 本ADRが与える前提 |
|---|---|
| `OPS-SAAS-SCALE-01`（Open P1） | AC-4〜8 が未達で本ADR待ちだった。session 失効の正本が DB 側の `session_key_hash` 行に定まることで、水平スケール時の失効伝播が設計可能になる |
| `SAAS-TENANT-SESSION-BINDING-01` | 詳細なデータ/API修正の正本。本ADRの Decision 3（session row のキー設計）が前提 |
| `AUTH-ONE-TIME-JWT-01` | Decision 7（access token `jti` を session 主キーへ流用しない）が方針を確定させる |

### 採択時に確認した現行実装との差分

現行の `saas_tenant_sessions`（`models.py`）は `principal_id` をキーとし version のみを保持する。本ADR採択は次の3点を**破壊的変更として認める**ことを含む。

1. `principal_id` 主キー → `session_key_hash` 主キー（別 device 非干渉のため。Decision 3）
2. SPA の Bearer 直接送信を廃止し、HttpOnly cookie ＋ anti-CSRF へ移行（Decision 2/5）
3. logout は提示 session のみ失効。全 session logout は明示的な別操作（Decision 6）

`direction-review-2026-08-13.md` が「session model is principal-scoped, not session-scoped」として記録した問題群（別browser/deviceで切替とlogoutが干渉する、次のrequestでJWTのclaim tenantへ戻り得る、cookieがDB行と照合されない、行が失効しない）はすべて 1 の帰結であり、本採択がその根本対策にあたる。

## Decision（採択済み）

**案2のserver-owned BFF sessionを採用する。**

1. kj-atlasまたは同一trust boundaryのgatewayをconfidential OAuth clientとし、access/refresh tokenをbrowserへ渡さない。
2. browserには128-bit以上のentropyを持つopaque session IDをHttpOnly、Secure、SameSite=LaxまたはStrict cookieで発行する。DBには生cookie値ではなくkeyed hashを保存し、key rotation手順を持つ。
3. session rowは`session_key_hash`を主キーとし、`principal_id`、`issuer`、`subject`、`active_tenant_id`、`tenant_session_version`、作成・最終利用・絶対失効時刻、失効状態を保持する。tenant membership/capabilityはrequestごとに正本を再確認し、session snapshotだけで許可しない。
4. active tenant変更はsession rowの現在tenant/versionを条件に、membership再確認後にCAS更新する。同じsessionの全タブだけが新versionへ進み、同じprincipalの別sessionへ波及しない。
5. state-changing requestはOrigin/Host検証に加えてsessionへ束縛したanti-CSRF tokenを要求する。SameSite cookieだけを唯一のanti-forgery境界にしない。
6. logoutは提示sessionだけを失効させる。全session logout、管理者失効、OIDC back-channel logoutは明示的な別操作として`issuer + subject`または検証済み`issuer + sid`の索引から対象sessionを失効させる。
7. access token `jti`、tenant claim、principal ID、client入力のsession IDをsession主キーへ流用しない。

## Three-Element Verification（ADR-0067）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | 利用者は1つのlogin session内でactive tenantを切り替え、同じsessionのタブだけが連動する。別browser/deviceの作業は維持される | logout UIは「このsession」と「全device」を区別する。切替時は同sessionの他タブへ影響する説明を維持する |
| **データ設計** | active tenantとversionをserver-owned session rowへ原子的に保存し、principal、token、tenant claimとは別キーにする | cookie生値・token・versionを監査本文へ保存しない。membership停止・失効・期限切れではrowが残っても利用を拒否する |
| **機能設計** | BFFがOAuth tokenを保持し、browser requestをsession cookie＋anti-CSRFで受ける。切替はCAS、全tenant APIはresource lookup前にversion照合する | SPAのBearer直接送信を廃止する。session bootstrap、refresh、logout、back-channel logout、複数workerを同じ失効正本へ接続する |

### 三要素間の牽制結果

- 業務上必要な「別device非干渉」はprincipal主キーを禁止し、データ設計へsession固有キーを要求する。
- データ上のactive tenant正本は、機能設計へtoken claimより先にsession rowを解決し、その後membershipを再確認する順序を要求する。
- cookie認証化はCSRFを新たに生むため、機能設計のOrigin/Host＋anti-CSRF検証がなければ業務上の安全な切替を満たさない。

## Consequences

- XSS時のtoken窃取範囲を縮小し、active tenant、version、logoutを同じserver sessionへ束縛できる。
- OAuth callback、token refresh、BFF proxy、CSRF、session expiry、key rotation、logout連携の実装・運用が増える。
- `ADR-0064`の「SPAがJWTをメモリ保持し、HttpOnly cookieとの二重管理は採用しない」という選択を、本ADRがAcceptedになった時点でsupersedeする。Proposed中は現行方針を変更しない。
- 現行`saas_tenant_sessions`はin-placeで意味を変えず、新tableへのexpand/backfill不可（既存行からsession ownershipを復元できない）・cutover・旧table削除の段階移行とする。cutover時は既存SaaS loginを再認証させる。

## Acceptance Gate

本ADRをAcceptedへ変更する前に、次をMaintainerが確認する。

- BFFをkj-atlas backendへ内蔵するか、同一trust boundaryのgateway責務にするか。
- cookie domain/path、SameSite、CSRF方式、絶対／idle timeout、refresh token保管・暗号鍵管理。
- Brokerごとのlogout連携範囲と、back-channel logout非対応時の全session失効手順。
- SPA Bearer直接送信を前提とする既存E2E、CORS、運用手順の移行範囲。

## Rejected for this proposal

- **Broker `sid`を直ちに採用**: 現行APIが受けるaccess tokenに標準必須ではなく、Broker固有claim契約を共通安全境界にするため見送る。BFF内部で検証済みlogout相関値として使う余地は残す。
- **principal単位のままactive tenant列だけ追加**: 別session非干渉を満たさない。
- **version cookieをsession IDへ昇格**: 現在はserver ownership検証なしに発行され、active tenant正本とも結び付かない。移行時に新規sessionとして再発行する。

## Traceability

- Derived-from: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`
- Related: `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`
- Implementation issue: `01_Plans/issues/issue-SAAS-TENANT-SESSION-BINDING-01-principal-keyed-session-state.md`
- Standards: OpenID Connect Back-Channel Logout 1.0, OAuth 2.0 for Browser-Based Applications (IETF draft)

