# Issue: SEC-HEADERS-01 本番runtime_profileでも/docs・/redoc・/openapi.jsonが無制限に公開される

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`
- Related ADR/Spec: `THREAT_MODEL.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `main.py:96` の `app = FastAPI(title="kj-atlas API", lifespan=lifespan)` は `docs_url`/`redoc_url`/`openapi_url` を無効化していないため、FastAPI標準の `GET /docs`（Swagger UI）・`GET /redoc`・`GET /openapi.json` が `settings.runtime_profile` に関わらず常に有効。
  - `THREAT_MODEL.md` §7 は、標準の `docker-compose.yml` デプロイでは `KJ_ATLAS_API_KEY` が既定で必須ではなく、同梱SPAは `X-API-Key` を送らないことを明記している。つまりこの既定構成では、`/docs`・`/redoc`・`/openapi.json` はAPIキー相当の保護を実質的に期待できない状態で到達可能。
  - `/docs`・`/redoc` はCDN（`cdn.jsdelivr.net`）からJSをロードするHTMLページであり、このバックエンドが生成する唯一のHTMLレスポンス。`/openapi.json` は全ルート・全ペイロード形状のスキーマダンプであり、偵察（recon）価値がある。
- 利用者または開発への影響:
  - 本番相当のデプロイでも、これらのエンドポイントを無効化する設定経路が存在しない。

## 対応方針

- 実施すること（人間の設計判断が必要。次のいずれか、または組み合わせ）:
  - (a) `settings.runtime_profile`（`local-dev`/`evaluation`/`enterprise-production`/`saas-multitenant`）に応じて `docs_url`/`redoc_url`/`openapi_url` を `None` にする（本番相当プロファイルでは無効化）。
  - (b) `/docs`・`/redoc` に対して、CDNを許可リストに含めた実効的な `Content-Security-Policy` を用意するか、swagger-ui/redocのJSをvendoring/self-hostして `script-src 'self'` を強制できるようにする。
  - どちらを採るか（あるいは両方）は、開発体験とデプロイ運用のトレードオフであり製品判断が必要。
- 実施しないこと:
  - `/docs` 系エンドポイント自体の機能変更（Swagger UIの見た目やAPI仕様生成ロジック）。

## 受入条件

- [ ] 採用した方針に応じて、本番相当の `runtime_profile` では `/docs`・`/redoc`・`/openapi.json` への到達性、または読み込むスクリプトの信頼境界が明示的に制御される。
- [ ] 関連する安全・互換性を損なわない（開発時の利便性を過度に損なわない）。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - 採用した方針に応じたintegrationテスト（例: `enterprise-production`/`saas-multitenant` プロファイルで `/docs` が404またはCSPヘッダ付きで返ることを確認）。
- 期待結果:
  - 意図した保護がruntime_profileごとに正しく適用される。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見はround 27の「CORS/セキュリティヘッダー」調査から得られた。同調査で見つかった「X-Content-Type-Options/X-Frame-Options が全レスポンスに欠けている」問題は、既存テストとの矛盾がなく機械的に修正済み（同PRの `main.py` の `add_security_headers` ミドルウェア）。本issueは、それとは別の「/docs系エンドポイントの本番露出」という、製品判断が必要な部分のみを切り出したもの。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
