# Issue Draft: CE2 Low-Risk AI Assist（CE2意思決定準備 / proposal-only contract lock）

- Type: Process / Decision preparation
- Status: Draft
- Priority: P1
- Owner: Stream G（CE2 Draft整備専任）
- Scope: `01_Plans/issues/issue-CE2-low-risk-ai-assist.md` のみ（single-file fixed）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `ADR-0001`, `02_Architecture/schemas.md`
- Dependencies: `CE-2`
- Dependency status: `未確定（CE-2 Open判定待ち）`
- Expected verification level: `docs-check`

## Fixed Operation Contract（2026-05-01）

- proposal-only 原則を固定し、AIは候補提示（`status=proposed`）のみを実施する。
- `accepted / rejected` は人間責務。AIによる自動確定経路は作成しない。
- Auto操作（`auto-apply / auto-confirm / auto-publish`）を禁止する。
- `reviewState` は `unreviewed | human_reviewed` の閉集合とし、AI提案は常に `unreviewed`。
- lifecycle は `proposed | accepted | rejected | held` の閉集合を維持する。
- 監査4点（`query / bundle / proposal / apply`）が欠損した場合は fail-closed。
- **合意未取得時は CE2実装へ進まない（Proceed禁止）。**

## Mandatory Workflow（Phase 1〜6 固定）

1. **Phase 1 Read同期**: `ADR-0028` / `ADR-0001` / `schemas.md` の語彙と契約を照合し、矛盾を解消する。
2. **Phase 2 ADR/CDC**: Context / Decision / Consequences を本Issue内に固定し、Draft→Open判断材料を明文化する。
3. **Phase 3 Plan（AC/DoD補完）**: 受入条件・DoD・非機能制約・停止条件を先に固定する。
4. **Phase 4 Execute（メモ整備のみ）**: 本Issue内の記述・表・トレーサビリティを整備し、実装は行わない。
5. **Phase 5 Verify（最大3回修復）**:
   - V1: single-file scope逸脱チェック
   - V2: proposal-only / human decision / fail-closed 文言チェック
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

## Phase 3: Plan（AC/DoD補完）

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
- Proposal I/F: AI候補出力（`status=proposed`, `reviewState=unreviewed`）。
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
