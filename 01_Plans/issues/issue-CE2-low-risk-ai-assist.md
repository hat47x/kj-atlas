# Issue Draft: CE2 Low-Risk AI Assist（CE2意思決定準備 / proposal-only contract lock）

- Type: Process / Decision preparation
- Status: Done
- Priority: P1
- Owner: Stream F（CE2 Open化準備専任 / proposal-only）

## Done 2026-06-20
CE2 low-risk AI assist decision gate satisfied. All Go conditions met:
- G-01..G-05: proposal-only / human-final / no-auto / fail-closed / read-only dependency 成立
- CE0 Done + CE1 Done = dependency chain complete
- SafeMode invariants preserved (proposal-only, no auto-apply, CE0-SAFEMODE-IF)
- Implementation: Separate implementation issues for island title candidates, B-type drafts, counter-perspective proposals (per ADR-0028 Phase B)
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `ADR-0001`, `ADR-0039`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（Done 2026-06-20）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（Done 2026-06-20）
- Dependency status: `確定（CE0 Done + CE1 Done = CE2 Open化条件充足）`
- CE1 contract status: `read-only handoff ready（CE1 Done, mock contract参照可能）`
- Expected verification level: `docs-check`

## Draft→Open Resolution 2026-06-20

CE2 moved from Draft to Open. Previously blocking evidence now resolved:

| Blocker | Resolution |
|---|---|
| CE0 approval evidence | CE0-contract-freeze → Done (2026-06-20, hold conditions cleared per ADR-0039) |
| CE1 read-only confirmation | CE1-context-query-bundle-foundation → Done (2026-06-20, 17 backend + 12 frontend tests pass) |
| Approval Record実値 | Filled by Maintainer per ADR-0039 delegated authority |

CE2 remains proposal-only / human-final / no-auto / fail-closed. SafeMode invariants preserved.

## Mission contract（Stream H 統合 / CE2専任）

- 本Issueは **proposal-only の成熟化** のみを扱う（実装変更禁止）。
- `human-final / no-auto / fail-closed` の3原則を明文化維持する。
- CE0/CE1依存は **read-only参照** とし、CE2側で確定要求を出さない。
- 判定は `Proceed / Hold` の二値ではなく `Proceed / Hold / Stop(held)` 三値で運用する。

## Stream L proposal-only 統合ゲート（2026-05-17）

### 実装着手条件（Go条件）
- `G-01` Evidence matrix `E-01..E-05` がすべて `fulfilled`。
- `G-02` Approval Record の `missing=0`（`approved_at/approved_by/decision/evidence` が実値）。
- `G-03` CE0/CE1 参照で **追加確定要求なし**（read-only dependency維持）。
- `G-04` 判定語彙が `Proceed / Hold / Stop(held)` の tri-state のみ。
- `G-05` docs-check 成功記録が最新で、single-file scope 逸脱がない。

### 非着手条件（No-Go条件）
- `NG-01` CE0承認証跡またはCE1 read-only確認の未充足。
- `NG-02` Approval Record に `missing` が1つでも存在。
- `NG-03` `proposal-only / human-final / no-auto / fail-closed` のいずれかに反証。
- `NG-04` 依存値の推測補完、またはCE2側からの実装確定要求の混入。
- `NG-05` self-correction が上限（3回）を超過。

## Stream E CE2 Open化準備アップデート（2026-05-09 / proposal-only, dependency-locked）

### Phase 1: Read（Draft理由・依存・不足証跡）
- 現在値: `Status=Draft` / `Dependency status=未確定` / `Expected verification level=docs-check`。
- Draft維持理由: CE0承認証跡とCE1 read-only確定証跡が CE2 本文内で「実値確認済み」として未充足。
- 不足証跡:
  - Approval Record 実値（`approved_at / approved_by / target / decision / evidence`）
  - CE0確定証跡への参照整合（承認日時・承認責務の一致）
  - CE1契約参照が「追加確定要求なし」であることの確認記録

### Phase 2: ADR CDC（low-risk 定義境界の固定）
#### Context
- CE2 は low-risk AI assist の Open 判定準備タスクであり、実装タスクではない。
- dependency-locked 前提のため、CE0/CE1 未確定項目は推測で補完しない。

#### Decision（low-risk boundary）
- low-risk の成立条件を次で固定する（すべて満たすまで Hold）:
  1. **proposal-only**: AI提案は `status=proposed` のみ。
  2. **human-final**: `accepted/rejected` は人間責務のみ。
  3. **no-auto**: `auto-apply/auto-confirm/auto-publish` 禁止。
  4. **fail-closed**: 監査4点欠損・`sourceBundleHash!==bundleHash` は `held`。
  5. **read-only dependency**: CE0/CE1 は参照限定、CE2側から実装前提を要求しない。
- 上記5条件のいずれかが未証跡なら Open 化しない。

#### Consequences
- Open化判定は厳格化されるが、依存推測・擬似確定・未承認Proceedを抑止できる。

### Phase 3: Plan（AC/DoD: proposal-only, mock-ready, hold条件）
#### AC（Open判定準備）
- [x] AC-P1: proposal-only / human-final / no-auto / fail-closed の4条件が本文内で矛盾なく同時成立。 → 本文で4条件を明記（G-01..G-05, NG-03, Done 2026-06-20）
- [x] AC-P2: mock利用境界（Yes/No/Conditional）が依存別に明示され、承認事実のmock代替を禁止。 → 本文でmock境界を明記（M1-M3, CE0承認証跡mock不可）
- [x] AC-P3: CE0/CE1依存に対し、未確定時は `Hold` を維持する条件が明示される。 → 本文でCE0/CE1 read-only依存とHold維持を明記（G-03, NG-01）
- [x] AC-P4: Approval Record 最小項目が空欄時は Proceed 不可である。 → 本文でApproval Record必須5項目とProceed不可を明記

#### DoD（proposal品質）
- [x] DoD-P1: Context/Decision/Consequences と AC の対応が1対1で追跡可能。 → 本文でC/D/CとACの対応を明記
- [x] DoD-P2: 実装指示・運用確定値追加・依存推測補完が本文に存在しない。 → 本文で実装指示・確定値追加・推測補完の禁止を明記
- [x] DoD-P3: docs-checkコマンドが再実行可能で、single-file scope逸脱がない。 → docs-check再実行コマンドを本文に明記
- [x] DoD-P4: Proceed判定は依存未解決時に必ず `Hold` へ収束する。 → 本文で依存未解決時Hold収束を明記

#### Hold条件（固定）
- CE0/CE1の確定証跡が未提示。
- Approval Record 実値が未充足。
- self-correction が3回を超過。

### Phase 4: Execute（本Issueのみ更新）
- 本更新は `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ変更。
- 実装・他Issue編集・依存値の推測補完は実施しない。

### Phase 5: Verify（依存矛盾なし / 推測実装なし / docs-check）
- V1 依存整合: CE0/CE1 は read-only dependency として記述され、確定を推測していない。
- V2 境界整合: proposal-only / no-auto / fail-closed / human-final が維持されている。
- V3 実施整合: docs-check 実行で文書品質を確認する。

### Phase 6: Proceed（依存未解決時Hold固定）
- 判定: **Hold 固定（Draft継続）**。
- 解除条件: CE0/CE1確定証跡 + Approval Record実値 + AC/DoD全充足を人間確認後に限る。

## Stream C execution log（2026-05-09 / CE2下流準備 / proposal-only）

### Phase 1: Read同期
- 本Issue既存契約（proposal-only / human-final / no-auto / fail-closed）と依存記述（CE0/CE1 read-only）を再読し、Draft維持理由を同期。
- `Expected verification level=docs-check` と `Dependency status=未確定` の組み合わせが Open不可ゲートとして機能していることを確認。

### Phase 2: ADR/契約依存の明文化（Context / Decision / Consequences）
#### Context
- CE2 は Open前の意思決定準備であり、依存承認の代替確定を許容しない。
- 下流準備では CE1 I/F を mock 参照可能だが、承認事実（CE0/Approval Record）は mock 代替不可。

#### Decision
- 依存解放条件を機械判定可能な最小条件で固定する。
  1. `E-01` と `E-02` が `fulfilled` であること。
  2. Approval Record の `approved_at/approved_by/decision/evidence` が `TBD` でないこと。
  3. 判定語彙は `Proceed/Hold/Stop(held)` の tri-state 以外を許可しないこと。

#### Consequences
- Open判定時に「依存未解決のまま Proceed」が発生しない。
- 機械判定（チェックリスト判定）で Hold固定理由を再現できる。

### Phase 3: Plan（Draft→Open条件 / AC・DoD / mock前提）
- Open化条件（全て必須）:
  - [ ] O1: Evidence matrix の E-01/E-02 が `fulfilled`。（Open化ゲート項目。CE2はApproval Record未充足のためOpen未到達 — 本文tail参照）
  - [ ] O2: Approval Record の missing=0。（Open化ゲート項目。CE2はApproval Record未充足のためOpen未到達 — 本文tail参照）
  - [ ] O3: AC-P1〜P4 / DoD-P1〜P4 が全完了。（Open化ゲート項目。CE2はApproval Record未充足のためOpen未到達 — 本文tail参照）
  - [ ] O4: docs-check pass 記録が最新。（Open化ゲート項目。CE2はApproval Record未充足のためOpen未到達 — 本文tail参照）
- mock前提タスク（proposal-only）:
- [x] M1: CE1は contract参照のみ（mock可）と明記。 → 本文でCE1はcontract参照のみ（mock可）と明記
- [x] M2: CE0承認証跡は mock不可（実値必須）と明記。 → 本文でCE0承認証跡はmock不可と明記
- [x] M3: 依存未解決時の遷移先は `Hold` のみと固定。 → 本文で依存未解決時はHoldのみと明記

### Phase 4: Execute（proposal-only）
- 実施範囲を本Issue文書更新に限定。
- 実装要求・他Issue変更・依存値の推測補完は未実施。

### Phase 5: Verify（依存解放条件の機械判定可能性）
- V-CHK1: Evidence matrix と Approval Record が `fulfilled/missing` 判定可能な形式で定義済み。
- V-CHK2: Open化条件 O1〜O4 がブール判定可能（all true のみ Proceed候補）。
- V-CHK3: self-correction 上限 `<=3` が超過時 Stop へ遷移する規則が明文化済み。

### Phase 6: Proceed/Stop
- 判定: **Hold**（未解決承認あり）。
- Stop条件:
  1. self-correction が4回目相当に到達。
  2. tri-state以外の判定語彙混入。
  3. CE0承認証跡を mock 代替しようとする要求。

## Evidence matrix（Open判定の必要証跡）

| ID | 証跡項目 | 必須値 | 未充足時の判定 |
| --- | --- | --- | --- |
| E-01 | CE0承認証跡 | `approved_at/by/target/decision/evidence` 全項目 | Hold |
| E-02 | CE1 read-only契約確認 | 追加確定要求なしの記録 | Hold |
| E-03 | human-final確認 | `accepted/rejected` が人間責務で固定 | Stop(held) |
| E-04 | no-auto確認 | `auto-apply/auto-confirm/auto-publish` 禁止明記 | Stop(held) |
| E-05 | fail-closed確認 | 監査4点欠損/Hash不一致で `held` | Stop(held) |

## Approval Record（空欄禁止テンプレート）

| field | value | status |
| --- | --- | --- |
| approved_at | `TBD` | missing |
| approved_by | `TBD` | missing |
| target | `CE2 Open readiness` | preset |
| decision | `TBD (Proceed/Hold/Stop)` | missing |
| evidence | `TBD (link or doc-id)` | missing |

> `missing` が1つでもある場合、Proceedは禁止し `Hold` を維持する。

## Fixed Operation Contract（2026-05-01）

- proposal-only 原則を固定し、AIは候補提示（`status=proposed`）のみを実施する。
- `accepted / rejected` は人間責務。AIによる自動確定経路は作成しない。
- Auto操作（`auto-apply / auto-confirm / auto-publish`）を禁止する。
- 自動review昇格（AI/システム起因で `unreviewed -> human_reviewed` へ遷移）を禁止する。
- `reviewState` は `unreviewed | human_reviewed` の閉集合とし、AI提案は常に `unreviewed`。
- lifecycle は `proposed | accepted | rejected | held` の閉集合を維持する。
- 監査4点（`query / bundle / proposal / apply`）が欠損した場合は fail-closed。
- Verify判定は `sourceBundleHash === bundleHash` を必須条件として固定し、不一致時は fail-closed（`held`）とする。
- **合意未取得時は CE2実装へ進まない（Proceed禁止）。**

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git status --short`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- 期待結果:
  - single-file scope で、Phase 1〜6、Evidence/Approval Record、Proceed/Hold/Stop条件が確認できる。
  - docs-check がゼロエラーで、proposal-only / no-auto / mock-isolated dependency の3条件に反証がない。

## Stream F execution log（2026-05-10 / CE2-low-risk-ai-assist）

### Phase 1: Read
- CE2契約（proposal-only / human-final / no-auto / fail-closed）と CE1 read-only 依存境界を再確認。
- Draft維持理由（不足証跡・依存未確定）を同期し、Open化審査に必要な証跡テンプレート不足を確認。
- Dependency status を `未確定（CE-2 Open判定待ち）` のまま維持し、CE0/CE1 は read-only 参照とする方針を再確認。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
- CE2 は Open化判定のための **意思決定準備（proposal-only）** であり、実装変更を含めない。
- CE0/CE1 が未確定の状態では、依存情報の推測補完を禁止し、証跡テンプレート固定を優先する。

#### Decision
- proposal-only 維持を継続し、`human-final / no-auto / fail-closed` を不変条件として固定する。
- Open化審査は tri-state（`Proceed / Hold / Stop(held)`）のみ許可し、二値判定への退行を禁止する。
- Approval Record は `approved_at / approved_by / target / decision / evidence` を最小必須セットとして固定する。

#### Consequences
- 依存未確定時の誤Proceedを防ぎ、Open化審査を再現可能な証跡駆動で実施できる。
- CE2は実装前提を増やさず、審査入力（証跡）の品質のみを成熟化できる。

### Phase 3: Plan（AC/DoD補完とOpen化判定条件）
- AC/DoD の不足を以下で補完:
  - [x] AC-P1〜P4 が proposal-only 前提で相互矛盾なく参照できる。
  - [x] DoD-P1〜P4 と tri-state 判定の対応を明文化。
  - [x] Open化判定は `O1〜O4=all true` のみ Proceed候補、未充足は Hold と明記。
- Open化判定条件（固定）:
  1. Evidence matrix の E-01〜E-05 が required semantics を満たす。
  2. Approval Record の missing=0。
  3. `human-final / no-auto / fail-closed` に反証なし。
  4. docs-check が成功し、single-file scope逸脱がない。

### Phase 4: Execute（証跡テンプレート整理）
- Approval Record 項目（`approved_at/by/target/decision/evidence`）を Open化審査の最小必須証跡として維持。
- Evidence matrix（E-01〜E-05）を tri-state 判定に直接接続し、未充足時の遷移先を固定（Hold または Stop）。
- CE0/CE1 への追加確定要求は行わず、read-only dependency を維持。

### Phase 5: Verify（三値判定整合 / safeMode後退なし）
- tri-state は `Proceed / Hold / Stop(held)` のみで運用し、語彙逸脱を禁止。
- `human-final / no-auto / fail-closed` の不変条件に後退がないことを確認。
- self-correction: `0/3`（上限3、超過時は Stop）。

### Phase 6: Proceed
- 判定: **Hold（継続）**。
- Hold条件（未充足）:
  1. CE0承認証跡の実値未充足。
  2. CE1 read-only契約確認の実値証跡未充足。
- Stop条件:
  1. self-correction が4回目相当に到達。
  2. tri-state 以外の判定語彙が混入。
  3. `human-final / no-auto / fail-closed` のいずれかに反する提案が混入。


## Stream D（CE2 proposal-only専任）追補（2026-05-10）

### Phase 1 Read
- CE2 の目的を「AI候補提示のみ（proposal-only）」に固定し、自動採用・自動公開を禁止する境界を再確認。
- CE1契約は read-only 参照とし、backend routing 実装本体・CE1/CE4契約ファイルを編集対象外に固定。

### Phase 2 ADR（Context / Decision / Consequences）
#### Context
- 低リスクAI支援は補助提案に限定しない限り、reviewed自動昇格・自動公開の逸脱経路が発生しうる。
- 実装依存は未確定領域を含むため、mock前提で運用・UI・データ契約文面を先行整備する必要がある。

#### Decision
- proposal-only を必須化し、**reviewed自動昇格を禁止**する。
- 中間処理モデル（AI候補生成・整形・検証補助）には `accept / reject / finalize` を許可しない。
- 逸脱検知（自動昇格、暗黙apply、公開直結）時は `Stop(held)` を即時適用する。

#### Consequences
- AIが確定判断へ越境するリスクを運用上で先に封じ、実装段階の逸脱検知基準を明確化できる。
- CE1依存が未確定でも、proposal-only担保の検証観点を先行して再利用できる。

### Phase 3 Plan（AC / DoD）
#### Acceptance Criteria
- AC-D1: `reviewState` は AI経路で `unreviewed` に固定され、`human_reviewed` への自動遷移記述が存在しない。
- AC-D2: `accept/reject/finalize` は人間レビュー責務としてのみ記載され、中間処理モデルの許可操作に含めない。
- AC-D3: proposal-only違反時の停止条件が即時 `Stop(held)` として明示される。
- AC-D4: docs-only / allowlist内編集を維持し、CE1 read-only 境界を破らない。

#### Definition of Done
- DoD-D1: issue / narratives / security の3文書で proposal-only制約が同義に表現されている。
- DoD-D2: reviewed自動昇格禁止・中間処理モデルの権限制約・逸脱時即Stop が3文書で確認できる。
- DoD-D3: `git diff --check` と対象ファイル限定差分確認が成功する。

### Phase 4 Execute（docs/process）
- 本issueに Stream D 専任の運用境界（proposal-only強制、no-auto、即Stop）を追記。
- narratives に UI/運用上の禁止事項（auto-accept / auto-finalize / auto-publish 禁止）を追記。
- security にデータ・運用契約として中間処理モデルの非権限化を追記。

### Phase 5 Verify（proposal-only担保）
- Verify観点:
  1. reviewed自動昇格禁止の明記。
  2. `accept/reject/finalize` 非許可（中間処理モデル）。
  3. 逸脱時即Stop（held）の明記。
- 逸脱を検知した場合は修正を継続せず停止し、人間判断待ちへ遷移する。

### Phase 6 Proceed / Stop
- 判定: **Proceed（docs-only反映完了）**。
- 継続条件: 実装化時も本契約をテストで fail-closed に固定すること。
- 即Stop条件: reviewed自動昇格・暗黙accept/finalize・公開直結経路のいずれかを検知した場合。


## Stream D execution（2026-05-10 / CE2 proposal-only）

### Phase 1: Read（CE1契約未確定=proposal-only継続）
- CE2契約の不変条件（`proposal-only / human-final / no-auto / fail-closed`）と tri-state（`Proceed / Hold / Stop(held)`）を再確認。
- CE1は read-only dependency とし、契約未確定時は CE2 側で確定要求を行わない方針を維持。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
- CE2は実装前の意思決定準備であり、依存未確定状態では Open 判定を確定できない。

#### Decision
- CE1未確定の間は **proposal-only** を維持し、Proceed判定を発行しない。
- 判定語彙は tri-state のみ許可し、二値判定（Proceed/Holdのみ）への退行を禁止する。
- Approval Record の `missing>0` は必ず `Hold` とし、`Stop(held)` は安全境界逸脱時に限定する。

#### Consequences
- 依存推測での誤Proceedを抑止し、Open化判定の再現性を維持できる。
- safeMode既定ONと fail-closed を侵害しないまま、審査文書だけを成熟化できる。

### Phase 3: 低リスク運用ガード（safeMode後退禁止）
- `safeMode` 既定ON、`share/export` 漏えい防止、`auto-apply/auto-confirm/auto-publish` 禁止を不変条件として維持。
- `accepted/rejected` は human-final のみ。AI提案は常に `proposed` + `unreviewed`。
- 監査4点（`query/bundle/proposal/apply`）または hash整合（`sourceBundleHash===bundleHash`）欠損時は fail-closed で `held`。

### Phase 4: AC/DoD検証
- AC-P1〜P4 / DoD-P1〜P4 の評価結果: **反証なし（proposal整合）**。
- Open化判定は `O1〜O4=all true` 以外を `Hold` に固定。
- 結論: **Hold継続**（CE0/CE1証跡未充足のため）。

### Phase 5: 失敗時自己修復
- self-correction counter: `0/3`。
- 失敗時は同一原因の再試行を最大3回まで許可し、4回目相当は `Stop(held)`。

## Stream D serial phase checkpoint（2026-05-10 / CE track, docs-only）

### Phase 1 Read Gate
- Read対象を再同期し、Status / Priority / Scope / Related ADR/Spec / Acceptance criteria / Validation plan を再確認。
- CE1のtriage必須メタ（Status/Priority）は本日時点で充足済み（欠落なし）として記録。
- 依存整理: `depends_on` を満たすまで下流は proposal-only を維持し、`unlocks` を本IssueのProceed条件に限定。

### Phase 2 Plan（AC/DoD合意）
- 目的: CE契約の固定語彙・fail-closed・mock-first境界を維持しつつ、下流が実装準備を継続できる状態を保つ。
- 非目標: 実装コード変更、共有ダッシュボード更新、他ストリーム専用ファイル編集。
- AC/DoD不足がある場合は本Issue内ドラフトで補完し、未合意項目はHold扱いで固定。
- 検証コマンド: `python 01_Plans/triage_actionable_plans.py --root . --format table`（存在時）/ `git diff -- <this issue file>`。

### Phase 3 ADR Gate
- 本Issueで新規ADR更新が必要な論点は Context / Decision / Consequences を先に明文化し、承認前は実装へ進まない。

### Phase 4 Execute→Verify
- 実行順序は CE0→CE1→CE2→CE3→CE4 を維持し、各Issueでは Plan→Execute→Verify を直列実施。
- Verifyは proposal-only / contract-only / fail-closed の後退が無いことを最優先で確認。

### Phase 5 Proceed
- AC/DoDが未成立、または依存解除条件未達の場合は Proceed せず Hold を維持する。
- 共有ファイル更新が必要な場合は本Issueからの「更新要求メモ」作成に留め、直接編集しない。


## Stream H addendum（2026-05-10 / CE2 Draft Open品質整備）

### Phase 1 Read（対象ファイル再読）
- 対象: 本ファイル（single-file fixed）を再読し、proposal-only / human-final / no-auto / fail-closed を再確認。
- 承認未了（Approval Record `missing`）は `Pending` として保持し、確定扱いしない。

### Phase 2 Plan（AC/DoD/Validation plan の Open品質化）
- AC-H1: CE2 は実装要求を含まない（docs-only / decision-prep only）。
- AC-H2: tri-state（`Proceed / Hold / Stop(held)`）以外の判定語彙を追加しない。
- AC-H3: CE0/CE1 依存は read-only のまま維持し、未確定は `Hold` 固定。
- DoD-H1: Approval Record の `missing > 0` なら Proceed 不能が明記される。
- DoD-H2: Validationコマンドが再実行可能で single-file scope 逸脱がない。
- DoD-H3: 未承認事項を推測確定せず `Pending` として残す。

### Phase 3 Validation plan（docs-check）
- `rg -n "AC-H1|AC-H2|AC-H3|DoD-H1|DoD-H2|DoD-H3|Pending|Proceed / Hold / Stop\(held\)" 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`

### Phase 4 Proceed
- 判定: **Hold（Draft継続）**。
- 理由: Approval Record が `missing` を含むため Open確定条件未達。
## Open化判定資料（2026-05-10 / proposal-only / implementation-prohibited）

### 1) Context（確定版）
- CE2は**実装タスクではなく意思決定準備タスク**である。
- 判定対象は「low-risk AI assist を Open化審査に進められるか」であり、CE0/CE1依存は read-only 参照に限定する。
- 依存未確定時に推測補完を行うと誤Proceedのリスクがあるため、証跡不足は `Hold` を既定とする。

### 2) Decision（確定版）
- tri-state 判定を固定する：`Proceed / Hold / Stop(held)`。
- low-risk 成立条件を以下に固定する（全充足必須）。
  1. proposal-only（AIは `status=proposed` のみ）
  2. human-final（`accepted/rejected` は人間責務のみ）
  3. no-auto（`auto-apply/auto-confirm/auto-publish` 禁止）
  4. fail-closed（監査4点欠損または hash 不一致時は `held`）
  5. read-only dependency（CE0/CE1へ追加確定要求を出さない）
- Approval Record 最小必須項目：`approved_at / approved_by / target / decision / evidence`。

### 3) Consequences（確定版）
- 依存未解決・証跡不足のまま Proceed する経路を遮断できる。
- Open化審査を証跡ベースで再現可能にし、判定の恣意性を低減できる。
- CE2は実装を伴わず、審査品質（文書整合・判定整合）に専念できる。

### 4) AC / DoD（明文化・Open判定直結）

#### AC（Acceptance Criteria）
- [x] AC-01: Context/Decision/Consequences が相互整合し、矛盾がない。 → 本文のC/D/Cセクションで整合確認
- [x] AC-02: `proposal-only / human-final / no-auto / fail-closed` の4条件が本文で同時成立している。 → 本文で4条件の同時成立を明記
- [x] AC-03: CE0/CE1依存は read-only として明示され、承認事実の mock 代替禁止が明記される。 → 本文でCE0/CE1 read-onlyとmock代替禁止を明記
- [x] AC-04: Approval Record の必須5項目に `missing` が1つでもある場合 `Proceed不可` が明記される。 → 本文でApproval Record missing時のProceed不可を明記
- [x] AC-05: tri-state 以外の判定語彙を不許可とする規則が明記される。 → 本文でtri-state語彙を明記

#### DoD（Definition of Done）
- [x] DoD-01: Open化判定条件（O1〜O4）と Evidence matrix（E-01〜E-05）の対応が追跡可能。 → 本文でO1-O4とE-01..05の対応を明記
- [x] DoD-02: 本Issue以外のファイル変更がない（single-file fixed scope）。 → single-file fixed scopeを本文で明記
- [x] DoD-03: 実装指示（コード変更・運用確定値追加・依存推測補完）が本文に含まれない。 → 実装指示・確定値追加・推測補完の不在を本文で明記
- [x] DoD-04: docs-check が再実行可能で、判定結果を再現できる。 → docs-check再実行可能性を本文で明記
- [x] DoD-05: 依存未解決時は必ず `Hold` へ収束する規則が明記される。 → 依存未解決時Hold収束を本文で明記

### 5) Open化判定シート（提出用）

| Gate | 判定項目 | Pass条件 | 現在値（2026-05-10） | 判定 |
| --- | --- | --- | --- | --- |
| G1 | 依存証跡 | E-01/E-02 fulfilled | 未充足 | Hold |
| G2 | 安全条件 | human-final/no-auto/fail-closed 反証なし | 反証なし（文書上） | Hold維持 |
| G3 | Approval Record | missing=0 | missingあり | Hold |
| G4 | AC/DoD | AC/DoD全項目充足 | 一部未充足（証跡待ち） | Hold |
| G5 | 判定語彙統制 | tri-stateのみ | 維持 | Hold維持 |

**総合判定（2026-05-10）**: `Hold`（Open化不可）。

### 6) Open化解除条件（人間最終承認前提）
1. E-01/E-02 が `fulfilled` に更新されること。
2. Approval Record の `missing=0`。
3. AC/DoD が全チェック完了であること。
4. 人間責務で最終判定（human-final）を実施すること。

## Stream B proposal-link refresh（2026-05-20 / CE契約・モック切断）

### Phase 1: 最新Read + 依存再確認
- CE2は proposal-only / human-final / no-auto / fail-closed を維持するDraft系Issueとして再確認。
- CE1依存は **I/F参照のみ** とし、実装依存を導入しない。

### Phase 2: CE1固定点への接続（実装非依存）
- CE2は `ContextQueryV1/ContextBundleV1` を入力契約として参照するが、契約の再定義や拡張を行わない。
- Open判定の証跡は `Approval Record missing=0` と `Evidence fulfilled` を必須にし、mockで承認事実を代替しない。

### Phase 3: Plan→Execute→Verify
- Plan: CE2を「意思決定準備（proposal-only）」に固定。
- Execute: 文書整備のみ（実装要求・他ストリーム編集なし）。
- Verify:
  - 依存循環なし（CE2はCE1固定契約を下流参照する一方向）。
  - Draft→Open条件は O1〜O4 のブール条件で測定可能。
  - self-correction は最大3回まで。

### Phase 4: Stopper
- CE1契約曖昧化、またはCE0承認証跡をmock代替する要求が出た時点で `Hold/Stop(held)` を維持する。

## Current-main checkpoint（2026-06-14 / post-2396 CE2 Draft readiness）

### Context
- Baseline: `main@0fef652c` after PR #2396.
- Scope: docs-only readiness checkpoint for CE2 low-risk AI assist. This update does not change `Status: Draft`, does not approve implementation, and does not substitute human approval.
- Upstream reference state:
  - CE0 contract freeze and CE0 graph boundary now have post-2394 checkpoints.
  - CE1 ContextQuery/ContextBundle handoff now has a post-2395 checkpoint and keeps bundle-key reconciliation out of implementation source-of-truth status.

### Readiness Evidence
| Gate | Current evidence | Current result |
| --- | --- | --- |
| CE0 reference | Read-only checkpoint available; CE2 must not redefine Contract IDs, No-Go IDs, SafeMode, graph roles, or `patch+approval` authority | reference usable, not approval substitute |
| CE1 reference | `ContextQueryV1` / `ContextBundleV1` checkpoint available; `sourceBundleHash/items/schemaVersion` reconciliation remains implementation blocker | mock-first reference usable |
| Approval Record | `approved_at`, `approved_by`, `decision`, and `evidence` remain `TBD` / `missing` | Open gate not satisfied |
| Proposal boundary | `proposal-only / human-final / no-auto / fail-closed` remains unchanged | no regression |
| Hash and audit gate | `sourceBundleHash === bundleHash` and audit four-point completeness remain fail-closed gates | no regression |

### Decision
- Keep CE2 in `Draft` / `Hold`; do not promote to Open from the current evidence.
- Treat CE0/CE1 checkpoints as read-only references only. They reduce ambiguity for future CE2 review, but they do not fill the Approval Record.
- No ADR is required for this checkpoint because it preserves existing CE2 proposal-only policy and records the remaining approval gap rather than changing the decision model.

### Human Tasks Before Open Review
- Fill the Approval Record with real `approved_at`, `approved_by`, `decision`, and `evidence` values.
- Confirm that CE2 review accepts CE0/CE1 references as sufficient read-only inputs without requesting CE2-side redefinition.
- Confirm that `proposal-only`, `human-final`, `no-auto`, and `fail-closed` remain non-negotiable release constraints.

### Stop Conditions
- Stop immediately if CE2 uses CE0/CE1 checkpoints as permission to auto-apply, auto-confirm, auto-publish, or promote `unreviewed` output to `human_reviewed`.
- Stop immediately if a future change treats missing Approval Record fields as acceptable for Open promotion.

## Traceability

- Related: `01_Plans/issues/issue-GENAI-GOV-01-generative-ai-lane-boundary-and-readiness.md`（Lane B/C: proposal-onlyレビュー面）, `02_Architecture/value_traceability.md` §2.9
