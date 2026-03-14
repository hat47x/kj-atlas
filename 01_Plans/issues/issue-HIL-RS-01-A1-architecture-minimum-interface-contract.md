# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定（Critique/再提案差分/レビュー帰属）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: `HIL-RS-01`
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`, `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`
- Expected verification level: `docs-check`

## 0) Stream A workflow log（Plan → Execute → Verify → Proceed）

### Phase 1: Read & Baseline

- Plan:
  - 対象3ファイルを再Readし、契約ID / schemaVersion / 禁止事項 / 単一参照先を抽出する。
  - AC: A1契約ID（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`）が一意、単一参照先が1件。
- Execute:
  - 再Read対象:
    1. `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
    2. `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
    3. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Verify（事実のみ）:
  - 抽出された契約IDは3件（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`）。
  - `schemaVersion` 固定値は `1.0.0`（Critique / Attribution / TieBreak）。
  - 単一参照先は `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`。
  - 禁止事項は SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止。
  - 想定との差分（契約ID / schemaVersion / 禁止事項 / 参照先）が存在しないことを確認。
- Proceed:
  - Phase 2へ進行。

> Stop Rule（Phase 1）:
> 想定との差分を検知した場合は即停止し、
> 1) 失敗再現手順
> 2) 競合ファイル
> 3) 必要な承認者と判断事項
> を提出する。

### Phase 2: ADR要否判定（Context / Decision / Consequences）

#### Context

A1の作業は `ADR-0026` D2（契約先行）の下位具体化であり、上位方針（価値軸・安全制約・停止条件）を変更しない。

#### Decision

ADR追加/更新は不要。上位方針変更が必要な契約変更要求が出た場合のみ、承認完了まで停止する。

#### Consequences

A2/A3は契約待ちなしで着手可能。契約変更要求はA1へ差し戻す。

### Phase 3: Contract Fix

- Plan:
  - 必須/任意/禁止の境界を固定し、単一参照先へ集約する。
- Execute:
  - 正本を `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定。
  - Freeze flag を明文化（`contractLinkLocked=true`, `sharedResourceFreeze=true`）。
- Verify:
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` が固定。
  - `schemaVersion=1.0.0`（Critique / Attribution / TieBreak）が固定。
  - 単一参照先が1件であることを確認。
- Proceed:
  - Phase 4へ進行。

### Phase 4: Handoff

- Plan:
  - A2/A3向けの固定値一覧・参照先一覧・禁止事項を発行する。
- Execute:
  - 引き渡し情報を本issueとArchitecture正本に同期。
- Verify:
  - 「契約変更禁止。逸脱要求はA1へ差し戻し」を明記。
- Proceed:
  - Stream A作業完了（契約/I-F固定のみ）。

## 1) Requirement meta I/F

- RequirementID: `HIL-RS-01-A1`
- RequirementStatement: Critique入力/再提案差分/レビュー帰属の最小I/F契約を固定し、A2/A3が契約参照のみで着手可能な状態にする。
- PriorityClass: Must
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check

## 2) Fixed handoff packet（A2/A3向け）

- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Single Reference（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Fixed Values（固定）:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
  - `DeterministicTieBreakContract.schemaVersion=1.0.0`
  - `DeterministicTieBreakContract.order=padding_compliance>self_intersection_avoidance>minimum_area_delta>minimum_vertex_count`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 禁止事項:
  - 契約ID / schemaVersion / requiredFields / overridePolicy の変更
  - 単一参照先の複線化
  - `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` の更新

## 3) Non-goals（固定）

- `03_Implement/**` の実装変更は実施しない。
- `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/README.md` / `01_Plans/issues/decision-pack-2026-03-human-judgement.md` は更新しない。
- A2/A3で契約変更を行わない。


## 4) Contract change request routing（固定）

- 差し戻し先（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 受付対象:
  - 契約ID / schemaVersion / requiredFields / overridePolicy / tie-break順序の変更要求
- A2/A3での禁止:
  - 契約本文の直接改訂
  - SSOT（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）の複線化

## 5) Fail-safe

- Self-Correctionは最大3回まで。
- 3回超過 / 前提崩壊 / 未定義競合を検知した場合は即停止し、
  1) 失敗再現手順
  2) 競合ファイル
  3) 必要な承認者と判断事項
  を提出する。

## 6) Phase 5 Gate判定（A2開始条件）

- チェックリスト（A2開始前に全項目必須）:
  - [x] SSOTが `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` で固定されている。
  - [x] `contractLinkLocked=true` / `sharedResourceFreeze=true` がA1 issueとSSOTの双方で一致している。
  - [x] `schemaVersion=1.0.0`（Critique / Attribution / TieBreak）が一致している。
  - [x] 禁止事項（SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止）が一致している。
  - [x] 「A2/A3で契約本文を変更しない」が明記されている。
- Gate判定:
  - Ready: チェックリストが全て満たされ、未定義契約変更要求が0件。
  - Block: 1項目でも未達、または未定義契約変更要求/共有リソース更新要求/SafeMode後退前提が発生。

## 7) Phase 5 Gate report（1-page）


- 着手可能条件（Ready）:
  - SSOT が `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` のみで固定。
  - 固定値一致: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`、`schemaVersion=1.0.0`、`overridePolicy=human_dual_control_only`。
  - Freeze flag一致: `contractLinkLocked=true` / `sharedResourceFreeze=true`。
  - 安全制約維持: SafeMode既定ON、share/export漏えい防止後退禁止、PII生値保存禁止。

- 停止条件（Block）:
  - 契約ID不一致、schemaVersion不一致、overridePolicy不一致。
  - SSOT複線化（契約参照先が2件以上）。
  - 未定義の共有リソース更新要求、またはSafeMode後退前提の要求。

- 未決裁項目（Pending approvals）:
  - なし（A1範囲で新規ADRは不要判定を維持）。
  - ただし上位方針変更を伴う契約変更要求が発生した場合のみ、A1差し戻し + 人間承認完了まで停止。
