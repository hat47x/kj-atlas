# Data Model Operations — Stream D formation history (2026-05)

Status: Informative history

Source document: [`02_Architecture/data_model_operations_overview.html`](../data_model_operations_overview.html)

Source anchors: former §1.2, §1.3, §8〜§13

Covered period: 2026-05-19〜2026-05-20

Snapshot / source revision: `1367740d8d03cf53bc0ad1eb09ffc45684ff51e1`（DOC-ARCH-02 inventory baseline）

Retention reason: `DocumentV2` support level、CRUD境界、migration整合を形成したStream Dの実行・検証経緯を、現行運用契約と誤認されない形で保持する。

Current normative anchors:

- [Support level](../data_model_operations_overview.html#support-boundary-classes)
- [CRUDサポート表](../data_model_operations_overview.html#crud-support-table)
- [DocumentV1フィールド支援レベル](../data_model_operations_overview.html#documentv1-field-support)
- [更新ルール](../data_model_operations_overview.html#update-rules)
- [Schema versioning](../schemas.md#61-document-versioning--support-level運用ルールdata-contract-01固定)

この文書は形成履歴であり、現在のsupport level、version、endpoint、運用責任を上書きしない。

## Former §1.2 Stream D運用注記（Read→Plan→Execute→Verify）

- DATA系Issue更新時は、`Status / Priority / Dependencies / Related ADR` のRead同期を同一セッションで実施する。
- CRUD境界・サポートレベル・運用責務の3観点が揃わない場合は、実装ではなく契約整理を優先する。
- Verifyが3回超過しても収束しない場合、または前提契約が崩壊した場合は `Stop` とする。

## Former §1.3 Stream D fixed execution scope（2026-05-20）

- 本Streamで編集・監査する対象は `DATA-MODEL-OPS-01` / `DATA-CONTRACT-01` / `DATA-MAINT-01` に限定する。
- アプリケーションコード（frontend/backend/deploy）への変更は行わず、schemaと運用境界文書の整合維持のみを実施する。
- Verifyは docs-check（差分整合・語彙一致・責務境界一致）を正本とし、実装テストの成否を完了条件に含めない。

## Former §8 Stream D fail-safe stop criteria

次のいずれかを満たす場合、実装へ進まず契約整備を優先する（Stop）。

1. **後方互換ルール不明瞭**: `Document.version` の上げ条件、version gate、非互換定義のいずれかが曖昧。
2. **support level未定義**: 新規データ領域に `L1/L1.5/L2/L2.5/L3/L0` が割り当てられていない。
3. **運用責務衝突**: Platform operator / Security officer / Support / Developer の責務分離が矛盾。

当時のProceed条件は、上記3点が`schemas.md`と元文書で同時に満たされることだった。

## Former §9 Stream D phase verification log (2026-05-19)

- Phase 1 Contract drift抽出: `DATA-CONTRACT-01` のドリフト観点（schema/api/frontend/backend）を再照合し、`DocumentV2` は version gate 先行で維持。
- Phase 2 Support level定義: CRUD表・フィールド支援表・issue ACで `L1/L1.5/L2/L2.5/L3/L0` を同一語彙に統一。
- Phase 3 CRUD境界更新: 「型がある = 運用CRUDあり」誤読を防ぐ注記を維持し、個別CRUD非対応行を明示。
- Phase 4 Admin maintenance/recovery境界更新: Platform operator / Security officer / Support / Developer の責務分離と `DATA-MAINT-01` 参照を固定。
- Phase 5 Verify（相互矛盾ゼロ）: `schemas.md`・`schemas_review_attribution.md`・元文書で support level と version gate の矛盾がないことを確認。

## Former §10 Stream D execution checkpoint (2026-05-19)

### Context

Model Opsの観点では、`DocumentV2`の契約固定と運用CRUD境界を同時に管理しないと、保守責務が曖昧化する。

### Decision at the time

- 元文書のCRUD境界表を運用責務の正本とし、`schemas.md`は型契約正本として役割を分離したまま同期する。
- Platform operator / Security officer / Support / Developerの責務分離に変更がある場合は、`DATA-MAINT-01`の受入条件更新を先行必須とする。

### Consequences recorded at the time

- Stream DのVerifyは「後方互換・support level・責務分離」の3軸で再現可能となった。
- Data Contract変更が運用手順へ波及する際の引き渡し先が明確になった。

## Former §11 DATA-CONTRACT-01 execution record (2026-05-19)

### Context

- `DocumentV2`は型契約が拡張される一方、MVP CRUD境界の誤読により「個別CRUDあり」と解釈されるドリフトが残っていた。
- contract testのfixture識別子が文書間で固定されておらず、下流が実装進捗に依存した判定を行う余地があった。

### Decision at the time

- mock schema versionを`mock-2026-05-19-dv2`で固定し、契約検証・handoffの識別子としてのみ使用する。
- CRUD境界は元文書の§4/§4.1を正本とし、`L2/L2.5`は保存往復を保証するが個別CRUDを保証しないと明文化する。
- review attribution参照IDは生ID/IdP識別子を禁止し、`user:<users.id>`正規化移行方針を継続する。

### Consequences recorded at the time

- runtime version (`1|2`) とmock schema versionを分離できた。
- 型契約と運用CRUDの責務を分離し、reviewer/owner参照のPII混入リスクを抑えた。

## Former §12 Schema/Migration consistency check (2026-05-20 / Stream D)

### Phase 1 Read

- `schemas.md`のAUTH-SCHEMA-01 / Decision Log契約と、Alembic revision `20260314_0005`までを照合した。
- 物理テーブル境界（`documents` / `users` / `user_identities` / `merge_decision_logs`）は一致し、追加migrationが必要な差分は検出しなかった。

### Phase 2 Plan

- 互換あり: 読取経路へ影響しないindex追加、大文字小文字非依存の一意制約強化（既存重複がない場合）。
- 互換なし: 既存列の削除・必須化・意味変更、`Document.version`を据え置いた破壊的変更。
- 提案AC: revision対応表、互換判定軸、主要テーブル/制約のcontract test。
- 提案DoD: `alembic upgrade head`成功、head一意、schema/運用文書/migration実体の矛盾ゼロ。

### Phase 3/4 Execute + Verify

- 元文書と`schemas.md`にmigration対応表と互換分類を追記した。
- 契約差分がなかったため新規migrationは追加しなかった。
- Alembic実行、head確認、テーブル存在確認で一致を再検証した。

## Former §13 Stream B ops-boundary sync (2026-05-20)

### Context

`DocumentV2`の保存往復保証と個別CRUD保証が混同されると、運用責務が衝突する。

### Decision at the time

- CRUD境界は元文書を正本とし、`L1/L1.5/L2/L2.5/L3/L0`を唯一語彙とした。
- backward compatibilityは`schemas.md`のversion gateを参照し、元文書側で独自判定を持たないこととした。
- CE系・A1系の統合ポイントはread-only contractとし、実DB/API依存が未確定の項目は`L2.5`のまま凍結した。

### Consequences recorded at the time

- 「契約固定」と「運用実装」の責務が分離され、docs-checkで再現可能になった。
- 未確定項目はfail-closedで停止できるようになった。

## Verbatim retained source extract

以下は元文書から物理移動した本文の原文である。表現上の`Decision`、`fixed`、`Proceed`は当時の形成記録であり、現行契約を上書きしない。

### Stream D運用注記（Read→Plan→Execute→Verify）

- DATA系Issue更新時は、`Status / Priority / Dependencies / Related ADR` のRead同期を同一セッションで実施する。
- CRUD境界・サポートレベル・運用責務の3観点が揃わない場合は、実装ではなく契約整理を優先する。
- Verifyが3回超過しても収束しない場合、または前提契約が崩壊した場合は `Stop` とする。

### Stream D fixed execution scope（2026-05-20）

- 本Streamで編集・監査する対象は `DATA-MODEL-OPS-01` / `DATA-CONTRACT-01` / `DATA-MAINT-01` に限定する。
- アプリケーションコード（frontend/backend/deploy）への変更は行わず、schemaと運用境界文書の整合維持のみを実施する。
- Verifyは docs-check（差分整合・語彙一致・責務境界一致）を正本とし、実装テストの成否を完了条件に含めない。

### Stream D fail-safe stop criteria

次のいずれかを満たす場合、実装へ進まず契約整備を優先する（Stop）。

1. **後方互換ルール不明瞭**: `Document.version` の上げ条件、version gate、非互換定義のいずれかが曖昧。
2. **support level未定義**: 新規データ領域に `L1/L1.5/L2/L2.5/L3/L0` が割り当てられていない。
3. **運用責務衝突**: Platform operator / Security officer / Support / Developer の責務分離が矛盾。

Proceed条件は、上記3点が `schemas.md` と本書で同時に満たされること。

### Stream D phase verification log (2026-05-19)

- Phase 1 Contract drift抽出: `DATA-CONTRACT-01` のドリフト観点（schema/api/frontend/backend）を再照合し、`DocumentV2` は version gate 先行で維持。
- Phase 2 Support level定義: CRUD表・フィールド支援表・issue ACで `L1/L1.5/L2/L2.5/L3/L0` を同一語彙に統一。
- Phase 3 CRUD境界更新: 「型がある = 運用CRUDあり」誤読を防ぐ注記を維持し、個別CRUD非対応行を明示。
- Phase 4 Admin maintenance/recovery境界更新: Platform operator / Security officer / Support / Developer の責務分離と `DATA-MAINT-01` 参照を固定。
- Phase 5 Verify（相互矛盾ゼロ）: `schemas.md`・`schemas_review_attribution.md`・本書で support level と version gate の矛盾がないことを確認。

### Stream D execution checkpoint (2026-05-19)

#### Context

- Model Ops の観点では、`DocumentV2` の契約固定と運用CRUD境界を同時に管理しないと、保守責務が曖昧化する。

#### Decision

- 本書の CRUD 境界表を運用責務の正本とし、`schemas.md` は型契約正本として役割を分離したまま同期する。
- Platform operator / Security officer / Support / Developer の責務分離に変更がある場合は、`DATA-MAINT-01` の受入条件更新を先行必須とする。

#### Consequences

- Stream D の Verify は「後方互換・support level・責務分離」の3軸で再現可能となり、3回修復上限を超える前に停止判断できる。
- Data Contract変更が運用手順へ波及する際の引き渡し先が明確化される。

### DATA-CONTRACT-01 execution record (2026-05-19)

#### Context

- `DocumentV2` は型契約が拡張される一方、MVP CRUD 境界（L1/L1.5/L2/L2.5/L3/L0）の誤読により「個別CRUDあり」と解釈されるドリフトが残っていた。
- contract test の fixture 識別子が文書間で固定されておらず、下流チームが実装進捗に依存した判定を行う余地があった。

#### Decision

- `DocumentV2` の mock schema version を `mock-2026-05-19-dv2` で固定し、契約検証・handoffの識別子としてのみ使用する。
- CRUD境界は本書4章と4.1章を正本とし、`L2/L2.5` 領域（evidence/review attribution/critique/reproposal等）は「保存往復は保証、個別CRUDは非保証」を明文化する。
- review attribution の参照IDは生ID/IdP識別子を禁止し、`user:<users.id>` 正規化移行方針を継続する。

#### Consequences

- 下流は mock schema version を使って fixture 更新有無を自律判定でき、runtime version (`1|2`) と混同しない。
- Data契約変更時の影響範囲が `schemas.md`（型）と本書（運用CRUD）で分離され、MVP責務境界の監査が容易になる。
- reviewer/owner参照のPII混入リスクを抑えたまま、移行期データの互換方針を維持できる。

### Schema/Migration consistency check (2026-05-20 / Stream D)

#### Phase 1 Read（現状一致確認）

- `schemas.md` の AUTH-SCHEMA-01 / Decision Log 契約と、`alembic/versions` の最新 revision (`20260314_0005`) を照合した。
- 物理テーブル境界（`documents` / `users` / `user_identities` / `merge_decision_logs`）と本書2章の説明は一致し、追加 migration が必要な差分は検出しなかった。

#### Phase 2 Plan（互換分類 + AC/DoD提案）

- 互換あり:
  - index追加のみの変更。
  - 大文字小文字非依存の一意制約強化（既存重複データが無い場合）。
- 互換なし:
  - 既存列の削除・必須化・意味変更。
  - `Document.version` を据え置いた破壊的変更。

提案AC（受入条件）:

1. schema文書に revision 対応表があり、現行 migration と相互参照できる。
2. 互換あり/なしの判定軸が明文化され、非互換変更は version gate 前提と明記される。
3. contract test で `documents/users/user_identities/merge_decision_logs` の存在と主要制約を再現できる。

提案DoD:

1. `alembic upgrade head` が成功する。
2. migration chain が単一路線（head一意）である。
3. schema文書・運用文書・migration実体の3者に矛盾がない。

#### Phase 3/4 Execute + Verify（実施結果）

- schema先行更新: 本書と `schemas.md` に migration 対応表と互換分類を追記。
- migration追随: 新規 migration は不要（契約差分なしのため未追加）。
- 整合検証: Alembic 実行・ヘッド確認・テーブル存在確認で一致を再検証。

### Stream B ops-boundary sync (2026-05-20)

#### Context

- Model Ops では `DocumentV2` の保存往復保証と個別CRUD保証が混同されると、運用責務（Platform operator / Security officer / Support / Developer）が衝突する。

#### Decision

- CRUD境界は本書を正本として維持し、`L1/L1.5/L2/L2.5/L3/L0` を唯一語彙とする。
- `DocumentV2` の backward compatibility 判定は `schemas.md` の version gate を上流正本として参照し、本書側で独自判定を持たない。
- CE系・A1系の統合ポイントは read-only contract として公開し、実DB/API依存が確定していない項目は `Contract-limited (L2.5)` のまま凍結する。

#### Consequences

- Stream間ハンドオフで「契約固定」と「運用実装」の責務が分離され、Phase 4 Verifyを docs-check で再現できる。
- 未確定項目は fail-closed で停止でき、DecisionStatus=Pending のまま実装へ越境するリスクを抑制できる。
