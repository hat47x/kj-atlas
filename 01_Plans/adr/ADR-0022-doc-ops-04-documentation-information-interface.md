# ADR-0022: DOC-OPS-04 情報設計I/F（用語・見出し・判定メタ）

- Status: Proposed
- Date: 2026-03-08
- Deciders: Platform Architecture Owner, Plan Owner, Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Derived-from: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`

## Context

DOC-OPS-04 で扱う ADR 候補 B/C/D（可読性ベースライン、品質ゲート、変更統治）は、
いずれも文書間の参照I/Fが揃っていない状態だと、以下の競合を起こしやすい。

1. 用語競合: 「正本」「補助メモ」「決裁入力」「例外承認」が文書ごとに異なる語で記述される。
2. 見出し競合: Plan/Execute/Verify/Proceed の段構成が一貫せず、レビュー比較が困難になる。
3. 判定メタ競合: `Status` / `Scope` / `Expected verification level` / `Source Issue` の必須性が揺れる。

このため、B/C/D を並列化する前に、最低限の情報設計I/Fを先行で固定する必要がある。
ただし、本ADRは「文書I/F」までを対象とし、品質ゲートのCI必須化境界や
例外承認フローの恒久ルールそのものは C/D 側 ADR で扱う。

## Decision

DOC-OPS-04 系 ADR 群の共通I/Fとして、次を採用する。

1. **用語I/F（固定語彙）**
   - 正本（source of truth）
   - 暫定メモ（pre-ADR / pre-approval record）
   - 決裁入力（approval input）
   - 例外承認（exception approval）

2. **見出しI/F（最小段構成）**
   - issue補助メモは `Plan → Execute → Verify → Proceed` を必須とする。
   - ADRは `Context / Decision / Consequences / Traceability` を必須とする。

3. **判定メタI/F（比較可能性の最小セット）**
   - issue補助メモ: `Type`, `Status`, `Scope`, `Related ADR/Spec`, `Expected verification level`, `Source Issue`
   - ADR: `Status`, `Date`, `Deciders`, `Scope`

4. **参照I/F（後続ADRの拘束条件）**
   - ADR-B/C/D は本ADRを `Related` に明記し、上記I/Fを逸脱する場合は逸脱理由を明文化する。
   - B/C/D並列作業中は、統合対象（`01_Plans/issues/README.md`、`01_Plans/project-progress-dashboard.md`）を更新しない。

採用理由:
- 並列化前に比較軸を揃えることで、差分レビューの粒度を一定化できる。
- 実装ルール（03_Implement）へ踏み込まず、計画・設計文書の競合だけを先に抑制できる。

非目標:
- docs-check/CI の fail-on-error 境界の確定。
- 例外承認の役割分離・承認SLAの確定。
- `03_Implement/` 配下の変更規約。

## Consequences

- 期待効果:
  - B/C/D の同時起票で、用語・見出し・メタの基線が一致し、マージ競合が減る。
  - レビュー時に「内容の是非」と「フォーマット差異」を分離して判定できる。

- 副作用/制約:
  - Aの承認が遅延すると B/C/D の実編集開始が遅れる。
  - 既存文書にI/F不一致が見つかった場合、同期修正が別PRで必要になる。

- 移行時対応:
  - 後続ADR-B/C/D起票時に、本ADR準拠チェックを Verify 項目へ追加する。
  - 統合フェーズでのみ README/dashboard の状態同期を行う。

## Traceability

- Related: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- Related: `01_Plans/issues/README.md`
- Related: `01_Plans/project-progress-dashboard.md`
- Related: `01_Plans/adr/ADR-0000-adr-governance.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `01_Plans/adr/ADR-0018-coding-standards-and-smell-remediation.md`
