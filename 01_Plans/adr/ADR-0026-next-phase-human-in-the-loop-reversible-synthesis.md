# ADR-0026: 次フェーズ計画（HIL-RS-01）Human-in-the-loop可逆統合ループ

- Status: Accepted
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

また、`HIL-RS-01` の停止条件（SafeMode後退禁止、共有リソース競合回避、上位層優先）を満たしたまま
下流（A1/A2/A3）へ進めるためには、ADR採否を Proposed のまま残さず Decider判断で確定する必要がある。

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

## Approval Log

- 2026-03-11: Deciders（Project Maintainers）が `Accepted` を確定。
- 判断根拠:
  1. `HIL-RS-01` の目的（保留維持・可逆性・HIL反復）が `domain.md` / `ADR-0001` と整合している。
  2. 非目標（単一正解示唆UI、SafeMode後退、LLM全面再設計）が明示され、スコープ逸脱を抑制できる。
  3. 停止条件（上位層矛盾・SafeMode契約後退・共有リソース競合）を維持したまま A1着手に進行可能。

## Verify

- 検証観点1: `HIL-RS-01` が Active issue として `issues/README.md` と dashboard の双方に同期されている。
- 検証観点2: AC に「安全」「可逆」「検証コマンド」が含まれる。
- 検証観点3: docs-check（validator/unittest）が成功する。

## Stream J Audit（ADR連動監査: active issue基準）

### Read

- `python 01_Plans/triage_actionable_plans.py` の出力を正とし、active issue 逆引きで対象ADRを抽出した。
- 抽出結果: active issue に直接連動するADRは `ADR-0026` / `ADR-0027` の2件。

### ADR/CDC

- `ADR-0026` / `ADR-0027` の本文に `Context` / `Decision` / `Consequences` が存在することを確認した。
- 本ADR（`ADR-0026`）は CDC 欠損なし。

### Plan

- active issue 連動ADRで CDC 欠損が検出された場合のみ、欠損見出しを最小追記する。
- 欠損なしの場合は「未処理ADRなし」をADR本文へ明文化し、Proceedで逆引き表を固定する。

### Execute

- 本監査回では CDC 欠損を検出しなかったため、仕様追記は監査結果の明文化に限定した（実質変更最小）。

### Proceed（issue逆引き表）

| Active issue | 連動ADR | CDC欠損 | 判定 |
| --- | --- | --- | --- |
| `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis` | `ADR-0026` | なし | 追補不要 |
| `issue-HIL-RS-02-next-phase-delivery-plan` | `ADR-0027` | なし | 追補不要 |

## Proceed

1. `HIL-RS-01` を起点に A1（Architecture最小I/F定義）を最初の実行タスクとして起票する。
2. A2（Frontend実装）/A3（Documentation同期）を依存順序つきで issue 化する。
3. フェーズ出口では `phase-exit-evaluation-HIL-RS-01-<date>.md` を追加して完了判定を記録する。

## Traceability

- Related: `01_Plans/phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`
- Related: `00_Prompt/domain.md`
- Derived-from: `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`


## Stream A critical-path checkpoint（2026-04-29）

### Phase 1: Contract Baseline Read
- 対象（Stream A allowlist）を再読し、`Status / Dependencies / Pending承認` を抽出した。
- 抽出結果: A1=`Open`、RS-01 umbrella=`Open`、RS-02 umbrella=`Open`、A2=`Open`、A3=`Draft`。
- Pending承認: `Approval Record` 必須項目（`approved_by` / `approved_at` / `evidence`）が未充足のため **承認待ち**。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約凍結未完了のまま A2/A3 を前進させると `A1 -> A2 -> A3` 依存が崩れる。
- Decision: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` を固定継続。
- Consequences: 承認待ちの間は Proceed 判定を `Conditional/Needs-decision` に維持し、確定化を行わない。

### Phase 4: Proceed Gate
- 前提差分: fixed keys diff=`0`（再読時点）。
- 判定: **Needs-decision（停止可能状態）**。承認未充足のため、次工程は人間承認入力後に再開する。

## Stream A serial gate verification（2026-04-29, critical path）

### Phase 1: Read同期
- allowlist対象4ファイルを再読し、`schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `Freeze Pack ID=HIL-RS-02-A1-CONTRACT-FREEZE-v1` の一致を確認した。
- fixed keys drift: `0`。

### Phase 2-5: 判定
- ADR側の Context / Decision / Consequences は欠損なし。
- `Pending bypass` 禁止、`A1 Done 前の A2/A3 Open禁止`、`SafeMode既定ON維持` を再確認した。
- 判定: **Conditional / Needs-decision**（`Approval Record` 未充足のため）。


## Stream A Phase 1-5 contract/governance lock (2026-04-29)

### Context
- Stream A（クリティカルパス）は HIL-RS 契約・統治の確定を最短で完了しつつ、A1→A2→A3 依存を崩さないことが要求される。
- 既存記録には `Needs-decision` が残存しており、合意入力前に下流を確定化しない統治境界を再固定する必要がある。

### Decision
- AC/DoD を本ADR上で再固定し、未承認時の判定を `Conditional/Needs-decision` に固定する。
- 固定契約値（`freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON`）は参照専用とし再定義しない。
- A2/A3 は `A2A3_OPEN_ALLOWED=true` を満たすまで `Draft -> Open` を禁止する。

### Consequences
- 合意未充足時に実装/運用更新へ誤進行する経路を遮断できる。
- Stream B/C など後続ストリームは、契約値を再解釈せず固定参照で前進できる。

### AC / DoD（Stream A固定）
- AC-1: `fixed keys diff=0` を維持する。
- AC-2: `Pending -> Approved | Pending -> Rejected` 以外の遷移を導入しない。
- AC-3: A1完了前の A2/A3 Open化を行わない。
- DoD-1: `Plan -> Execute -> Verify -> Proceed` の直列運用を維持する。
- DoD-2: self-correction 試行回数を `0/3` から記録し、4回目相当で停止する。
- DoD-3: `Approval Record` 未入力時は `Needs-decision` で停止またはConditional維持。
