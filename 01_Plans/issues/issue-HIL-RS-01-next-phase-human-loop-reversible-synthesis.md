# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: HIL-RS-01
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- `ENV-ARCH-01` は Close 判定済みだが、次フェーズの作業起点（Backlog/依存順序/停止条件）が未固定だと再開時に手戻りが発生する。
- HIL-RS-01 では A1（契約固定）を先行し、A2/A3 の重複解釈と競合を防ぐ必要がある。

## 2) 背景 / Context

- `ADR-0026` D2は A1→A2→A3 の契約先行順序を要求する。
- `domain.md` / `ADR-0001` は保留維持・単一正解否定・可逆性・Human-in-the-loop反復を価値軸として固定している。

## 3) 解決方針 / Proposed solution

- A1で契約ID（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`）と単一参照先を固定する。
- A2/A3は参照専用で着手し、契約変更要求はA1へ差し戻す。
- 共有リソース（`issues/README.md` / `project-progress-dashboard.md`）更新は統合フェーズへ分離する。

## 4) 受入条件 / Acceptance criteria

- [x] `ADR-0026` と本issueで、目的/非目標/停止条件が一致している。
- [x] A1→A2→A3 の依存順序が明示されている。
- [x] 安全制約（SafeMode既定ON、share/export漏えい防止後退禁止）が明記されている。
- [x] A1契約の単一参照先が固定されている。
- [x] `contractLinkLocked=true` / `sharedResourceFreeze=true` の証跡がある。

## 5) Phase 1 Read同期で抽出した契約未確定項目

- 型（Type）: 未確定項目なし（A1契約IDごとの必須/任意/禁止を固定済み）。
- `schemaVersion`: 未確定項目なし（`1.0.0`で固定）。
- 責務境界: 未確定項目なし（A1=契約固定、A2/A3=参照専用）。
- 禁止事項: 未確定項目なし（SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止を固定）。

## 6) Stream A log（Plan → Execute → Verify → Proceed）

### Phase 1: Read & Baseline

- Plan:
  - 対象3ファイル再Read、契約ID・schemaVersion・禁止事項・単一参照先を抽出。
- Execute:
  - `issue-HIL-RS-01` / `issue-HIL-RS-01-A1` / `hil_rs_01_a1_minimum_interface_contract.md` を再Read。
- Verify（事実のみ）:
  - 契約ID: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`。
  - schemaVersion固定値: `1.0.0`（Critique / Attribution / TieBreak）。
  - 単一参照先: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`。
  - 禁止事項: SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止。
  - 想定との差分（契約ID / schemaVersion / 禁止事項 / 参照先）が存在しないことを確認。
- Proceed:
  - Phase 2へ進行。

> Stop Rule（Phase 1）:
> 想定との差分を検知した場合は即停止し、
> 1) 失敗再現手順
> 2) 競合ファイル
> 3) 必要な承認者
> 4) 解決のYes/No質問
> を提出する。

### Phase 2: ADR要否判定（Context / Decision / Consequences）

- Context:
  - A1契約固定は `ADR-0026` の下位具体化に限定される。
- Decision:
  - ADR追加/更新は不要。
- Consequences:
  - A2/A3は契約待ちなしで着手可能。契約変更要求はA1へ差し戻し。

### Phase 3: Contract Fix

- Plan:
  - 必須/任意/禁止を固定し、単一参照先へ集約。
- Execute:
  - A1契約正本を `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` に固定。
  - `contractLinkLocked=true` / `sharedResourceFreeze=true` を証跡化。
- Verify:
  - 契約ID・schemaVersion・overridePolicy・tie-break順序の不一致なし。
- Proceed:
  - Phase 4へ進行。

### Phase 4: Handoff

- Plan:
  - A2/A3向け固定値一覧・参照先一覧・禁止事項を発行。
- Execute:
  - 引き渡しパケットをA1 issueとA1契約正本に同期。
- Verify:
  - 「契約変更禁止。逸脱要求はA1へ差し戻し」を明記。
- Proceed:
  - Stream A範囲の目的（契約/I-F固定）を完了。

## 7) Contract change request routing（固定）

- 差し戻し先（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 受付対象:
  - 契約ID / schemaVersion / requiredFields / overridePolicy / tie-break順序の変更要求
- A2/A3での禁止:
  - 契約本文の直接改訂
  - SSOT（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）の複線化

## 8) Handoff packet（A2/A3）

- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
- Single Reference（固定）:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Freeze flags:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 固定値:
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
  - `DeterministicTieBreakContract.order=padding_compliance>self_intersection_avoidance>minimum_area_delta>minimum_vertex_count`
- 明示禁止:
  - 契約変更禁止。逸脱要求はA1へ差し戻し。


## 9) Phase 5 Gate判定（A2開始条件）

- チェックリスト（A2開始前に全項目必須）:
  - [x] SSOTが `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` で固定されている。
  - [x] `contractLinkLocked=true` / `sharedResourceFreeze=true` がissueとSSOT双方で一致している。
  - [x] `schemaVersion=1.0.0`（Critique / Attribution / TieBreak）が一致している。
  - [x] 禁止事項（SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止）が一致している。
  - [x] 「A2/A3で契約本文を変更しない」ルールが明記されている。
- Gate判定:
  - Ready: チェックリスト全項目達成かつ未定義契約変更要求0件。
  - Block: 1項目でも未達、または未定義契約変更要求/共有リソース更新要求/SafeMode後退前提が発生。

## 10) Phase 5 Gate report（1-page）


- 着手可能条件（Ready）:
  - SSOT が `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` のみで固定。
  - 固定値一致: `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF`、`schemaVersion=1.0.0`、`overridePolicy=human_dual_control_only`。
  - Freeze flag一致: `contractLinkLocked=true` / `sharedResourceFreeze=true`。
  - 安全制約維持: SafeMode既定ON、share/export漏えい防止後退禁止、PII生値保存禁止。

- 停止条件（Block）:
  - 契約ID不一致、schemaVersion不一致、overridePolicy不一致。
  - SSOT複線化（契約参照先が2件以上）。
  - 未定義の共有リソース更新要求、またはSafeMode後退前提の要求。

## 11) Fail-safe stop report template（固定）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問

- 未決裁項目（Pending approvals）:
  - なし（A1範囲で新規ADRは不要判定を維持）。
  - ただし上位方針変更を伴う契約変更要求が発生した場合のみ、A1差し戻し + 人間承認完了まで停止。
