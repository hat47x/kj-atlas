# Issue: SEC-AUTH-REPLAY-01 JWTリプレイ防御が宣言どおりに機能しない（jti任意・プロセス内・毎回O(n)）

- Type: Security
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py`, `03_Implement/backend/tests/test_trusted_auth_edge.py`, `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`, `01_Plans/adr/ADR-0074-server-owned-saas-auth-session.md`（Proposed）, `01_Plans/issues/issue-AUTH-ONE-TIME-JWT-01-request-token-supply-contract.md`
- Expected verification level: `unit`

## 課題

`trusted_auth_edge.py:1-15` の module docstring は、達成済みのセキュリティ特性として宣言している。

> - jti replay detection with bounded time-based cache.

実装（`trusted_auth_edge.py:51-78`, `413-420`）には3つの制約があり、いずれも docstring に記載がない。

### 制約1: `jti` を持たないトークンは検査を素通りする

`trusted_auth_edge.py:413-420`:

```python
jti = verified.get("jti")
if isinstance(jti, str) and not _jti_cache.check_and_record(jti):
    ...raise token_replayed
```

`jti` が無ければ条件が偽になり、**リプレイ検査は一切行われない**。`jwt.decode()` の `require` リスト（`218-226`）は `exp / iss / aud / sub / iat` のみで `jti` を含まないため、`jti` を発行しない IdP のトークンは**リプレイ防御ゼロ**で通る。防御の有無が外部 IdP の実装依存になっている。

### 制約2: キャッシュがプロセス内に閉じている

`_jti_cache` は `trusted_auth_edge.py:78` のモジュールグローバルである。

```python
_jti_cache = _JtiCache()
```

`uvicorn --workers N` や Kubernetes 複数レプリカでは**ワーカーごとに独立**する。攻撃者は同じトークンを繰り返し送るだけで、いずれ別ワーカーに当たりリプレイが成立する。N ワーカー構成ではリプレイ成功確率が実質 `(N-1)/N`。

`InMemoryActiveTenantSessionPersister` 側は docstring で「Production upgrade path」を自認しているが（`active_tenant_session.py:178-184`）、**jti キャッシュ側にはその記載がない**。

### 制約3: 認証1回ごとに全件走査（性能・DoS）

`trusted_auth_edge.py:58-74`:

```python
with self._lock:
    expired = [k for k, ts in self._seen.items() if now - ts > _JTI_CACHE_TTL_SECONDS]
    for k in expired:
        del self._seen[k]
    ...
    if len(self._seen) >= _JTI_CACHE_MAX_ENTRIES:
        oldest = min(self._seen.items(), key=lambda x: x[1])[0]   # ← さらに O(n)
```

上限 `_JTI_CACHE_MAX_ENTRIES = 100_000`（`41行`）。**認証のたびにロック内で最大10万件を走査**し、満杯時は `min()` でもう一度全走査して1件だけ退避する。TTL 3660秒（`39行`）なので、毎秒30リクエスト程度で上限へ達する。ロック直列化と相まって、認証スループットの断崖およびDoS増幅要因になる。

## 付随: 到達不能な診断ログ（同一ファイル）

`trusted_auth_edge.py:400-406`:

```python
if provider is None:
    raise JwtIdentityError(status_code=401, code="unknown_provider")
if provider is None:                              # ← 到達不能
    logger.info("auth edge: unknown provider issuer=%s", issuer)
    raise JwtIdentityError(status_code=401, code="unknown_provider")
```

**ログを出す側が死んでいる。** 未登録 issuer からの認証試行という運用上重要な兆候（設定ミスまたは攻撃）が記録されない。本issueで併せて修正する。

## 対応方針（実装者向け）

制約1・3 と付随項目は実装欠陥として直せる。制約2 は設計判断を含むため、`OPS-SAAS-SCALE-01` と整合させること。

- **制約1**: `jti` を必須にするか（`require` へ追加）、`jti` 無しトークンを別途どう扱うかを決める。必須化は IdP 側要件になるため、`04_Documentation/` の IdP 要件へ明記が要る。互換のため「`jti` 無しは警告付きで許容」を選ぶ場合、その旨を docstring と運用文書へ明記し、**「リプレイ防御あり」と読める記述を修正する**こと。
- **制約2**: `OPS-SAAS-SCALE-01` の共有ストア決定に合わせる。単独で解決しようとしないこと。
- **制約3**: 全件走査を廃し、期限順の構造（`collections.OrderedDict` の先頭からの期限切れ除去、またはヒープ）へ置き換える。1回の認証あたり償却 O(1) にすること。
- **付随**: 重複した `if provider is None` を1つに統合し、ログを到達可能にする。ログに含めるのは `issuer` までとし、`subject` を INFO で出す既存箇所（`320-323`, `336-339`, `428-431`）と併せて PII 方針との整合を確認する。

## 受入条件

- [x] AC-1: `jti`を持たない通常Bearer tokenを許可し、code、docstring、運用文書を一致させた。
- [x] AC-2: 誤ったone-time access-token方式と`_JtiCache`自体を削除したため、O(n) cache経路は存在しない。強いreplay防御の性能要件は採用方式のissueへ移した。
- [x] AC-3: `trusted_auth_edge.py`のdocstringを、Bearer再利用は期限に従いsender-constrained replay防御は別protocolであるという実保証へ訂正した。
- [x] AC-4: 未登録issuerをINFOで記録する分岐を到達可能にした。
- [x] AC-5: auth edge logはprovider/issuerまでに限定し、tenant ref、subject、user ID、生`jti`を出さない。
- [x] AC-6: 同じ有効Bearer tokenの連続利用、異なる`jti`、`jti`欠損を回帰testで固定した。

## 後続課題（依存ではない）

- 強いsender-constrained replay防御の方式判断と実装は`AUTH-ONE-TIME-JWT-01`および`ADR-0074`を正本とする。本issueは「存在していた不正確なone-time jti実装とO(n) cacheの撤去」を完了範囲とし、BFF/DPoPが未実装であることを隠さない。

## 検証

- `python -m pytest tests/test_trusted_auth_edge.py -q`
- `python -m pytest tests/test_saas_oauth_login_e2e.py tests/test_saml_broker_jwt_coordinated_flow.py -q`
- `python -m pytest tests/ -q`（backend 全体回帰）

## 訂正記録（2026-08-11）

- process-local `_JtiCache`とO(n)走査は廃止したが、access token `jti`のunique insertによる一回使用化も通常のBearer token契約を壊すため撤回した。
- `jti`はRFC 7519どおり任意とし、同じ有効Bearer tokenを連続要求へ使用できる回帰testを追加した。
- 強いreplay防御はaccess token `jti`だけでは成立しない。DPoP/BFF/短命Bearer継続の方式判断は`AUTH-ONE-TIME-JWT-01`を正本とするため、本issueをOpenへ戻した。
- unknown providerのlogを到達可能にし、tenant ref、subject、user ID、生`jti`をauth-edge logへ出さない形に統一した。
- module docstring、operations、認証architectureを現行Bearer方式の保証範囲へ同期した。

## 完了確認（2026-08-11）

- 現コードに`_JtiCache`、`_jti_cache`、`token_replayed`経路が存在しないことを再確認した。
- `TestBearerTokenJtiHandling`が同一tokenの連続利用と`jti`任意契約を直接検査する。旧issueの6 ACはすべて現在のコード／test／文書で充足し、未決の強いreplay防御は別issueへ一意に移管済みのためDoneとする。
