# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Active (Stream E orchestrator)
- Source Issue: N/A
- Priority: P0
- Owner: Stream E（P0 orchestration / planning only）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/island_shapes.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

---

## Phase 1: Read同期

### Plan
- Stream E編集許可ファイルのみを対象にし、共有統合ファイル・HIL系・実装コードが変更対象外であることを固定する。
- P2B A1契約（`CTR-2B-01-CANDIDATE-GROUP-V1` / `CTR-2B-02-DECISION-LOG-V1`）と P0優先度（P0）の整合を再確認する。

### Execute

| チェック項目 | 入力ソース | 判定 | 備考 |
| --- | --- | --- | --- |
| 編集境界 | Stream E 指示 | Pass | 許可3ファイルのみ編集 |
| P0優先度 | 本メモ + P2B A1メモ | Pass | すべて `Priority: P0` |
| A1契約ID整合 | `issue-FB-P2B-01/02-a1-interface-contract.md` | Pass | 参照契約ID不整合なし |
| 競合有無 | 管轄境界（共有/HIL/実装） | Pass | 対象外ファイルは非変更 |

### Verify
- Proceed 条件（編集境界固定 + P0優先度整合 + 契約ID整合）を満たす。
- Stop 条件（依存矛盾 / 優先度矛盾 / 未定義競合）は現時点で非該当。

### Proceed
- Phase 2（P0 orchestrator方針更新）へ進行。

---

## Phase 2: P0 orchestrator方針更新

### Plan
- Stream Eのオーケストレーション方針を「Plan → Execute → Verify → Proceed」へ統一する。
- A1契約固定を前提とした A2/A3 進行順序を明文化し、契約改訂要求はA1差戻しへ限定する。

### Execute
- 方針固定:
  1. `Plan`: 依存・優先度・競合を先に確認
  2. `Execute`: 契約本文は改変せず、参照関係のみ更新
  3. `Verify`: 契約ID/優先度/停止条件をチェック
  4. `Proceed`: 次Phaseへ移行可否を明示
- 実行順序（P2B）:
  - `A1 interface-contract`（固定済）→ `A2 mock-validation` → `A3 implementation`
- 停止ルール:
  - 契約逸脱、未定義競合、優先度逆転を検知した時点で即停止。

### Verify
- P0 orchestrator方針は既存ADRの範囲内（新規アーキ決定なし）。
- 変更は計画メモ内に閉じ、実装依存なし（Pass）。

### Proceed
- Phase 3（P2B A1契約チェック）へ進行。

---

## Phase 3: P2B A1契約チェック

### Plan
- `FB-P2B-01` / `FB-P2B-02` のA1契約が A2/A3 で再利用できる固定点になっているかを確認する。

### Execute

| Contract | Fixed ID | 必須確認点 | 判定 |
| --- | --- | --- | --- |
| P2B-01 candidate group | `CTR-2B-01-CANDIDATE-GROUP-V1` | `SimilarCandidateGroup` / `CandidateListViewModel` 固定、非自動確定 | Pass |
| P2B-02 decision log | `CTR-2B-02-DECISION-LOG-V1` | `MergeDecisionRecord` 4値 action、append/list/restore固定 | Pass |

- Cross-check結果:
  - Priority: 2件ともP0で一致。
  - 依存順: A1→A2→A3の直列で一致。
  - 競合: 未定義競合なし。

### Verify
- A1契約はA2/A3の単一参照点として成立（Pass）。
- 契約拡張要求はA1差戻しで統制可能（Pass）。

### Proceed
- Phase 4（モック活用前提の依存切り離し記述）へ進行。

---

## Phase 4: モック活用前提の依存切り離し記述

### Plan
- A2でのmock-validationを成立させるため、実装依存を排除した依存境界を定義する。

### Execute
- 依存境界（許可）:
  - 契約ID一致確認
  - 型・必須フィールド・比較キー（`snapshotVersion` / action enum / group関連キー）
  - fixture/stubベース検証
- 依存境界（禁止）:
  - `03_Implement/**` への実コード依存
  - backend/frontend実装詳細（アルゴリズム・永続化方式）への拘束
  - 共有統合ファイルへの直接編集

### Verify
- A2はmock前提で閉じた検証が可能（Pass）。
- A3開始前に実装依存を持ち込まない条件が明文化済み（Pass）。

### Proceed
- Phase 5（整合Verify）へ進行。

---

## Phase 5: Verify（優先度・依存・競合記述の整合）

### Plan
- 本メモとP2B A1メモ間で、優先度・依存順・競合停止条件の整合を最終確認する。

### Execute

| 観点 | 判定 | 根拠 |
| --- | --- | --- |
| 優先度整合 | Pass | すべて P0 |
| 依存整合 | Pass | A1→A2→A3 直列固定 |
| 競合記述整合 | Pass | 未定義競合は即停止で統一 |

### Verify
- フェイルセーフ（依存矛盾/優先度矛盾/未定義競合で停止）を満たす。
- Stream Eの更新範囲は許可3ファイル内に限定されている。

### Proceed
- Stream E baseline更新を完了。A2/A3はA1固定契約を参照して継続可能。

---

## ADRルール適用記録

- 判定: **ADR更新不要**。
- 理由: 本更新は既存契約の参照整合・依存境界整理であり、上位設計の新規決定を追加していない。
- 追跡: 契約ID変更、優先度変更、依存順序変更が発生した場合のみ `Context / Decision / Consequences` を先に作成し承認待ちへ移行。

## Self-Correction Log（最大3回）

1. 修正1: Owner/Statusを Stream E オーケストレーション責務へ更新。
2. 修正2: Phase構成をユーザー指定の5段（Read同期〜整合Verify）へ再編。
3. 修正3: フェイルセーフ停止条件（依存矛盾・優先度矛盾・未定義競合）を全Phaseへ統一適用。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は更新を停止し、競合一覧を提出する。
