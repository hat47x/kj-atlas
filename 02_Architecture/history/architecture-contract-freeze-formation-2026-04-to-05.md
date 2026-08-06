# Architecture contract-freeze formation history (2026-04 to 2026-05)

Status: Informative history

Source document: [`02_Architecture/architecture.html`](../architecture.html)

Source anchors: former §7A.0 Input Contract Snapshot, former §7A.2.1 Interface Freeze, former post-§12 Contract Freeze Baseline, former §13 Stream B Contract Reflection Note

Covered period: 2026-04-27〜2026-05-04

Snapshot / source revision: `6a81ee07`（DOC-ARCH-02 H-A移動直前）

Retention reason: CE0/CE1の型・method・event-orderをarchitecture層でfreezeし、mock-firstの下流検証へ接続した形成経緯を、現行の責務・型・API契約と誤認されない形で保持する。

Current normative anchors:

- [Architecture responsibilities and trust boundaries](../architecture.html#ce0-responsibility)
- [Architecture input/output boundary](../architecture.html#ce0-io-boundary)
- [Schema contracts](../schemas.md#12-ce1ce2ce4-型契約実装非依存)
- [API Context Query / Bundle endpoints](../api.md#28-context-query--bundle-contractce1-context-foundation)
- [CE1 v1 reconciliation issue](../../01_Plans/issues/issue-CE1-CONTRACT-01-v1-keyset-and-envelope-reconciliation.md)

この文書は形成履歴であり、現在のrequired/optional key、列挙、既定値、endpoint、status/error、SafeMode境界を上書きしない。以下の`固定`、`freeze`、`Decision`は当時の記録である。

## Former §7A.0 Input Contract Snapshot 固定（CE0）

- **Input Contract Snapshot 固定（CE0）**:
  - snapshot_id: `ce0-contract-freeze-2026-04-27`
  - freeze_mode: `contract-only`
  - downstream_policy: `read-only reference`（CE1/CE2/CE4 は参照のみ）

## Former §7A.2.1 Interface Freeze（APIシグネチャ / データ型 / イベント契約）

CE0では実装詳細ではなく、下流がmockで自走できる最小契約のみを固定する。

- **Type Signatures（v1固定）**
  - `ContextQueryV1 = { goal: string; scope: string[]; depth: "shallow"|"standard"|"deep"; constraints: string[]; reviewFilter: "all"|"human_reviewed_only"; safeModePolicy: { safeMode: true; allowUnreviewedText: false }; outputMode: "preview"|"proposal" }`
  - `ContextBundleV1 = { bundleHash: string; queryRef: string; cards: object[]; islands: object[]; relations: object[]; generatedAt: string }`
  - `ProposalPatchV1 = { proposalId: string; diff: object; rationale: string; sourceBundleHash: string; requestedBy: string }`
  - `AuditEventV1 = { eventId: string; eventType: "proposal.submitted"|"proposal.approval_requested"|"proposal.approved"|"consensus.patch_applied"; at: string; actor: string; proposalId?: string; bundleHash?: string }`

- **Contract Methods（mock-first）**
  - `previewQuery(input: ContextQueryV1): ContextBundleV1`
  - `submitProposal(input: ProposalPatchV1): AuditEventV1`
  - `requestApply(proposalId: string, approver: string): AuditEventV1`

- **Compatibility / Validation Rules**
  - 未知キーは `unknown_contract_key` として拒否する。
  - `ContextBundleV1.bundleHash` は deterministic でなければならず、非決定的結果は `nondeterministic_bundle` とする。
  - `previewQuery` を経ない apply 要求は `preview_required` として失敗扱い。

- **Event-order invariant（適用前提）**
  - 許可順序: `proposal.submitted -> proposal.approval_requested -> proposal.approved -> consensus.patch_applied`
  - 欠落・逆順・直接 `consensus.patch_applied` は No-Go（`consensus_direct_write` 相当）。

## Former 7B.1 Contract Freeze Baseline（2026-05-04 / interface-only）

- Scope: `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の **I/F境界のみ** を固定し、実装詳細は追加しない。
- Fixed boundary: 上記4型は `02_Architecture/schemas.md` の定義をSSOTとし、`02_Architecture/api.md` はその入出力契約を参照する。
- Mock-first policy: CE1/CE2/CE4 は backend/frontend の実装完了待機を禁止し、`A1-CONTRACT-MOCK-v1` 互換fixtureで契約検証を継続する。
- Downstream rule: 下流は判定式と契約IDを read-only 参照し、派生I/Fの再定義を行わない。

## Former 13. Stream B Contract Reflection Note（interface-only / conditional）

### Context

- Stream B は `02_Architecture` の契約反映のみを担当し、実装値ではなく schema/type/signature を固定する。
- CE1/CE2/CE4 の並行進行により、A系契約IDの更新が遅延する可能性があるため、未確定項目は conditional 参照で保持する。

### Decision

- 本書では `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` を interface freeze 対象として維持する。
- A系契約ID参照（例: `A1-ATTR-IF`）は read-only で引用し、未確定時は `conditional` 扱いとして再定義しない。
- mock payload を契約検証の前提に許可し、backend/frontend 実装完了待機を行わない。

### Consequences

- 下流は mock-first で独立検証を継続でき、契約待ちで停止しない。
- safeMode既定ON・未レビュー保護・proposal-only 境界を architecture 層で固定できる。
- conditional 参照が確定した時点で、再採番ではなく参照先更新のみを許可する。
