# Issue: SEC-DOC-BOUND-03 ContextQuery.constraintsが無制限の再帰構造を許容し、深いネストで未捕捉例外を招く

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/request_body_safety.py`, `03_Implement/backend/src/kj_atlas_api/models_context.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`, `03_Implement/backend/src/kj_atlas_api/main.py`, 近接テスト、`02_Architecture/api.md`, `02_Architecture/schemas.md`, `THREAT_MODEL.md`
- Related ADR/Spec: `ADR-0039`, `ADR-0047`, `issue-SEC-DOC-BOUND-01-unbounded-document-and-identity-fields.md`, `issue-CE0-contract-freeze.md`, `issue-CE1-context-query-bundle-foundation.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`, `THREAT_MODEL.md`
- Expected verification level: `unit + integration`

## 課題

- 現在の問題:
  - `models_context.py:17` の `ContextQuery.constraints: dict[str, object]` は、深さ・キー数・値サイズのいずれにも制約がない。同モデルの `depth: int = Field(ge=0, le=5)`（1行上）は明示的に範囲制約されているのと対照的。
  - `POST /context/query` と `POST /context/bundle`（`routes/context.py`）はどちらも `payload: object = Body(...)` として生JSONを受け取り、`_validate_payload()` 経由で `ContextQuery.model_validate(payload)` に渡す。検証後、`_canonical_query_hash_payload()`（`models_context.py`）が `query.constraints` を手書きの再帰関数 `_stable_value()` にそのまま渡す。`_stable_value()` は `dict`/`list` を無制限に再帰しており、深さ上限・ノード数上限・例外処理のいずれも持たない。
  - `main.py:113` には `RequestValidationError` 用のハンドラしか登録されておらず、キャッチオール（`except Exception` 相当）のハンドラはリポジトリ内のどこにも存在しない。そのため、深くネストしたJSONボディに起因する未捕捉例外（`RecursionError` 等）は素の500として利用者に返る。
  - **重要な訂正**: 当初の調査では「`_stable_value()` 内の再帰が直接の破綻点」と推定していたが、独立した検証の結果、CPythonの `json.loads`（FastAPI/Starletteがリクエストボディを読む際に内部的に使用）自体が構文的に妥当な深いネストJSONに対して `RecursionError` を送出しうることが分かった。これは `_stable_value()` やPydantic検証に到達する**前**、リクエストボディのパース段階で発生しうる。つまりこの脆弱性クラス（深くネストしたJSONボディ → 未捕捉 `RecursionError` → 素の500）は `constraints` フィールドや `_stable_value()` に固有ではなく、JSONボディを受け取るこのアプリの任意のエンドポイントに及ぶ可能性がある、より広いフレームワークレベルの欠落である可能性が高い。`_stable_value()` だけに深さガードを追加しても、リクエストボディのパース段階で先に例外が発生する経路は塞げない。
  - 検証により、`issue-CE0-contract-freeze.md` 内に見える `constraints: string[]`（フラットな配列）という初期ドラフト表記は、`ContextQuery` に `constraints` フィールド自体が存在しない段階のものであり、より実装に近い `issue-CE1-context-query-bundle-foundation.md` は複数箇所で `constraints: Record<string, unknown>`（実装済みの `dict[str, object]` と同型）を明記している。したがって「フラット配列に戻すべきか」という設計上の緊張関係は当初想定したほど明確ではない。
- 利用者または開発への影響:
  - 深くネストした（構文的には妥当な）JSONボディを送るだけで、`/context/query` または `/context/bundle` を呼び出すクライアントがサーバーを未捕捉例外でクラッシュさせ、クリーンな4xxではなく素の500を受け取る可能性がある。
  - 同種のギャップが他のJSONボディ受け取りエンドポイントにも存在する可能性があり、`constraints` だけを直したのでは解決しない。

## 対応方針

- 採用:
  - backendの `application/json` / `application/*+json` bodyをparser前段の反復的scannerで検査し、構造ネスト64超過を `400 json_nesting_too_deep` で拒否する。`sys.setrecursionlimit` や再帰的な事前parseには依存しない。
  - `ContextQuery.constraints` をJSON互換値、深さ8以下、総ノード数1024以下、canonical UTF-8 64 KiB以下に制限し、違反を `400 invalid_constraints` で拒否する。
  - validation errorからraw input/contextを除き、境界違反は安定したcodeだけを返す。API key認証はbody走査より先に行う。
- 不採用:
  - catch-all例外ハンドラは追加しない。既知の失敗クラスはparser前で4xxにし、未知のprogramming errorまで一律に隠さない。
  - 全JSON bodyのbyte上限は追加しない。浅い巨大値のfield制約は `SEC-DOC-BOUND-01`、公開transportのrate/body上限は各境界で扱う。
  - `ContextQuery`/`ContextBundleResponse` のfield構造、canonicalization、hash入力、schema versionは変更しない。
- ADR判断:
  - field/versionを変更しない局所的な安全境界であり、選択肢と残余リスクを本issueおよび現行正本へ記録できるため、新規ADRは作成しない（`ADR-0039` / `ADR-0047`）。

## 受入条件

- [x] 深くネストしたJSONボディを `/context/query`、`/context/bundle`、他のJSON endpointへ送っても、素の500ではなくサニタイズされた4xxが返る。
- [x] `constraints` 固有のresource boundと、全JSON endpoint共通のparser前安全境界を実装した。
- [x] `ContextQuery`/`ContextBundleResponse` の凍結field契約、hash規則、SafeMode、認証順序を破壊しない。
- [x] 近接テスト、backend回帰、lint、docs-check、diff-checkを実行し、環境起因の未実施範囲を記録した。

## 検証結果

- 近接回帰: `test_request_body_safety.py`, `test_context_bundle_routes.py`, `test_api_key.py` は `27 passed`。
- backend回帰（migration系7ファイルと既知のenv-prefix違反1件を明示除外）: `622 passed, 25 skipped, 1 deselected`。
- 全backend回帰の参考結果: `626 passed, 25 skipped, 16 failed`。失敗15件はWSL環境に `alembic` executableがないため、残る1件は既存 `monkey_adversarial_probes.mjs` の `ONLY/SEED/ACTIONS/VIEWPORT` によるenv-prefix違反で、いずれも本変更外。
- `ruff check .`: pass。
- `01_Plans/docs_check.py`: pass（`active_memos=59`, `tracked_markdown=467`）。
- `git diff --check`（本issue対象ファイル）: pass。

## 補足

- rollbackは `JsonRequestBodySafetyMiddleware` の登録と `ContextQuery` validatorを同時に戻す。片方だけ戻すとparser前またはcanonicalization前の一方に欠落が再発する。
- 残余リスクは浅い巨大JSON全般であり、本issueでは `constraints` の64 KiB上限だけを扱った。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
