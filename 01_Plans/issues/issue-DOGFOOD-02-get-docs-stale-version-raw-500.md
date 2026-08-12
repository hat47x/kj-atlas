# Issue: DOGFOOD-02 GET /docs/{id} が旧版文書（version≠1）で素の500を返す（三要素不整合）

- Type: Bug / Process
- Status: Draft
- Source Issue: DOGFOOD-01（ドッグフーディング検証経路の拡張で発見）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `01_Plans/dogfood/`
- Related ADR/Spec: `01_Plans/adr/ADR-0058-document-contract-v1-rebaseline.md`, `02_Architecture/schemas.md`, `03_Implement/backend/scripts/verify_api.sh`
- Expected verification level: `unit` + `docs-check`

## 課題

2026-08-12 に追加された API 検証経路 `verify_api.sh` を実走行したところ、
`GET /docs/{doc_id}` が保存文書の `version` が現行契約（`DocumentV1.version = Literal[1]`）と不一致のときに
**素の HTTP 500** を返した（`sqlite3` 上の旧版サンプル `doc_phase1_canvas`、`version: 2` で再現）。

### 三要素分析

- **機能設計**: GET 読取経路（`routes/docs.py` `get_document`）は `document_payload_adapter.validate_python(payload)` を直接呼び、`ValidationError` が未捕捉で 500 になる。一方 PUT 経路（`put_document`）は `_validate_document_payload_with_a1_contract` を通り、構造化 A1 エラー（422）を返す。**GET と PUT で検証・エラー契約が非対称**。
- **データ設計**: 保存文書の `version` フィールドが契約の `Literal[1]` と不一致（旧構造・未知版）の状態が DB に残り得る。ADR-0058 のデータ設計は「未知版・欠落・旧構造は fail-closed で拒否」を意図しているが、拒否方法が読み手に「サーバーが壊れている」と誤解させる 500 になっている。
- **業務設計**: 導入組織の利用者が旧版/移行途中の文書を開いたとき、「この文書は現在の契約で読み込めません（版不一致）」という構造化された案内で返るべき。500 は利用者の操作を原因と誤認させ、診断を遅らせる。

## 実地確認（2026-08-12、Web経路での増幅）

API経路の 500 は**Web初回起動のブロッカー**に増幅されることを実地確認した。

- frontend は起動時に `DEFAULT_DOCUMENT_ID = "doc_phase1_canvas"`（`App.tsx` L244）を
  `loadDocument(DEFAULT_DOCUMENT_ID, { allowCreateOnNotFound: true })`（`App.tsx` L3740）で自動ロードする。
- `allowCreateOnNotFound` は **404 のみ**を救済する。保存済み `doc_phase1_canvas` が 500（contract外version）を返すと
  404分岐に入らず、`formatLoadDocumentFailure(error)` がエラー状態を表示する。
- 実測（Playwright、backend:8000 + frontend:4173、`kj_atlas.db` に `version:2` の `doc_phase1_canvas` が残る状態）:
  - `GET /packs/index.json` → 200、`GET /api/docs/doc_phase1_canvas` → **500**
  - ステータスメッセージ: 「ドキュメントを読み込めませんでした（HTTP 500: Internal Server Error）…」が表示
  - キャンバスは空（0カード）、「サンプルを開く」ボタンのみが抜け道

→ **初回利用者が Web を開いた瞬間に 500 エラー画面を見る**。fresh DB では 404 → 既定文書自動作成で通るが、
  API 移行・DB 再利用・旧version文書が残る環境では確実に踏む。

### 対応の広がり

- backend の GET/PUT 検証経路の非対称（本issueの主問題）に加え、frontend の起動時デフォルト文書ロードも対象になる。
- 受入条件に「Web 初回起動で 500 エラー画面を出さない」を追加する。

## 期待される改善

- GET 読取経路も PUT と同様に A1 契約検証を通過させ、版不一致は構造化 422（`A1_SCHEMA_VERSION_MISMATCH` 相当）で返す。
- あるいは GET に固有の「契約外版を明示的に拒否」する明示的分岐を設け、500 を一切漏らさない。
- `verify_api.sh` の `/docs/{id}` チェックが「500/503 以外は reachable」の判定に依存しているため、500 が恒久的に消えることを CI で固定する。

## 受入条件

- [ ] `GET /docs/{doc_id}` が、旧版（`version ≠ 1`）文書に対して素の 500 を返さない。
- [ ] 版不一致の応答が構造化された 4xx（A1 契約）として返り、内部スタックトレースが漏れない。
- [ ] `verify_api.sh` が旧版文書を明示的に含む環境でも fail しない（または意図的な期待失敗として文書化される）。
- [ ] **Web 初回起動（デフォルト文書 `doc_phase1_canvas` の自動ロード）が 500 エラー画面にならない**（404 と同様に既知状態として扱うか、構造化エラーを回復可能な形で表示する）。

## 検証計画

- 実行コマンド:
  - backend 起動後: `bash 03_Implement/backend/scripts/verify_api.sh http://127.0.0.1:8000`
  - 再現用 DB 文書（`version: 2`）を投入したうえで `curl -i http://127.0.0.1:8000/docs/doc_phase1_canvas`
- 期待結果: 500 ではなく 422 相当の構造化エラー。ログに pydantic スタックトレースが漏れない。

## 補足

- 再現環境の `kj_atlas.db` は gitignore 対象のローカル DB であり、2026-06-20 時点の `version: 2` サンプルが残っていた。新しい検証経路が「素の500」を検出できたことは、経路追加の効果の実証でもある。
- 根本原因は GET/PUT の検証経路の非対称であり、ADR-0058 の fail-closed 意図自体は正しい。この issue は「拒否方法の非対称」の解消を求める。

## 修正案（proposal-only・L2: 最終判断は人間）

**対象1: backend GET 経路**（`03_Implement/backend/src/kj_atlas_api/routes/docs.py` `get_document` 末尾）

現状:
```python
return document_payload_adapter.validate_python(payload)  # ValidationError → 素の500
```

提案: PUT と同じ A1 契約検証へ通す（`_validate_document_payload_with_a1_contract` は既に PUT で使用）。
```python
return _validate_document_payload_with_a1_contract(payload)  # 版不一致 → 構造化 A1 422
```

これにより GET も PUT と同じ A1 契約（422）を返し、pydantic スタックトレースが 500 から漏れなくなる。

**検証済みの挙動（2026-08-12 確認）**: `version: 2` ペイロードを `_validate_document_payload_with_a1_contract` に通すと
`HTTP 422`・`errorCode=A1_REQUIRED_FIELD_MISSING`・`message="Input should be 1"` を返す（素の 500 ではなくなる）。

**留意点**: errorCode は汎用の `A1_REQUIRED_FIELD_MISSING` になる。これは `version` リテラル不一致が
A1 の `schemaVersion`/`critiqueInputs`/`reviewAttribution` マッピングに該当しないためで、
「版不一致」を明示する専用コードではない。fail-closed・構造化・トレース非漏洩の目的は達成されるが、
errorCode を `A1_SCHEMA_VERSION_MISMATCH` 相当へ寄せる（`version` 不一致を明示的にマッピング）のは任意の改善。

**対象2: frontend 起動時ロードの回復**（`03_Implement/frontend/src/App.tsx` `loadDocument` catch 節）

現状: `allowCreateOnNotFound` は 404 のみ救済。A1 422 は `formatLoadDocumentFailure` でエラー画面になる。

提案: A1 契約エラー（422 / `A1_SCHEMA_VERSION_MISMATCH`）を「文書が現行契約で読めない」既知状態として扱い、
「サンプルを開く」への明示的な回復導線を提示する（404 と同列の分岐を追加するか、専用メッセージ＋既存のサンプル導線）。

**対象3: 検証の固定**

- backend: GET が `version: 2` 文書に対して 422（A1）を返す unit テストを追加。
- `verify_api.sh`: 旧版文書投入環境で `/docs/{id}` が「500でない・構造化4xx」であることを assert（DOGFOOD-06 の異常系ルール適用）。
