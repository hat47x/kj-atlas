# Issue Draft: CE2 Low-Risk AI Assist（CE2意思決定準備 / proposal-only contract lock）

- Type: Process / Decision preparation
- Status: Draft
- Priority: P1
- Owner: Stream D（CE2 Draft proposal品質改善 / implementation dependency cut）
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `ADR-0001`, `02_Architecture/schemas.md`
- Dependencies: `01_Plans/issues/issue-CE0-contract-freeze.md`（契約依存）, `01_Plans/issues/issue-CE1-context-query-bundle-foundation.md`（I/F依存; mockで切断可能）
- Dependency status: `未確定（CE-2 Open判定待ち）`
- CE1 contract status: `参照限定（CE1完了待ちは不要。mock contract参照のみ）`
- Expected verification level: `docs-check`

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


## Stream D mission lock（2026-05-07）

- Scope lock: 本Issueを **proposal品質向上** のみに限定し、実装仕様・実装タスク・運用確定値の追加を禁止する。
- Dependency stance: `CE0` / `CE1` は **read-only 依存** とし、参照は契約確認（語彙・I/F・停止条件）に限定する。
- Implementation decoupling: CE2 Draft段階では mock contract 以外の結合（実データ接続・実ランタイム依存・実装前提の状態遷移）を受理しない。

### 実装着手条件（Implementation Start Gate）

次の全条件を満たすまで CE2 実装着手を禁止する。

1. `CE0 contract freeze` が承認済みで、証跡（日時・承認者・対象・判断・evidence）が参照可能。
2. `CE1 context/query/bundle foundation` が **read-only contract として確定** し、CE2側で追加確定を要求しない。
3. 本Issueの tri-state 判定が `Proceed` で、`Hold/Stop` 要因（未承認・契約衝突・修復超過）がゼロ。
4. proposal-only / human final decision / fail-closed / safeMode既定ON の後退ゼロを再検証済み。

満たさない場合は `held` を継続し、実装議論へ遷移しない。

## Mandatory Workflow（Phase 1〜6 固定）

1. **Phase 1 Read同期**: `ADR-0028` / `ADR-0001` / `schemas.md` の語彙と契約を照合し、矛盾を解消する。
2. **Phase 2 ADR/CDC**: Context / Decision / Consequences を本Issue内に固定し、Draft→Open判断材料を明文化する。
3. **Phase 3 Plan（AC/DoD補完）**: 受入条件・DoD・非機能制約・停止条件を先に固定する。
4. **Phase 4 Execute（メモ整備のみ）**: 本Issue内の記述・表・トレーサビリティを整備し、実装は行わない。
5. **Phase 5 Verify（最大3回修復）**:
   - V1: single-file scope逸脱チェック
   - V2: proposal-only / reviewState自動昇格禁止 / sourceBundleHash一致 / fail-closed 文言チェック
   - V3: Phase欠落・表の不整合チェック
   - 3回以内に修復不能な場合は `status=held` で停止。
6. **Phase 6 Proceed/Stop**: 人間承認ログ確認後のみ Proceed。未承認または超過時は Stop（`held`）。

## Phase 1: Read同期（語彙・契約）

### Read対象（固定）
- `ADR-0028`：CE2の上位計画と境界条件
- `ADR-0001`：価値→要件の判断基準
- `02_Architecture/schemas.md`：語彙・状態集合・契約語の整合

### 同期結果（本Draft時点）
- AI提案は `proposed` に限定し、`accepted/rejected` は人間責務として分離されている。
- fail-closed（監査4点欠損時停止）と safeMode境界を後退させない方針で整合している。
- 自動確定・自動公開系操作（auto-*）を禁止し、合意前の Proceed 禁止を維持している。

## Phase 2: ADR/CDC（Context / Decision / Consequences）

### Context
- CE2は「低リスクAI補助」を扱うが、意思決定責務の混線を防ぐため proposal-only 契約が必要。
- Draft→Open移行前に、契約語（status/reviewState/lifecycle）と停止条件を固定する必要がある。

### Decision
- 本Issueは **Draft→Open準備のみ** を対象とし、実装・運用変更を行わない。
- AI出力は `proposed` 限定、人間のみが `accepted/rejected` を確定可能とする。
- Verifyは3段（scope/contract/phase integrity）で最大3回修復。超過時は `held`。

### Consequences
- メリット: 責務分離と監査可能性が先に固定され、誤進行を抑止できる。
- 制約: 実装前進は人間承認ログ取得後に限定され、短期の進行速度は意図的に抑制される。
- 運用影響: Draft段階では記述整備と検証のみ実施し、auto-*導線追加は不可。

## Phase 3: Plan（AC/DoD補完・実装依存遮断）

### 受入条件（CE2計画の成立条件）
- proposal-only のまま AI補助案を作成し、`accepted/rejected` は人間判断として固定されている。
- CE2計画文に「実装禁止」「自動確定禁止」「未承認時は held 継続」が併記されている。
- safeMode既定ON、未レビュー保護、監査欠損時fail-closed の3点が後退しない。

### 非機能制約（NFR）
- **Security**: 未レビュー提案の外部共有・自動公開を許可しない。
- **Auditability**: `query/bundle/proposal/apply` の4点監査を欠損なく追跡可能にする。
- **Traceability**: 判定根拠を Phaseごとに再読可能（誰が何を承認したか復元可能）。
- **Reversibility**: 合意前は常に `held` に戻せる（不可逆操作禁止）。

### AC（Acceptance Criteria）
- [ ] CE2計画が proposal-only の範囲に限定されている。
- [ ] Phase 1〜6（Read同期/ADR-CDC/Plan/Execute/Verify/Proceed-Stop）が記述済み。
- [ ] safeMode既定ON、未レビュー保護、監査欠損fail-closed が後退していない。
- [ ] 承認未取得時に Proceed しない条件が明示されている。

### DoD（Definition of Done）
- [ ] single-file scope を維持し、他ストリーム領域を編集していない。
- [ ] CE2判断材料が再読可能（文言・表・条件が矛盾しない）。
- [ ] Verify 3段（scope / contract / phase integrity）を通過している。
- [ ] 次工程へ渡す「実装禁止解除条件」が1文で明示されている。

## Phase 4: Execute（メモ整備のみ）

### 依存I/F（実装せず、契約のみ列挙）
- Decision Input I/F: 人間レビュー入力（`accepted/rejected/held` の判定記録）。
- Proposal I/F: AI候補出力（`status=proposed`, `reviewState=unreviewed`, `sourceBundleHash` 必須）。
- Audit I/F: 監査4点の存在検査（欠損時 fail-closed）。
- Policy I/F: safeMode と No-Go（auto-* 禁止）制約の適用確認。

### mock方針（計画フェーズ限定）
- **Mock-Decision-Log**: 承認者・日時・対象をダミー値で記録し、ログ形式のみ検証。
- **Mock-Audit-Matrix**: 4点監査の有無を `present/missing` で評価。
- **Mock-Policy-Gate**: auto-* 要素が混入した場合に `blocked` を返す判定表。
- 実データ接続・実運用ログ接続は CE2範囲外（次Phaseへ持ち越し）。

### リスク台帳（誤提案 / 漏洩 / 監査不能）

| Risk ID | リスク | 兆候 | 影響 | 予防策 | 検知時アクション |
| --- | --- | --- | --- | --- | --- |
| R-CE2-01 | 誤提案の採択圧力 | AI提案が確定語で記述される | 人間判断の形骸化 | proposal-only表現を固定、確定語禁止 | `held` へ戻し文言を修正 |
| R-CE2-02 | 未レビュー情報の漏洩 | share/export相当の導線が追加される | 安全境界逸脱 | safeMode既定ONと未レビュー保護を明記 | fail-closed、Proceed停止 |
| R-CE2-03 | 監査不能 | 監査4点のいずれか欠損 | 後追い検証不能 | 4点必須チェックを運用前提化 | 欠損補完まで `held` 継続 |

## Phase 5: Verify（最大3回修復）

### Verify観点
- V1 Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` 以外に差分がない。
- V2 Contract: proposal-only / human decision / auto-*禁止 / fail-closed が明記されている。
- V3 Integrity: Phase 1〜6 と AC/DoD/リスク台帳/CDC の対応が崩れていない。

### 修復ルール
- 修復は最大3回まで。
- `4回目相当` を要する場合は **即時 `held`** とし、原因と未解決項目のみ記録する。

## Phase 6: Proceed / Stop

### Proceed条件（Open準備完了）
- Draft→Open移行条件を **全件** 満たす。
- 人間承認ログ最小項目（日時・承認者・対象・判断）を確認済み。
- 「実装禁止解除条件」が次工程向け引継ぎ文に明示される。

### Stop条件（held）
- 合意未取得のまま次工程（実装・確定運用）へ進む要求。
- Verify修復が3回を超過。
- safeMode既定ON / 未レビュー保護 / fail-closed の後退要求。
- mock contract参照範囲を超えた CE1実装依存の仕様確定要求。
- 未定義競合（契約衝突・語彙衝突・責務分離崩壊）の検知。

## Draft→Open 移行条件（再掲）

- CD&C（Context / Decision / Consequences）が本Issue内で明文化されている。
- 依存I/Fと mock方針が記録され、実装作業へ越境していない。
- リスク台帳（R-CE2-01〜03）に予防策と停止条件が紐付いている。
- 人間承認ログの最小項目（日時・承認者・対象・判断）が記録されている。
- 「未承認なら held 継続」の fail-safe が残っている。

## 実装タスクへの引継ぎ文（承認後に使用）

> CE2は proposal-only 契約・safeMode境界・監査4点必須を満たした計画として承認済み。実装フェーズは本契約を変更せず、`accepted/rejected` 人間責務と fail-closed を維持すること。実装禁止の解除は、Open化後に人間承認ログが確認できた場合に限る。

## Validation Plan

- 実行コマンド:
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git status --short`
- 期待結果:
  - single-file scope で、Phase 1〜6、I/Fとmock方針、リスク台帳、Draft→Open条件、Proceed/Stop条件が確認できる。
- 未実施時の理由・代替検証:
  - なし（docs-checkのみ）。

## Stream E Draft昇格メモ（2026-05-01）

### AC/DoD/Validation/Dependency 明確化
- AC補足:
  - [ ] `Dependency status` が `確定` へ遷移する条件（CE-2 Open判定者/証跡）が記録されている。
  - [ ] Proceed判定前に `Approval Record`（日時・承認者・対象・判断）を確認する手順がある。
- DoD補足:
  - [ ] Open化可否を `Proceed / Hold / Stop` の三値で再判定できる。
  - [ ] 依存未確定時は `Hold` を維持する fail-safe が残っている。
- Validation補足（docs-check固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`

### Proceed（Open化可否）
- 判定: **Hold（依存未確定のため Open不可）**
- Stopper:
  1. `CE-2` の依存確定条件（誰が何を承認したか）が本Issue単体で未確定。
  2. `Approval Record` の実値（approved_by / approved_at / evidence）が未記入。


## Stream F preparation log（2026-05-02 / Draft-to-Open Preparation）

### Phase 1: Read（依存状態・固定キー確認）
- 依存状態再確認: `Dependency status=未確定（CE-2 Open判定待ち）` を維持。
- 固定契約再確認: proposal-only / human decision / auto-*禁止 / fail-closed の4点を再読し、矛盾なし。

### Phase 2: ADR/CDC明文化（必須）
- Context: CE-2依存未確定のため、Draftのまま判断材料整備を継続する必要がある。
- Decision: 本Issueは「Open化判断材料の整備」に限定し、実装・運用確定を禁止する。
- Consequences: 依存確定前の誤Proceedを抑止し、承認後の再開手順を維持できる。

### Phase 3: Plan（Open gate基準・AC/DoD補完）
- Open gate補完:
  1. `Dependency status=確定`（CE-2 Open判定者/証跡明記）。
  2. `Approval Record`（日時・承認者・対象・判断）充足。
  3. proposal-only / fail-closed / safeMode既定ON の後退なし。
- DoD補完: `Proceed / Hold / Stop` 三値再判定が再現可能であること。

### Phase 4: Execute（メモ整備のみ）
- 実施: Draft文面の再確認とOpen gate補完項目の明文化のみ。
- 非実施: 実装作業、契約値追加、承認なしの状態遷移。

### Phase 5: Verify（docs-check、3回修復上限）
- 実行予定（docs-check固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
- self-correction: `0/3`（上限超過なし）。

### Phase 6: Proceed/Stop（未承認/競合/超過は停止）
- 判定: **Hold**。
- 理由:
  1. CE-2依存の確定証跡が未入力。
  2. Approval Record が未充足。
- Stop条件: 未承認確定化要求 / 契約衝突 / self-correction 4回目相当を検知した場合は即時 `held`。


## Stream D update log（2026-05-03 / CE2 low-risk proposal lifecycle）

### Read（Phase 1: 対象ファイル最新同期）
- 対象: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみを再読し、single-file scope を再確認。
- 同期結果: proposal-only / human final decision / fail-closed / auto-*禁止 / `sourceBundleHash === bundleHash` 必須 の固定契約が本文内で維持されている。

### ADR C/D/C（Phase 2: 承認前提の明文化）
- Context: CE2は低リスク補助であっても意思決定責務の混線リスクがあるため、AIは提案に限定する必要がある。
- Decision: `status=proposed` のみAIが扱い、`accepted/rejected` は人間最終決定とする。未承認状態での Proceed は禁止し `held` を継続する。
- Consequences: 承認ログ（日時・承認者・対象・判断）未取得時は Go 判定不可。auto-*導線混入は No-Go として即時停止できる。

### Workflow（Phase 3: Plan→Execute→Verify→Proceed）
- Plan: AC/DoD不足の提案のみを行い、実装変更提案・状態確定提案を行わない。
- Execute: 文書整備のみを実施し、コード変更・他Issue編集を行わない。
- Verify: scope / contract / phase integrity を最大3回まで修復。4回目相当は `held` 固定で停止。
- Proceed: 承認ログ取得済みかつ No-Go 条件なしの場合のみ検討可。未承認時は Proceed しない。

### Gate（Phase 4: Proceed制御）
- Go条件:
  1. 承認ログ最小項目（approved_at / approved_by / target / decision / evidence）充足。
  2. proposal-only・human final decision・fail-closed の後退ゼロ。
- No-Go条件:
  1. 承認ログ未取得（`held` 継続）。
  2. auto-*導線（auto-apply / auto-confirm / auto-publish）混入。
  3. 未定義競合（契約衝突・語彙衝突・責務分離崩壊）を検知。
- Stopper: 修復3回超過、未定義競合、前提崩れ（依存確定証跡の欠落）が発生した時点で停止。

## Stream CE2 Draft昇格準備（2026-05-06 / Read→Plan→Execute→Verify→Proceed）

### Read（根拠再同期）
- 再同期対象: `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` / 本Issue既存フェーズ定義。
- 整合確認:
  - proposal-only（`status=proposed`）維持。
  - `accepted/rejected` は人間責務で固定。
  - `sourceBundleHash === bundleHash` 不一致時 fail-closed（`held`）維持。

### Plan（Draft→Open判断材料の明確化）
- AC明確化（Open判定ゲート）:
  - [ ] `Dependency status=確定` の証跡（日時/承認者/対象/判断/evidence）が本文に記録済み。
  - [ ] `Approval Record` 最小項目（approved_at / approved_by / target / decision）が充足。
  - [ ] proposal-only / fail-closed / safeMode既定ON 後退ゼロが確認可能。
- DoD明確化:
  - [ ] tri-state（Proceed/Hold/Stop）を同一条件で再判定可能。
  - [ ] 依存未確定時は自動的に Hold 継続（誤Proceed不可）。
  - [ ] docs-check結果と差分確認コマンドが再現可能。
- Validation明確化:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`

### Execute（文書整備のみ）
- 実施: Open判定に必要な AC/DoD/Validation の判定軸を本文へ明記。
- 非実施: 実装作業、依存の推測確定、承認記録の代入。

### Verify（停止条件付き）
- Verify結果: **Hold維持**（依存確定証跡と Approval Record 実値が未充足）。
- self-correction: `0/3`（超過なし）。
- Stop条件再掲: 4回目相当の修復要求、または未承認での Proceed 要求を検知した時点で `held` 固定。

### Proceed判定（現時点）
- 判定: **Hold（Draft継続）**
- Open移行に不足する項目:
  1. `Dependency status=確定` の一次証跡。
  2. `Approval Record` 実値（approved_by / approved_at / evidence）。
- CE1/CE2契約の境界を再確認し、CE1未確認時は仕様確定しないフェイルセーフを固定。

## Stream F integration log（2026-05-03 / Draft Gate Management）

### Read
- proposal-only 契約、監査4点、`sourceBundleHash===bundleHash`、Proceed禁止条件を再確認。

### CDC
- Context: CE-2依存/CE1契約確認が未確定のため、Open化条件の厳密化が必要。
- Decision: 実装禁止を維持し、Open化条件を「依存確定 + 承認ログ + 3段Verify通過」に限定。
- Consequences: 誤Proceedを抑止し、承認後の再開条件を単一化できる。

### Plan
- Open化条件（未達時Hold）
  1. `Dependency status=確定`（CE-2 Open判定証跡）
  2. `Approval Record`（日時/承認者/対象/判断）充足
  3. V1〜V3 Verify通過、self-correction `<=3`

### Execute
- 本Issue内のゲート定義整備のみ（実装・運用確定は非実施）。

### Verify（max3）
- Verify attempt: `1/3`
- 判定: Pass（条件定義は整合、依存/承認未充足でHold継続）。

### Proceed
- Decision: **Hold**。

### ADR明文化（Context / Decision / Consequences）
- Context: CE2はproposal-onlyを維持しつつ、`sourceBundleHash` をCE1の `bundleHash` と一致検証できる状態で管理する必要がある。
- Decision: `reviewState` のAI自動昇格を禁止し、Verifyの必須判定に `sourceBundleHash === bundleHash` を追加する。
- Consequences: 一致しない提案は `held` へ遷移し、承認待ちのまま停止するため、誤適用を抑止できる。

### Plan
- AC追加: `sourceBundleHash` 一致検証が明示されている。
- DoD追加: `reviewState` がAI操作で `human_reviewed` へ遷移しないことを確認できる。

### Execute
- 本Issue内の契約文言のみ更新（コード変更なし）。

## Stream D execution log（2026-05-04 / proposal-only safe advancement）

### Phase 1: Read（Plan）
- Read対象を `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` に固定し、CE2は proposal-only の判断準備に限定する方針を再確認。
- CE1は **参照限定**（mock contract）とし、CE1未確定項目をCE2実装前提にしない境界を固定。

### Phase 2: ADR/CDC（Execute）
#### Context
- CE2は「低リスクAI補助」の意思決定準備段階であり、実装着手前に責務分離（AI提案 / 人間確定）を文書契約として固定する必要がある。
- CE1依存は未確定要素を含むため、CE2側で仕様を先行確定すると契約衝突のリスクがある。

#### Decision
- 本Issueの作業範囲は `issue-CE2-low-risk-ai-assist.md` の文書整備に限定する（single-file fixed）。
- proposal-only 契約（`status=proposed` / `reviewState=unreviewed` / auto-*禁止 / fail-closed）を維持し、実装・運用変更は実施しない。
- Verifyは V1/V2/V3 の3段固定、修復は最大3回までとする。

#### Consequences
- CE1未確定項目の先行実装を回避でき、契約衝突時の誤Proceedを抑止できる。
- 短期的な前進は文書整備に限定されるが、承認後の実装再開条件が明確化される。

### Phase 3: Plan（Verify criteria）
- AC/DoD観点を再確認:
  1. Phase 1..6（Plan→Execute→Verify→Proceed）を欠落なく記述する。
  2. CE1未確定項目を実装前提にしない文言を保持する。
  3. ADR要素（Context/Decision/Consequences）を本ログで明文化する。
  4. Verify失敗時の自律修正上限（3回）を超えたら `held` で停止する。

### Phase 4: Execute（memo-only）
- 実施内容: Stream Dログの追加とゲート文言の補強（本ファイルのみ）。
- 非実施内容: コード変更、CE1契約の先行確定、Open化の強行。

### Phase 5: Verify（max 3 self-corrections）
- Attempt `1/3`: V1 scope check（single-file）を確認 -> Pass。
- Attempt `1/3`: V2 contract check（proposal-only / human decision / auto-*禁止 / fail-closed / `sourceBundleHash===bundleHash`）を確認 -> Pass。
- Attempt `1/3`: V3 integrity check（Phase 1..6 + ADR + AC/DoD整合）を確認 -> Pass。
- 判定: 修復不要（`self-correction=0/3` 追加修復なし）。

### Phase 6: Proceed / Stop
- 判定: **Hold継続**（proposal-onlyの安全前進）。
- Proceed不可理由:
  1. CE-2依存確定証跡および承認ログ実値が未充足。
  2. CE1未確定項目を実装前提にしない制約を維持する必要がある。
- Stop条件再確認: Verify 4回目相当が必要になった時点で `held` へ停止し、未解決項目のみ記録する。

### Verify
- docs-checkで single-file scope / 契約語 / フェイルセーフ条件を確認する。

### Proceed
- CE1契約確認ログ（承認者・日時・対象・証跡）が揃うまで **Hold継続**。

## Stream G single-issue pass（2026-05-03 / Draft individual processing）

### Phase: Read
- 対象を本ファイル単独に固定し、既存の固定契約（proposal-only / auto-*禁止 / fail-closed / CE1未確認時仕様確定禁止）を再確認。

### Phase: Plan（不足補完）
- Open化に必要な不足条件を以下へ集約。

#### Open化ゲート（AC / DoD / Validation / 依存条件）
| 区分 | 必須条件 | 判定方法 | 未充足時 |
| --- | --- | --- | --- |
| AC-DEP-1 | `Dependency status=確定` かつ CE-2判定者/証跡が記録済み | `Dependency status` 行と Approval Record を目視確認 | **Hold維持** |
| AC-SEC-1 | proposal-only + auto-*禁止 + fail-closed が同時に明記 | 本Issue内の Fixed Operation Contract と Verify観点を照合 | **Hold維持** |
| AC-TRACE-1 | `sourceBundleHash === bundleHash` のVerify必須化 | Verify観点V2の契約文言を確認 | **Hold維持** |
| DOD-GATE-1 | Proceed/Hold/Stop 三値で再判定可能 | Phase 6 と Draft→Open移行条件の整合確認 | **Hold維持** |
| DOD-GATE-2 | 依存未確定時にProceedしない fail-safe が明示 | Stop条件・Proceed条件を照合 | **Hold維持** |
| VAL-DOC-1 | docs-check 2コマンドが再現可能 | Validation Planのコマンド実行結果で確認 | **Hold維持** |

### Phase: ADR合意（必要時）
- 新規ADRは不要（既存 `ADR-0028` / `ADR-0001` の範囲内で契約補完が完結）。

### Phase: Execute（issueメモ更新のみ）
- 本セクション追加のみを実施。実装・仕様確定操作は未実施。

### Phase: Verify
- 修復回数カウンタ: `0/3`（超過なし）。
- 判定: `AC-DEP-1` 未充足のため Open化は不可。

### Phase: Proceed
- 最終判定: **Hold継続**。
- Hold理由（固定）:
  1. CE-2依存確定の承認証跡が未入力。
  2. Approval Record 実値（approved_by / approved_at / evidence）が未充足。

## Draft gate解消条件（Open化判定・合意形成専用 / 2026-05-03）

### Phase 1〜6 適合チェック（厳守）
- Phase 1 Read: 上位根拠（関連ADR/Spec）再読ログが当日付で記録されている。
- Phase 2 ADR/CDC: `Context / Decision / Consequences` が本Issue内で更新されている。
- Phase 3 Plan: AC/DoD/依存関係/停止条件が明文化されている。
- Phase 4 Execute: **メモ整備のみ** を実施し、実装変更（`03_Implement/**`）が 0 件である。
- Phase 5 Verify: docs-check 実行結果と self-correction 回数（`<=3`）が記録されている。
- Phase 6 Proceed/Stop: Open可否を `Proceed / Hold / Stop` の三値で記録している。

### Open化 AC（全件必須）
- [ ] AC-Open-1: 依存ステータスが `確定` であり、承認証跡（日時・承認者・対象・判断）が追跡可能。
- [ ] AC-Open-2: 本Issueの Go 条件と NoGo/Hold 条件が矛盾なく併記されている。
- [ ] AC-Open-3: docs-check 結果が最新化され、self-correction が `3回以内`。
- [ ] AC-Open-4: 実装禁止（proposal-only / docs-only / mock I/Fのみ など当該契約）を維持したまま判断情報が完結している。

### Open化 DoD（完了定義）
- [ ] DoD-Open-1: Open判定に必要な入力（AC/DoD/Dependency/Verification）が本Issue単体で再読可能。
- [ ] DoD-Open-2: 未承認・依存未確定・検証未達のいずれかで **自動的に Hold/Stop** へ遷移する fail-safe が残っている。
- [ ] DoD-Open-3: 次工程への引継ぎ文が「実装禁止解除条件」を1文で含む。

### 停止報告（Open化不可時）
- 判定: **Hold（Open化不可）**
- 停止理由: 依存または承認証跡が未確定のため、Draft gate を解消できない。
- 必須アクション（合意形成のみ）:
  1. 依存判定者が `Dependency status=確定` を記録。
  2. 承認ログ最小項目（日時・承認者・対象・判断）を補完。
  3. docs-check を再実行し、self-correction 回数を更新。
- 再開条件: 上記 1〜3 が揃った時点で Phase 6 を再判定する。

## Stream H CE2 Draft pass（2026-05-03 / proposal-only contract hardening）

### Phase 1 Read同期
- `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` の契約語に対し、本Issue内の `status` / `reviewState` / lifecycle 記述を照合。
- 照合結果: AIは `proposed` 限定、人間のみ `accepted/rejected` 決定、監査欠損時 fail-closed、`sourceBundleHash === bundleHash` 不一致時 `held` の固定契約と矛盾なし。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE2 Draft→Open準備では、proposal-only と人間責務分離を崩さずに判断材料を完結させる必要がある。
- Decision: 本Issueは docs-only の判断材料整備に限定し、auto-* 操作導線と AIによる `accepted/rejected` 変更経路を追加しない。
- Consequences: 実装前進は意図的に遅くなるが、責務混線・誤確定・監査欠損を Draft段階で封じる。

### Phase 3 Plan（AC/DoD不足補完）
- AC補完:
  - [ ] AC-H-1: proposal-only と human-only decision が同時に満たされる。
  - [ ] AC-H-2: `reviewState` の自動昇格禁止と fail-closed が Verify観点で再確認できる。
  - [ ] AC-H-3: 承認未取得時は Proceed せず `held` を維持する。
- DoD補完:
  - [ ] DoD-H-1: Open判定に必要な契約条件が本Issue単体で再読可能。
  - [ ] DoD-H-2: self-correction 回数管理（3回上限）が明示され、超過時停止条件がある。

### Phase 4 Execute（メモ整備のみ）
- 実施: 本Issueへの追記のみ（契約整理・不足AC/DoDの補完）。
- 非実施: 実装変更、状態確定、承認代行、auto-* 追加。

### Phase 5 Verify（scope / contract / phase integrity）
- V1 Scope: 本ファイル以外の差分がないことを確認（single-file fixed）。
- V2 Contract: proposal-only / human責務分離 / auto-*禁止 / 監査欠損fail-closed / hash一致必須 を確認。
- V3 Integrity: Phase 1〜6 の欠落がなく、AC/DoD/Stop条件の整合を確認。
- self-correction: `0/3`（上限超過なし）。

### Phase 6 Proceed / Stop
- 判定: **Hold継続**。
- 理由:
  1. 人間承認ログ最小項目（日時・承認者・対象・判断）が未充足。
  2. CE-2依存確定の証跡が未記録。
- ルール固定: 未承認・依存未確定・検証未達のいずれかを検知した場合は `held`（fail-closed）で停止し、4回目相当の修復要求は行わない。

## Stream F CE2 Draft昇格判定（2026-05-03 / Open readiness checkpoint）

### Phase 1: Read & Sync
- Draft理由を再抽出: `Dependency status=未確定` と `Approval Record未充足` が Open化阻害要因として継続。
- 契約固定点を再確認: proposal-only / human-only decision / auto-*禁止 / fail-closed / `sourceBundleHash===bundleHash` 必須。

### Phase 2: Plan（Open昇格の最小条件）
- **Scope**: 本Issue本文の判定材料整備のみ（docs-only / single-file fixed）。
- **Non-scope**: 実装変更、ADR更新、他Issue更新、状態遷移の強制実行。
- **Dependencies**:
  1. CE-2 Open判定の確定証跡（判定者・日時・対象・判断）
  2. Approval Record 実値（approved_by / approved_at / evidence）
- **検証観点**:
  - V1: single-file scope
  - V2: 固定契約語（proposal-only / fail-closed / auto-*禁止 / hash一致）
  - V3: Phase 1〜6 + AC/DoD + Proceed/Hold/Stop 三値整合

### Phase 3: Execute（issueメタ/本文整備）
- Open判定に必要な最小入力を本Issue内で再読可能な形に統合済み。
- 未承認時の fail-safe（`held` 継続）を維持し、Proceed条件を依存確定+承認ログ充足に限定。
- 実装作業は未実施（計画整備のみ）。

### Phase 4: Verify（self-correction上限3）
- Verify結果: **Pass（整合） / Open gateは未達**。
- self-correction: `0/3`（超過なし）。
- 未達項目:
  1. `Dependency status=確定` の証跡未記入。
  2. `Approval Record` 実値未記入。

### Phase 5: Proceed（Open化可否）
- 判定: **Open化不可（Hold継続）**。
- 阻害要因（具体）:
  1. CE-2依存確定ログ（判定者・日時・対象・判断）が欠落。
  2. Approval Record の `approved_by / approved_at / evidence` が未充足。
- 再開条件:
  1. 上記2点を記入。
  2. docs-check再実行で V1〜V3 を再確認。


## Open化準備ゲート（Stream K 2026-05-04）

### RACI（CE2 Draft→Open判定）
| Activity | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| proposal-only 契約の維持（`proposed`固定・auto-*禁止） | Stream D | System Owner | Security Officer | Platform Operator |
| Approval Record 確認（日時/承認者/対象/判断） | Platform Operator | System Owner | Stream D | Security Officer |
| 監査4点と `sourceBundleHash===bundleHash` 検証 | Stream D | Security Officer | Platform Operator | System Owner |
| Proceed/Hold/Stop 判定記録 | Stream D | System Owner | Security Officer | Platform Operator |

### Open化受入条件（確定版）
- [ ] AC-CE2-01: `Dependency status=確定` かつ CE-2 Open判定証跡（判定者・日時・リンク）を記録。
- [ ] AC-CE2-02: `Approval Record` の4項目（`approved_by` / `approved_at` / `target` / `decision`）が空欄なし。
- [ ] AC-CE2-03: proposal-only 契約、`reviewState` 閉集合、auto-*禁止、fail-closed が全文中で矛盾しない。
- [ ] AC-CE2-04: `sourceBundleHash===bundleHash` の不一致時 `held` が明記される。
- [ ] AC-CE2-05: Open化判定を `Proceed/Hold/Stop` 三値で再現できる。

### DoD（Open化準備完了の定義）
- [ ] DoD-CE2-01: 本Issue単体で Context/Decision/Consequences・AC・DoD・Validation・RACI が再読可能。
- [ ] DoD-CE2-02: docs-check証跡（validator / diff check / scope check）をログ化。
- [ ] DoD-CE2-03: blocker未解消時に `Hold` 維持で終了し、誤Proceedができない。

### Validation（docs-check固定 / 実行順）
1. `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
2. `rg -n "^## Phase [1-6]:|^### RACI|^### Open化受入条件|^### DoD" 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
3. `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
4. `git status --short`

### Blockers（Open不可条件）
- B-CE2-01: CE-2依存の判定証跡未入力。
- B-CE2-02: Approval Record 未充足（必須4項目欠落）。
- B-CE2-03: CE1契約未確認のまま仕様確定要求。
- B-CE2-04: self-correction 4回目相当。


## Stream E preparation log（2026-05-04 / Draft→Open昇格準備, proposal-only）

### Phase 1: Read
- `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` と本Issueを再照合し、`proposal-only`・`fail-closed`・`sourceBundleHash===bundleHash` 必須契約の維持を確認。
- 依存状態 `Dependency status=未確定` と `CE1 contract status=未確認` を再確認し、実装禁止境界を維持。

### Phase 2: Plan（AC/DoD不足補完）
- AC補完:
  - [ ] Open判定前に `Approval Record`（日時/承認者/対象/判断/evidence）を必須項目として充足。
  - [ ] `Proceed / Hold / Stop` 三値判定を同一基準で再演算可能。
- DoD補完:
  - [ ] 依存未確定時は `Hold` 維持、未定義競合時は即 `Stop(held)` を明記。
  - [ ] self-correction 上限 `<=3` を超えた場合は修復停止。

### Phase 3: Execute（proposal-only）
- 実施範囲は本Issue文書の準備記述のみに限定（実装/運用確定/状態遷移は非実施）。
- `auto-*` 禁止、AIによる `accepted/rejected` 自動確定禁止を再固定。

### Phase 4: Verify（gate条件整合）
- Gate整合チェック観点:
  1. Scope逸脱なし（single-file）。
  2. 契約語（proposal-only / human decision / fail-closed / hash一致）欠落なし。
  3. Open条件（依存確定 + 承認ログ + Verify通過）の全件一致。
- self-correction: `0/3`（超過なし）。

### Phase 5: Proceed（Open条件判定）
- 判定: **Hold**（依存未解放・承認ログ未充足のため）。
- 昇格提案条件（揃えばOpen提案可能）:
  1. `Dependency status=確定` の証跡記録。
  2. `Approval Record` 最小項目の実値記入。
  3. Verify 3段を再実行して pass。
- 停止条件: self-correction 4回目相当、または未定義競合（契約衝突/語彙衝突/責務衝突）を検知した場合は **Stop(held)**。

## Open化最終整備（proposal-only / 2026-05-04）

### Read→ADR/CDC→Plan→Execute→Verify→Proceed（固定運用）
1. **Read**: 上位根拠（ADR / schemas / 関連Issue）との差分を再読して語彙ドリフトを検知する。
2. **ADR/CDC**: Context / Decision / Consequences を本Issue内で閉じる（外部依存で確定しない）。
3. **Plan**: Open判定の AC / DoD / Validation / Stop 条件を先に固定する。
4. **Execute**: **blocker明文化・Open化条件定義・AC/DoD整備のみ** 実施し、実装化は行わない。
5. **Verify**: docs-check を基準に、自己修復は最大3回（4回目相当は Stop）で運用する。
6. **Proceed**: 依存確定と Approval Record が充足した場合のみ Proceed、それ以外は Hold/Stop。

### Blocker明文化（Open不可時の固定理由）
- 依存ステータス未確定、または承認証跡（日時/承認者/対象/判断/evidence）の欠落。
- proposal-only 契約（実装禁止 / auto-*禁止 / fail-closed）に抵触する要求の混入。
- Verify再試行が3回を超過、または未定義競合（契約衝突・責務分離崩壊）の検知。

### Open化条件（proposal-only gate）
- [ ] 条件1: 本Issue単体で Context/Decision/Consequences・AC・DoD・Validation・Proceed tri-state が再読可能。
- [ ] 条件2: docs-check の pass 記録と self-correction `<=3` が記録済み。
- [ ] 条件3: 依存確定証跡と Approval Record の最小項目が充足。
- [ ] 条件4: 実装タスク化を行わず、未承認依存を確定扱いしていない。

### Verify失敗時 Self-Correction ルール
- Attempt 1: 文言矛盾・欠落メタの修正。
- Attempt 2: Gate条件と Stop条件の再整列。
- Attempt 3: 依存/承認証跡の未充足を Hold理由へ明示。
- 4回目相当: **Stop**（超過または依存崩壊として終了）。


## Stream G execution log（2026-05-04 / proposal-only hard lock）

### Phase 1: Read
- `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` の契約語を再読し、CE2を候補提示専用に固定する前提を確認。
- CE1は完了待ちしない方針とし、I/Fは mock contract 参照のみに限定する。

### Phase 2: ADR
- Context: CE2は低リスク補助だが、責務混線を防ぐため proposal-only を不変条件として保持する必要がある。
- Decision: 自動採用（accepted化）/自動公開（publish/share相当）/自動review昇格（human_reviewed化）を禁止する契約を明文化。
- Consequences: 実装速度より統治・監査整合を優先し、未承認時は常に `held` を維持する。

### Phase 3: Plan
- AC-G-1: AI出力は `status=proposed` 固定、`accepted/rejected` は人間のみ。
- AC-G-2: auto-apply / auto-confirm / auto-publish / auto-review-promotion を禁止語として維持。
- AC-G-3: CE1依存は mock contract 参照のみとし、CE1完了待ちをProceed条件にしない。

### Phase 4: Execute
- 本Issue文書内の契約・運用条件のみ更新（実装詳細の追記なし、コード変更なし）。

### Phase 5: Verify
- V1 Scope: single-file fixed を維持。
- V2 Contract: proposal-only / 自動採用禁止 / 自動公開禁止 / 自動review昇格禁止 / fail-closed を確認。
- V3 Integrity: Read→ADR→Plan→Execute→Verify→Proceed の各Phase記述が存在。

### Phase 6: Proceed
- 判定: **Hold継続**。
- 条件: 人間承認ログ未充足時は Proceed せず `held` を維持。


## Stream H Proposal-Only Normalization（2026-05-04）

### Phase 1 Read
- 最新メタ再確認: `Status=Draft` / `Dependency status=未確定` / proposal-only契約維持。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: CE2は責務分離を崩すと自動確定リスクが高い。
- Decision: 本IssueはDraft昇格準備の文書整備に限定し、実装着手を禁止する。
- Consequences: Open判定までは `held` を維持でき、誤Proceedを回避できる。

### Phase 3 Plan（Open化条件 / Go-NoGo）
- Go: `Dependency status=確定` かつ `Approval Record`（日時/承認者/対象/判断）充足、V1〜V3通過。
- No-Go: 承認未充足、契約衝突、Verify 4回目相当。
- Conditional(Hold): 依存未確定だが契約整合は維持。

### Phase 4 Execute（proposal-only整備）
- 実施対象: 文言整備、ゲート定義、停止条件の明示。
- 非実施: 実装指示、状態遷移の自動化導線追加、運用確定。

### Phase 5 Verify（3回まで修復）
- 検証軸: scope固定 / proposal-only契約 / Phase整合。
- 失敗時: 最大3回まで修復し、超過時は `held`。

### Phase 6 Stopper
- 依存未確定・競合疑義・承認不足のいずれか検知で停止し、照会待ちに遷移する。


## Stream G execution pass（2026-05-04 / CE2 P1）

### Phase Start Re-read
- 対象再読: `issue-CE2-low-risk-ai-assist.md` をPhase開始時に再読し、proposal-only / fail-closed / self-correction上限の固定条件を再確認。

### Plan → Execute → Verify → Proceed
- Plan: Open判定に必要な判定メタ（Context/Decision/Consequences, AC/DoD, Proceed tri-state）を保持。
- Execute: docs-onlyで文言整備し、実装・状態遷移の確定化を行わない。
- Verify: docs-check前提で整合確認、self-correction `<=3` を維持。
- Proceed: 依存確定証跡未充足のため **Hold継続**。

### ADR task C / D / Csq
- Context: CE2は人間責務境界（accepted/rejected）を先に固定しないと誤確定リスクが高い。
- Decision: 本IssueをOpen判定準備品質まで整備し、proposal-only契約を維持する。
- Consequences: 実装前に監査可能性と停止条件が担保され、誤Proceedを抑止できる。


## Phase 6: Proceed / Hold 判定（最終）

### Open昇格条件（Proceed）
- CE0 契約凍結との差分がなく、CE2文言が `proposal-only` / `fail-closed` / `auto-*禁止` を維持している。
- CE1 参照I/Fに対して **推測補完なし** で整合が取れている（未確定は `TBD` 明示）。
- Verify（V1〜V3）を3回以内で通過し、承認ログ最小項目（日時・承認者・対象・判断）が確認済み。

### Hold条件（停止）
- CE1未確定を仮定で補完しないと文章が成立しない。
- `reviewState` 自動昇格・`auto-apply/confirm/publish` 許容・`fail-open` を示唆する記述が混入。
- Verify修復が3回を超過、または依存表記（CE0/CE1）に矛盾が残る。

### Stopメモ（Fail-safe）
- CE1未確定は推測で埋めず、`status=held` で停止する。

## Stream G pre-open gate pass（2026-05-05 / proposal-only）

### Phase 1: Read（依存・停止条件の再確認）
- 本Issueを単体再読し、`Draft gate` 判定に必要な `AC/DoD/Proceed tri-state/Stopper` の存在を確認。
- 依存未解決のまま実装へ進まない原則を再固定（推測Go判定を禁止）。

### Phase 2: Plan（不足AC/DoD提案）
- AC追加提案（Open化ゲート）:
  - [ ] 依存確定証跡（日時・承認者・対象・判断・evidence）が明記される。
  - [ ] Approval Record 未充足時は `Proceed=Hold` を維持する。
  - [ ] docs-only / proposal-only の境界逸脱がない。
- DoD追加提案（Open化ゲート）:
  - [ ] Open可否を `Proceed/Hold/Stop` 三値で再判定可能。
  - [ ] self-correction `<=3` を超えた場合は `Stop` へ遷移。

### Phase 3: ADR（Context / Decision / Consequences）
- Context: 依存が揃うまでの待機期間でも、Open判定材料を先に固定して再作業を削減する必要がある。
- Decision: 実装・本文改稿には進まず、Open化ゲートと依存I/F（mock可能範囲）だけを先行定義する。
- Consequences: 依存完了後に即Open判定できる一方、未承認時の誤Proceedを抑止できる。

### Phase 4: Execute（依存・検証条件・停止条件の明文化のみ）
- Dependency I/F（mock-first）:
  - `ApprovalRecordIF`: `{approved_at, approved_by, target_issue, decision, evidence}`
  - `DependencyStatusIF`: `{dependency_id, status, confirmed_by, confirmed_at}`
  - `GateVerdictIF`: `{proceed_decision, unmet_conditions[], checked_at}`
- mock運用規約:
  - 依存本体未接続時は `mock:*` 値でI/F形式のみ検証。
  - mockでも fail-closed を維持し、必須キー欠損は `NoGo/Hold`。

### Phase 5: Verify（Open化ゲート検証）
- 検証条件:
  1. `AC/DoD/Proceed tri-state/Stopper` が本文内で再読可能。
  2. 依存証跡が未充足なら `Hold` のまま。
  3. self-correction 上限超過時 `Stop` に遷移可能。
- 検証失敗時: 3回まで自己修復し、4回目相当は `Stop`。

### Phase 6: Proceed（現時点判定）
- 判定: **Hold（依存未解決）**。
- Open化解除条件（全件必須）:
  1. 依存確定証跡の充足。
  2. Approval Record の充足。
  3. proposal-only / docs-only / fail-closed の維持。

## Stream E execution log（2026-05-06 / CE0-CE2 planning lane / contract-check enforced）

### Phase 1 Read（CE0/CE1依存確認）
- 参照元を `issue-CE0-contract-freeze.md` と `issue-CE1-context-query-bundle-foundation.md` に固定し、CE2側は read-only dependency として扱うことを再確認。
- CE0 canonical No-Go（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）を再確認。
- CE1固定語彙（`preview_required` / `unknown_contract_key` / `nondeterministic_bundle`）と hash決定論前提（`sourceBundleHash === bundleHash`）の参照整合を再確認。

### Phase 2 Contractチェック（Aレーン契約参照）
- Aレーン契約の未確定要素が残る場合は CE2を `held` 維持する方針を固定。
- shared resource 更新要求、または他レーン競合要求が発生した場合は CE2作業を停止する fail-safe を再確認。
- CE2側では契約の再定義・語彙追加を行わず、proposal-only 契約の参照適用に限定する。

### Phase 3 Mock-first計画（A2観点）
- Mock-Decision-Log / Mock-Audit-Matrix / Mock-Policy-Gate の3系統で A2検証を実施する計画を維持。
- 正常系は `status=proposed` のみ、異常系は `auto-*混入` / `監査欠損` / `bundleHash不一致` の3種で fail-closed 判定を固定。
- 実装依存（backend/frontend/worker）を持ち込まず、文書内 contract check だけで検証可能な粒度を維持。

### Phase 4 実装準備（A3前提の検証計画）
- A3進行前提として、承認ログ最小項目（`approved_at / approved_by / target / decision / evidence`）の充足確認を必須化。
- 実装禁止解除条件を「A契約確定 + Approval Record充足 + No-Goゼロ」のAND条件として明文化。
- A3前提が1つでも欠ける場合は Proceedせず `held` を継続する。

### Phase 5 Verify（整合性監査）
- Verify checklist:
  1. single-file scope 維持（本Issue以外に差分なし）
  2. proposal-only / human decision / fail-closed 文言の後退なし
  3. CE0/CE1参照語彙との衝突なし
  4. A契約未確定時の停止条件が明記されている
- 判定: **Hold-Ready**（契約確定待ち）。
- fail-safe result: A契約未確定・shared resource更新要求・他レーン競合のいずれか検知時は即時停止。


## Stream C 直列Phase運用ログ（2026-05-06）

- Phase 1 Read同期: 実施済み（ADR-0028 / ADR-0001 / schemas.md の契約語を再照合）。
- Phase 2 CE1契約参照チェック: `issue-CE1-context-query-bundle-foundation.md` を**参照限定**で確認し、`ContextQueryV1/ContextBundleV1` は未確定要素を含むため CE2は proposal-only を維持。
- Phase 3 Plan→Execute→Verify→Proceed: 本Issueは docs整備のみ実施、Proceedは人間承認ログ取得まで禁止。
- Phase 4 Self-Correction: Verify失敗時の自己修復は最大3回。4回目相当は `held` 固定。
- Phase 5 Stopper: 予定超過・前提崩壊（CE1契約破綻）・契約競合発生時は即時停止し `held` へ遷移。

### CE1契約未確定時の扱い（proposal-only固定）
- CE1 I/Fに未確定要素/差分が残る場合、CE2は**契約変更提案のみ**を許可し、実装・運用導線追加を禁止する。
- `sourceBundleHash === bundleHash` の照合不能時は fail-closed で `held`。
- unknown contract key を許容せず、closed-world前提のまま判定する。

## Stream C update（2026-05-06 / Phase C Read→ADR→Plan→Execute→Verify→Proceed）

### Phase 1 Read（Status / Dependencies整合確認）
- Status再確認: `Draft` を維持（Open未移行）。
- Dependencies再確認: CE0契約依存 + CE1 I/F依存（mock切断可）。`Dependency status=未確定` を維持。
- CE1参照制約: CE1契約は参照のみ。CE1仕様の確定化・CE1ファイル編集は行わない。

### Phase 2 ADR C/D/C
- Context: CE2は low-risk でも意思決定責務混線リスクがあるため、proposal-only を壊さずに Open判断材料を整備する必要がある。
- Decision: CE2は proposal-only のまま、mock前提I/F接続条件のみ整理し、実装詳細は確定しない。
- Consequences: 実装着手速度は抑制されるが、未承認Proceedと自動確定経路の混入を防止できる。

### Phase 3 Plan→Execute（mock前提I/F接続条件のみ）
- Plan（I/F接続条件）:
  1. `Proposal I/F`: `status=proposed` + `reviewState=unreviewed` + `sourceBundleHash` 必須。
  2. `Decision I/F`: 人間入力でのみ `accepted/rejected/held` を記録。
  3. `Audit I/F`: `query/bundle/proposal/apply` 4点欠損時は fail-closed。
- Execute: 文書整備のみ（実装手順・内部アルゴリズム確定は非実施）。

### Phase 4 Verify（draft gate/Open移行/非目標）
- Draft gate条件: proposal-only維持、auto-*禁止、`sourceBundleHash===bundleHash` 不一致時 `held`。
- Open移行条件: `Dependency status=確定` の証跡 + Approval Record最小項目充足 + docs-check pass。
- 非目標: CE1実装依存の仕様確定、状態遷移自動化、運用本番化。

### Phase 5 Proceed 判定
- 判定: **Hold**。
- 根拠: 依存確定証跡とApproval Record実値が未充足。依存未確定のままOpen化を強行しない。

## Stream G execution log（2026-05-06 / CE2 Low-Risk AI Assist Draft整備専任）

### Phase 1: Read同期（最新状態確認）
#### Plan
- 変更対象キーを `Status / Priority / Dependencies / Dependency status / CE1 contract status` の抽出結果整理に限定。
- 参照専用ファイル（CE0/CE1/ADR-0028/ADR-0001/schemas）との語彙一致を確認し、差分を列挙する。

#### Execute
- 抽出結果:
  - `Status=Draft`
  - `Priority=P1`
  - `Dependencies=CE0契約依存 + CE1 I/F依存（mock切断可）`
  - `Dependency status=未確定（CE-2 Open判定待ち）`
  - `CE1 contract status=参照限定（CE1完了待ちは不要。mock contract参照のみ）`
- 語彙整合:
  - CE0由来の No-Go 方針（auto-*禁止 / safeMode後退禁止）と矛盾なし。
  - CE1由来の hash・closed-world 前提（`sourceBundleHash===bundleHash` / unknown key不許容）と矛盾なし。

#### Verify
- AC/DoD不足を点検し、Draft→Open判定の証跡項目（approval/evidence）が未充足であることを明示。
- 禁止事項違反（Allowlist外編集・実装変更）はなし。
- self-correction: `0/3`。

#### Proceed
- Phase 1 合格。Phase 2へ進行。

### Phase 2: ADR（Context / Decision / Consequences）明文化
#### Plan
- CE2の Draft→Open判断に必須な C/D/C を、CE0依存・CE1 mock切断条件・禁止導線の3観点で明文化する。

#### Execute
- **Context**: CE2は low-risk 補助でも、AIの自動確定経路が混入すると責務分離が崩壊するため、proposal-only 契約を固定する必要がある。
- **Decision**:
  1. CE0契約は read-only 参照とし、CE2側で契約再定義しない。
  2. CE1依存は mock contract参照で切断可能とし、CE1完了待ちをOpen条件にしない。
  3. `auto-apply / auto-confirm / auto-publish` と `unreviewed -> human_reviewed` の自動昇格導線を禁止する。
- **Consequences**:
  - 責務分離と監査可能性は強化される。
  - 承認ログ未充足時は `held` 維持となり、短期速度は制限される。

#### Verify
- C/D/Cに曖昧語（実装確定を示す語）が混入していないことを確認。
- CE0/CE1との用語衝突なし。
- self-correction: `0/3`。

#### Proceed
- Phase 2 合格。Phase 3へ進行。

### Phase 3: Plan（AC/DoD定義）
#### Plan
- Draft→Open遷移判定に必要な AC/DoD を「依存定義」「用語一貫性」「停止条件」「非対象範囲」で再定義する。

#### Execute
- AC（Open候補判定）:
  1. 依存関係が「待機」ではなく「参照条件（CE0 read-only / CE1 mock参照）」で記述されている。
  2. `status / reviewState / lifecycle` が閉集合語彙で一貫している。
  3. 停止条件（self-correction超過・未定義競合・未承認Proceed禁止）が明示されている。
  4. 非対象範囲（実装・運用変更禁止）が明示されている。
- DoD:
  1. tri-state（Proceed/Hold/Stop）を同一根拠で再判定できる。
  2. Approval Record最小項目（approved_at / approved_by / target / decision / evidence）がチェック対象として定義済み。

#### Verify
- AC/DoDが既存 fail-safe（fail-closed, safeMode後退禁止）を弱めていないことを確認。
- self-correction: `0/3`。

#### Proceed
- Phase 3 合格。Phase 4へ進行。

### Phase 4: Execute（文書整備）
#### Plan
- CE2ファイル内の契約語彙、依存式、mock-first境界、禁止導線を明示し、実装記述を追加しない。

#### Execute
- 契約語彙を `proposal-only / human decision / fail-closed / held` に固定。
- 依存式を「CE0=契約参照」「CE1=mock contract参照」に整理。
- mock-first境界を「Decision Log/Audit Matrix/Policy Gateの形式検証」に限定。
- 禁止導線を auto-* と reviewState自動昇格の2系統で明記。

#### Verify
- Allowlist外変更なし。
- 実装タスク・運用変更手順の追記なし。
- self-correction: `0/3`。

#### Proceed
- Phase 4 合格。Phase 5へ進行。

### Phase 5: Verify（自己検証）
#### Plan
- AC/DoDチェック、依存整合、禁止事項違反の有無を点検し、必要なら3回以内で修復する。

#### Execute
- AC/DoDチェック結果:
  - AC1（参照条件化）: pass
  - AC2（語彙一貫）: pass
  - AC3（停止条件明記）: pass
  - AC4（非対象範囲明記）: pass
  - DoD1（三値再判定）: pass
  - DoD2（Approval Record定義）: pass
- 依存整合:
  - CE0契約再定義なし。
  - CE1はmock参照限定で整合。
- 禁止事項違反: なし。

#### Verify
- self-correction: `0/3`（修復不要）。
- 停止条件該当: なし。

#### Proceed
- Phase 5 合格。Phase 6へ進行。

### Phase 6: Proceed（完了判定）
#### Plan
- Done化せず、Open候補またはDraft継続理由を明記し、次アクションを責務付きで整理する。

#### Execute
- 判定: **Open候補（条件付き）**。
- なお現時点は Approval Record実値未記入のため、運用上の最終判定は **Hold継続**。

#### Verify
- Draft範囲逸脱なし（実装・運用変更なし）。
- tri-state 判定の再現可能性を維持。

#### Proceed（Next Action Block）
- **Who**: System Owner + Security Officer（人間承認責務）
- **What**: `Dependency status=確定` 証跡と `Approval Record` 実値（approved_at / approved_by / target / decision / evidence）を記入
- **Condition**: proposal-only / fail-closed / safeMode既定ON / auto-*禁止 の後退ゼロを再確認後にのみ Draft→Open 判定を実施

## Stream G update（2026-05-06 / CE2下流提案仕様化・実装着手前）

### Phase: Read同期 → ADR様式整理 → Plan → Execute（モック前提のI/F合意）→ Verify → Proceed

#### Read同期
- `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` の契約語彙を再照合し、`proposal-only` / `fail-closed` / `reviewState閉集合` の3点を再固定。
- 依存の扱いは **契約参照のみ** とし、CE1実装への依存要求はスコープ外として隔離。

#### ADR様式整理（Context / Decision / Consequences）
- Context: CE2は実装前に責務分離（AI提案と人間確定）を凍結しないと、承認経路と監査経路が混線する。
- Decision: CE2下流提案仕様は mock I/F 合意までを対象とし、実装依存（実データ接続・実運用連携）は禁止。
- Consequences: 監査可能性を維持したまま、実装着手前の合意材料を単独再読可能に保持できる。

#### Plan（実装前合意条件）
- AC-G1: `status=proposed` / `reviewState=unreviewed` / `sourceBundleHash` 必須を I/F 合意条件として固定。
- AC-G2: 監査4点（`query/bundle/proposal/apply`）欠損時は常に `held`（No-Go）。
- AC-G3: 承認未取得時は Proceed 禁止を維持。
- DoD-G1: 本Issue単体で tri-state（Proceed/Hold/Stop）を再判定可能。
- DoD-G2: self-correction は **最大3回**、4回目相当は即時停止（`held`）。

#### Execute（モック前提のI/F合意）
- Mock Proposal I/F:
  - input: `equivalenceKey`, `bundleHash`, `sourceBundleHash=mock:<64hex>`
  - output: `status=proposed`, `reviewState=unreviewed`, `lifecycle=proposed|held`
- Mock Decision I/F:
  - human actionのみ `accepted/rejected/held` を記録可能（AI起因の状態確定は不可）
- Mock Audit I/F:
  - `query -> bundle -> proposal -> apply` の順序検査と存在検査を実施
  - 1件でも欠損・順序逆転があれば fail-closed

#### Verify（3回自己修復上限）
- V1: single-file scope（CE2ファイルのみ差分）
- V2: 契約語彙（proposal-only / auto-*禁止 / fail-closed / human decision）
- V3: Phase欠落・AC/DoD/tri-state整合
- self-correction: `0/3`（本更新時点）

#### Proceed
- 判定: **Hold**（承認証跡未入力のため）。
- Proceed解除条件: 人間承認ログ（日時・承認者・対象・判断）充足後に再判定。


## Stream C update（2026-05-07 / CE2 Draft→Open準備 / proposal-only）

### Phase 1: Read（CE0/CE1契約再確認）
- `issue-CE0-contract-freeze.md` の Contract Freeze を read-only 参照し、No-Go canonical IDs と safeMode既定後退禁止を再確認。
- `issue-CE1-context-query-bundle-foundation.md` の handoff keys（`sourceBundleHash === bundleHash` / `equivalenceKey + bundleHash`）を参照し、CE2は mock contract 接続のみで進める方針を再確認。
- CE2は proposal-only の判断準備に限定し、実装・状態遷移確定・運用確定を禁止する前提を再同期。

### Phase 2: ADR（Context / Decision / Consequences 追記）
- **Context**: CE2は低リスクAI補助であっても、意思決定責務分離（AI提案 vs 人間確定）を先に固定しないと downstream で誤Proceedが起こる。
- **Decision**: CE2 Open準備では `status=proposed` 固定、`reviewState=unreviewed` 固定、`accepted/rejected` は人間責務固定、監査4点欠損時fail-closed固定を維持する。
- **Consequences**: CE1未実装でもmockで契約検証を継続できる一方、承認未取得時は `held` 継続となり短期速度より安全を優先する。

### Phase 3: Plan（Open化判定 AC / DoD / Validation 固定）
- AC追加（Open gate）:
  - [ ] `Approval Record`（日時・承認者・対象・判断）が記録されている。
  - [ ] `Dependency status=確定` の根拠（判定者・証跡）が本文で追跡可能。
  - [ ] proposal-only / auto-*禁止 / fail-closed / safeMode既定ON後退なしが同時成立。
- DoD追加:
  - [ ] `Proceed / Hold / Stop` 三値で再判定可能。
  - [ ] 依存未確定・承認未充足時は `Hold` を維持する fail-safe が残存。
- Validation（docs-only）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`
  - `git diff --check -- 01_Plans/issues/issue-CE2-low-risk-ai-assist.md`

### Phase 4: Execute（メモ整備のみ / mock I/F接続条件）
- 実施: 本Issue内の判断軸を補強し、mock接続条件を明文化。
- mock I/F接続条件（実装非依存）:
  1. Proposal出力は常に `status=proposed` かつ `reviewState=unreviewed`。
  2. Verify時に `sourceBundleHash === bundleHash` を必須比較。
  3. 監査4点（`query/bundle/proposal/apply`）が1つでも欠損なら fail-closed（`held`）。
- 非実施: backend/frontend/schema/API実装変更、運用確定、承認代行。

### Phase 5: Verify（AC/DoD・依存・語彙統一チェック）
- self-repair attempt: `1/3`（語彙を `proposal-only / fail-closed / held` に統一）。
- self-repair attempt: `2/3`（Open gate の `Approval Record` 要件を再掲）。
- self-repair attempt: `3/3`（mock I/F条件と Proceed条件の対応を明示）。
- 判定: 3回以内で整合完了、超過なし。

### Phase 6: Proceed / Stop（Open候補可否）
- 判定: **Open候補化は条件付き可（Conditional Open Candidate）**。
- Open化の前提（未充足ならHold）:
  1. `Dependency status=確定` の証跡入力。
  2. `Approval Record` 4項目（日時・承認者・対象・判断）入力。
  3. proposal-only / fail-closed / safeMode境界の後退ゼロ確認。
- 停止条件: 前提不整合・契約競合・4回目修復要求のいずれか検知時は即時 `held`。

## Stream D CE2 Open移行品質整備（2026-05-07 / Phase 1→5）

### Phase 1 Read（固定順序の再同期）
- Read 実施: `ADR-0028` / `ADR-0001` / `02_Architecture/schemas.md` / 本Issue既存ログを再読し、proposal-only契約と語彙集合（`status` / `reviewState` / `lifecycle`）の衝突がないことを確認。
- 範囲確認: Stream Dの編集範囲を本Issueに固定し、`03_Implement/*` を含む実装領域へ越境しないことを再宣言。

### Phase 2 ADR補強（Context / Decision / Consequences）
#### Context
- CE2 DraftはOpen移行前に「実装依存を切断した意思決定準備文書」であることを明確化する必要がある。
- 依存契約（CE0/CE1）が未確定のまま実装前提を書くと、責務分離崩壊と誤Proceedのリスクが高い。

#### Decision
- CE2 Draftは **proposal-only contract lock** を維持し、実装仕様・実行手順・運用確定値の新規追加を禁止する。
- tri-state 判定は `Proceed / Hold / Stop` を維持し、依存契約未確定時は `Hold` を唯一許可する。
- `sourceBundleHash === bundleHash` 不一致、監査4点欠損、auto-*導線混入のいずれかを検知した場合は `Stop`（`held`）で停止する。

#### Consequences
- Open移行判定に必要な文脈が ADR 形式で再読可能になり、実装依存の混入を抑制できる。
- 短期的には進行速度が下がるが、依存契約確定前の誤実装着手を防止できる。

### Phase 3 AC/DoD強化（Open判定専用）
#### AC 追加（Open候補に必要な最小条件）
- [ ] CE0/CE1 の依存契約確定証跡（日時/承認者/対象/判断/evidence）が本Issueから参照可能。
- [ ] proposal-only / human final decision / fail-closed / safeMode既定ON 後退ゼロが同一セクションで確認可能。
- [ ] `sourceBundleHash === bundleHash` 一致必須が Verify 条件として明示されている。

#### DoD 追加（Stream D完了条件）
- [ ] 実装依存の切断方針（mock contract参照のみ、実データ接続禁止）が明文化されている。
- [ ] tri-state 再判定の入力（依存証跡・承認ログ・Verify結果）と出力（Proceed/Hold/Stop）が追跡可能。
- [ ] 依存契約未確定時の Hold 理由が1文で再利用可能。

### Phase 4 Verify（docs-check / max 3 repairs）
- Verify V1（scope）: 本Issue単独差分であることを `git diff --` と `git status --short` で確認。
- Verify V2（contract）: proposal-only / auto-*禁止 / fail-closed / human decision / hash一致必須の記述を目視照合。
- Verify V3（integrity）: Phase 1〜5、AC/DoD、Proceed/Hold/Stop、Stop条件の整合を確認。
- self-correction: `0/3`（修復超過なし）。

### Phase 5 昇格判定（Draft→Open）
- 判定: **Hold（Open移行不可）**。
- Hold理由（依存契約未確定のため停止）:
  1. CE0/CE1 依存契約の一次証跡（承認済みログ）が未提示。
  2. Approval Record 実値（approved_by / approved_at / evidence）が未充足。
  3. 上記未充足のため、実装依存切断を維持したまま Draft継続が唯一の安全選択。
- Stop宣言: 未承認での Proceed 要求または契約衝突検知時は、即時 `held` で停止し追加提案を行わない。


## Assumption Log（CE1契約前提 / CE2 Draft）

| ID | Assumption（CE1前提） | 根拠 | 破綻時の扱い |
| --- | --- | --- | --- |
| A-CE2-01 | CE1の `ContextQuery/ContextBundle` は read-only contract として参照可能である。 | `schemas.md` CE1/CE2/CE4 freeze 節 | CE2を `held` に戻し、CE1再確認が完了するまで Proceed禁止。 |
| A-CE2-02 | `sourceBundleHash === bundleHash` 検証は CE2側でも fail-closed として適用できる。 | CE0/CE1固定契約（hash deterministic） | 不一致または未検証なら No-Go とし、Draft更新のみ許容。 |
| A-CE2-03 | CE1未実装でも mock contract で CE2判断材料を整備できる。 | mock-first 方針（契約先行） | 実装依存要求が出た時点で scope逸脱として Stop。 |

## Draft→Open 昇格条件（CE2 / contract-only gate）

- [ ] Context / Decision / Consequences が本Issue内で矛盾なく再読可能。
- [ ] Assumption Log（A-CE2-01〜03）に未解決破綻がない。
- [ ] proposal-only / human final decision / fail-closed / safeMode既定ON の後退がゼロ。
- [ ] Approval Record（日時・承認者・対象・判断・evidence）が記録済み。
- [ ] Verify（V1〜V3）を最大3回以内で完了し、4回目相当に到達していない。
