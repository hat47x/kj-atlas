# Canonicalization（公開概要）

> DOC-OPS-05 Classification: **Move internal**
> Audience: 外部利用者（概要参照のみ）
> Goal: canonicalization の公開境界を明示し、内部正本への導線を提供する。
> Non-goal: 詳細運用手順・内部レビュー手順・実装契約の公開。
> Public boundary: 本書は概要のみを公開し、詳細設計/運用は内部文書へ移設する。
> Outcome: 読者が「公開範囲」と「正本参照先」を誤解なく判断できる。
> Related: `02_Architecture/schemas.md`, `02_Architecture/architecture.md`, `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`

本ページは公開向けの**最小概要**です。canonicalization の詳細手順は内部正本で管理します。

## 公開する最小説明

- canonicalization は、類似カードを代表カードへ束ねるための概念です。
- AI は候補提案のみを行い、確定は人間レビューで実施します。
- SafeMode/レビュー境界（未レビューの自動確定禁止）を緩和しません。

## Go/No-Go gate（公開判定）

公開「Go」は次を満たす場合のみ:

1. Audience / Goal / Non-goal / Public boundary / Outcome / Related が明示されている。
2. AI提案の自動確定を許可しない旨が明記されている。
3. 詳細運用は内部文書へ誘導され、公開文書へ混在していない。

いずれか未充足の場合は「No-Go」として公開更新を停止します。

## 詳細参照先（内部正本）

- 設計整合: `02_Architecture/schemas.md`
- 全体境界: `02_Architecture/architecture.md`
- トラッキング: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`


## DOC-OPS-05 実行記録（Phase 1〜5）

### Phase 1 Read

- Latest Read: 2026-04-13
- Audience / Goal / Public boundary / Related を確認し、公開境界を再確認。

### Phase 2 Plan

- Latest Read: 2026-04-13
- 本文は docs-only の範囲で更新し、仕様正本（00〜02）を上書きしない方針を固定。

### Phase 3 Execute

- Latest Read: 2026-04-13
- DOC-OPS-05 classification に沿って本文の公開メタと導線を整備。

### Phase 4 Verify

- Latest Read: 2026-04-13
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md`
- `git diff --check`

### Phase 5 Proceed

- Latest Read: 2026-04-13
- 状態: **Ready**
- 次アクション: 内部正本への参照stub化を維持し、詳細運用情報は 02_Architecture 側で管理する。


## Stream F docs-only execution cycle（DOC-OPS-05）

1. **Read**: 対象文書と関連正本（00〜02）を再読し、公開境界を確認する。
2. **Plan**: AC/DoD を先に定義する。不足時はドラフトを提示し、合意後に実行へ進む。
3. **Execute**: 文書本文を更新し、Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
4. **Verify**: リンク・語彙・固定値（必要時 D1〜D4）を確認し、`git diff --check` で体裁崩れを検査する。
5. **Proceed**: Ready/Hold/Needs-decision を記録し、次Issueへ引き継ぐ。

### Fail-safe

- 参照仕様未確定、または競合検知時は作業を停止する。
- 語彙ドリフトが解消不能な場合は作業を停止する。
- Verify の自己修復は最大3回まで。3回超過時は Hold 化してエスカレーションする。

## DOC-OPS-05 追加実行記録（2026-04-16 / Target 05-01..05）

### Phase 1 Read（再Read）
- 本書と関連Issueを再Readし、公開境界とdocs-onlyスコープを確認。

### Phase 2 Plan（再Read）
- 5Phase（Read→Plan→Execute→Verify→Proceed）で進行し、対象外文書へは非接触とする。

### Phase 3 Execute（再Read）
- 本書の既存分類・公開境界メタを維持しつつ、05-01..05セットの実行記録を追記。

### Phase 4 Verify（再Read）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md 01_Plans/documentation_quality.md`
- `git diff --check`
- 修復は最大3回まで。3回超過は停止（Hold）。

### Phase 5 Proceed（再Read）
- 判定: **Ready**
- 次アクション: 同一セット内Issue本文とScope本文の整合を維持して進行。

## DOC-OPS-05 Stream G 前半フェーズ実行記録（2026-04-16）

- Classification確認: **Move internal**（再判定なし）
- フェイルセーフ固定: 用語ドリフト検知・固定値不一致検知・自己修復3回超過で停止（Hold）

### Phase 1: Read（対象ファイル再読）
- 本ファイルを再読し、Scope / Audience / Goal / Public boundary / Related の整合を確認。

### Phase 2: Plan（対象ファイル再読）
- 本ファイルを再読したうえで、docs-only の変更範囲と受入条件を固定。

### Phase 3: Execute（対象ファイル再読）
- 本ファイルを再読したうえで、分類方針（Move internal / Improve external）を維持して更新。

### Phase 4: Verify（docs-check、対象ファイル再読）
- 本ファイルを再読したうえで docs-check を実施。
- 推奨確認: `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go" 04_Documentation/canonicalization.md`
- 体裁確認: `git diff --check`

### Phase 5: Proceed（対象ファイル再読）
- 本ファイルを再読したうえで状態を判定し、`Ready / Hold / Needs-decision` を記録。
- 判定: **Ready**（現時点で保留なし）。

## Stream G serial checkpoint（2026-04-16）

- Classification: **Move internal**（公開は概要stubを維持）。
- docs-only gate: 本書は公開境界の説明に限定し、内部運用/契約の詳細は `02_Architecture/*` と issue トラッキングへ委譲する。
- Stop conditions: 公開境界未確定 / 責務分離矛盾 / 指定外編集要求を検知した場合は更新を停止する。

## Focused execution record（2026-04-17 / DOC-OPS-05-01）

- Target files only: `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md` + `04_Documentation/canonicalization.md`
- Prohibition: **他4xドキュメント編集禁止**

### Phase: Read
- 本文の Classification / Audience / Public boundary / Go-No-Go 条件を再確認。

### Phase: CDC（必要時）
- 判定: **不要**（DecisionStatus=Fixed、既存CDCで十分）。

### Phase: Plan
- 変更は実行記録の同期追記に限定し、公開内容（概要stub）を変更しない。

### Phase: Execute
- 本書へ Focused cycle 記録を追記し、Issue側の同記録と整合させる。

### Phase: Verify（<=3）
1. `rg -n "Focused execution record|Phase: Read|Phase: CDC|Phase: Verify（<=3）" 04_Documentation/canonicalization.md 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
2. `git diff --check`
3. `git diff -- 04_Documentation/canonicalization.md 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`

### Phase: Proceed
- Status: **Ready**
- Note: DOC-OPS-05 の Move internal 方針は維持。

## Stream H docs群1 serial cycle (2026-04-18)

### Phase 1 Read
- 対象ファイルを再読し、`Audience / Goal / Non-goal / Public boundary / Outcome / Related` の整合を確認した。
- Scopeを docs-only に固定し、編集禁止対象（`security.md` / `security_operational_guidelines.md` / shared files）へ非接触であることを確認した。

### Phase 2 Plan
- 1Phase1責務で進行し、変更は「実行記録の同期」と「公開境界の維持」に限定する。
- AC/DoD不足があれば先に補完提案し、未合意の新規仕様決定は持ち込まない。

### Phase 3 Execute（1ファイル直列）
- Classification: **Move internal**
- 04_Documentation/canonicalization.md は公開stubを維持し、内部正本導線のみを更新する。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5" 04_Documentation/canonicalization.md`
- `git diff --check`
- 修復は最大3回まで。4回目相当は `StoppedForClarification` として停止する。

### Phase 5 Proceed（差分要約）
- 判定: **Ready**
- 停止条件: 分類不能・対象外編集要求・自己修復3回超過を検知した場合は停止する。

## DOC-OPS-05 Stream J2 execution record (2026-04-18)

### Phase 1: Read
- Target issue scope and this document were re-read to confirm Audience / Goal / Public boundary.
- Classification remains **Move internal** and no Stream H-owned file edits are required.

### Phase 2: ADR CDC
- CDC update is **not required** because the existing placement policy is within current DOC-OPS-05 decisions.

### Phase 3: Plan
- AC/DoD補足: 分類根拠（Audience/Goal/公開境界）・次アクション・検証一致（docs-check）を1セットで記録する。
- 次アクション固定: 内部正本導線（02_Architecture）を維持し、公開stubを継続する。

### Phase 4: Execute
- docs-onlyで本ファイルのみを更新し、実装仕様変更は行わない。

### Phase 5: Verify
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|DOC-OPS-05 Stream J2" 04_Documentation/canonicalization.md`
- `git diff --check`
- Self-correction policy: max 3 attempts, then stop and reassign if unresolved.

### Phase 6: Proceed
- 判定: **Ready**
- 根拠: 分類根拠・次アクション・検証一致を同一文書内で追跡可能。


## Stream H serial cycle（2026-04-19 / DOC-OPS-05-01）

### Phase 1 Read
- `issue-doc-ops-05-01` と本書を再Readし、Classification=**Move internal** と DecisionStatus=Fixed の整合を確認。

### Phase 2 ADR CDC
- 追加ADRは不要。既存CDCのまま継続。

### Phase 3 Plan
- AC/DoD不足なし。公開stub維持と内部正本導線の明確化を継続。

### Phase 4 Execute
- 公開境界メタ（Audience/Goal/Non-goal/Public boundary/Outcome/Related）を維持。

### Phase 5 Verify
- docs-check（メタ整合・リンク整合・`git diff --check`）を適用。
- 自己修復は最大3回。

### Phase 6 Proceed
- 状態: **Ready**

## Stream F serial cycle（2026-04-19 / DOC-OPS-05-01）

### Phase 1 Read同期
- `issue-doc-ops-05-01-04doc-canonicalization.md` と本書を照合し、Classification=**Move internal**、公開境界メタ、関連導線の整合を確認。
- `02_Architecture/schemas.md` / `02_Architecture/architecture.md` 参照が現行方針（公開は概要、詳細は内部正本）と矛盾しないことを確認。

### Phase 2 Plan（AC/DoD草案→合意）
- AC:
  1) 公開stub方針（Move internal）を維持する。
  2) Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
  3) Verifyで docs-check（`rg` + `git diff --check`）を実行する。
- DoD:
  - docs-onlyで対象3文書以外を編集しない。
  - 自己修復は最大3回、超過時は停止する。

### Phase 3 Execute
- 本書の方針を変更せず、Stream Fとしての5Phase実行記録を追記。

### Phase 4 Verify（docs-check）
- `rg -n "DOC-OPS-05 Classification|Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream F serial cycle" 04_Documentation/canonicalization.md`
- `git diff --check`
- 自己修復回数: **0/3**

### Phase 5 Proceed/Stop
- 判定: **Proceed (Ready)**
- Stop条件: docs-check不整合の自己修復が3回を超えた場合は **Stop** とし、保留化する。


## DOC-OPS-05-01 serial run log（2026-04-19）

### Phase 1 Read
- Read対象: `04_Documentation/canonicalization.md` と対応Issue `01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`。
- 公開境界/内部境界と `VerificationLevel=docs-check` を再確認。

### Phase 2 Plan
- 本ファイルは docs-only で局所更新し、対象外（05-06以降・共有統合3ファイル・コード）へ非接触。

### Phase 3 Execute
- 既存分類 `Move internal` と Audience/Goal/Non-goal/Public boundary/Outcome/Related を維持したまま、2026-04-19 実行ログを追記。

### Phase 4 Verify
- `rg -n "DOC-OPS-05-01 serial run log|Phase 1 Read|Phase 2 Plan|Phase 3 Execute|Phase 4 Verify|Phase 5 Proceed" 04_Documentation/canonicalization.md 01_Plans/issues/issue-doc-ops-05-01-04doc-canonicalization.md`
- `git diff --check`

### Phase 5 Proceed
- 状態: **Ready**
- 次アクション: 本セット（05-01..05）内での整合維持を継続。

## Stream D execution log（2026-04-20 / DOC-OPS-05-01）

### Phase 1 Read
- 対象: `04_Documentation/canonicalization.md` と対応Issueの Requirement meta I/F を再読し、docs-only 境界を確認。
- 判定: Classification=`Move internal` を維持し、編集禁止範囲（README / dashboard / decision-pack / 実装コード）へ非接触。

### Phase 2 Plan（AC/DoD不足補完）
- AC補完: Audience / Goal / Non-goal / Public boundary / Outcome / Related と Go/No-Go 判定導線が追跡可能であること。
- DoD補完: Read → Plan → Execute → Verify → Proceed の5Phase記録を残し、Verifyは docs-check 手順を明示すること。

### Phase 3 Execute
- 既存の分類方針と公開境界メタを維持し、DOC-OPS-05前半（01〜05）の同期記録を本節へ追加。
- 非目標を維持し、仕様正本（00〜02）の上書き・実装変更は行わない。

### Phase 4 Verify（docs-check）
- `rg -n "Audience|Goal|Non-goal|Public boundary|Outcome|Related|Go/No-Go|Stream D execution log" 04_Documentation/canonicalization.md 04_Documentation/canonicalization.md`
- `git diff --check`
- 失敗時は自己修復を最大3回まで。4回目相当は停止して Hold とする。

### Phase 5 Proceed（残課題記録）
- 状態: **Ready**
- 残課題: 移設先の正本文書を確定した時点で本書のRelatedを更新する。


## Stream G serial cycle（2026-04-20 / DOC-OPS-05 Canonicalization）

### Phase 1 Read
- `04_Documentation/canonicalization.md` の冒頭メタ、Go/No-Go、既存の停止条件を再読し、Classification=`Move internal` の維持を確認。
- 依存参照として `02_Architecture/schemas.md` と `02_Architecture/architecture.md`、および release workflow（`.github/workflows/release.yml`）を参照し、実装仕様の再定義を行わない方針を確認。

### Phase 2 Plan（AC/DoDドラフト→合意）
- AC draft:
  1. 公開stub方針（Move internal）を維持する。
  2. Audience / Goal / Non-goal / Public boundary / Outcome / Related を維持する。
  3. Verify は docs-check（`rg` + `git diff --check`）で再現可能に残す。
- DoD draft:
  - docs-only で編集許可範囲3ファイル以外を変更しない。
  - Read→Plan→Execute→Verify→Proceed の記録を残す。
  - 自己修復は最大3回、超過時は停止する。
- 合意: 上記AC/DoDで実行し、未定義競合が出た場合は停止する。

### Phase 3 ADR CDC（必要時判定）
- 判定: **不要**。既存分類と公開境界は上流文書と整合しており、新規CDCは要求されない。

### Phase 4 Execute→Verify
- docs-only で本節を追記し、既存の安全境界（SafeMode既定ON / 漏えい防止後退禁止）に抵触しないことを確認。
- docs-check:
  - `rg -n "Stream G serial cycle|Phase 1 Read|Phase 2 Plan|Phase 3 ADR CDC|Phase 4 Execute→Verify|Phase 5 Proceed" 04_Documentation/canonicalization.md`
  - `git diff --check`
- 自己修復回数: 0/3

### Phase 5 Proceed（残課題 / 外部依存）
- 判定: **Ready**
- 残課題: Move internal の最終移設先確定時に Related の導線更新が必要。
- 外部依存: リリース関連の実行確認は `.github/workflows/release.yml`（タグ `v*.*.*` で Release Build 実行）に依存し、本書では参照のみ行う。
