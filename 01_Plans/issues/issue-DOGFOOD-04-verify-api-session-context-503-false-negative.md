# Issue: DOGFOOD-04 verify_api.sh の /session/context チェックが 503 を reachable として見逃す

- Type: Bug / Process
- Status: Done
- Source Issue: DOGFOOD-01（ドッグフーディング検証経路の拡張で発見）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_api.sh`
- Related ADR/Spec: `03_Implement/backend/scripts/verify_api.sh`, `02_Architecture/runtime_parameter_registry.md`（`saas-multitenant`）
- Expected verification level: `docs-check`

## 課題

`verify_api.sh` の `/session/context` チェックは 500 以外をすべて「reachable」と判定する。

```bash
# 4. /session/context — session context (may require auth)
code=$(curl -s -o /dev/null -w '%{http_code}' ... "$BASE_URL/session/context")
check "/session/context reachable (non-500)" "reachable" "$([ "$code" = "500" ] && echo fail || echo reachable)"
```

実走行では `/session/context` が **503**（`tenant_admin_auth_unavailable`）を返したが、スクリプトはこれを PASS と数えた（3 passed, 1 failed の「1」は `/docs/{id}` の 500 のみ）。

### なぜ問題か

- **local-dev（既定）では `/session/context` が常に 503**: `saas_identity_context_resolver` が local-dev では初期化されないため、このエンドポイントは既定 profile で恒常的に 503 を返す。したがってこのチェックは既定 profile では**無内容**（何を確認しても必ず PASS）。
- **saas-multitenant では実障害を隠す**: 将来の `saas-multitenant`（ADR-0063 D9）で JWKS 取得失敗や resolver 例外が起きると 503 になるが、本チェックはそれを「reachable」と見逃す。ヘルス確認として誤検知の温床になる。

### 三要素分析

- **機能設計**: チェックの判定が「route が 500 でない」ことだけを見ており、「サービスとして利用可能か」を見ていない。503（Service Unavailable）は route が存在しても利用不能であることを意味するため、判定基準が目的（可用性確認）とズレている。
- **データ設計**: 503 の応答本文には構造化された `code: "tenant_admin_auth_unavailable"` が含まれるが、スクリプトは `-o /dev/null` で本文を破棄し、code を全く見ない。503 の意味を区別する情報を捨てている。
- **業務設計**: ドッグフーディング検証経路の目的は「各利用経路が実際に使えるか」の確認。既定 profile で恒常的に使えないエンドポイントを「reachable」と報告すると、検証結果の信頼性（特に将来の CI 化や L3 昇格基準への利用）を損なう。

## 期待される改善

- `/session/context` の期待ステータスを profile 依存で明示する:
  - `local-dev`: 503（resolver 未初期化）が**意図通り**であることをコメントと期待値で明示し、5xx 以外の混入を区別する。
  - 実可用性チェックが必要なら、`/healthz` と分離して「service-level チェック」として別途行う。
- 少なくとも 503 を「reachable」ではなく「unavailable」と報告し、`/docs/{id}` のような route 存在チェックとは意味が異なることを出力に明示する。

## 受入条件

- [ ] `verify_api.sh` が `/session/context` の 503 を PASS として数えない（または profile 依存の意図的期待値として文書化する）。
- [ ] 検証出力が 503（unavailable）と 500（crash）と reachable を区別して表示する。
- [ ] local-dev で実行した結果が「実可用性」を過大報告しない。

## 検証計画

- 実行コマンド:
  - `bash 03_Implement/backend/scripts/verify_api.sh http://127.0.0.1:8000`（local-dev、resolver 未初期化）
- 期待結果: `/session/context` が 503 であることが出力に現れ、実可用性として pass 扱いされない。

## 補足

- MCP 検証経路の同種の問題（DOGFOOD-03、isError を JSON として誤解析）と同じく、**2026-08-12 に追加されたばかりの検証経路のエッジ**が CI 未カバーであることが背景。
- 本 issue は検証経路自体の品質改善であり、プロダクトの安全境界変更は含まない。

## 対応記録（2026-08-12）

- `verify_api.sh` の `/session/context` チェックを case 分岐へ変更。
  - 500 → FAIL（crash）
  - 503 → INFO（Service Unavailable。local-dev では SaaS resolver 未初期化のため期待値。reachable として数えない）
  - 2xx/3xx/404 → PASS（reachable）
  - その他 → FAIL（予期しない status）
- 検証: local-dev で実走行し、`/session/context` が INFO（503）として報告され、PASS 扱いされないことを確認。
- これにより saas-multitenant で JWKS 取得失敗などが 503 を返した場合、誤って「reachable」とは報告されなくなる。
- DOGFOOD-06 の受入条件のうち「503/not_found を区別して報告する」を1件充足（DOGFOOD-03 と合わせて）。
