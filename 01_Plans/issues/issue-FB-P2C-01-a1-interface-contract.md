## Stream D (contract-connection surface only) — 2026-05-01

- Context: CE4 `/context/bundles:resolve` + `/context/v1/bundles:resolve` の接続面は `queryCanonicalHash` / `bundleHash` / `equivalenceKey` を最小契約として固定。
- Decision: 契約面は `proposalLifecycle=proposed`（候補提示のみ）と `safeMode=true required` を維持し、unknown contract key は 400 を返す。
- Consequences: 下流FB-P2C実装は監査4点セット（`query/bundle/proposal/apply`）を read-only 参照し、契約変更はA1再起票時のみ許可。

# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream A critical path）

- Type: Feature request
- Status: Open
- Priority: P0
- Owner: Stream A（critical path contract freeze）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Dependencies: `A1 -> A2 -> A3`, A2/A3はA1 read-only参照
- Related ADR: `ADR-0001`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`
- Non-target file policy: allowlist（本Issue + `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）以外は不干渉

- Contract snapshot date: `2026-05-01`（固定入力）
- Execution order (Stream A fixed serial): 2/2 FB-P2C A1契約凍結

---

## Phase 1: Read & Contract Inventory（Plan → Execute → Verify → Proceed）

### Plan
- 目的: 未確定契約項目（APIシグネチャ / 型 / schemaVersion / 判定ゲート）を棚卸しし、A2/A3に渡せる固定一覧を準備する。

### Execute（確定/未確定抽出）

| Category | Key | Current Value | State | Note |
| --- | --- | --- | --- | --- |
| ID | `freezeContractId` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | Fixed | SSOT一致必須 |
| IDs | `contractIds` | `A1-CRITIQUE-IF\|A1-REDIFF-IF\|A1-ATTR-IF\|A1-ERROR-IF` | Fixed | 順序固定 |
| Version | `schemaVersion` | `1.0.0` | Fixed | 改版はA1 CDCのみ |
| Policy | `overridePolicy` | `human_dual_control_only` | Fixed | 緩和禁止 |
| Gate | `contractLinkLocked` | `true` | Fixed | 解除禁止 |
| Gate | `sharedResourceFreeze` | `true` | Fixed | 解除禁止 |
| Safety | `safeModeDefault` | `ON` | Fixed | 後退禁止 |
| Safety | `safeModeBoundary` | `SAFE_MODE_STRICT_ON` | Fixed | 後退禁止 |
| Queue | `decisionQueueTransition` | `Pending -> Approved \| Pending -> Rejected` | Fixed | bypass禁止 |
| API shape | `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1` | SSOT参照 | Fixed | A2/A3再定義禁止 |
| Pending | `Approval Record` | `Pending` | Unresolved | human approval required |
| Held | `HIL-RS-02-GOV-EXCEPTION-01` | `held` | Unresolved | human decision required |

### Verify
- AC-1: 未確定項目が明示列挙されていること（`Approval Record`, `held`）。
- AC-2: 固定契約キーが閉集合で列挙されていること。
- AC-3: A2/A3が read-only 参照であること。
- 判定: AC充足（Proceed可）。

### Proceed
- 欠落なし。Phase 2へ遷移。

---

## Phase 2: ADR明文化（承認待ち）

### Context
- A1を唯一ゲートとして固定しない場合、A2/A3が派生契約を再定義して依存順 `A1 -> A2 -> A3` が崩れる。

### Decision
- 契約固定値は以下を採用し、承認までは `draft/frozen-candidate` として扱う。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

### Consequences
- 承認前にA2/A3へ破壊的影響を出す変更（ID変更・schema改版・安全境界緩和）は確定しない。
- 未承認事項（`Approval Record`, `held`）は開始条件に使わず、`Needs-decision` を維持する。

---

## Phase 3: Contract Freeze

### Gate Conditions（固定）
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `validatorPass=true`
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`

### A2/A3向け固定値一覧（凍結）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

---

## Phase 4: Handoff

### Stream B/C向け引継ぎメモ（read-only）
- Reference SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Contract Freeze memo: 本Issue本文「Phase 3: Contract Freeze」
- Prohibited:
  1. 契約IDの追加/改名/削除
  2. `schemaVersion` 改版
  3. `Pending` bypass
  4. SafeMode/share-export 境界緩和

### 変更凍結宣言
- `contractLinkLocked=true` かつ `sharedResourceFreeze=true` を満たす間、A1契約を凍結対象とし、A2/A3は参照専用とする。
- 解除は A1 CDC 承認記録（`approved_by`, `approved_at`, `evidence`）完備時のみ。
