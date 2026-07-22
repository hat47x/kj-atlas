# Issue: SEC-DOC-BOUND-03 ContextQuery.constraintsが無制限の再帰構造を許容し、深いネストで未捕捉例外を招く

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_context.py`, `03_Implement/backend/src/kj_atlas_api/context_adapter.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`, `03_Implement/backend/src/kj_atlas_api/main.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-01-unbounded-document-and-identity-fields.md`, `issue-SEC-DOC-BOUND-02-unbounded-list-fields-in-llm-prompts.md`, `issue-CE0-contract-freeze.md`, `issue-CE1-context-query-bundle-foundation.md`
- Expected verification level: `unit`

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

- 実施すること（人間の設計判断が必要。次のいずれか、または組み合わせ）:
  - (a) アプリ全体のリクエストボディ解析に対して、深さ・サイズの安全弁を設ける（例: FastAPI/Starletteのボディ読み取りをラップし、事前にJSON文字列の深さ/長さを軽量にチェックする、または `sys.setrecursionlimit` に依存しない反復的なJSONバリデーションに置き換える）。
  - (b) `main.py` にキャッチオールの例外ハンドラを追加し、未捕捉例外（`RecursionError` を含む）を安全な5xx（詳細を漏らさない）に正規化する。これは本問題を隠すのではなく、同種の未知のクラッシュ経路全般に対する安全網として有効（`issue-SEC-AUDIT-LOG-01` で確立した「例外詳細のサニタイズ」方針とも整合する）。
  - (c) `_stable_value()` 自体にも深さ/ノード数上限を追加し、`constraints` フィールドに `Field` レベルの制約（例: JSON文字列化後の最大バイト数）を設ける。ただしこれは(a)のフレームワークレベルの欠落を塞がない点に注意。
  - 上記のいずれを採用するかは、既存の `AuditEvent.metadata`（`audit.py`、フラットな辞書をキー数・キー長・値長で制約する確立済みパターン）のような、再帰構造に対する確立済みの制約パターンがこのコードベースに存在しないため、設計判断が必要。
- 実施しないこと:
  - `ContextQuery`/`ContextBundleResponse` の凍結されたフィールド構造（`issue-CE0-contract-freeze.md`）自体の変更。

## 受入条件

- [ ] 深くネストしたJSONボディを `/context/query` または `/context/bundle` に送っても、素の500ではなく、クリーンな4xx（または安全にサニタイズされた5xx）が返る。
- [ ] 採用した対応が `constraints` フィールドだけでなく、JSONボディを受け取る他のエンドポイントにも及ぶフレームワークレベルの欠落かどうかを踏まえた範囲になっている。
- [ ] 関連する安全・互換性を損なわない（`ContextQuery`/`ContextBundleResponse` の凍結契約を破壊しない）。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - 深くネストした `constraints`（および可能であれば他のJSONボディエンドポイント）を使った回帰テストを追加し、クリーンなエラー応答（4xxまたはサニタイズされた5xx）を返すことを確認する。
  - `pytest 03_Implement/backend/tests`（対応するテストファイル）
- 期待結果:
  - 深いネスト入力に対してサーバーがクラッシュせず、意図したエラー応答を返す。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この調査は3体の独立検証者のうち2体がセッション利用上限により失敗し、1体のみが完了した（PARTIALLY CONFIRMED判定）。核心となる事実（`constraints` フィールドの制約欠如、`_stable_value()` の未制限再帰、キャッチオールハンドラの不在、SEC-DOC-BOUND-01/02との非重複）はすべてorigin/mainのソースを直接読んで検証済みだが、「深いネストJSONで実際に`RecursionError`が発生する具体的な閾値」は同検証者もPython実行環境が使えず実測できておらず、対応着手前に実測での再現を推奨する。
- ADR化が必要になる条件: フレームワーク全体のリクエストボディ安全弁（上記(a)）を追加する場合、既存の全JSONエンドポイントの挙動に影響しうるため、影響範囲次第では新規ADRでトレードオフを固定する。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
