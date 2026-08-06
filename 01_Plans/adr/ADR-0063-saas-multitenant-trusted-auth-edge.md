# ADR-0063: saas-multitenant の trusted auth edge を broker 前提の multi-issuer JWT 検証で実装する

- Status: Proposed
- Date: 2026-08-06
- Deciders: Project Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/`（`auth_context.py` / `tenant_context.py` / `trusted_saas_runtime.py` / `main.py` / `settings.py` / `models.py`）、`02_Architecture/`、`saas-multitenant` runtime profile

## Context

`ADR-0059` D5 は「active tenant は署名・issuer・audience を検証した claim から解決する」と固定し、`ADR-0020` は「認証プロトコルはアプリに実装せず前段 IAP へ委譲する」と固定した。しかし両者の交点——**実 HTTP リクエストの credential を検証して `VerifiedTenantClaim` を作る層**——だけが未実装で、`saas-multitenant` profile は `settings.py:425` の無条件 `ValueError` で起動を拒否され続けている。`SAAS-TENANT-01` の AC-4/6/7/8/9/10/12/13 はここで止まっている（`issue-SAAS-TENANT-AUTHEDGE-01`）。

### 実装済みの範囲（コード確認結果 2026-08-06）

想定より多くが既に存在する。本 ADR のスコープはその差分だけである。

- `resolve_verified_claim_tenant_context()`（`tenant_context.py:150`）は完成しており、provider の issuer/audience 一致、`tenant_identity_providers` の active、`(identity_provider_id, subject)` の一意性と `user_id` 一致、membership active を全て検証して deny する。unit test 済み（`test_verified_tenant_context.py`）。
- `resolve_trusted_saas_request_session()`（`saas_request_context.py:51`）は identity → tenant → recheck → capability までの request pipeline を実装済みである。
- `routes/docs.py:196` の `_authorize_request()` は `tenant_session_precondition_required(request)` で分岐し、SaaS 経路では既に上記 pipeline を呼ぶ。
- `main.py:73/85/94` の lifespan は `validate_trusted_saas_runtime_preflight()` / `initialize_trusted_saas_runtime()` / `release_trusted_saas_runtime()` を呼んでいる。

### 起票時の前提に対する訂正（本 ADR で確定させる事実）

1. **`install_trusted_saas_runtime()` の呼び出し元はゼロだが、`initialize_trusted_saas_runtime()` は `main.py` から呼ばれている。** 欠けているのは「adapter bundle を install する側」だけである。`install_` も `_trusted_saas_runtime_preflight()` も `_kj_atlas_runtime_started` が立った後の実行を拒否するため、install は lifespan の中ではなく `app = FastAPI(...)` 直後の module scope で行う必要がある。issue AC-3 はこの粒度で読む。
2. **`TRUSTED_PROXIES` は実装されていない。** `03_Implement/backend/src` に該当コードは無く、`ADR-0020` §3-1 は未達のままである。`resolve_identity_context()` は proxy allowlist なしで `X-Forwarded-User` 等を読む。したがって「trusted proxy 判定は既存」という前提で SaaS を設計できない。これは single-tenant profile 側にも残る別 gap であり、本 ADR では解決せず follow-up として明示する。
3. **Level 2 の mock IdP は JWT を発行していない。** `tests/level2/mock_idp.py` の `/oidc/token` は claim の JSON dict を返すだけで、署名も JWKS endpoint も無く、`mock_sp.py` はそれを平文 header へ写している。`ADR-0020` §6 の harness は header mapping fixture であり、暗号的な IdP スタブではない。SaaS の e2e にはこの harness を骨格として **実署名と JWKS を足す** 必要がある。
4. **`identity_providers` / `tenant_identity_providers` に trust material が無い。** 現在の列は `identity_providers(id, issuer, audience, lifecycle_state, created_at, updated_at)` と `tenant_identity_providers(tenant_id, identity_provider_id, lifecycle_state, created_at, updated_at)` だけである。protocol 判別列も JWKS URI も署名鍵も外部 org 参照も無い。「protocol 非依存で既に存在する」は「protocol が名指しされていない」という意味であって、どの選択肢を採っても migration は必要である。
5. **`TenantContextResolver.resolve()` は `request` も claim も受け取らない**（`def resolve(self, *, db, user_id)`）。検証済み claim を identity 層から tenant 層へ渡す経路が型として存在しない。これは issue の AC に書かれていない未認識の blocker である。

### なぜ今この判断が必要か

`ADR-0047` の再起票基準 R-1〜R-4 に該当する新規論点ではなく、`ADR-0059` の Implementation gate が follow-up として明示的に残した決定の消化である。同時に AGENTS.md §6 の「安全境界変更」「複数の合理的選択肢が残る」に該当する。判断を先送りするコストは既に顕在化しており、issue によれば同一文言の実装チェックポイントが 30 箇所以上反復されている。

## Decision

### D1: multi-IdP は upstream identity broker で吸収し、アプリは single-issuer を前提としない multi-issuer 検証として実装する

`saas-multitenant` の本番構成は、**顧客ごとの IdP（Okta / Azure AD / SAML IdP 等）を 1 つの identity broker が集約し、kj-atlas へは単一 issuer・単一 audience の JWT と tenant 識別 claim を渡す**構成を前提とする。broker 製品は固定しない（Keycloak の identity brokering、Authentik、WorkOS、Auth0 Organizations 等はいずれもこの形をとる）。

これは `ADR-0020` の再決定ではない。`ADR-0020` が禁じたのは「アプリが SP/RP として redirect / callback / assertion 交換を行うこと」であり、broker モデルはその責務境界をそのまま保つ。tenant ごとの IdP 差異は broker の設定で吸収され、アプリのコード分岐にはならない——`ADR-0020` §3-3 の「provider 差異は設定で吸収し実装分岐を増やさない」と同じ原則の延長である。

ただしアプリ側実装は **issuer をハードコードせず、検証済み issuer から `identity_providers` 行を引く multi-issuer 構造**とする。理由は、(a) `resolve_verified_claim_tenant_context()` が既に `identity_provider_id + issuer + audience` を受け取る形になっており single-issuer 前提の方がむしろ不自然、(b) broker 移行・並行運用・staging 併存で複数 issuer は現実に発生する、(c) 将来 tenant 自己申告 IdP を許す場合に検証コードではなく **trust material の登録経路だけ**が変わる、の 3 点である。

v1 では `identity_providers` 行の作成を Platform Control Plane（`ADR-0059` D9）の運用者操作に限定し、tenant admin からの self-service 登録は提供しない。**アプリが信頼する鍵の出所を tenant 編集可能なデータにしない**ことが、この段階で守るべき唯一の線である。

### D2: `saas-multitenant` では JWT 検証を必須とし、平文 header mode を起動時に拒否する

- `ADR-0020` §3-2 の 2 mode のうち、SaaS profile が受理するのは `jwt_header` だけとする。`header` mode は設定検証で拒否する。
- 理由: single-tenant では header mode の信頼境界は「1 組織の proxy を正しく置いたか」であり組織内リスクに閉じるが、shared SaaS では trusted proxy 設定の 1 箇所のミス・header 除去漏れが即座に全 tenant 越境になる。かつ訂正 2 のとおり `TRUSTED_PROXIES` は未実装で、network 配置と `KJ_ATLAS_API_KEY` 以外の境界が無い。
- `TenantContext.resolved_by = "verified_claim"` と `VerifiedTenantClaim` の docstring が要求する「署名・issuer・audience 検証済み」を満たすには暗号的証拠が要る。header mode ではこの契約を型どおりに満たせない。
- `trusted_host_mapping`（tenant 別 subdomain 等）は `TenantResolutionMethod` に予約されているが、本 ADR では実装対象外とする。

### D3: protocol 範囲は OIDC/JWT のみとし、SAML はアプリに実装しない

- v1 のアプリ側検証は JWS 署名付き JWT bearer だけを対象とする。
- SAML tenant は broker が SAML→OIDC へ変換して収容する。D1 を採る限り、**SAML 対応は運用構成で達成でき、アプリに XML 署名検証（`xmlsec1` native 依存、canonicalization、XML Signature Wrapping 対策）を持ち込む必要が無い**。「OIDC 先行か SAML 同時か」という issue の問いは、broker モデルを採った時点で「アプリ側は OIDC のみで SAML 顧客も収容できる」に解消される。これは D1 を選ぶ積極的な理由でもある。
- ただし migration では `identity_providers.protocol` 判別列を今回同時に追加し、既定値 `oidc`、受理値は v1 では `{oidc}` のみ、未知値は fail-closed で拒否する。将来 SAML 行を足すときに破壊的 migration を起こさないための最小の先回りであり、実装は増やさない。

### D4: JWT 検証は PyJWT + cryptography、JWKS 取得は既存の trusted HTTP 規約に従う

- 検証ライブラリは **PyJWT（+ `cryptography`）** を推奨する。`decode()` が `algorithms=` を必須引数として要求し、`audience=` / `issuer=` が第一級であるため、algorithm confusion と検証漏れが API の形で防がれる。用途に対して scope が最も狭い。
- `python-jose` は不採用とする。3.3.0（2021）から 3.4.0（2025）まで実質的な release が無く、CVE-2024-33663（algorithm confusion）/ CVE-2024-33664（JWE 展開 DoS）の修正まで数か月〜年単位を要した。solo OSS が security 応答をこの latency の依存に預けるべきではない。
- `Authlib` は保守されているが、必要なのは「検証 1 関数」であるのに OAuth1/2 + OIDC の client と **server** を含む framework 全体を抱えることになる。`ADR-0020` の「protocol 実装責務をアプリへ持ち込まない」に逆行する。同著者の `joserfc`（JOSE に絞った後継）は PyJWT の代替として許容範囲とする。
- **`PyJWKClient` の内蔵 fetcher は使わない。** `urllib.request` で直接取得するため、`settings._validate_trusted_http_endpoint()` の endpoint 正準化・loopback 以外 HTTPS 必須・credential/query/fragment 禁止、および `ADR-0062` が固定した「明示した外部連携は完全設定を起動条件にする」規約の外側に出る。JWKS 取得は既存の `httpx` ベース外部 HTTP と同じ規約（endpoint 検証・timeout 上限・秘密値非出力）で実装し、取得した JWK set から鍵を組み立てて PyJWT へ渡す。
- 検証時の固定制約: algorithm allowlist は `RS256,ES256` 既定の設定値とし、`none` と HMAC 系は常に拒否。token header の `jku` / `x5u` / 埋め込み鍵は一切参照しない。`kid` は取得済み JWK set 内でのみ解決する。clock skew の許容は 60 秒固定（設定にしない）。
- 採用確定前に、PyJWT と `cryptography` の最新 advisory / release 状況を再確認する。

### D5: JWKS のキャッシュと鍵ローテーション

`identity_provider_id` 単位でキャッシュし、次を既定とする（いずれも設定可能、上限あり）。

- 正常 TTL 600 秒。
- 未知 `kid` を受けた場合、cooldown 60 秒を満たしていれば 1 回だけ強制 refresh する。provider ごとに in-flight refresh は 1 本に制限する。cooldown を置かないと、ランダムな `kid` を送るだけで IdP の JWKS endpoint への増幅攻撃になる。
- refresh 失敗時は最後の既知 JWK set を **最大 1800 秒まで**返す。超過したら「検証不能」として扱う（D6）。無期限の stale 継続はしない。
- stale 供給は「どの署名鍵を受理するか」だけに作用し、`exp` / `iss` / `aud` / `alg` / membership の検証は一切緩めない。IdP は通常ローテーション時に新旧鍵を重ねて公開するため、1800 秒は IdP 側の overlap を超えない範囲の有界なリスクである。
- 署名検証を省略する fallback、token 由来の鍵の採用は、いかなる状況でも行わない。

### D6: identity 検証が不能なときは deny 固定とし、fail-safe mode 設定を設けない

`access_control_fail_safe_mode` に `read_only` があるのは、PDP 障害時でも **principal と tenant は判っていて capability だけが不明**だからである。identity 層にはこの縮退が成立しない。検証できないとき不明なのは「誰か」と「どの tenant か」そのものであり、あらゆる fallback は「未検証の principal をどこかの tenant のデータへ入れる」に等しい。`ADR-0059` D5 も tenant 不明時は read を含めて deny としている。

したがって identity 検証には fail-safe mode 設定を **作らない**。「設定可能にする」は、正しい運用が一つも選ばないはずの構成を作ることであり、`ADR-0062` が扱った「安全に見える縮退設定そのものが危険」と同じ失敗である。可用性の予算は D5 の有界 stale window に一本化して支出する。

応答の分離（内部監査には正確な理由 code を残し、外部には最小限を返す）:

- header 欠落 / 署名不正 / `iss` `aud` `alg` `kid` 不一致 / 期限切れ → `401`。どの検証で落ちたかを外部へ区別させない単一の opaque code とする。
- JWKS が max-stale を超えて取得不能 → `503` + 専用 code。access を与えない点は同じだが、運用者が「攻撃」と「外部障害」を区別できるようにする。tenant の存在を示唆する情報は含めない。
- 検証成功・subject 未登録 → `403` `identity_not_provisioned`（既存）。SaaS profile は `allow_jit_provisioning=false` が必須（`TrustedSaasRuntimePolicy.validate()`）なので、**auth edge は `users` / `user_identities` を一切書かない**。provisioning は `POST /admin/provision/users` と Tenant Admin `membership.provision` の責務である。
- 検証成功・membership 不成立 → `403` `tenant_context_untrusted`（既存）。

### D7: 検証済み claim は `ResolvedIdentity` に載せて明示的に受け渡す

訂正 5 の型の穴を、次の最小変更で塞ぐ。

- `ResolvedIdentity` に `verified_tenant_claim: VerifiedTenantClaim | None = None` を追加する（既定値ありのため single-tenant 経路は無変更）。
- `TenantContextResolver.resolve()` を `resolve(self, *, db, user_id, claim: VerifiedTenantClaim | None = None)` へ広げる。呼び出し元は `saas_request_context.py:106` と `routes/docs.py:215` の 2 箇所だけである。
- `contextvars` などの暗黙の request-scope 側チャネルは採らない。安全境界のデータ経路は型で追えることを優先する。
- `resolve_verified_claim_tenant_context()` は **変更しない**。既存の unit test の証明価値をそのまま残す。

### D8: tenant claim は tenant の「要求」であって権限ではない

- token の tenant claim は「どの tenant として振る舞いたいか」の表明にすぎず、権限の根拠は常に DB 側の `tenant_identity_providers` + `user_identities` + `tenant_memberships` である。これは既に `resolve_verified_claim_tenant_context()` が実装している性質であり、broker 共有 issuer 構成でも越境が成立しないことの根拠になる。
- claim が運ぶのは kj-atlas 内部 ID ではなく **外部 organization 参照**とする。`tenant_identity_providers` に `external_tenant_ref` 列を追加し、`unique(identity_provider_id, external_tenant_ref)` を張って `tenants.id` へ写す。理由は、(a) 運用者に IdP 設定へ kj-atlas の内部 ID を書かせない、(b) `ADR-0059` D5/D10 の「`tenants.id` は opaque・外部へ出さない」を保つ、(c) 共有 broker では `tenant_identity_providers` 行が単なる N:1 の飾りになってしまうところに実データを持たせられる、の 3 点である。
- tenant claim が無い token は deny する。membership が 1 件だけなら推定する、という縮退は入れない。`resolved_by="verified_claim"` は「検証済み証拠から解決した」を意味しなければならず、複数 membership 利用者の tenant 切替は `ADR-0061` の tenant session と `select_active_tenant_context()` が既に扱う別経路である。

### D9: 実装スコープと起動拒否の解除条件

**いま作る**（この順で 1 本の変更として実行可能な粒度にしてある）:

1. migration: `identity_providers` に `protocol` / `jwks_uri`、`tenant_identity_providers` に `external_tenant_ref` を追加する。`jwks_uri` は書き込み時に `_validate_trusted_http_endpoint()` 相当で検証する。
2. JWKS key store（D4/D5）。
3. `SaasIdentityContextResolver` の具象実装（JWT 検証 → subject 照合 → 書き込みなし → `ResolvedIdentity` + claim を返す）。
4. `TenantContextResolver` の具象実装（claim を受けて既存 `resolve_verified_claim_tenant_context()` を呼ぶだけ）。
5. D7 の型変更と 2 箇所の呼び出し元更新。
6. `main.py` の module scope で profile が `saas-multitenant` のときだけ bundle を組んで `install_trusted_saas_runtime()` する。`settings.py:425` の無条件 `ValueError` は**削除ではなく差し替え**——既存の `TrustedSaasRuntimePolicy.validate()` に auth edge 側の必須設定（mode、tenant claim 名、algorithm allowlist、有効な `identity_providers` 行の存在）を加えた fail-closed 検証にする。
7. Level 2 mock IdP に RS256 実署名と `/jwks.json` を足す。鍵は `ADR-0020` §7 のとおり起動時動的生成とし、平文コミットしない。
8. tenant A/B・同一 docId の HTTP レベル negative matrix e2e。AC-4 を resolver 単体ではなくリクエスト経由で証明する。

**いま作らない**: アプリ内 SAML、tenant self-service の IdP 登録 API/UI、SCIM、broker 製品の同梱・選定、`trusted_host_mapping` 経路、複数 broker の同時運用手順。

**「実顧客がまだ居ない」ことの意味**: 決定を先送りする理由にはならない——先送りのコストは既に 8 件の AC 停止と反復チェックポイントとして支払われている。一方で、顧客が居て初めて価値が出るもの（self-service onboarding、SAML のアプリ内実装、複数 broker、課金連動）は明確に defer してよい。上の 8 項目が 1 本の変更に収まらない規模へ膨らむなら、それは日程の問題ではなく設計が間違っている合図として扱う。起動拒否は 8 が通るまで維持し、その後も削除せず条件を絞る形で残す。

## Alternatives considered

1. **tenant ごとに IAP/gateway インスタンスを立てる（issue 想定の A の素直な読み）**: アプリは最も単純になるが、tenant 追加が infra 作業になり、SaaS の単位経済が壊れる。solo OSS が運用手順として要求できる現実味が無い。broker モデルは同じ app 側単純性を、gateway を増やさずに得られる。
2. **tenant が自分の IdP を登録し、アプリが request ごとに JWKS を取りに行く（B）**: 最終形としては妥当だが、v1 で採ると「アプリが信頼する鍵の出所」が tenant 編集可能データになり、tenant 供給 URL への outbound（SSRF 面）、per-tenant の可用性依存、cache poisoning が同時に載る。D1 は検証コードを multi-issuer で作るため、trust material の登録経路を差し替えるだけで後から B へ到達できる。**順序の問題であって排他ではない**と判断した。
3. **`header` mode を SaaS でも許し、`TRUSTED_PROXIES` を実装して境界とする**: 暗号的証拠なしに `resolved_by="verified_claim"` を名乗ることになり `ADR-0059` D5 と整合しない。CIDR 設定 1 行のミスが全 tenant 越境になる点も shared SaaS では受け入れられない。ただし `TRUSTED_PROXIES` 自体は single-tenant profile の未達 gap として別途必要である。
4. **アプリ内に SAML SP を実装して OIDC と同時提供**: `xmlsec1` native 依存と XML 署名検証の攻撃面を、broker で代替できるのに抱え込むことになる。`ADR-0020` §2-A で一度否決した構図の再現。
5. **identity 層にも `fail_safe_mode` 設定を置く**: 「誰か不明でも通す」設定は正しい運用が選ばない。存在すること自体が誤設定の入口になる（`ADR-0062` の教訓）。
6. **`contextvars` で claim を運ぶ**: 型変更を避けられるが、安全境界のデータ経路が暗黙になり、async での取り違えを静的に検出できない。

## Consequences

- `saas-multitenant` の運用者は identity broker の設置・維持を負う。kj-atlas はその選定・同梱を行わない。
- SAML 顧客はアプリのコード変更なしに収容できる。protocol 差異の吸収点が broker に一元化される。
- 新規 runtime 依存が 2 つ増える（PyJWT、`cryptography`）。現在 backend は JWT ライブラリを一切持っていない。
- migration が 1 本増える（`identity_providers` 2 列、`tenant_identity_providers` 1 列）。
- `TenantContextResolver` protocol の署名が変わる。呼び出し元は 2 箇所で、single-tenant 挙動は既定値により無変更。
- `resolve_verified_claim_tenant_context()` と既存の unit test は無変更のまま流用され、AC-4 の証明が resolver 単体から HTTP 経由へ拡張される。
- IdP/JWKS 障害時、SaaS deployment は 1800 秒の猶予の後に全面停止する。可用性より機密性を優先する `ADR-0059` の帰結を identity 層へも適用したことになる。
- `TRUSTED_PROXIES` 未実装は本 ADR では解消されない。single-tenant profile 向けの独立した gap として残る。

## Non-goals

- `ADR-0020` の「アプリは OIDC/SAML の handshake を実装しない」原則の変更。本 ADR は bearer token の検証だけを扱い、redirect / callback / logout / step-up は前段の責務のまま維持する。
- broker 製品の選定・推奨・同梱。
- tenant による IdP 自己登録、SCIM、deprovisioning 自動化。
- `saas-multitenant` の起動拒否の解除そのもの（解除は `SAAS-TENANT-01` 側で D9-8 の達成を確認してから判断する）。
- single-tenant profile の認証挙動の変更。

## Open questions for the maintainer

本 ADR が承認を求めている論点は次の 4 つである。ここが redirect されれば D2 以降は組み替えになる。

1. **D1 の broker 前提を SaaS 運用の必須要件として運用者へ課してよいか。** 課さないなら選択肢 2（tenant 登録型 multi-IdP）を v1 から実装することになり、規模は数倍になる。
2. **D3 のとおり SAML をアプリに実装しないと確定してよいか。** `ADR-0020` のタイトルは SAML を含んでおり、ここは明示的な範囲縮小である。
3. **D4 の PyJWT 採用**（`Authlib` / `joserfc` ではなく）。broker モデルを採る限り必要なのは検証のみ、という前提に依存する。
4. **D6 の「identity 層に fail-safe 設定を作らない」**。IdP 障害が全 tenant 停止に直結する運用リスクを受け入れる決定であり、D5 の 1800 秒という数値もここで承認対象になる。

## Traceability

- Implementation: `01_Plans/issues/issue-SAAS-TENANT-AUTHEDGE-01-no-concrete-trusted-auth-edge-implementation.md`
- Implementation gate 親: `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Derived-from: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`
- Related: `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`（認証責務境界・Mock SP/IdP profile）
- Related: `01_Plans/adr/ADR-0061-saas-active-tenant-session-concurrency.md`（tenant session と切替の再認可）
- Related: `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`（外部 HTTP 連携の完全設定要求）
- Related governance: `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`, `01_Plans/adr/ADR-0047-design-decision-adr-saturation-and-execution-first.md`
- Runtime contract: `02_Architecture/runtime_parameter_registry.md`（新規 `KJ_ATLAS_*` キーは実装時に登録する）
- Schema contract: `02_Architecture/schemas.md`
- API contract: `02_Architecture/api.md`
- Security boundary: `THREAT_MODEL.md`, `04_Documentation/security.md`
