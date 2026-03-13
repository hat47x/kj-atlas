# Issue Draft: FB-P2C-01-A2 Polygon auto-fit / モック検証

- Type: Feature request
- Status: Blocked (Gate 0待ち)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2C-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2C-02`
- RequirementStatement: `Polygon auto-fit` を モック検証 の責務で前進させる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: Gate 0で `deterministicTieBreakOrder` が承認済みである。
  - 操作: モック検証に限定し、A1契約順序に基づく同一入力同一出力の再現性を検証する。
  - 期待結果: A3実装に渡せる再現可能な検証ログが揃う。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Pending（Gate 0未承認のため開始不可）
- DecisionQueueRef（未確定時の参照先）: `issue-FB-P2C-01-a1-interface-contract.md` / Human Decision Gate 0

## 1) 課題 / Problem statement

- A2はA1契約に従ったモック検証フェーズだが、deterministic tie-break order が承認されない限り検証根拠が成立しない。
- そのため本Issueは **Gate 0解除までBlock** とし、推測実装・推測検証を禁止する。

## 2) 背景 / Context

- Backlog基準: `FB-P2C-01` / AC-2C-2, AC-2C-3 / DoD: 同一入力で同一polygonを生成し、padding制約を満たす。
- DoD依存: `02_Architecture/island_shapes.md` deterministic geometry contract。
- 入力契約: A1で定義した `deterministicTieBreakOrder` を唯一の判定順序として採用する。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 判定順序を固定した上で再現性を確認し、レビュー認知負荷を下げる。
- 安全（THREAT_MODEL / SafeMode）: 計画段階では既定ポリシーを不変更。
- 企業・行政要件（enterprise_architecture）: 対象外（N/A）だが、監査可能な検証ログ構造を重視。
- 後方互換（schemas）: 実装前に契約順序の互換リスクを可視化する。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs/Plans only（`01_Plans/issues/issue-FB-P2C-01-*.md`）。
- 実行条件: Gate 0承認後にのみ Execute/Verify へ進む。
- 非目標: 承認前のモック実行、契約順序の独自解釈。

## 5) 受入条件 / Acceptance criteria

- [ ] Gate 0承認記録（deterministicTieBreakOrder）が参照可能である。
- [ ] 同一入力同一出力の検証手順（fixture固定・seed固定・比較キー固定）が明文化される。
- [ ] A1の契約順序（padding遵守優先）を検証観点に含める。
- [ ] 検証レベル `integration` が宣言・整合している。
- [ ] 編集対象ファイル境界が明記され、他レーンとの重複がゼロである。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: Gate 0承認IDを取り込み、Plan開始条件を満たす。
- [ ] T2: モック検証ケース（同一入力反復、境界ケース、padding衝突ケース）を定義する。
- [ ] T3: Verify結果をA3入力契約として明示する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo命名・メタ項目が整合し、検証スクリプトが成功する。
- 未実施時の理由・代替検証:
  - Gate 0未承認の間は Execute/Verify に進まない（Fail-safe）。

## 8) 代替案 / Alternatives considered

- 代替案A: Gate 0未承認でも仮順序でモック実行 → 却下（推測検証を禁止）。
- 代替案B: A2を省略してA3へ直接進行 → 却下（再現性未検証）。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 承認前着手によりA3で契約破綻が発生。
- 影響範囲: `FB-P2C-01` の品質保証と監査可能性。
- ロールバック手順: A2をBlocked維持し、A1のDecision packetへ差し戻す。

## 10) Additional context

- 編集対象ファイル境界: `01_Plans/issues/issue-FB-P2C-01-a2-mock-validation.md` のみ。
- 競合回避メモ: Stream D は FB-P2C系のみ担当し、共有ファイル/FB-P2A/P2B/HIL領域へ非接触。
- Workflow: Plan → Execute → Verify → Proceed（Verify失敗時は最大3回自己修復）。

## 11) Stream D Phase status（2026-03-13 再確認）

- Phase 1 (Read同期): `issues/README.md` / `project-progress-dashboard.md` / `decision-pack-2026-03-human-judgement.md` を再読し、A1→A2→A3依存を再確認。
- Phase 2 (Gate判定): Gate 0承認記録未確認のため、A2はBlocked継続（Execute/Verify未着手）。
- Phase 3 (A2進行): 条件未充足のため未実行。モック検証ログ固定はGate 0承認後に実施。
- Phase 4 (統合同期): 共有3ファイルへ Gate未充足（`DQ-FB-P2C-01: Open`）を同一PRで反映。
