# Issue: SEC-TENANT-SESSION-01 テナントセッション版数の3.1%が自己検証に失敗し、当該利用者が恒久的に503になる

- Type: Bug / Security（可用性）
- Status: Open
- Source Issue: N/A
- Priority: P0
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/tests/test_active_tenant_session_persister.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`, `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`
- Expected verification level: `unit`

## 課題

### 生成器と検証器のアルファベットが一致していない

`active_tenant_session.py:165-167` はセッション版数を生成する。

```python
def _new_session_version() -> str:
    return secrets.token_urlsafe(32)
```

`secrets.token_urlsafe()` は base64url アルファベット（`A-Z a-z 0-9 - _`）を使う。

`active_tenant_session.py:17-19` の検証パターンは**先頭文字を `[A-Za-z0-9]` に限定**している。

```python
_TENANT_SESSION_VERSION_PATTERN = re.compile(
    rf"[A-Za-z0-9][A-Za-z0-9._~-]{{0,{MAX_TENANT_SESSION_VERSION_LENGTH - 1}}}"
)
```

先頭が `-` または `_` になった版数は、自プロジェクトの `canonical_tenant_session_version()` に**拒否される**。

### 実測

```
$ cd 03_Implement/backend && python3 -c "
import secrets
from kj_atlas_api.active_tenant_session import _TENANT_SESSION_VERSION_PATTERN
N=200000; bad=sum(1 for _ in range(N) if _TENANT_SESSION_VERSION_PATTERN.fullmatch(secrets.token_urlsafe(32)) is None)
print(f'{bad}/{N} = {bad/N*100:.2f}%')"
6210/200000 = 3.10%
```

例: `_yG69xXQlHBzlia9DdkYx9Tos1OXi5I_Sg2EAnIzis4`, `-e-RNrpN9s7dXPFS7eUvZVgxiT3soE44m9-DYC3SZMs`

### 単発の失敗では終わらない（恒久化する）

`InMemoryActiveTenantSessionPersister.persist()`（`active_tenant_session.py:213-241`）は、**検証より前に**サーバ側状態を書き換える。

```python
new_version = _new_session_version()
self._sessions[principal_id] = new_version      # ← 先に格納
response.set_cookie(...)                        # ← Cookie も発行済み
return new_version
```

呼び出し元 `persist_active_tenant_selection()`（`131-162`）が戻り値を検証する。

```python
next_version = canonical_tenant_session_version(next_version)   # ← ここで ValueError
...
except Exception:
    logger.warning(...)
    raise _active_tenant_update_unavailable() from None          # → HTTP 503
```

非正規値が `self._sessions[principal_id]` に残るため、**以降のリクエストは毎回** `resolve_active_tenant_session_version()`（`94-114`）→ `canonical_tenant_session_version()` → ValueError → **HTTP 503 `session_context_unavailable`** になる。インメモリ保持のためプロセス再起動まで回復しない。

再現確認:

```
$ python3 -c "
from unittest.mock import MagicMock
from kj_atlas_api.active_tenant_session import InMemoryActiveTenantSessionPersister, canonical_tenant_session_version
p = InMemoryActiveTenantSessionPersister()
p._sessions['user-1'] = '-9-dpSiWxtLta9mJ9ezzpnmur93TsnVJEomRKO2eyLk'
req = MagicMock(); req.cookies = {}
canonical_tenant_session_version(p.current_version(request=req, principal_id='user-1', active_tenant=MagicMock()))"
ValueError: tenant session version is not canonical
```

### 利用者影響

`saas-multitenant` でテナント切替を行うたび **約3.1% の確率で、その利用者が恒久的にサービス利用不能**になる。復旧手段は運用者によるプロセス再起動のみで、利用者側の操作（再ログイン・Cookie削除）では戻らない（サーバ側 dict が汚染されているため）。

### 既存テストの状態

`tests/test_active_tenant_session_persister.py::TestInMemoryActiveTenantSessionPersister::test_persist_returns_new_version` が本欠陥により**確率的に失敗する**。バックエンド全体回帰（2026-08-09 実施、768 passed / 1 failed）で観測された唯一の失敗がこれである。フレーク（環境依存の不安定テスト）ではなく、**実欠陥の確率的顕在化**である。

## 対応方針（実装者向け）

本件は設計判断を伴わない実装欠陥であり、ADR は不要。

修正方向は2つあり、どちらでもよいが**一方に統一**すること。

- **(a) 生成器を検証器に合わせる**: 先頭が必ず英数字になる生成に変える（例: 生成後に先頭文字を検査して再生成、または英数字1文字を前置）。エントロピーを実質的に減らさないこと。
- **(b) 検証器を生成器に合わせる**: 先頭文字クラスに `-` `_` を許可する。ただし当該パターンが Cookie 値・ヘッダ値として安全であることを確認すること（`-`/`_` は RFC 6265 の cookie-octet として問題ない）。

**併せて必須**: `persist()` が「格納・Cookie発行より前に版数を検証する」順序へ直すこと。これを直さないと、将来別の理由で非正規値が生じたときに同じ恒久化が再発する。

## 受入条件

- [ ] AC-1: `_new_session_version()` が生成する値が、`canonical_tenant_session_version()` を**常に**通過する。20万回規模の統計的テストで 0 件失敗を確認する。
- [ ] AC-2: `persist()` は、サーバ側状態の更新および `set_cookie` の**前に**新版数を検証する。検証失敗時は状態を変更せず例外を送出する。
- [ ] AC-3: 非正規値が何らかの理由で格納された場合でも、当該 principal が恒久的に 503 へ固定されない（回復経路があるか、そもそも格納され得ないことをテストで固定する）。
- [ ] AC-4: `test_persist_returns_new_version` が確定的に成功する。
- [ ] AC-5: 生成器または検証器のどちらを変更したかを、`active_tenant_session.py` のコメントに理由付きで記録する。

## 検証

- `python -m pytest tests/test_active_tenant_session_persister.py -q`
- `python -m pytest tests/test_tenant_session_precondition.py tests/test_session_context_routes.py -q`
- backend 全体回帰
