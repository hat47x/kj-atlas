# Issue Draft: CE2 低リスクAI支援（proposal-only契約固定）

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Stream D (CE0/CE1/CE2/CE4 contract-first planning only)
- Scope: `01_Plans/issues/`（Stream D: contract-only / mock-first / docs-only）
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `docs-check`

## Stream D Phase execution record（2026-04-18 / CE2 low-risk assist）

### Phase 1: Read（再読結果）
- 契約ID固定: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`。
- 禁止事項固定: auto-apply、`human_reviewed` 自動昇格、safeMode後退。
- mock依存切断: CE1未完了でも `sourceBundleHash=mock:<hash>` 前提で進行。

### Phase 2: ADR CDC（変更判定）
- 本更新は既存提案I/Fの確認であり、列挙値変更（`status` / `reviewState`）なし。
- CDC追加は不要（意味変更時のみ承認待ち）。

### Phase 3: Plan（API signature / data type 先行固定）
- Proposal最小I/Fを凍結: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`。
- 列挙凍結: `status=proposed|accepted|rejected|held` / `reviewState=unreviewed|human_reviewed`。

### Phase 4: Execute（contract-first + mock-first）
- 実装待機禁止。proposal-only境界（apply責務外）を維持。
- drift検知時は `status=held` で fail-safe停止。

### Phase 5: Verify（docs-check + self-correction <=3）
- 検証観点: 必須フィールド完備、auto-apply 0件、自動昇格0件、drift-stop記述整合。
- self-correction 3回超過で停止。

### Phase 6: Proceed（進行条件）
- 衝突0・安全後退0・同値性条件充足時のみ Proceed。


## Requirement meta I/F（共通キー）
- RequirementID: `CE2-LOW-RISK-AI-ASSIST`
- RequirementStatement: AI提案は全件 proposalId+diff を持つ patch として扱う。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE1最小I/F（ContextQuery + ContextBundle + bundleHash）をモック契約として利用 / 操作=提案生成 / 期待結果=自動適用0件 / 除外=最終結論の自動生成
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `D` (CE0/CE1/CE2/CE4 contract-first planning only / docs-only)
- DecisionQueueRef: `CE2-DRIFT-STOP`

## Stream D 専属実行プロトコル（2026-04-18 / Contract-first + mock-first）

### Scope lock（編集境界）

- 編集対象は以下5Issueのみ（本Issueを含む）:
  - `issue-CE0-contract-freeze.md`
  - `issue-CE0-core-graph-repositioning.md`
  - `issue-CE1-context-query-bundle-foundation.md`
  - `issue-CE2-low-risk-ai-assist.md`
  - `issue-CE4-api-cli-audit-integration.md`
- `03_Implement/**` と shared統合3ファイル（README/dashboard/decision-pack）、他Issueは編集禁止。
- 本Issueは実装依存を持ち込まない（contract-only / docs-only）。

### 固定フェーズ（Phase 1〜6）

1. **Phase 1 Read**: 契約ID・禁止事項・mock依存切断方針を再確認する。
2. **Phase 2 ADR-CDC**: 変更が必要な場合のみ `Context / Decision / Consequences` を明文化し、承認がない限り先へ進まない。
3. **Phase 3 Plan**: APIシグネチャ/データ型を先行固定し、AC/DoD不足をドラフト合意する。
4. **Phase 4 Execute**: contract-first + mock-first で依存を切断し、実装待機を禁止する。
5. **Phase 5 Verify**: docs-check + 契約ID整合を検証し、失敗時は自己修復を最大3回まで許可する。
6. **Phase 6 Proceed**: 契約確定（衝突0 / 安全後退0）時のみ次段へ進む。

### 強制サイクル（各Phase内で固定）

- **Plan → Execute → Verify → Proceed** の順序を必須化する（省略・逆順禁止）。

### Fail-safe（停止条件）

- 契約未確定、または安全境界後退（safeMode既定ONの破壊、auto-apply許容、review自動昇格許容）を検知した場合は即停止。
- Verify自己修復が3回を超えた時点（`attempt=4` 相当）で停止。
- 停止時は推測継続せず、競合点と保留理由を明示する。


### 依存切断（mock）固定条件（Stream D）

- CE1未完了でも `sourceBundleHash=mock:<hash>` を許容し、実装完了待ちを禁止する。
- API/CLI/GUI の同値性判定は `equivalenceKey + bundleHash` の AND 条件で固定する。
- proposal-only を固定し、auto-apply 禁止・`human_reviewed` 自動昇格禁止を全フェーズで維持する。


## Stream D Parallel Prep Snapshot（2026-04-18）

> 目的: `CE2-low-risk-ai-assist` を CE0/CE4 と並列準備する。**proposal-only** を崩さず、APIシグネチャ先行 + mock依存切断で実装待機を排除する。

### Phase運用（固定）
1. **Read**: CE2契約ID（`CE2-PROPOSAL-IF` ほか）と禁止事項を再確認。
2. **CDC（必要時）**: `status/reviewState` 列挙変更や安全境界変更時のみ CDC 追記。
3. **Plan**: APIシグネチャを先に凍結し、CE1差分は mock bundle で吸収。
4. **Execute**: 契約本文と検証項目（No-Go）を対応付ける。
5. **Verify**: AC/DoD整合 + drift-stop（最大3回修復）。
6. **Proceed**: CE4連携は参照専用（再定義禁止）。

### API Signature Freeze（実装前固定）
```ts
export type ProposalStatus = "proposed" | "accepted" | "rejected" | "held";
export type ReviewState = "unreviewed" | "human_reviewed";

export type ProposalDraftV1 = {
  proposalId: string;
  diff: Record<string, unknown>;
  sourceBundleHash: string; // mock:<hash> 許容
  rationale: string;
  status: ProposalStatus;
  reviewState: ReviewState;
};
```

### Mock decoupling（依存切断）
- CE1実装完了待ちを禁止し、`sourceBundleHash=mock:<hash>` で契約検証を継続。
- CE0/CE4は read-only参照とし、CE2側で再定義しない。

### Verify観点（AC/DoD）
- AC-1: auto-apply経路0件（UI/API/worker）。
- AC-2: AIによる `human_reviewed` 自動昇格0件。
- AC-3: CE1 drift検知時は `status=held` で fail-closed。
- DoD: proposal語彙と状態遷移が docs 間で単一正本に一致。

## Stream D 実行契約（2026-04-18 / CE2/CE0-core-graph 計画専属）

### Scope（編集境界）

- 本Issueは Stream D が CE0/CE1/CE2/CE4 の**計画・契約文書のみ**を扱う前提で維持する。
- 編集対象は `01_Plans/issues/issue-CE*.md` と CE関連の `02_Architecture` 契約文書の最小差分に限定する。
- `03_Implement/**` と shared統合3ファイル（README/dashboard/decision-pack）は編集禁止とする。

### Phase 固定（Read → Contract-first → Mock-first → Verify → Proceed）

1. **Read**: CE対象Issueと参照ADRの整合を先に確認する。
2. **Contract-first**: I/F・型・監査キーを先に固定し、実装仕様を持ち込まない。
3. **Mock-first**: 実装完了待ちを禁止し、モック契約で検証可能性を先行確保する。
4. **Verify**: docs-check とトレーサビリティ（契約ID・語彙・No-Go条件）を検証する。
5. **Proceed**: 実装レーンへは参照専用契約として引き渡し、再定義を禁止する。

### ADR 必須条件（Stop & Ask）

- **方針変更を伴う差分**（契約ID追加・意味変更・列挙値変更・安全境界変更）は、Context / Decision / Consequences を文書化するまで進行しない。
- ADR承認前は Proceed を実行せず、契約凍結を維持したまま停止する。

### Fail-closed 停止条件

- Verify自己修復は最大3回。`attempt=4` 相当は即停止する。
- 未定義競合（同一IDの意味衝突、未規定状態遷移、安全境界矛盾）を検知した時点で停止する。
- 停止時は推測継続せず、競合点と保留理由を明示する。

## 0) Serial Phase Contract（Stream D 固定フロー）

Stream D（CE2/CE0-core-graph 専属）は、以下の固定フローでのみ進行する。

1. **Phase 1: Read**（対象Issue/ADRと契約語彙の再確認）
2. **Phase 2: ADR CDC**（Context/Decision/Consequencesを固定）
3. **Phase 3: Plan**（契約固定とAC/DoD確認）
4. **Phase 4: Execute**（status/reviewState契約固定 + drift-stop固定）
5. **Phase 5: Verify/Proceed**（最大3回まで修復して再検証。条件達成時のみProceed）

`Verify` で3回失敗しても受入条件を満たせない場合は、`status=held` で停止し、人手判断待ちへ遷移する。

Plan開始時には契約語彙（`proposalId/diff/sourceBundleHash/status/reviewState`）と状態遷移定義を再確認し、drift検知時は即停止する。

## 0.1) Independent Execution Rules（Stream D）

- CE1は **mock contract参照** として扱い、実装完了待ちをしない。
- 実装待ちを理由に停止せず、契約検証（docs-check）を先行する。
- drift検知時のみ `status=held` で停止し、人手判断待ちへ遷移する。

## 0.2) 実装開始条件（Gate-first / 先行固定）

- **I/F固定**: `proposalId/diff/sourceBundleHash/rationale/status/reviewState` と `status/reviewState` 列挙値を固定し、未承認の追加・意味変更を禁止する。
- **Risk boundary固定**: proposal-only 境界（auto-apply禁止 / review自動昇格禁止 / safeMode既定ON）を崩す提案は No-Go とする。
- **Rollback条件固定**: drift検知・未定義競合・safeMode後退・self-correction 3回超過のいずれかで `status=held` 停止し、推測継続しない。

## 1) Contract Freeze Preconditions（Plan前提 / mock許容 / 依存切断）

- CE2必須I/F: `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState`。
- CE1依存は `mock bundleHash` で切断し、契約検証を先行（待機禁止）。
- CE0/CE4 の完了待ちは行わず、read-only参照に限定する（再定義禁止）。
- 提案は **proposal-only** 境界に固定し、適用はCE2責務外とする。
- `status` は `proposed|accepted|rejected|held`、`reviewState` は `unreviewed|human_reviewed` のみ許可し、追加状態を禁止する。

## 1.1) Contract ID Freeze（CE2）

| Contract ID | Summary | Must |
| --- | --- | --- |
| `CE2-PROPOSAL-IF` | Proposal 最小I/F固定 | `proposalId/diff/sourceBundleHash/rationale/status/reviewState` |
| `CE2-LIFECYCLE-IF` | status 遷移固定 | `proposed -> accepted/rejected/held` のみ |
| `CE2-DRIFT-STOP-IF` | CE1差分検知時の停止契約 | 差分検知時は `status=held` で停止、再検証開始禁止 |
| `CE2-NO-AUTOAPPLY-IF` | proposal-only 強制 | API/UI/worker すべて auto-apply 禁止 |

## 2) Contract Rationale（CDC snapshot）

### Context

- CE-2は「低リスク導入」が目的であり、AIを確定器として扱わない契約固定が必要。
- CE-1で確定した `bundleHash` を入力として受け、比較可能・可逆な proposal 運用へ接続する。
- Stream D は CE1 完了待ちを行わず、CE1最小I/Fを **モック契約** として参照して先行整備する。
- CE1 実装との差異（フィールド欠落・命名差分・状態遷移差分）を検知した場合は CE2 側の実装/文書更新を停止し、差分解消指示を待つ（drift-stop）。

### Decision

- proposal-only 契約を固定し、CE2の責務を「提案生成と監査可能性の担保」に限定する。
- 自動適用（auto-apply）と自動昇格（AIによる `reviewState=human_reviewed` 付与）を全面禁止する。
- CE1差分検知時は `status=held` を強制し、解消確認まで `accepted/rejected` へ遷移しない。
- 前提崩壊（CE1最小I/F不成立、または契約語彙の単一正本喪失）時は推測補完を禁止し、`status=held` で停止する。

### Consequences

- CE2成果物は常に `proposalId/diff/sourceBundleHash/status/reviewState` を含む提案オブジェクトとして監査可能となる。
- CE1とのI/Fドリフト検知時は `held` 停止が最優先となり、仕様未定義競合を未解消のまま先送りできない。
- CE3は CE2 proposal I/F を変更せず受理する必要があり、後方互換性を維持する。

## 3) Plan（AC/DoD不足はドラフト提案を必須化）

### 2.1 対象ユースケース（提案のみ）

- 島タイトル候補
- B型文章ドラフト（reviewed-only既定）
- contradiction/evidence 由来の論点候補

### 2.2 Proposal 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `proposalId` | string | Yes | 一意識別子 |
| `diff` | object | Yes | 比較・部分採用可能な差分 |
| `sourceBundleHash` | string | Yes | CE-1 bundleHashとの対応 |
| `rationale` | string | Yes | 提案根拠 |
| `status` | enum | Yes | `proposed/accepted/rejected/held` |
| `reviewState` | enum | Yes | `unreviewed/human_reviewed` 表示専用（自動昇格禁止） |

### 2.3 固定値（CE2 Contract Freeze）

- `proposalId`: 必須、proposal単位で不変
- `diff`: 必須、apply差分でなく **比較差分** として保持
- `sourceBundleHash`: 必須、CE1 ContextBundleと1対1対応
- `status`: `proposed | accepted | rejected | held` 以外を禁止
- `reviewState`: `unreviewed | human_reviewed` のみ。AIによる `human_reviewed` 付与禁止
- Auto-apply: UI/API/worker の全経路で禁止
- Drift-stop: CE1差分検知時は必ず `status=held` に遷移し、解除まで `accepted/rejected` 判定を凍結

### 2.4 責務境界（Responsibility）

- CE-2は proposal 作成までを責務とし、apply は人手承認ゲートの外で実行しない。
- proposal の `accepted` は「適用許可の意思表示」であり、自動適用トリガーではない。
- `held` は drift-stop 専用状態として扱い、`held` 中は apply 導線へ遷移禁止。
- `human_reviewed` 自動昇格は禁止（`reviewState` の AI 更新を含む）。昇格は人手操作のみ。
- safeMode ON では未レビュー本文を含む提案生成を禁止する。

### 3.1 AC/DoD不足の補完提案（Plan出力）

- AC補完:
  - `status=held` の間は `accepted` への遷移を禁止する検証文言を必須化する。
  - `sourceBundleHash` が mock 参照であることを監査ログに残す検証文言を追加する。
  - CE1差分検知時に `status=held` で停止し、差分解消完了まで Verify を再開しない文言を必須化する。
- DoD補完:
  - Read/ADR CDC/Plan/Execute/Verify/Proceed の実施記録に attempt 番号（`verifyAttempt=1..3`）を必須化する。
  - Verify 判定時に `drift-stop解除確認` を明文化し、未解除なら pass 不可とする。
  - 停止条件（3回超過 / 安全後退 / 未定義競合）を毎回のVerify記録に併記する。

## 4) Execute（proposal-only / no-auto-apply / status遷移固定）

- UI/APIともに auto-apply 経路を契約違反として扱い、検知時は即No-Go。
- すべてのAI応答は patch/diff と監査ログで追跡可能でなければならない。
- CE-3 の Patch Workspace は CE-2 proposal I/F を変更せず利用する。
- review自動昇格・safeMode後退・直接適用経路を検知した場合はフェイルセーフ停止し、運用判断待ちとする。
- status遷移固定:
  - 許可遷移は `proposed -> accepted | rejected | held` のみ。
  - `held -> accepted/rejected/proposed` の自動遷移を禁止する（人手解除の判断ログ必須）。
- drift-stop固定:
  - CE1 mock I/Fとの差分検知時は `status=held` を強制し、Verifyは停止する。
  - drift未解消の状態で proposal を再生成・再採用しない。

## 5) Verify/Proceed（proposal-only維持 + drift-stop検証）

- [ ] すべてのAI応答が `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState` を持つ。
- [ ] auto-apply経路が0件（API/UIともに禁止）。
- [ ] `human_reviewed` への自動昇格が0件。
- [ ] 提案の採用/却下/保留が監査ログで追跡可能。
- [ ] safeMode ONで未レビュー本文を含む提案が生成されない。
- [ ] CE1モック契約との差異検知時に `status=held` で停止し、適用経路が進行しない。
- [ ] CE0/CE1/CE2 間で契約語彙とContract IDの衝突が0件である。
- [ ] 前提崩壊（CE1最小I/F不成立、契約語彙の不整合）を検知した場合は即停止し、推測で継続しない。
- [ ] `held` 状態のまま自動的に `accepted/rejected/proposed` へ遷移しない。
- [ ] proposal-only 境界が維持され、`accepted` が自動適用トリガーとして扱われない。
- [ ] `reviewState` は AI/worker/API により自動で `human_reviewed` に遷移しない（人手操作のみ）。

## 5.1) DoD（Contract-only）

- [ ] 各Phaseで `Read -> ADR CDC -> Plan -> Execute -> Verify -> Proceed` を記録し、Plan開始時の契約チェックを記録する。
- [ ] Verify 修復は 3 回以内。4 回目相当の失敗時は即停止し推測で継続しない。
- [ ] CE1 mock I/F 依存切断（待機禁止）を維持し、実装詳細の規定を追加しない。
- [ ] `CE2-PROPOSAL-IF / CE2-LIFECYCLE-IF / CE2-DRIFT-STOP-IF / CE2-NO-AUTOAPPLY-IF` が CE0/CE1 契約と矛盾しない。

## 6) Verify 修復上限（最大3回）

- Verify で不整合を検知した場合、修復→再検証を最大3回まで許可する。
- 3回以内に解消しない場合は `status=held` へ遷移し、再検証開始を禁止する。
- 修復回数は監査ログで追跡可能にする（attempt=1..3）。
- 停止条件:
  - 3回超過（attempt=4相当）で即 `status=held`。
  - safeMode後退・auto-apply許容を検知した時点で即停止。
  - 未定義競合（Contract ID意味衝突 / 未規定状態遷移）検知時は即停止。
  - 前提崩壊（CE1最小I/F不成立 / 契約語彙の単一正本喪失）検知時は即停止。

## 7) タスク分解（文書限定）

- [ ] T1: proposal schema 契約を architecture/docs へ同期。
- [ ] T2: auto-apply禁止と review昇格禁止を運用文書へ明示。
- [ ] T3: proposal lifecycle（create/reject/hold/adopt）の語彙を統一。
- [ ] T4: CE-3引き渡し項目（部分採用可逆性）を記録。

## 8) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "proposalId|diff|sourceBundleHash|status|reviewState|auto-apply|human_reviewed|safeMode|unreviewed|held|drift-stop|Read -> ADR CDC -> Plan -> Execute -> Verify -> Proceed" 01_Plans/issues/issue-CE2-low-risk-ai-assist.md 02_Architecture/llm_quality_strategy.md 02_Architecture/llm_escalation_policy.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 提案I/Fと禁止事項が文書間で一致し、validatorが成功する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 差分を持たない提案や自動適用導線が混入し監査不能。
- ロールバック: proposal契約違反箇所をrevertし、CE-1連携キー準拠へ戻す。


## 10) フェイルセーフ（Stream D 固定）

- Self-Correction 3回超過で停止し、人手判断待ちへ遷移する。
- Contract ID collision（重複IDまたは同一IDの意味不一致）を検知した場合は停止する。
- スコープ逸脱（03_Implement/**、CE3/CE4 issue、dashboard、issues/README）要求が発生した場合は停止する。
- 未定義競合（前提矛盾 / 未規定状態遷移）を検知した場合は推測せず停止する。


## 11) ADR必要性判定（contract 判定結果）

- 判定: **新規ADRは現時点では不要**（既存 `ADR-0028` と CE0/CE1/CE2 Contract Freeze で意思決定が固定済み）。
- CDC明文化（差分追記）:
  - Context: Stream D は CE2 の低リスク化を docs 契約で先行固定し、実装依存を持ち込まない。
  - Decision: 新規ADRを起票せず、当Issueと `02_Architecture/llm_quality_strategy.md` / `02_Architecture/llm_runtime_constraints.md` を単一正本として同期する。
  - Consequences: 仕様変更要求が Contract ID 追加/意味変更を伴う場合は **ADR起票を再判定し、承認待ちで停止** する。
- 承認待ち条件（Stop & Ask）:
  - `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF` の意味変更。
  - `status` / `reviewState` 列挙値の追加。
  - safeMode既定ONまたは漏洩防止境界（share/export）を弱める要求。

## 12) AC/DoD 合意版（Plan 固定）

### Acceptance Criteria（合意版）

- [ ] CE2提案I/Fを `proposalId/diff/sourceBundleHash/rationale/status/reviewState` で固定し、必須化する。
- [ ] `status` は `proposed|accepted|rejected|held`、`reviewState` は `unreviewed|human_reviewed` のみ許可する。
- [ ] auto-apply 経路は UI/API/worker すべてで 0 件を維持する。
- [ ] `reviewState=human_reviewed` へのAI自動昇格は 0 件を維持する。
- [ ] CE1ドリフト検知時は `status=held` で fail-closed 停止し、再検証開始を禁止する。
- [ ] 前提崩壊（CE1最小I/F不成立、契約語彙の単一正本喪失）検知時は `status=held` で即停止する。
- [ ] safeMode既定ONと未レビュー本文除外（reviewed-only既定）を非破壊で確認する。

### Definition of Done（合意版）

- [ ] Read/ADR CDC/Plan/Execute/Verify/Proceed の実施証跡を残し、Plan開始時の契約チェックを記録する。
- [ ] Verify試行回数（`verifyAttempt=1..3`）と停止理由を監査ログに残す。
- [ ] 4回目相当の再試行は行わず `status=held` で停止した事実を記録する。
- [ ] 未定義競合および前提崩壊の停止理由を明示し、推測継続を禁止する。

## 13) Verify 証跡テンプレート

### 13.1 Verify evidence（監査可能性）

- `verifyAttempt`: `1|2|3`
- `phaseGate`: `Read|ADR CDC|Plan|Execute|Verify|Proceed`
- `proposalId`
- `sourceBundleHash`（mock可: `mock:<hash>`）
- `statusBefore` / `statusAfter`
- `reviewStateBefore` / `reviewStateAfter`
- `driftDetected`: `true|false`
- `safeModeDefaultOnConfirmed`: `true|false`
- `unreviewedLeakPrevented`: `true|false`
- `autoApplyPathCount`: `0`
- `autoReviewPromotionCount`: `0`
- `decision`: `pass|held|stop`

## 14) Proceed（CE4連携向け引継ぎ）

- Proceed は `Read -> ADR CDC -> Plan -> Execute -> Verify -> Proceed` の順序を崩さない。
- CE3完了待ちは禁止し、`sourceBundleHash=mock:<hash>` を許容した状態で CE4 連携へ引き継ぐ。
- 引継ぎ時は次の固定事項を記録する。
  - `proposalId/diff/sourceBundleHash/status/reviewState` の必須キーが欠損していないこと。
  - `status=held` が drift-stop 専用であること（未解除での再開禁止）。
  - auto-apply 経路 0 件、`reviewState` 自動昇格 0 件であること。
  - Verify の修復回数（`verifyAttempt`）が 3 回以内であること。
- 3回修復で収束しない場合は Proceed せず、`status=held` のまま停止する。

## Stream B Alignment Addendum（2026-04-17, mock-first / contract-only）

### Plan
- `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF` を固定IDとして再確認する。
- CE1 は mock contract 参照とし、実装完了待ちを行わない。

### Execute
- proposal-only を固定し、direct write / auto-apply / review自動昇格を禁止する。
- `status` は `proposed|accepted|rejected|held`、`reviewState` は `unreviewed|human_reviewed` のみ許可する。

### Verify
- CE1ドリフト検知時の `status=held` 強制停止、`held` 自動解除禁止、safeMode後退0件を確認する。
- Self-Correction は最大3回。`attempt=4` 相当は即停止する。

### Proceed
- CE3/CE4 への契約再定義要求は受理せず、参照専用 handoff のみ実施する。


---

## Stream E Update (2026-04-18): CE2 Contract-first Planning（実装不要確定）

### Phase 1: Read
- CE2 は proposal-only 境界を維持し、適用責務を持たない。
- CE1差分が未解消なら `status=held` を強制する。

### Phase 2: 共通I/F最小セット定義
- Proposal最小I/F:
  `proposalId/diff/sourceBundleHash/rationale/status/reviewState`。
- 列挙固定:
  - `status: proposed|accepted|rejected|held`
  - `reviewState: unreviewed|human_reviewed`

### Phase 3: モック可能境界の切り出し
- `sourceBundleHash=mock:<hash>` を許容し CE1完了待ちを禁止。
- mock時も `auto-apply=禁止` / `reviewState自動昇格=禁止` を維持。

### Phase 4: 監査項目・受入条件整備
- 監査項目:
  - auto-apply path 0件
  - review auto-promotion 0件
  - held遷移漏れ 0件
- 受入条件:
  1) proposal語彙の単一正本化
  2) CE1/CE4 参照互換性の維持
  3) self-repair 最大3回

### Phase 5: Proceed（実装不要の確定範囲）
- CE2 は契約と遷移ルールの固定で Proceed。
- 実装不要: apply API、UI操作実装、モデル選定。
