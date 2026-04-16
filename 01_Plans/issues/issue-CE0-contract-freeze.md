# Issue Draft: CE0 Contract Freeze（ACCI + Graph Contract）

- Type: Process
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/issues/`, `02_Architecture/`（Stream D: Contract Freeze / mock-first / Docs-Architecture only）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE0-CONTRACT-FREEZE`
- RequirementStatement: ACCI方式・Guard-01〜05・CG-01〜05 を文書横断で凍結する。
- PriorityClass: Must
- AcceptanceScenario: 前提=ADR-0028更新済 / 操作=契約ID同期 / 期待結果=定義衝突0件 / 除外=実装コード変更
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `D` (Contract Freeze / mock-first / Docs-Architecture only)
- DecisionQueueRef: `UNC-VSC-CE-01-01`, `UNC-VSC-CE-02-01`


## 0) Phase 1 Read（I/F必須項目抽出 + mock前提確認）

- CE0必須I/Fキーを `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` に固定し、後続Issueの再定義を禁止する。
- CE1/CE2/CE4 は **実装待機禁止** とし、依存は `mock I/F` で切断して契約検証を先行する。
- CE2/CE4（実装レーン）へ渡す情報は本Issueの Contract ID Matrix を参照専用で利用する（本Issueで実装詳細は扱わない）。
- Contract ID Matrix は本Issueを一次正本とし、`02_Architecture/architecture.md` と `02_Architecture/schemas.md` は責務境界の同期先として扱う。
- 再抽出結果（固定語彙）: `Consensus Graph` / `WorkingGraph` / `ContextProjectionGraph` / `proposal-only` / `Query Preview` / `safeMode` / `human_reviewed`。
- 再抽出結果（禁止事項）: Query Preview bypass / Consensus direct write / auto-apply / AI review自動昇格 / safeMode既定緩和。

### Phase 1 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: CE0契約ID（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）と禁止事項語彙を再抽出し、本Issueを一次正本に固定する。
- **Execute**: 固定語彙・禁止事項・mock-first依存切断（CE1/CE2/CE4待機禁止）を明文化した。
- **Verify**: 契約IDの再定義を禁止し、語彙を `Consensus Graph` 系へ統一する方針を確認した。
- **Proceed**: Phase 2でADR追記は不足補完（Context/Decision/Consequences）に限定し、再定義禁止を継続する。

## 0.1) Phase 2 ADR明文化（不足分のみ追記）

- ADR記述は Context / Decision / Consequences の不足分のみを補完し、既存合意を再定義しない。
- CE1/CE2 が参照する語彙（`proposal-only`, `safeMode`, `human_reviewed`, `sourceBundleHash`）を CE0用語に接続する。

### Phase 2 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: ADR-0028本文の再定義はせず、参照注記だけで不足語彙の接続関係を明確化する。
- **Execute**: CE0語彙から CE1/CE2参照語彙へのマッピング方針を明記した。
- **Verify**: ADR再定義禁止と「不足分補完のみ」の境界を固定した。
- **Proceed**: Phase 3でAC/DoD不足項目を追加提案し、Go/No-Go判定に接続する。

## 0.2) Phase 3 Mock-first契約化（依存切断）

- CE1/CE2/CE4 依存は mock I/F で切断し、CE0契約検証をブロックしない。
- CE0は実装を伴わず契約固定に限定する。

### Phase 3 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: AC/DoDで「依存待機禁止」を明示し、契約凍結の完了条件を先に固定する。
- **Execute**: 依存切断と docs-check 完了をProceed条件へ組み込んだ。
- **Verify**: CE0が実装レーン（03_Implement）を要求しないことを再確認した。
- **Proceed**: Phase 4でdrift-stopと修復上限（3回）を停止条件として固定する。

## 0.3) Phase 4 AC/DoD固定（drift-stop）

- drift-stop 条件を固定する（契約ID衝突、語彙衝突、safeMode後退、auto-apply許容）。
- Verify自己修復は最大3回。4回目失敗相当で即停止し、推測継続を禁止する。

### Phase 4 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: Fail-safeを定量化し、`collision=0` と `safeMode後退=0` を必須ゲート化する。
- **Execute**: 自己修復3回上限と4回目相当即停止を契約化した。
- **Verify**: 安全後退（safeMode/auto-apply/review昇格）を1件でもNo-Goにすることを確認した。
- **Proceed**: Phase 5で契約ID衝突0・語彙衝突0・SafeMode後退0の3点検証へ進む。

## 0.4) Phase 5 Verify（CE0/CE1/CE2整合）

- CE0/CE1/CE2 の契約ID整合を検証し、衝突0件をProceed条件にする。
- 契約語彙の差異（同義語ズレ含む）を0件にする。
- Verify結果は `Contract ID collision=0` / `safeMode後退=0` を同時記録し、どちらかが1件でもNo-Go停止とする。

### Phase 5 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: 参照先Issue間で契約IDと語彙の一意性を機械検索で確認する。
- **Execute**: 検証コマンドを固定し、衝突0件以外はProceed不可と定義した。
- **Verify**: Contract ID collision=0 / 語彙 collision=0 / SafeMode後退0 を同時条件として扱う。
- **Proceed**: Phase 6でCE1/CE2へ参照専用Contract Matrixを引き渡す。

## 0.5) Phase 1 Read Snapshot（契約・統治 現状表）

| Contract / Key | Current Value (as-is) | schemaVersion | overridePolicy | Freeze Flags |
| --- | --- | --- | --- | --- |
| `CE0-CTX-IF` | ContextQuery/ContextBundle最小I/F（Query Preview必須, deterministic `bundleHash`） | `N/A (meta contract)` | `N/A` | `contractIdFixed=true` |
| `CE0-SAFEMODE-IF` | safeMode既定ON + `allowUnreviewedText=false` 既定 | `N/A (meta contract)` | `N/A` | `safemodeRegressionBlocked=true` |
| `CE0-REVIEW-IF` | `human_reviewed` 昇格は人手のみ | `N/A (meta contract)` | `human_dual_control_only`（A1連携時） | `reviewAutoPromotionBlocked=true` |
| `CG-01..05` | Working/Projection/Consensus 分離 + proposal-only + 監査4点セット必須 | `N/A (meta contract)` | `N/A` | `directWriteBlocked=true`, `autoApplyBlocked=true` |
| `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（参照） | A1契約凍結パック | `1.0.0` | `human_dual_control_only` | `contractLinkLocked=true`, `sharedResourceFreeze=true` |

> 判定: CE0はメタ契約凍結（schemaVersion非対象）、A1は実体I/F凍結（schemaVersion対象）として直列管理する。

## 1) Context

- CE-1以降の実装で参照する契約が複数文書に散在しており、語彙ズレ（Core/Consensus、reviewed/unreviewed、safeMode）が発生しやすい。
- ADR-0028 の CE-0 は「設計前固定」を要求しており、実装着手前に I/F と禁止事項を先に凍結する必要がある。

## 2) Decision

### 2.1 責務境界（Responsibility）

- CE0が固定する対象:
  - 認知外在化AIの最小契約（ContextQuery/ContextBundle/PatchProposal）
  - Graph責務境界（Working / Projection / Consensus）
  - 安全境界（safeMode既定ON・unreviewed保護・auto-apply禁止）
- CE0が固定しない対象:
  - API詳細スキーマ・CLI引数・UI配置・モデル選定・RBAC実装

### 2.2 入出力境界（Input / Output）

- 入力（許可）:
  - `document/view/patch` の正規入力のみ
  - ContextQuery（`goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode`）
- 出力（許可）:
  - Patch Proposal（`proposalId + diff + rationale`）
  - 監査4点セット（`query/bundle/proposal/apply`）
- 出力（禁止）:
  - Consensus Graphへの直接書込
  - `human_reviewed` の自動昇格
  - Query Previewを通さない送信経路

### 2.3 CE-0 Contract ID Matrix（固定）

| Contract ID | Responsibility | Input | Output | Prohibitions |
| --- | --- | --- | --- | --- |
| `CE0-CTX-IF` | ContextQuery/ContextBundle最小I/Fを固定 | `goal/scope/depth/constraints/reviewFilter/safeModePolicy/outputMode` | deterministic `bundleHash` を持つ ContextBundle | Query Previewバイパス、非決定論bundle |
| `CE0-SAFEMODE-IF` | safeMode既定ONと未レビュー保護を固定 | `safeMode=true` 時のreview state情報 | `allowUnreviewedText=false` を既定適用 | 未レビュー本文のAI入力混入、保護緩和 |
| `CE0-REVIEW-IF` | review状態遷移の責務境界を固定 | `human_reviewed`/`unreviewed` state | 人手操作でのみ `human_reviewed` 昇格 | AIによるreview自動昇格 |
| `CG-01..05` | Working/Projection/Consensus責務固定 | KJ構造 + query constraints + actor/modelTier | proposal-only運用（patch+approval経由） | Consensus直接更新、監査欠損成功扱い |

### 2.4 AC/DoD補強ドラフト（Phase 3: Plan）

- 追加AC（ドラフト→本Issueで採用）:
  - [ ] Query Preview を経由しない ContextQuery 送信経路が 0 件である。
  - [ ] `Consensus Graph` への direct write（patch+approval 以外）が 0 件である。
  - [ ] `mode=autonomous` でも `proposal-only` 契約が明文化されている。
  - [ ] 監査4点セット（`query/bundle/proposal/apply`）欠損時は No-Go と定義される。
- DoD（CE0完了判定）:
  - Plan → Execute → Verify → Proceed の順序で記録され、各段の証跡（定義表・同期差分・検証コマンド）が残る。
  - CE0-CTX-IF / CE0-SAFEMODE-IF / CE0-REVIEW-IF / CG-01..05 の語彙が `01/02/04` で一致する。
  - Query Preview必須・direct write禁止・proposal-only・監査4点セット必須の4要件が No-Go 条件と矛盾なく同居する。

### 2.5 Go/NoGo Key（固定）

- **Go**:
  - Query Preview 必須経路が維持される。
  - `patch + approval` 以外で Consensus 更新が発生しない。
  - SafeMode既定ON・未レビュー本文保護・review自動昇格禁止が同時に成立する。
- **No-Go**:
  - Query Preview bypass の導線が1件でも存在する。
  - direct write / auto-apply / review自動昇格を許容する記述が1件でも存在する。
  - SafeMode後退（既定OFF化・例外既定化）の兆候を検知する。

### 2.6 Drift-stop 固定（Phase 4 Execute）

- Contract ID collision は **0件固定**（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` の重複再定義禁止）。
- 語彙 collision は **0件固定**（`Core Graph` は履歴注記のみ、契約語彙は `Consensus Graph` に統一）。
- SafeMode後退（既定OFF化・例外既定化）兆候は 1件でも検知時点で No-Go 停止。
- Verify自己修復は最大3回。4回目相当は停止し、推測継続を禁止する。

## 3) Consequences

- CE-1〜CE-4 は本Issueの Contract ID を参照し、契約再定義を禁止する。
- `safeMode` 後退、share/export緩和、Core Graph直接更新許容の兆候を検知した場合は即時No-Goとする。
- CE0完了後にのみ、実装レーンへ API/型/UI 具体化を引き渡す。

## 4) 受入条件 / Acceptance criteria

- [ ] ACCIの5段手順が 01/02/04 で同語彙定義される。
- [ ] Guard-01〜05 の意味が文書間で一致し、禁止事項に矛盾がない。
- [ ] CG-01〜05（Consensus/Working契約）が Architecture と Ops に反映される。
- [ ] `safeMode` と `unreviewed` の後退表現が 0 件。
- [ ] Go/NoGo判定を1行で実施できる（Yes/No）。
- [ ] CE0/CE1/CE2 の Contract ID に重複・異義定義がない。

## 4.1) DoD（Contract Freeze）

- [ ] Phase 1〜5 の各段で `Plan -> Execute -> Verify -> Proceed` 記録が残る。
- [ ] Verify自己修復は3回以内で完了し、超過時は停止記録が残る。
- [ ] CE0 Contract ID Matrix が architecture/schemas/CE1/CE2 参照節と一致する。
- [ ] Contract ID collision=0 / 語彙 collision=0 / drift-stop固定（safeMode後退検知即停止）が検証ログで追跡できる。
- [ ] 実装指示（03_Implement配下変更前提）が本Issueに含まれない。

## 5) タスク分解（Stream D: 編集許可ファイル限定）

- [ ] T1: 本Issueと `issue-CE0-core-graph-repositioning.md` の Contract ID Matrix を参照専用固定値として一致させる。
- [ ] T2: 編集許可ファイル内（CE0 / CoreGraph / HIL-RS A1契約文書）で契約語彙を同期し、指定外ファイル編集を行わない。
- [ ] T3: CE2/CE4向け参照専用ハンドオフ（再定義禁止）を本Issue末尾のMatrixに固定する。
- [ ] T4: ドリフト検知コマンド結果（collision=0 / 安全後退=0）を記録する。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "CE0-CTX-IF|CE0-SAFEMODE-IF|CE0-REVIEW-IF|CG-0[1-5]|Consensus Graph|WorkingGraph|ContextProjectionGraph|Query Preview|direct write|proposal-only|safeMode|human_reviewed|auto-apply" 01_Plans/issues/issue-CE0-contract-freeze.md 01_Plans/issues/issue-CE0-core-graph-repositioning.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 用語不一致がなく、validatorが成功する。
- 未実施時の理由・代替検証:
  - 未実施不可（CE-0 Gate条件）。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 語彙同期不足によりCE-1以降のI/Fが多義化する。
- ロールバック: 変更文書を契約ID単位でrevertし、ADR-0028を正本として再同期。


## 8) Phase 6 Proceed（CE2/CE4向け参照専用I/F）

> 参照専用。CE2/CE4は以下を変更せず利用すること。

- `CE0-CTX-IF`: Query Preview必須 + deterministic `bundleHash` 前提。
- `CE0-SAFEMODE-IF`: `safeMode` 既定ON、`allowUnreviewedText=false` 既定。
- `CE0-REVIEW-IF`: `human_reviewed` 昇格は人手のみ。
- `CG-01..05`: Working/Projection/Consensus 分離、`patch + approval` 以外の適用禁止、監査4点セット必須。
- CE2/CE4へのハンドオフは **read-only** とし、契約改訂要求は CE0/CE1 へ差し戻して再起票する。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。

追記フェイルセーフ: Self-Correction 3回超過 / Contract ID collision / scope逸脱要求で停止し、推測で継続しない。

### Phase 6 Workflow（Plan -> Execute -> Verify -> Proceed）

- **Plan**: CE2/CE4向け引き渡しは本IssueのContract Matrix参照専用とし、再定義を禁止する。
- **Execute**: `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` を引き渡し固定値として明記した。
- **Verify**: 引き渡し対象に実装詳細やADR本文再定義が混入していないことを確認する。
- **Proceed**: CE2/CE4は本Matrixを上書きせず参照し、差分提案はCE0再起票で扱う。

## 9) CE2/CE4 引き渡し Contract Matrix（固定）

| Consumer | Required Contract IDs | Must Keep | Must Not |
| --- | --- | --- | --- |
| CE2 Low-risk AI Assist | `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05` | Query Preview必須 / deterministic `bundleHash` / human review昇格は人手のみ | Preview bypass / AI review自動昇格 / auto-apply |
| CE4 API/CLI/Audit Integration | `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CG-05` | 監査4点セット必須 / safeMode既定ON / mock-first検証継続 | 監査欠損成功扱い / safeMode既定緩和 / direct write |

> ADR-0028は参照注記のみ（本文再定義禁止）。本MatrixはCE0 Contract Freezeの参照専用固定値として運用する。

## Stream D Contract Freeze Fixpoint (2026-04-12)

### Phase 1: Read（最新再読 + 未確定抽出）
- 未確定I/F: `なし`（固定対象は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）。
- 未確定責務: `なし`（A1は契約凍結の唯一正本、A2/A3はread-only参照）。
- 未確定ゲート: `なし`（唯一ゲートは `a1Status=="Done" && pendingDecisionQueueCount==0`）。
- 事前想定との差分（箇条書き）:
  - `A1 Done` という自然文ゲート表記が残存していたため、機械判定式 `a1Status=="Done"` に統一した。
  - 承認キュー遷移の `Pending -> Approved | Rejected` を、禁止遷移判定しやすい `Pending -> Approved` または `Pending -> Rejected` に明示化した。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: 契約・統治のクリティカルパスを実装依存から切り離し、docs-checkで閉じる。
- Decision: 本メモの契約ID・凍結値・停止条件を正本として再定義禁止に固定する。
- Consequences: 差分要求はA1へ差し戻し、下流は参照専用で運用する。
- 合意記録: `DecisionStatus=Fixed` を承認済み契約として継続（本メモ内合意）。

### Phase 3: Plan（AC/DoD補強）
- AC補強: Contract ID collision=0 / 語彙collision=0 / SafeMode後退=0 を同時成立。
- DoD補強: `Plan -> Execute -> Verify -> Proceed` の順序証跡を本メモに残す。

### Phase 4: Execute（契約ID・判定条件・停止条件固定）
- 契約ID固定: `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`, `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`。
- 判定条件固定: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`。
- 停止条件固定: Query Preview bypass / direct write / auto-apply / review自動昇格 / SafeMode後退 / Self-Correction 3回超過。

### Phase 5: Verify -> Proceed
- Verify: docs-checkで契約ID整合・語彙整合・安全後退0件を確認し、不一致時はSelf-Correction最大3回まで。
- Proceed条件（1行）: `Proceed = (collision==0 && vocabularyDrift==0 && safeModeRegression==0 && a1Status=="Done" && pendingDecisionQueueCount==0)`。

### Fail-safe（停止報告テンプレ）
- 失敗条件:
- 影響範囲（ファイル/契約ID）:
- 人間判断が必要な選択肢（2案）:
  - 案1: 契約固定値を維持し、差分要求をA1へ差し戻す。
  - 案2: 契約固定値の変更を承認会議へエスカレーションし、承認後に再凍結する。
