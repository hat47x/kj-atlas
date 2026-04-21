# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Contract Reference Only）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: TBD
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Out of scope:
  - `03_Implement/**`
  - `04_Documentation/**`
  - `01_Plans/project-progress-dashboard.md`
  - `01_Plans/issues/README.md`
  - `01_Plans/issues/decision-pack-2026-03-human-judgement.md`
- Dependencies: `ADR-0027`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## 1) Objective

A3 を「operations/documentation sync の契約参照専用」計画メモとして確定し、A1 完了前の逸脱実行を防止する。

## 1.1) Task Brief（Phase 2 Plan）

- Scope:
  - A3 を `contract reference only` の運用同期メモとして整合維持する。
- Non-Goals:
  - A3 内での契約値確定/再定義。
  - `02_Architecture/**` や `04_Documentation/**` の直接更新。
- Acceptance Criteria:
  - `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
  - D1〜D4 と役割語彙が参照専用で固定される。
- DoD:
  - A1未完了時の A3 Open 禁止が明示。
  - 差戻し先が A1 で一意。
- Validation:
  - `docs-check`（`python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` + `git diff --check`）。
- Stop Conditions:
  - A1未完了での Open 化要求。
  - A3 内での契約再定義要求。
  - Self-Correction 3回超過。

## 2) Contract Freeze（read-only reference）

- snapshotId=`MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- freezeContractId=`HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Dependency order: `A1 -> A2 -> A3`
- unlockRule=`a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- decisionQueueTransition=`Pending -> Approved | Pending -> Rejected`
- Fixed identifiers:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
- Fixed decision criteria:
  - `contractLinkLocked`
  - `sharedResourceFreeze`
  - `validatorPass`

### 2.2) Phase 1 Read 差分確認（2026-04-20 固定）

- 対象: `issue-HIL-RS-02-A3` / `issue-HIL-RS-02-A1` / `issue-HIL-RS-02` / `issue-HIL-RS-01-A1`
- 固定キー差分:
  - `schemaVersion`: 差分なし（`1.0.0`）
  - `overridePolicy`: 差分なし（`human_dual_control_only`）
  - `unlockRule`: 差分なし（`a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`）
  - `decisionQueueTransition`: 差分なし（`Pending -> Approved | Pending -> Rejected`）
  - `contractLinkLocked`: 差分なし（`true`）
  - `sharedResourceFreeze`: 差分なし（`true`）
  - `safeModeDefault`: 差分なし（`ON`）
- 判定: `DiffCount=0`（Proceed可）


## 2.1) Operations/Documentation Sync Alignment（A3 固定参照）

- Canonical source（正本）: `02_Architecture/strict_mode_exception_approval_flow.md`
- Sync route（固定導線）: `02_Architecture` -> `04_Documentation` -> `01_Plans` -> `AGENTS.md`
- Role vocabulary（固定語彙）:
  - `Security Officer`
  - `System Owner`
  - `Platform Operator`
- D1〜D4 fixed values（AUTH-OPS-03 決定値、A3は参照のみ）:
  - `D1`: Security Officer先行、承認TTL=`4h`
  - `D2`: tenant単位、例外最大継続時間=`2h`
  - `D3`: 復旧判定は2者共同、代理承認なし
  - `D4`: 変更台帳+監査ID相互参照、48hレビュー、15m一次/60m二次エスカレーション
- A3 restriction: 上記語彙・導線・固定値は **read-only reference only**（A3内で再定義しない）。

## 3) ADR CDC（必要時のみ）

- Context:
  - A3 は A1 契約固定後に開放される下流計画であり、契約変更窓口ではない。
- Decision:
  - （Draft / held）A3 は契約参照のみ許可し、契約差分要求は A1 へ差し戻す。
- Consequences:
  - A1 未完了または Queue 未解決時は `Draft/Open(hold)` を維持する。

### 3.1) ADR合意ステータス（承認待ち）

- ApprovalStatus: `Pending (Human approval required)`
- ApprovalScope: `CDC Context/Decision/Consequences`
- Pre-approval lock: `承認前は確定扱い禁止（A3はread-only referenceのみ）`

## 4) Acceptance Criteria / DoD

- [x] A3 が contract reference only であることが明文化されている。
- [x] 依存順序 `A1 -> A2 -> A3` が明文化されている。
- [x] `contractLinkLocked / sharedResourceFreeze / validatorPass` 判定が固定されている。
- [x] `safeModeDefault=ON` 後退禁止が明文化されている。
- [x] Proceed 条件・停止条件・差戻し先が明文化されている。
- [x] 役割語彙（Security Officer / System Owner / Platform Operator）が正本と一致している。
- [x] D1〜D4 の固定値が参照専用で明文化されている。
- [x] `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md` 導線が明文化されている。

## 5) Serial Phase Protocol（強制）

各Phaseは **冒頭で必ず対象ファイル（本ファイル）を再読** し、**Plan -> Execute -> Verify -> Proceed** を順に実施する。

### Phase 1 Read
- Plan: 本ファイル再読後、対象5ファイル（`issue-HIL-RS-01` / `issue-HIL-RS-01-A1` / `issue-HIL-RS-02` / `issue-HIL-RS-02-A1` / `issue-HIL-RS-02-A3`）の再読チェックポイント（A1契約値・D1〜D4固定値・役割語彙）を固定。
- Execute: A1/A2/A3依存、unlockRule、凍結キー（`schemaVersion / contractLinkLocked / sharedResourceFreeze / safeModeDefault`）に加え、AUTH-OPS-03語彙とD1〜D4を照合。
- Verify: 差分/競合=0件。
- Proceed: 差分があれば即停止し指示待ち。差分なしで Phase 2 Plan へ。

### Phase 2 Plan（AC/DoD補完）
- Plan: 本ファイル再読後、operations/documentation同期の AC/DoD 不足（語彙・導線・固定値・停止条件）を補完提案としてドラフト化。
- Execute: 追加提案を既存契約語彙へ正規化し、A3 の `read-only reference only` 制約を維持。
- Verify: A3 単独で契約変更を起こせない。
- Proceed: 変更が CDC を要する場合は **CDC を明文化して承認待ち** とし、承認後に Phase 3 Execute へ。CDC不要なら直ちに Phase 3 Execute へ。

### Phase 3 Execute
- Plan: 本ファイル再読後、凍結I/F統一対象（`contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`）とA1依存順を再固定。
- Execute: 役割語彙・同期導線・D1〜D4固定値・A1依存順を正規化し一貫化。
- Verify: 禁止遷移/語彙ドリフト/固定値ドリフト=0件、`validatorPass=true`。
- Proceed: Verify pass で Phase 4 Verify へ。

### Phase 4 Verify
- Plan: 本ファイル再読後、固定I/F一覧と docs-check 実施手順を検証条件として固定。
- Execute: read-only handoff 形式で検証出力を整え、`docs-check`（`python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` + `git diff --check`）を実施。
- Verify: frozen keys 一致、docs-check pass、Self-Correction が3回を超えていない。
- Proceed: 失敗時は自己修復（最大3回）。3回超過/未定義競合/前提崩壊は即停止し指示待ち。

### Phase 5 Proceed
- Plan: 本ファイル再読後、参照専用 handoff（freezeContractId / fixed keys / unlockRule / Go-NoGo / return path）を確定。
- Execute: A1契約を単一正本として、A3からの再定義禁止と差戻し先A1固定を明示して引き渡す。
- Verify: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` と凍結キー完全一致。
- Proceed: 一致時のみ handoff 完了。不一致時は Phase 2 Plan へ戻す。

## 6) Open/Proceed Gate（固定）

- Gate predicate（唯一）:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
  - `NoGo = !Go`
- Open化条件（Draft -> Open を許可）:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
  - `validatorPass==true`
- 維持条件（Draft維持 / Open(hold)維持）:
  - `a1Status!="Done"` の間は `Draft` 固定（A3 Open化禁止）
  - `pendingDecisionQueueCount>0` の間は `Draft` または `Open(hold)` を維持
  - A3 は `contract reference only` を維持し、契約値の再定義を行わない
- 停止条件（即停止）:
  - A1未完了でA3 Open化要求を受領
  - 契約差分をA3内で確定しようとする要求を受領
  - `safeModeDefault=ON` を後退させる変更要求を受領
- 差戻し先（固定）:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Gate State Summary（as-is）

- 現状:
  - `a1Status="Open"`（`Done` ではない）
  - `A3 Status="Draft"` を維持する
- 解放条件:
  - `A1 Done && pendingDecisionQueueCount==0` を満たし、かつ `Go=true`
- 停止条件:
  - 上記「停止条件（即停止）」のいずれかに該当した時点で作業停止し、指示待ち

## 7) Fail-safe

- 即停止:
  1. Self-Correction 3回超過
  2. 未定義競合
  3. 前提崩壊
  4. 担当外ファイル編集要求
- 停止時報告:
  - 失敗条件 / 影響範囲 / 要承認事項

## 8) Next Step 固定I/F（read-only handoff）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
