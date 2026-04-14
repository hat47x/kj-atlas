# Issue Draft: CE2 低リスクAI支援（proposal-only契約固定）

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Stream E (CE2 proposal-only契約固定, docs-first)
- Scope: `01_Plans/issues/`, `02_Architecture/`
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE2-LOW-RISK-AI-ASSIST`
- RequirementStatement: AI提案は全件 proposalId+diff を持つ patch として扱う。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE1最小I/F（ContextQuery + ContextBundle + bundleHash）をモック契約として利用 / 操作=提案生成 / 期待結果=自動適用0件 / 除外=最終結論の自動生成
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `E` (CE2 proposal-only契約固定専任 / Contracts + Docs only / mock-first)
- DecisionQueueRef: `CE2-DRIFT-STOP`

## 0) Serial Phase Contract（Stream E 固定フロー）

CE2 Stream E は、以下の固定フローでのみ進行する。

1. **Phase 1: Read**（必須I/F再確認）
2. **Phase 2: ADR CDC**（Context / Decision / Consequences）
3. **Phase 3: Plan**（AC/DoD不足提案）
4. **Phase 4: Execute**（status遷移とdrift-stop固定）
5. **Phase 5: Verify**（最大3回まで修復して再検証）

`Verify` で3回修復しても受入条件を満たせない場合は、`status=held` で停止し、人手判断待ちへ遷移する。

各Phase開始時には、直前成果物との差分を対象に `Read` チェックポイントを実施し、契約語彙（`proposalId/diff/sourceBundleHash/status/reviewState`）と状態遷移定義を再確認する。

## 0.1) Independent Execution Rules（Stream E）

- CE1は **mock contract参照** として扱い、実装完了待ちをしない。
- 実装待ちを理由に停止せず、契約検証（docs-check）を先行する。
- drift検知時のみ `status=held` で停止し、人手判断待ちへ遷移する。

## 1) Phase 1 Read（必須I/F抽出 + mock許容 / 依存切断）

- CE2必須I/F: `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState`。
- CE1依存は `mock bundleHash` で切断し、契約検証を先行（待機禁止）。
- CE0/CE4 の完了待ちは行わず、read-only参照に限定する（再定義禁止）。
- 提案は **proposal-only** 境界に固定し、適用はCE2責務外とする。
- `status` は `proposed|accepted|rejected|held`、`reviewState` は `unreviewed|reviewed` のみ許可し、追加状態を禁止する。

## 1.1) Contract ID Freeze（CE2）

| Contract ID | Summary | Must |
| --- | --- | --- |
| `CE2-PROPOSAL-IF` | Proposal 最小I/F固定 | `proposalId/diff/sourceBundleHash/rationale/status/reviewState` |
| `CE2-LIFECYCLE-IF` | status 遷移固定 | `proposed -> accepted/rejected/held` のみ |
| `CE2-DRIFT-STOP-IF` | CE1差分検知時の停止契約 | 差分検知時は `status=held` で停止、再検証開始禁止 |
| `CE2-NO-AUTOAPPLY-IF` | proposal-only 強制 | API/UI/worker すべて auto-apply 禁止 |

## 2) Phase 2 ADR CDC（Context / Decision / Consequences）

### Context

- CE-2は「低リスク導入」が目的であり、AIを確定器として扱わない契約固定が必要。
- CE-1で確定した `bundleHash` を入力として受け、比較可能・可逆な proposal 運用へ接続する。
- Stream E は CE1 完了待ちを行わず、CE1最小I/Fを **モック契約** として参照して先行整備する。
- CE1 実装との差異（フィールド欠落・命名差分・状態遷移差分）を検知した場合は CE2 側の実装/文書更新を停止し、差分解消指示を待つ（drift-stop）。

### Decision

- proposal-only 契約を固定し、CE2の責務を「提案生成と監査可能性の担保」に限定する。
- 自動適用（auto-apply）と自動昇格（AIによる `reviewState=reviewed` 付与）を全面禁止する。
- CE1差分検知時は `status=held` を強制し、解消確認まで `accepted/rejected` へ遷移しない。
- 前提崩壊（CE1最小I/F不成立、または契約語彙の単一正本喪失）時は推測補完を禁止し、`status=held` で停止する。

### Consequences

- CE2成果物は常に `proposalId/diff/sourceBundleHash/status/reviewState` を含む提案オブジェクトとして監査可能となる。
- CE1とのI/Fドリフト検知時は `held` 停止が最優先となり、仕様未定義競合を未解消のまま先送りできない。
- CE3は CE2 proposal I/F を変更せず受理する必要があり、後方互換性を維持する。

## 3) Phase 3 Plan（AC/DoD不足提案）

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
| `reviewState` | enum | Yes | `unreviewed/reviewed` 表示専用（自動昇格禁止） |

### 2.3 固定値（CE2 Contract Freeze）

- `proposalId`: 必須、proposal単位で不変
- `diff`: 必須、apply差分でなく **比較差分** として保持
- `sourceBundleHash`: 必須、CE1 ContextBundleと1対1対応
- `status`: `proposed | accepted | rejected | held` 以外を禁止
- `reviewState`: `unreviewed | reviewed` のみ。AIによる `reviewed` 付与禁止
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
  - Phase 1〜5 の実施記録に attempt 番号（`verifyAttempt=1..3`）を必須化する。
  - Verify 判定時に `drift-stop解除確認` を明文化し、未解除なら pass 不可とする。
  - 停止条件（3回超過 / 安全後退 / 未定義競合）を毎回のVerify記録に併記する。

## 4) Phase 4 Execute（proposal-only / no-auto-apply / status遷移固定）

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

## 5) Phase 5 Verify（proposal-only維持 + drift-stop検証）

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
- [ ] `reviewState` は AI/worker/API により自動で `reviewed` に遷移しない（人手操作のみ）。

## 5.1) DoD（Contract-only）

- [ ] 各Phaseで `Plan -> Execute -> Verify` を記録し、Phase開始時にReadチェックを記録する。
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
  - `rg -n "proposalId|diff|sourceBundleHash|status|reviewState|auto-apply|human_reviewed|safeMode|unreviewed|held|drift-stop" 01_Plans/issues/issue-CE2-low-risk-ai-assist.md 02_Architecture/llm_quality_strategy.md 02_Architecture/llm_escalation_policy.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 提案I/Fと禁止事項が文書間で一致し、validatorが成功する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 差分を持たない提案や自動適用導線が混入し監査不能。
- ロールバック: proposal契約違反箇所をrevertし、CE-1連携キー準拠へ戻す。


## 10) フェイルセーフ（Stream E 固定）

- Self-Correction 3回超過で停止し、人手判断待ちへ遷移する。
- Contract ID collision（重複IDまたは同一IDの意味不一致）を検知した場合は停止する。
- スコープ逸脱（03_Implement/**、CE3/CE4 issue、dashboard、issues/README）要求が発生した場合は停止する。
- 未定義競合（前提矛盾 / 未規定状態遷移）を検知した場合は推測せず停止する。


## 11) ADR必要性判定（Phase 2 判定結果）

- 判定: **新規ADRは現時点では不要**（既存 `ADR-0028` と CE0/CE1/CE2 Contract Freeze で意思決定が固定済み）。
- CDC明文化（差分追記）:
  - Context: Stream E は CE2 の低リスク化を docs 契約で先行固定し、実装依存を持ち込まない。
  - Decision: 新規ADRを起票せず、当Issueと `02_Architecture/llm_quality_strategy.md` / `02_Architecture/llm_runtime_constraints.md` を単一正本として同期する。
  - Consequences: 仕様変更要求が Contract ID 追加/意味変更を伴う場合は **ADR起票を再判定し、承認待ちで停止** する。
- 承認待ち条件（Stop & Ask）:
  - `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF` の意味変更。
  - `status` / `reviewState` 列挙値の追加。
  - safeMode既定ONまたは漏洩防止境界（share/export）を弱める要求。

## 12) AC/DoD 合意版（Phase 3 固定）

### Acceptance Criteria（合意版）

- [ ] CE2提案I/Fを `proposalId/diff/sourceBundleHash/rationale/status/reviewState` で固定し、必須化する。
- [ ] `status` は `proposed|accepted|rejected|held`、`reviewState` は `unreviewed|reviewed` のみ許可する。
- [ ] auto-apply 経路は UI/API/worker すべてで 0 件を維持する。
- [ ] `reviewState=reviewed` へのAI自動昇格は 0 件を維持する。
- [ ] CE1ドリフト検知時は `status=held` で fail-closed 停止し、再検証開始を禁止する。
- [ ] 前提崩壊（CE1最小I/F不成立、契約語彙の単一正本喪失）検知時は `status=held` で即停止する。
- [ ] safeMode既定ONと未レビュー本文除外（reviewed-only既定）を非破壊で確認する。

### Definition of Done（合意版）

- [ ] Phase 1〜5 の実施証跡を残し、各Phase開始時のReadチェックを記録する。
- [ ] Verify試行回数（`verifyAttempt=1..3`）と停止理由を監査ログに残す。
- [ ] 4回目相当の再試行は行わず `status=held` で停止した事実を記録する。
- [ ] 未定義競合および前提崩壊の停止理由を明示し、推測継続を禁止する。

## 13) Verify 証跡テンプレート（Phase 5）

### 13.1 Verify evidence（監査可能性）

- `verifyAttempt`: `1|2|3`
- `phaseGate`: `Read|ADR|Plan|Execute|Verify`
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
