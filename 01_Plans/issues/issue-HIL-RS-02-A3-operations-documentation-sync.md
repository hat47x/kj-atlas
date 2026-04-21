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

## 3) Serial Phase Protocol（強制）

各Phaseは **開始時に対象5ファイルを再読** し、`Plan -> Execute -> Verify -> Proceed` を順に実施する。

### Phase 1: Read & Baseline（2026-04-21）
- Plan: `Status / Priority / Dependencies / AC / DoD` と A1ゲート条件を比較軸として固定。
- Execute: 5ファイルで固定キー、依存順、語彙、NoGo差戻し先を照合。
- Verify: 差分/競合=0件。
- Proceed: 差分ありは Plan 更新後に Phase 2。

### Phase 2: Plan（合意済み）
- Plan: A3は contract reference only を維持し、契約差分要求をA1へ集約する。
- Execute: AC/DoDへ `A1未完了時Open禁止` `NoGo時A1差戻し` `decisionQueueTransition固定` を補完。
- Verify: A3単独で契約変更を起こせない。
- Proceed: CDC必要時のみ Phase 3。

### Phase 3: ADR CDC Gate
- Plan: ADR変更要否を判定。
- Execute: A3は参照専用であり、現更新は契約整合のみ（ADR変更なし）。
- Verify: 承認待ちCDCなし。
- Proceed: Phase 4。

### Phase 4: Execute
- Plan: 凍結I/F統一対象（`contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`）を再固定。
- Execute: 役割語彙・同期導線・D1〜D4固定値・A1依存順を正規化し一貫化。
- Verify: 禁止遷移/語彙ドリフト/固定値ドリフト=0件。
- Proceed: Phase 5。

### Phase 5: Verify
- Plan: docs-check 手順を固定。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` + `git diff --check`。
- Verify: frozen keys一致、docs-check pass、self-correctionが3回以下。
- Proceed: Pass時のみ Phase 6。

### Phase 6: Proceed（handoff）
- handoff固定値: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff禁止遷移: `A1!=Done で A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- D1〜D4 と役割語彙が参照専用で固定される。
- `safeModeDefault=ON` / `human_dual_control_only` を後退させない。

### DoD

- A1未完了時の A3 Open 禁止が明示される。
- 差戻し先が A1 で一意である。
- `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md` 導線が固定される。

## 5) Open/Proceed Gate（固定）

- Gate predicate（唯一）:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
  - `NoGo = !Go`
- Open化条件（Draft -> Open）:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
  - `validatorPass==true`
- 維持条件:
  - `a1Status!="Done"` の間は `Draft` 固定（A3 Open化禁止）
  - `pendingDecisionQueueCount>0` の間は `Draft` または `Open(hold)` 維持
  - A3 は `contract reference only` を維持
- 差戻し先（固定）:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 6) Stop Conditions / Fail-safe

- 固定値ドリフト検出
- `Pending bypass` 要求
- A1未完了でA3 Open化要求
- A3内で契約再定義要求
- Self-Correction 3回超過
- 前提崩壊 / 未定義競合
- 担当外ファイル編集要求

## 7) Gate State Summary（as-is, 2026-04-21）

- `a1Status="Open"`（`Done` ではない）
- `A3 Status="Draft"` を維持
- Open化再判定トリガ:
  1. A1完了（Done化）
  2. Decision Queue pending=0
  3. `validatorPass=true` 再確認

## 8) Next Step 固定I/F（read-only handoff）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
