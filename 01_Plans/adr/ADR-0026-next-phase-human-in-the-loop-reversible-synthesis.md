# ADR-0026: 次フェーズ計画（HIL-RS-01）Human-in-the-loop可逆統合ループ

- Status: Proposed
- Date: 2026-03-11
- Deciders: Project Maintainers
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/frontend/`, `04_Documentation/`
- Source Issue: `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Related: `00_Prompt/domain.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md`

## Context

`ENV-ARCH-01` は phase-exit 評価で Close 可となり、次フェーズ開始条件として
「次Backlog IDに紐づく Open issue memo 化」が明示された。

プロジェクト目的（`00_Prompt/domain.md`）と価値→要件（`ADR-0001`）に照らすと、
次に優先すべきは次の3点である。

1. **意味の保留**を維持した探索（P-01）。
2. **単一正解の否定**を維持した複数案比較（P-02）。
3. **Human-in-the-loop 反復**（Critique→再提案）とレビュー追跡（P-04/P-03）。

上記を満たすため、次フェーズは大規模一括実装ではなく、契約先行で可逆統合ループを段階導入する計画へ固定する。

## Decision

次フェーズ Backlog を **HIL-RS-01（Human-in-the-loop Reversible Synthesis）** として開始する。

### D1. フェーズ目的（Value Anchor）

- 目的は「精度競争」ではなく、**保留を維持した探索支援**の強化とする。
- AI提案は常に候補扱いとし、確定操作は人間操作でのみ行う。

### D2. 実行順序（契約先行）

1. Plan: issue で AC/非目標/検証計画を固定する。
2. Architecture: 最小 I/F（Critique入力、再提案差分、レビュー帰属）を定義する。
3. Implement: frontend を小粒度タスクへ分割して実装する。
4. Documentation: 操作手順と制約を運用文書へ同期する。

### D3. 非目標（このフェーズで扱わない）

- LLM Provider の全面再設計。
- 採点・ランキング導入など単一正解を示唆するUI。
- SafeMode既定ONを緩める変更。

### D4. Gate（着手・停止・再開）

- 着手条件:
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` が Open で、AC/Validation plan が充足している。
- 停止条件:
  1. `domain.md`（保留/違和感/可逆性）と矛盾する設計が必要になった場合。
  2. SafeMode 契約の後退が前提になる場合。
  3. 共有リソース（dashboard / issues index）で同時編集競合が発生した場合。
- 再開条件:
  - 上位層（00〜02）へ修正提案を先に反映し、Deciders合意後に再開する。

## Consequences

- 期待効果:
  - 価値整合を維持しつつ、次フェーズ着手の作業起点を明確化できる。
  - 契約先行により frontend 実装の手戻りを抑制できる。
- 副作用/制約:
  - 短期の機能追加速度は抑制される。
  - 01/02/03/04 の同期運用コストが増える。

## Verify

- 検証観点1: `HIL-RS-01` が Active issue として `issues/README.md` と dashboard の双方に同期されている。
- 検証観点2: AC に「安全」「可逆」「検証コマンド」が含まれる。
- 検証観点3: docs-check（validator/unittest）が成功する。

## Proceed

1. `HIL-RS-01` を起点に A1（Architecture最小I/F定義）を最初の実行タスクとして起票する。
2. A2（Frontend実装）/A3（Documentation同期）を依存順序つきで issue 化する。
3. フェーズ出口では `phase-exit-evaluation-HIL-RS-01-<date>.md` を追加して完了判定を記録する。

## Traceability

- Related: `01_Plans/phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `00_Prompt/domain.md`
- Derived-from: `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
