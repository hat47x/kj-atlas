# Issue: OPS-SAAS-SCALE-01 SaaS認証状態がプロセス内保持のため水平スケールできない

- Type: Operations / Security
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Unassigned
- Scope: `03_Implement/backend/src/kj_atlas_api/active_tenant_session.py`, `03_Implement/backend/src/kj_atlas_api/trusted_auth_edge.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, `04_Documentation/operations.md`, `02_Architecture/enterprise_architecture.html`
- Related ADR/Spec: `01_Plans/adr/ADR-0064-saml-oidc-broker-jwt-coordinated-auth-flow.md`（Phase 3-2）, `01_Plans/adr/ADR-0063-saas-multitenant-trusted-auth-edge.md`, `02_Architecture/enterprise_architecture.html`
- Expected verification level: `integration`

## 課題

`saas-multitenant` プロファイルに**実際に配線されている**認証状態保持は、いずれもプロセス内メモリである（`main.py:110-130`）。

```python
if settings.runtime_profile == "saas-multitenant":
    install_trusted_saas_runtime(app, TrustedSaasRuntimeAdapters(
        identity_context_resolver=JwtSaasIdentityContextResolver(jwks_store=JwksStore()),
        tenant_context_resolver=ClaimBasedTenantContextResolver(),
        active_tenant_session_persister=InMemoryActiveTenantSessionPersister(),
    ))
```

| 状態 | 実体 | 複数プロセス時の帰結 |
|---|---|---|
| テナントセッション版数 | `InMemoryActiveTenantSessionPersister._sessions`（dict） | ワーカーをまたぐとセッション不一致 → 409 / 503 が頻発 |
| JWT リプレイ検出 | `trusted_auth_edge._jti_cache`（module global） | **別ワーカーに当てるだけでリプレイが成立** |
| JWKS キャッシュ | `JwksStore._entries` | 機能影響は小（各ワーカーが個別に取得）。ただし IdP への JWKS 取得が worker 数倍になる |

`uvicorn --workers N` や Kubernetes 複数レプリカという、企業・行政案件では標準的な可用性構成が**現状では成立しない**。単一プロセス運用は SPOF となり、通常は許容されない。

### 既存の認識状況

- セッション側は `active_tenant_session.py:178-184` の docstring で自認あり。`ADR-0064` の Phase 3-2 に「`InMemoryActiveTenantSessionPersister` → Redis/DB ベース」として列挙されている。
- **リプレイ検出側には自認がない。** `trusted_auth_edge.py:1-15` の docstring は「jti replay detection with bounded time-based cache」を達成済み特性として宣言しており、プロセス内である旨の記載がない（`SEC-AUTH-REPLAY-01` 制約2）。

つまり ADR-0064 Phase 3 は将来項目として列挙されているが、**SaaS プロファイルは既に起動可能な状態で出荷されており**、列挙と実態の間に運用上のギャップがある。

## 対応方針（実装者向け）

`ADR-0064` Phase 3-2 の実装化。ただし以下を決めてから着手すること。

- **D1: 共有ストアの選択**。Redis / PostgreSQL / その他。既に PostgreSQL は SaaS の必須要件（`TrustedSaasRuntimePolicy.validate()` が `database_backend == "postgresql"` を要求、`trusted_saas_runtime.py:74`）であるため、依存を増やさない選択肢として DB 実装が有力。ただしセッション更新の頻度と TTL 掃除のコストを見積もること。
- **D2: 単一プロセス運用の扱い**。共有ストア未設定時に (a) fail-fast する、(b) インメモリで起動し警告する、(c) 単一プロセス構成として明示的に許容する、のいずれか。`ADR-0062` の fail-fast 方針との整合を検討すること。
- **D3: `_jti_cache` の共有化範囲**。セッションと同じストアに載せるか、別扱いか。`SEC-AUTH-REPLAY-01` の制約3（O(n) 走査）の解消と同時に設計すること。

D1〜D3 が設計判断として重いと判断される場合は、`ADR-0064` の Phase 3 を独立 ADR へ切り出すこと。本issueは実装課題として起票しており、ADR 化の要否は保守者が判断する。

## 受入条件

- [ ] AC-1: 複数ワーカー（最低2）構成で、テナントセッションが維持されることを integration テストで確認する。
- [ ] AC-2: 複数ワーカー構成で、同一 `jti` のトークン再送が**どのワーカーに当たっても**拒否されることを確認する。
- [ ] AC-3: 共有ストア障害時の挙動が定義され、fail-closed（認証拒否）であることをテストで固定する。認証が素通りしないこと。
- [ ] AC-4: 共有ストア未設定での起動時挙動が D2 の決定どおりであることをテストで固定する。
- [ ] AC-5: `04_Documentation/operations.md` に、SaaS の推奨デプロイ構成（プロセス数・共有ストア・障害時挙動）を記載する。
- [ ] AC-6: `trusted_auth_edge.py` の docstring が、共有化後の実際の保証範囲を記述している。
- [ ] AC-7: `ADR-0064` Phase 3-2 の状態を実装済みへ更新する。

## 依存関係

- `01_Plans/issues/issue-SEC-TENANT-SESSION-01-session-version-canonicalization-mismatch.md`（先に解消しておくこと。非正規版数の問題を共有ストアへ持ち込まない）

### 連携（依存ではない）

`SEC-AUTH-REPLAY-01` は本issueの D3（`_jti_cache` の共有化範囲）の決定を待つ側であり、本issueが同issueを待つわけではない。ただし `SEC-AUTH-REPLAY-01` の制約3（O(n) 走査）の解消方針は D3 の設計に影響するため、**D3 を決める前に同issueの分析結果を参照すること**。両者を同一PRで実施してもよい。

## 検証

- `python -m pytest tests/test_active_tenant_session_persister.py tests/test_tenant_session_precondition.py -q`
- `python -m pytest tests/test_saas_e2e_tenant_isolation.py -q`
- 複数ワーカー構成での手動またはCI検証（手順を `04_Documentation/operations.md` へ記録）

## 実装・訂正記録（2026-08-11）

- D1: SaaSで既に必須のPostgreSQLを共有ストアとし、Redis等の追加依存は導入しない。tenant session版数を共有DBへ移した。
- D2: `saas-multitenant`は共有表の起動前queryに失敗した場合にfail-fastする。稼働中もin-memoryへfallbackせずfail-closedする。
- D3訂正: access token `jti`の一回使用化は通常のBearer token再利用を壊すため撤回した。sender-constrained replay防御方式は`AUTH-ONE-TIME-JWT-01`を正本とする。
- AC-1: 独立する2 store instanceのintegration testでsession共有とCAS競合を固定した。AC-2は未達のため本issueをOpenへ戻した。
- AC-3/4: DB例外はauth/session境界で503へ変換され、未migration DBはstartup preflightで拒否される。欠損表testを追加した。
- AC-5〜7: operations、認証architecture、resolver docstring、ADR Phase 3を実際の保証範囲へ同期した。
