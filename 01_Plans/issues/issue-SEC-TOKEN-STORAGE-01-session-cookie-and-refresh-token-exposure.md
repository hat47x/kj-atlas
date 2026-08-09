# Issue: SEC-TOKEN-STORAGE-01 セッションCookieにSecure欠落、refresh tokenをsessionStorageへ保持

- Type: Security
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/frontend/src/session/token_store.ts`, `03_Implement/frontend/src/session/oauth_callback.ts`, `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`, `THREAT_MODEL.md`, `04_Documentation/security.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`, `THREAT_MODEL.md`
- Expected verification level: `unit`

## 課題1: セッションCookieに `Secure` 属性がない

`active_tenant_session.py:234-240`:

```python
response.set_cookie(
    key=self._COOKIE_KEY,
    value=new_version,
    httponly=True,
    samesite="strict",
    max_age=3600,
)
```

`httponly` と `samesite=strict` は設定されているが、**`secure=True` と `path` が無い**。HTTPS 必須の企業・行政環境では、`Secure` 欠落は平文送出の余地を残すため指摘対象になる。`path` 未指定は同一ホスト上の別アプリへの送出範囲を広げる。

`local-dev`（HTTP）との両立が必要なため、profile 依存で `secure` を切り替える実装が要る。

## 課題2: refresh token を `sessionStorage` に保持している

`03_Implement/frontend/src/session/token_store.ts:19-21`:

```typescript
sessionStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
if (...) {
  sessionStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
}
```

`sessionStorage` は同一オリジンの任意の JavaScript から読める。XSS が1件成立すれば、**長期資格情報である refresh token が奪取される**。アクセストークン（短命）の `sessionStorage` 保持は議論の余地があるが、refresh token は通常許容されない。

### ADR で採択された方針との乖離

`ADR-0064` の Alternatives considered #2 はこう記録している。

> **フロントエンドが JWT を直接保持しない**: セッション cookie のみで運用する方式。SPA の API 呼び出しに JWT が必要なため、フロントエンドが JWT を**メモリに保持**することは許容する。HttpOnly cookie との二重管理は複雑性を増すため不採用。

採択されたのは「**メモリ**に保持」である。実装は `sessionStorage`（永続ストレージ）であり、かつ ADR が言及していない **refresh token まで**保存している。**採択済み決定と実装の乖離**であり、いずれかを正へ揃える必要がある。

## 対応方針（実装者向け）

### 課題1

- `secure=True` を profile 依存で設定する。`local-dev` / テスト以外では常に有効にすること。既存の profile 判定（`resolve_tenant_session_bootstrap_mode` または `settings.runtime_profile`）を用いる。
- `path` を明示する。
- Cookie 属性を検証する unit テストを追加する。

### 課題2

以下のいずれかを選ぶ。**ADR-0064 の記述と実装を必ず一致させること**（実装を変える／ADR を改訂する、のどちらでもよいが、乖離を残さない）。

- **(a) ADR どおりメモリ保持へ戻す**: アクセストークンを JS 変数（モジュールスコープ）に保持し、リロード時は再認証。refresh token はブラウザへ渡さない。
- **(b) refresh token を httpOnly cookie へ移す**: refresh は Cookie、access は メモリ。ADR の「二重管理は複雑」という不採用理由の再評価が要る。
- **(c) refresh token を発行しない**: broker 側でセッション維持し、SPA は都度 broker へリダイレクト。

いずれを選んでも、`ADR-0064` の Alternatives / Decision を改訂して実態と一致させること。

## 受入条件

- [ ] AC-1: セッション Cookie が `Secure` と `path` を持ち、`local-dev` 以外で `Secure` が必ず有効であることを unit テストで固定する。
- [ ] AC-2: トークン保存方式が決定され、実装と `ADR-0064` の記述が一致している。
- [ ] AC-3: refresh token が（採択方式に応じて）JS から読めない、または発行されないことをテストで固定する。
- [ ] AC-4: `THREAT_MODEL.md` に XSS 時のトークン奪取リスクと緩和策を記載する。
- [ ] AC-5: ログアウト時にトークン・Cookie が確実に破棄されることを確認する。

## 検証

- `python -m pytest tests/test_active_tenant_session_persister.py -q`
- frontend: `npx vitest run src/session/` および `npx tsc --noEmit -p .`
- `python -m pytest tests/test_saas_oauth_login_e2e.py -q`
