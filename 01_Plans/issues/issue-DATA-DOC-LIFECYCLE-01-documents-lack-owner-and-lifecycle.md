# Issue: DATA-DOC-LIFECYCLE-01 documentsに所有者とライフサイクルが無く、post-MVP要件4領域が設計できない

- Type: Feature / Data model
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/alembic/versions/`, `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.html`
- Related ADR/Spec: `01_Plans/adr/ADR-0073-document-ownership-and-lifecycle-model.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `02_Architecture/post-mvp-business-scope-design-program.html`
- Expected verification level: `unit`

## 課題

`post-MVP 業務全体設計プログラム`（`02_Architecture/post-mvp-business-scope-design-program.html`）の第1反復で三要素分析を進めた際、**第2反復以降が現行のデータ設計の上に載らない**ことが判明した。

### 現状（コード実読、2026-08-10）

`DocumentRow`（`models.py:402-416`）の列は次の5つのみである。

```
tenant_id  (複合主キー)
id         (複合主キー)
version
updated_at
payload_json
```

- **所有者を表す列が無い**（`created_by` / `owner_user_id` 等。`models.py` 全体を `created_by|owner_user|author_id` で検索してヒット0件）
- **ライフサイクルを表す列が無い**（`lifecycle_state` 列が無い）
- 作成時刻も無い（`updated_at` のみ）

### 非対称

対照的に、**同一性の側は既にライフサイクルを持っている**。`lifecycle_state` 列は `identity_providers` / `tenants` / `tenant_memberships` を含む5テーブルに存在する（`models.py:75, 346, 378, 397, 550`）。

つまり現行データ設計は **「主体には生涯があるが、成果物には無い」** という非対称の状態にある。MVP（単一利用者・単一文書）ではこの非対称が表面化しなかったが、業務全体スコープでは4つの要件領域が同時にここで止まる。

### この欠落が阻む要件領域

| 要件領域 | 現状では設計できないこと |
|---|---|
| キャンバス一覧・管理 | 「自分の文書」で絞り込めない。テナント内が常に平坦な一覧になる |
| ユーザ無効化 | 「その人が所有していた文書をどうするか」が問いとして成立しない。所有が記録されていない |
| 権限変更・組織変更 | 文書をチーム間で移す操作が定義できない。移動元・移動先の帰属概念が無い |
| キャンバス無効化 | archive / trash / purge を表す列が無い |

最後の項目は `non-canvas-ui-flow-design.html` §9 が既に「文書アーカイブUI ─ データ設計: ✗（lifecycle state列なし）」として記録済みであり、本issueはその記録と一致する。本issueはそれを**単独UIの問題ではなく、4領域に共通するデータ次元の欠落**として捉え直したものである。

### 共有側との対比

共有側は `document_access_metadata`（`visibility`: Public / Unlisted / Org / Restricted ＋ `policy_binding_id`）が既に実装済みである。すなわち **「誰に見せるか」は設計済みだが「誰のものか」が未設計** という状態にある。

## 論点（人的判断が必要な理由）

> **2026-08-13: `ADR-0073` は Accepted（D1=C / D2=A / D3=A）。着工可能。**
>
> 採択内容: 作成者（不変）＋テナント所有＋管理権は capability（D1=C）、`active` / `archived` の2状態のみで削除を持たない（D2=A）、既存文書の作成者は `NULL` 許容で「不明」のまま（D3=A）。
>
> **D1=C の帰結として「ユーザ無効化された利用者の文書をどうするか」という要件領域が消滅する**（付け替える対象が無いため問い自体が成立しない）。本issueのスコープからこの領域を外してよい。詳細は `ADR-0073`「採択記録（2026-08-13）」。
>
> なお起票時に4論点としていたうち「作成者と所有者を分けるか」は、ADR-0073 の D1=C（作成者は不変・帰属はテナント・管理権はcapability）を採ると自動的に決まるため、独立の論点から外した。

データ列を足すこと自体は機械的だが、**何を表す列を足すか**は製品判断を伴う。

1. **所有の単位**: 所有者は「個人」か「チーム」か。KJ法の実務ではファシリテーターが場を作るが、成果物は組織に帰属することが多い。個人所有にすると退職時の付け替えが必須になり、組織所有にすると「自分の文書一覧」が別の仕組み（参加者テーブル等）を要する。
2. **作成者と所有者の分離**: 監査上「誰が作ったか」（不変）と「今誰のものか」（可変）は別概念である。両方を持つか、一方に統合するか。
3. **ライフサイクル状態の語彙**: `active` / `archived` / `trashed` / `purged` のどこまでを持つか。`ADR-0033` は「文書削除UIを標準機能にしない」と既に決めており、その決定と整合する状態集合でなければならない。
4. **既存文書の移行**: 現在保存されている文書には所有者が記録されていない。migration時に何を埋めるか（NULL許容か、テナント既定所有者か）。

いずれもコードだけでは決められず、`ADR-0033` の削除方針との整合を要するため、ADR起票が必要になる可能性がある。

## 対応方針

- 実施すること: 上記4論点をMaintainerが判断し、必要に応じてADRを起票する。判断後に列追加・migration・`schemas.md`／`data_model_operations_overview.html` の同期を行う。
- 実施しないこと: 論点の判断を経ずに列を追加すること。特に所有単位（個人／チーム）は後から変更すると全ての参照側に波及するため、先に決める。

## 受入条件

- [ ] 所有の単位（個人／チーム）が決定される。
- [ ] 作成者と所有者を分けるか統合するかが決定される。
- [ ] ライフサイクル状態の語彙が決定され、`ADR-0033` の削除方針と矛盾しないことが確認される。
- [ ] 既存文書のmigration時の初期値が決定される。
- [ ] 決定に基づく列追加・migrationが実装され、`schemas.md` と `data_model_operations_overview.html` が同期される。

## 検証計画

- 実行する確認: 列追加後、`python -m pytest tests/test_docs_roundtrip.py tests/test_data_model_operations_contract.py -q` と migration の upgrade/downgrade 往復。
- 期待結果: 既存文書の読み書きが回帰せず、新列の制約が意図どおり効く。

## 補足

- 発見経緯: post-MVP設計プログラム第1反復（制御プレーン背骨）の三要素分析中に、第2反復（作業の器）の前提を確認した際に判明。業務次元（「自分の文書を管理したい」）とデータ次元（所有者列が無い）の突き合わせで検出した、三要素牽制設計法の適用事例そのものである。
- 本issueは第2反復の起点であり、これが解決するまで「キャンバス一覧・管理」「ユーザ無効化」「権限変更・組織変更」「キャンバス無効化」の設計は着工しない。
