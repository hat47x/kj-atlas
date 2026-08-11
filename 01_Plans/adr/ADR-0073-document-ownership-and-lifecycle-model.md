# ADR-0073: 文書の帰属とライフサイクルを定め、成果物側の生涯を主体側と対称にする

- Status: Proposed
- Date: 2026-08-11
- Deciders: Maintainer（本ADRは提案。採択判断は保守者が行う）
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/alembic/versions/`, `02_Architecture/schemas.md`, `02_Architecture/data_model_operations_overview.html`, `02_Architecture/api.md`

## Context

`02_Architecture/post-mvp-business-scope-design-program.html` の第1反復（制御プレーン背骨）を三要素牽制設計法で進めた際、第2反復（作業の器）の前提が現行データ設計の上に載らないことが判明した（`issue-DATA-DOC-LIFECYCLE-01`）。

### 事実: 主体側と成果物側でライフサイクル設計が非対称である

`lifecycle_state` 列は同一性・テナンシーの背骨をなす **5テーブルすべて**に存在する。

| テーブル | 定義位置 |
|---|---|
| `tenants` | `models.py:75` |
| `identity_providers` | `models.py:346` |
| `tenant_identity_providers` | `models.py:378` |
| `tenant_memberships` | `models.py:397` |
| `users` | `models.py:550` |

対して `documents`（`models.py:402-416`）の列は次の5つのみである。

```
tenant_id (複合主キー) / id (複合主キー) / version / updated_at / payload_json
```

**所有者を表す列も、ライフサイクルを表す列も存在しない**（`created_by|owner_user|author_id|lifecycle_state` の全文検索で `documents` にヒット0件）。作成時刻も持たない。

すなわち現行設計は **「主体には生涯があるが、成果物には無い」**。MVP（単一利用者・単一文書）ではこの非対称が表面化しなかったが、業務スコープでは4領域（キャンバス一覧・管理／ユーザ無効化／権限・組織変更／キャンバス無効化）が同時にここで止まる。

なお共有側の `document_access_metadata`（`visibility`: Public / Unlisted / Org / Restricted ＋ `policy_binding_id`）は実装済みである。**「誰に見せるか」は設計済みだが「誰のものか」が未設計**という状態にある。

### この判断が ADR を要する理由

列を足すこと自体は機械的だが、**何を表す列を足すか**が製品判断を伴う。特に所有の単位は、後から変更すると全参照側（一覧API・認可・無効化・組織変更）へ波及するため、実装前に固定する必要がある。`AGENTS.md` §6 の「複数の合理的選択肢が残る場合」に該当する。

## 決定すべき論点

- **D1**: 所有の単位。文書は誰のものか。
- **D2**: ライフサイクル状態の語彙。
- **D3**: 既存文書の移行時の初期値。

## 選択肢

### D1: 所有の単位

| 案 | 内容 | 利点 | 欠点 |
|---|---|---|---|
| **A** | 個人所有（可変の `owner_user_id` 列） | 「自分の文書」が自明。個人利用と地続き | 退職・無効化のたびに付け替えが必須。付け替え漏れが孤児文書を生む。`owner` 変更操作とその認可を新設する必要がある |
| **B** | テナント所有のみ（現行 `tenant_id` で足り、所有者概念を持たない） | 追加列ゼロ。孤児化しない | 「自分の文書」を表現できず、一覧が常に平坦。監査で作成者を追えない |
| **C** | **作成者（不変）＋テナント所有＋管理権はcapability** | 孤児化しない。監査で作成者を追える。「自分の文書」は作成者で表現できる | 「所有者を移す」という直感的操作が無く、管理権はcapability側の話になるため説明が要る |
| **D** | チーム概念を新設し、チーム所有とする | 大組織の実務に最も近い | テナントとチームの二層認可を新設することになり、`ADR-0043` 複雑性予算を大きく超える |

### D2: ライフサイクル状態の語彙

| 案 | 内容 |
|---|---|
| **A** | `active` / `archived` の2状態のみ（削除を持たない） |
| **B** | `active` / `archived` / `trashed` / `purged` の4状態（ゴミ箱と物理削除を持つ） |

### D3: 既存文書の移行時の初期値

| 案 | 内容 |
|---|---|
| **A** | 作成者は `NULL` 許容とし、移行済み文書は「不明」のままにする |
| **B** | テナントの既定管理者を作成者として埋める |

## 推奨（保守者の判断を拘束しない）

**D1=C**、**D2=A**、**D3=A** を推奨する。

### D1=C の三要素整合

| 次元 | 主張 | 他次元への制約 |
|------|------|---------------|
| 業務 | KJ法の実務では「場を作る人」と「成果物の帰属先」が別である。コンサル案件や行政計画では成果物は組織に帰属し、担当者の異動後も残らねばならない | データ: 個人を可変の所有者にすると、異動のたびに付け替えが必要になり、漏れが孤児文書を生む |
| データ | 作成者は**起きた事実**であり不変。帰属は**現在の状態**でありテナントが持つ。両者を1列に混ぜない | 機能: 「所有者変更API」が不要になる。変更されない列に認可は要らない |
| 機能 | 「誰が管理できるか」は既存の `AccessControlAdapter`／capability で判定済みの領域である。所有列を認可の根拠にしない | 業務: 管理権の付け替えは組織変更の一部として membership 側で扱え、文書側を触らずに済む |

### D1=C が「無効化」を横断的性質として正しく扱う

設計プログラム §3 が指摘したとおり、「Xが無効化されたとき依存物はどうなるか」は各設計が自ら答えるべき問いである。D1 の各案はこの問いに対して次の答えを持つ。

| 案 | 利用者が無効化されたとき、その人の文書はどうなるか |
|---|---|
| A（個人所有） | **答えが必要になる**。孤児化するため、移譲先の決定・移譲の認可・移譲漏れの検出を設計せねばならない |
| C（作成者＋テナント所有） | **問いが消える**。文書はもともとテナントに帰属しており、作成者は歴史的事実として残るだけで、参照は壊れない |

**Cは、ユーザ無効化の設計を不要にすることで、要件領域を1つ減らす。** これがCを推奨する最大の理由である。

### D2=A の根拠

`ADR-0033` は「文書削除UIを標準機能にしない」と既に決定している。`trashed` / `purged` は削除の存在を前提とする語彙であり、この既存決定と矛盾する。したがって `active` / `archived` の2状態から始め、削除が実務上必要と判明した時点で別ADRとして扱う。既存5テーブルの `lifecycle_state` と同じ列名・同じ既定値 `active` を用い、語彙の一貫性を保つ。

### D3=A の根拠

既存文書には作成者の記録が存在しない。これを既定管理者で埋めることは、**記録されていない事実を記録されたことにする**ことであり、監査証跡の意味を損なう。`NULL`（不明）のままにするほうが正直である。これは SafeMode の fail-closed 思想（不明なものを既知として扱わない）と同じ判断軸に立つ。

## Non-goals

- チーム／プロジェクト等の中間階層の新設（D1=D を採らない限り不要）。
- 文書の物理削除・ゴミ箱UIの設計（D2=A を採る限り本ADRの対象外。`ADR-0033` の再検討を要する）。
- 共有・公開範囲の設計（`document_access_metadata` が既に担当。本ADRは帰属のみを扱う）。
- 既存の `payload_json` 内部構造（`DocumentV1` 契約）の変更。本ADRは行レベルのメタデータのみを追加する。

## ADR-0047 ゲート判定

`ADR-0047` の再起票基準に照らす。

- **R-2（段階遷移）**: **該当すると考える。** MVP（単一利用者・単一文書）から業務スコープ（複数主体・文書群）への段階遷移そのものが本ADRの契機であり、遷移に伴い既存データ設計が要件を支えられなくなった。
- **R-4（破壊的契約変更）**: 該当しない。全て加算列であり、既存の読み書きを壊さない。
- **R-1 / R-3**: 該当しない。実使用の摩擦ではなく設計時の三要素突き合わせで検出した。

R-2 該当の是非は保守者が確認すること。非該当と判断される場合、本ADRは Rejected とし、`DATA-DOC-LIFECYCLE-01` も第2反復の前提から外す（その場合、第2反復の4領域は設計不能のまま残る）。

## Traceability

- Implementation: `01_Plans/issues/issue-DATA-DOC-LIFECYCLE-01-documents-lack-owner-and-lifecycle.md`
- Derived-from: `02_Architecture/post-mvp-business-scope-design-program.html` §6（欠落の検出）
- Method: `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Related: `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`（D2の制約元）
- Related: `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`（D1=Dを退ける根拠）
- Related: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`（tenant境界の正本）
- Related: `02_Architecture/non-canvas-ui-flow-design.html` §9（「文書アーカイブUI: lifecycle state列なし」の既存記録）
