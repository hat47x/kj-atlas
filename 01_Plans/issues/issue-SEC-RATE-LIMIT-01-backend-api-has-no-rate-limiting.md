# Issue: SEC-RATE-LIMIT-01 backend APIにrate limitが一切ない（MCP transportとの非対称）

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`
- Related ADR/Spec: `03_Implement/mcp/src/http_server.ts`, `THREAT_MODEL.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: `03_Implement/mcp/src/http_server.ts`はTHREAT_MODEL.mdの記述通り（「全route（metadata含む）に60 req/min/IPのrate limitを適用」）、`express-rate-limit`を使い実際に60 req/min/IPのrate limitを実装している。一方、backend API（`03_Implement/backend/src/kj_atlas_api`）にはrate limit相当の仕組みが一切存在しない（`rate.?limit|slowapi|throttl|Retry-After|429`でrepository全体をgrepしても`pyproject.toml`含め0件）。`main.py`の唯一のmiddlewareは`require_api_key`（静的な共有シークレットheader確認）で、`settings.api_key`が未設定の場合は素通りする。
- 利用者または開発への影響: 特に`POST /admin/provision/users`（`Depends(get_db)`のみで認証依存なし）と、`auth_context.py`内のJIT provisioning（`settings.allow_jit_provisioning`の既定値`True`時、未知のprovider/external_uidヘッダーから新規`UserRow`/`UserIdentityRow`を作成）は、事前認証なしに到達可能かつ状態変更を伴う。`settings.api_key`の既定値は`None`（未設定）であるため、既定構成ではこれらのエンドポイントへのrequest数に上限が一切ない。`POST /session/active-tenant`も同様に未制限。

## 対応方針

- 実施すること: backend APIへrate limitを導入するかどうか、導入する場合どの方式（プロセス内limiter、共有store（Redis等）を用いた分散limiter等）を採るかをMaintainerが判断する。FastAPI/uvicornの実際のデプロイ形態（単一worker/複数worker）によって、プロセス内limiterでは不十分な場合があるため、アーキテクチャ判断を要する。
- 実施しないこと: rate limit実装そのもの。方式選定なしに特定のlibraryを追加することは行わない。

## 受入条件

- [ ] backend APIのrate limit方針（採用する場合の方式、対象エンドポイント）が決定される。
- [ ] 導入する場合、少なくとも`/admin/provision/users`とJIT provisioning経路が対象に含まれる。

## 検証計画

- 実行する確認: 方針決定・実装後、対象エンドポイントへの過剰requestが期待通り制限されることを統合テストで確認する。
- 期待結果: 制限超過時に一貫した応答（例: 429）を返す。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第6ラウンド）で発見。`01_Plans`内の既存rate-limit言及は、ADR-0059や関連research文書内の「将来rate limitを実装する場合はtenantIdをkeyに含める」という前向きな設計メモのみで、「backendにrate limitがない」という現状のギャップ自体はどこにも記録されていなかった。

## 実装記録（2026-08-06）: デプロイ形態を確認し、方式選定の前提を1つ確定

上記「対応方針」が保留していた論点のうち、「FastAPI/uvicornの実際のデプロイ形態（単一worker/複数worker）」は事実確認だけで解決できる部分だったため確認した。方針決定・実装そのものはまだ行っていない。

- `03_Implement/backend/Dockerfile:21`と`03_Implement/deploy/docker-compose.yml:33`の`uvicorn`起動コマンドはいずれも`--workers`未指定（既定値=1）。`gunicorn`は`03_Implement`のプロジェクトコードに存在しない（`grep -rln gunicorn`のヒットは`.venv`内のuvicorn自身の`workers.py`のみで無関係）。Kubernetes等のmanifestも存在しない。つまり**現在の唯一の配布経路は単一プロセス・単一workerのuvicornである**。
- この事実により、「プロセス内limiterでは複数worker間で状態が共有されず不十分」という懸念は、少なくとも現在の配布形態では当てはまらない。プロセス内limiterで正しく機能する。
- 既存の非対称性（MCP側`http_server.ts:32-38`）を直接確認した: `express-rate-limit`をin-memory（既定store、Redis等の外部store未使用）・`windowMs`+`limit: 60`・`app.use(limiter)`で全routeへグローバルに適用している。つまりこのリポジトリには既に「プロセス内・in-memory・全route一括」というrate limit方式の前例が存在し、今回の判断はこれと同種の方式を後追いするか、別の方式を選ぶかという選択になる。
- 上記2点から、backend側も同種の**プロセス内（in-memory）limiter**を採用するのが、新規の外部store依存を持たずMCP側と対称になる自然な選択と考えられる。Python/FastAPI側の対応候補は`slowapi`（`limits`パッケージを基盤とし、Flask-Limiterと同型のAPIをFastAPI/Starlette向けに提供）。`limits`はin-memoryとRedis/Memcached等の外部storeを同じAPIで切替できるため、将来複数worker構成へ移行する場合もstorage backendの差し替えだけで対応でき、今回in-memoryを選んでも将来の選択肢を閉じない。
- **ただし、これは方式（in-process vs 分散）の論点だけを狭めるものであり、以下は依然Maintainer判断のまま残す**: (a) rate limitを導入するかどうかそのもの、(b) 導入する場合の対象エンドポイント範囲（`/admin/provision/users`とJIT provisioning経路は受入条件で最小限として既に指定されているが、`/session/active-tenant`や他の書き込み系routeまで広げるか）、(c) 具体的な閾値（MCP側の60 req/min/IPを踏襲するか、backend APIの実際の利用パターンに応じた別の値にするか）、(d) 既存のE2E/integration test群（短時間に多数requestを送るテストがあれば）への影響評価。これらはbackend APIの全requestパスに新しい挙動（429応答）を追加する変更であり、機械的に決定できる範囲を超える。
- **追記（2026-08-12・検証）**: 本文の「`/admin/provision/users`は認証依存なし」は**部分的に古い**。現行は `require_single_tenant_provisioning_surface`（`routes/admin.py:78`）で**単一テナントモードに限定**され、SaaS ランタイムでは 404（曝露縮小）。ただし単一テナントでは未レート制限のまま。
- **追記2（2026-08-12・JIT provisioning の現行ゲート確認）**: `allow_jit_provisioning` は **既定 True**（`settings.py:388`）で、`auth_context.py:194` のゲートは False 時のみ 403。つまり既定構成では**未知の provider/external_uid ヘッダーからユーザー行を自動作成する状態変更経路が有効で、レート制限なし**。受入条件の「JIT provisioning 経路を対象に含める」は妥当。
