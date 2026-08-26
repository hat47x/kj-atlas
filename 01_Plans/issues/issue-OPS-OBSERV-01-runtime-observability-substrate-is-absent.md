# Issue: OPS-OBSERV-01 全ての運用手順が「ログを見る」で終わるが、そのログに情報が無い

- Type: Operations
- Status: In Progress
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/observability.py`（新規）, `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/frontend/Dockerfile`, `03_Implement/deploy/docker-compose.yml`, `04_Documentation/operations.md`, `04_Documentation/diagnostics.md`, `03_Implement/backend/README.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0053-support-diagnostics-bundle.md`, `01_Plans/adr/ADR-0050-llm-provider-observability-and-contract-fidelity.md`, `04_Documentation/security.md`（ログのPII方針）
- Expected verification level: `integration`

## 課題

`04_Documentation/` の運用文書は、この規模のプロジェクトとしては例外的に整備されている。7製品分の backup/isolated-restore 手順、障害分類5種、診断バンドル契約（`ADR-0053`）、切り分け順序まで揃っている。**問題は文書ではなく、文書が前提にしている実行時基盤が存在しないことにある。** `operations.md` も `diagnostics.md` も `SUPPORT.md` も、最終的に「`docker compose logs` を見る」「`/api/healthz` を叩く」へ収束するが、その両方が実質的に空である。

### 事実1: `extra={...}` で渡したログ情報は全て捨てられている

バックエンドにログ設定が一切存在しない（`basicConfig` / `dictConfig` / ログ設定ファイル / `--log-config` のいずれも無し。`KJ_ATLAS_LOG_LEVEL` も未定義）。`logging.Formatter` の既定フォーマット文字列は `extra` のキーを描画しないため、**`extra` に載せた構造化情報は出力に現れない**。

```python
# routes/ai.py:92
logger.info("llm_generate", extra=metadata)   # 実際の出力: llm_generate
```

同じ形が8箇所にある（`audit.py:310,333,352`、`routes/context.py:72`、`routes/docs.py:594,614`、`routes/ai_relations.py:135`、`routes/ai.py:92`）。最も影響が大きいのは監査ディスパッチャ自身の失敗警告で、`tenantId` / `docId` / `queueLength` / `error` を `extra` に載せているため、**「audit event send failed; keep fail-open」という一文だけが出力され、どのテナントの何が失われたのか分からない**。

なお全32箇所の `logger.*` のうち内訳は warning 22 / info 9 / debug 1 で、**`error` / `exception` / `critical` はゼロ**。管理者は `ERROR` でgrepできない。

`03_Implement/backend/README.md:146-153` は `/ai/*` が `provider` / `model_id` / `trace_id` 等を「構造化ログへ記録します」と書いているが、**現状の出荷物では事実ではない**。

### 事実2: 相関IDが存在しない

`main.py` が登録するミドルウェアは3つ（body safety / api key / security headers）で、いずれもリクエスト識別子を発行・伝播しない。`X-Request-Id` も `traceparent` も無い。`x-trace-id` は**受信専用**で、生成もログ出力もエコーもされず、frontend は送信しない（`client.ts` に該当経路なし）。したがってブラウザ起点の監査イベントは常に `traceId: null` になる。

結果として、利用者が「14:32に開けなかった」と報告したとき、**画面にもレスポンスボディにもログにも突き合わせるIDが無い**。管理者に残るのは uvicorn のアクセスログ（method / path / status のみ。テナントも主体も含まない）と時刻の目視照合だけである。

`ADR-0053` の診断バンドルは設計としては良いが、**サーバ側の識別子を一切含まない**ため、サーバ側の何とも結合できない。さらに唯一の識別フィールドである `app.revision` は、`KJ_ATLAS_APP_REVISION` が `frontend/Dockerfile` の ARG にも `docker-compose.yml` にも渡されていないため、**標準Compose構成では常に `"unknown"`** になる（`vite.config.ts` の `envPrefix` は通っているので、配線2行の欠落）。

### 事実3: `/healthz` は定数を返す

```python
# main.py:214-216
@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}
```

DB ping も `alembic_version` 照合も provider 到達確認もしない。にもかかわらずこれは `docker-compose.yml:36` で `web` の起動ゲートに使われ、`operations.md:84` / `diagnostics.md:49` / `SUPPORT.md:39` が最初に叩けと指示する唯一のAPI確認手段である。**DBを失ったバックエンドが `{"status":"ok"}` を返す。** `/readyz` / `/livez` / `/version` はいずれも存在しない。

依存関係の実検証は起動時にのみ、致命例外として行われる（`_assert_linear_migration_history` 他）。しかもこれは Alembic のスクリプトディレクトリだけを見ており、**DBの `alembic_version` を読まない**。スキーマが古いままのDBに対して正常起動し、最初のクエリで落ちる。

### 事実4: メトリクスとトレースが皆無

Prometheus / OpenTelemetry / statsd / `/metrics` のいずれも存在しない（リポジトリ全体をgrepして確認済み。lockfile中の `@opentelemetry/api` は推移的なoptional peerで未import）。リクエスト数・レイテンシ・エラー率・DBプール状態・LLM呼び出し回数/コストのいずれも観測できない。監視・アラート・SLO・オンコールに言及するADRもissueも**リポジトリ全体で0件**。

したがって障害の検知経路は**利用者からの申告のみ**であり、「影響範囲はどこまでか」「復旧したか」に答える手段が無い。`operations.md` の「小規模運用での判断」節が「個人運用では Maintainer が状況判断と復旧操作を兼ねてよい」と明示している通り、これは小規模前提としては一貫した設計だが、**複数テナント並行運用や規模拡大の瞬間に成立しなくなる**。

## この issue が他の軸の前提になっていること

本件は単独の運用改善ではなく、**複数の拡張軸が共通に依存する土台**である。

| 依存する軸 | 本件が無い場合に成立しないこと |
|---|---|
| 複数テナント並行運用 | エラーがどのテナント由来か判別できない（テナントIDが描画されるのは `document_access_resource.py:161-167` の1モジュールのみ） |
| 規模の大小を問わない運用 | 容量計画の入力が存在しない。スケールアウト判断の基準を作れない |
| システム管理者の管理容易性 | 全 runbook の終端が「ログを見る」であり、その先が空 |
| 業務フローの拡大 | 利用者が実際に何をしているか観測できず、業務フロー設計の入力が経験則のみになる |

## 対応方針

- 実施すること（優先順）:
  1. **ログ設定を出荷する。** `dictConfig` によるJSON formatter と `KJ_ATLAS_LOG_LEVEL` を追加する。これだけで既存8箇所の `extra` ペイロード（`tenantId` / `docId` / `eventType` / `queueLength` / LLM `trace_id`）が**コード変更なしで有効になる**。既に計算して捨てている情報なので、費用対効果が最も高い。`backend/README.md:146-153` の記述も同時に真になる。
  2. **リクエストIDミドルウェアを追加する。** 受信時に生成（inbound `x-trace-id` があれば尊重）、`contextvars` フィルタでログレコードへ注入、`X-Request-Id` としてエコー、全エラーボディに含める。frontend の `ApiError` に保持させ、エラー表示と診断バンドルの許可リストへ追加する。**サーバ生成の不透明IDであり利用者コンテンツを含まないため `ADR-0053` の境界に抵触しない。**
  3. **`/healthz` を正直にし、`/readyz` を追加する。** `/healthz` は liveness のみと文書化し、`/readyz` で `SELECT 1` と `alembic_version` × `ScriptDirectory.get_heads()` の照合を行う。事実3のスキーマ齟齬もこれで塞がる。
  4. **`KJ_ATLAS_APP_REVISION` を配線し、`/version` を追加する。** Dockerfile に ARG/ENV 2行、compose に build-arg 1行、route 1本。診断バンドルが匿名から特定可能になる。
  5. **`04_Documentation/` へ観測ガイドを追加する。** ログ行の実例、フィールドの意味、リクエストIDからの追跡手順。
- 実施しないこと:
  1. メトリクス基盤（`/metrics` / Prometheus / OTel）の導入 — 依存が大きく、判断を要する。別issue（下記論点）。
  2. ログのPII方針の変更 — `security.md:188-190` の主体識別子を出さない方針は維持する。ただし下記論点を参照。

## 論点（保守者判断が必要な理由）

- **主体の擬似識別子を持つか。** 現行方針は「ログに主体識別子を出さない」であり妥当だが、代替の擬似識別子を用意していないため、実質「主体の帰属が一切分からない」状態になっている。監査イベントは既に `actorRefHash`（SHA-256 24桁）を使っているので、**同じハッシュをログにも使う**のが一貫する。方針変更ではなく方針の完成として扱える。**2026-08-26決定: 出す**（保守者確認済み）。実装は未着手（下記「残作業」参照）。
- **メトリクス基盤を入れるか、入れるとして何を。** `ADR-0039`（個人OSSの運用規模）との整合が要る。`/metrics` を足すだけなら依存は `prometheus_client` 1つだが、収集・保存・可視化は運用者側の責務になる。**2026-08-26決定: 導入しない。** `ADR-0039`の個人OSS運用規模との整合を優先し、規模拡大・複数テナント並行運用でのスケールアウト判断を非目標として明示する（`04_Documentation/observability.md`へ反映済み）。
- **監査イベントのローカル永続化との関係。** `DATA-MAINT-05` / `DATA-MAINT-06`（両方 Draft）が扱う。本issueの1〜4は監査とは独立に進められるが、5（観測ガイド）は監査の照会経路が決まらないと完成しない。

## 受入条件

- [x] AC-1: JSON formatter と `KJ_ATLAS_LOG_LEVEL` を出荷し、既存の `extra` ペイロードが出力に現れることを固定した（`test_observability.py::test_extra_fields_are_rendered`）。`KJ_ATLAS_LOG_JSON=false` の人間可読書式でも `requestId` を保持することも固定。秘密名のフィールドは `[redacted]` へ落とす。
- [x] AC-2: 全リクエストに `X-Request-Id` を付与し、ログレコードとエラーボディの双方から同じ値が取れることを固定した。inbound `x-trace-id` は安全な形式のみ採用し、不正値は**リクエストを失敗させず**サーバ発行へ倒す。
- [x] AC-3: `/readyz` を追加し、DB到達不能時に 503 かつ接続文字列を反射しないことを固定した。`/healthz` の意味を `operations.md` / `diagnostics.md` / `SUPPORT.md` で liveness のみに訂正し、docstring にも明記した。
- [x] AC-4: `KJ_ATLAS_APP_REVISION` を frontend build ARG と compose build arg へ配線した（`vite.config.ts` の `envPrefix` は既に通っていたため配線のみ）。併せて `GET /version` を追加した。
- [x] AC-5: `03_Implement/backend/README.md` の構造化ログ記述を事実へ合わせた（`extra` 経由であること、以前は出力されていなかったこと、レベル変更方法）。
- [x] AC-6: `04_Documentation/observability.md` を追加し、`operations.md` の「ログを見る」節と `04_Documentation/README.md` の公開一覧から参照した。**まだ観測できないこと**（メトリクス皆無、監査イベントが既定で捨てられること、ローカル保存と照会APIの不在、ログのローテーション未設定）も明記した。※管理面操作の監査は `SEC-ADMIN-PLANE-03`（マージ時点で実装済み・`GET /admin/provision/audit`）に委譲しているため観測ガイドからは「未監査」を削除した。

## 残作業（本issueを In Progress のまま残す理由）

- **メトリクス基盤は導入しないと決定した（2026-08-26）。** `04_Documentation/observability.md`へ非目標として明記済み。本項目はこれで解消した。
- **主体の擬似識別子は決定済み（出す）だが実装は未着手（2026-08-26）。** ログへ`actorRefHash`相当の擬似識別子を出力するコード変更が残っている。
- **監査イベントのローカル永続化との接続は未着手**（`DATA-MAINT-05` / `DATA-MAINT-06`）。観測ガイドの「まだ観測できないこと」節は、これが決まったら更新する。

## 検証

```bash
python -m pytest 03_Implement/backend/tests/ -k "logging or request_id or readyz"
python 01_Plans/docs_check.py
docker compose -f 03_Implement/deploy/docker-compose.yml up --build
curl -i http://127.0.0.1:8000/api/healthz    # X-Request-Id ヘッダの存在
curl -s http://127.0.0.1:8000/api/readyz     # DB停止時に非200
```

## 対応記録（2026-08-14）

項目1〜4（ログ設定・リクエストID・/readyz・/version）と文書5を実装した。メトリクス基盤と主体の擬似識別子は「実施しないこと」のまま（判断待ち）。

- **AC-1（ログ設定）**: `logging_config.py` を新設 — JSON formatter が `extra={...}` ペイロード（`tenantId`/`docId`/`queueLength`/`eventType`/`error`/LLM `trace_id` 等）を描画。`KJ_ATLAS_LOG_LEVEL` を settings へ追加（未知値は INFO へフォールバック）。`main.py` が `configure_logging(settings.log_level)` を module 読込時に呼ぶ。実走行で監査失敗 warning が `requestId` 込みの JSON 1行として出力されることを確認。
- **AC-2（リクエストID）**: `add_request_id` middleware を追加 — inbound `x-trace-id`（安全形式 `^[A-Za-z0-9._:-]{1,128}$`）を尊重、contextvar でログへ注入、全レスポンスへ `X-Request-Id` をエコー、エラーボディ（401/422/409/503/500）へ `requestId` を追加。catch-all 500 ハンドラも追加（例外をログし `requestId` を返す）。実走行でログの `requestId` == レスポンス `X-Request-Id` を確認。
- **AC-3（/readyz）**: `/healthz` は liveness のみと文書化。`/readyz` を新設 — `SELECT 1` と `alembic_version` × `ScriptDirectory.get_heads()` 照合。DB 停止時 503 `database_unavailable`、schema 不一致時 503 `schema_mismatch`（`applied`/`expected` 付き）。`/readyz` は api-key middleware から除外（/healthz と同様）。
- **AC-4（app.revision）**: settings へ `KJ_ATLAS_APP_REVISION`（既定 `unknown`）を追加し `/version` ルートを新設。frontend `Dockerfile` に ARG/ENV、`docker-compose.yml` の web build-arg と api environment に配線。registry へ `KJ_ATLAS_LOG_LEVEL` / `KJ_ATLAS_APP_REVISION` を登録。
- **AC-5（README）**: `03_Implement/backend/README.md` の LLM 監査 metadata 節に JSON 形式・`requestId`・`KJ_ATLAS_LOG_LEVEL` を追記し、実装と一致させた。
- **AC-6（観測ガイド）**: `04_Documentation/observability.md` を新設（ログ形式・相関IDの突き合わせ手順・ヘルスチェックの意味）。operations.md / diagnostics.md / SUPPORT.md の /healthz 記述へ liveness と /readyz の注記を追加し、operations.md の「ログを見る」節から参照。

検証: `tests/test_observability.py`（14 tests: formatter・requestId・readyz の成功/DB停止/schema不一致）、tenant-session exemption へ `/readyz`・`/version` を追加、docs-check pass、実走行で `/healthz` 200・`/readyz` 200・`/version` が `KJ_ATLAS_APP_REVISION` を反映・`X-Request-Id` ヘッダを確認。フル backend suite は実行中。

## 補足

- 発見経緯: ドッグフーディングの方向性レビューで「システム管理者の管理容易性」を軸として調査した際、運用文書の品質と実行時基盤の乖離として検出した。
- **文書が悪いのではない。** `operations.md` の backup/restore 手順は実際に演習テスト（`test_data_maintenance_recovery_exercise.py`）で裏付けられており、この水準の運用文書を持つプロジェクトは多くない。本issueは、その文書が指す先に実体を用意する作業である。
- 三要素牽制の観点: 業務設計（運用手順・障害対応）は詳細に設計されているが、それを支えるデータ設計（何を記録するか）と機能設計（どう観測可能にするか）が追随していない。**業務設計だけが単独で先行した典型例**であり、`ADR-0067` の「三者が揃わない設計判断は着工しない」を運用面へ適用すると、運用手順の整備時点で観測基盤の要求が出ているべきだった。
