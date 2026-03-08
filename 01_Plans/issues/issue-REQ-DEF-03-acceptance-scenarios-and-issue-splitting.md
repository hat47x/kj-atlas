# Issue Draft: REQ-DEF-03 受入シナリオ先行型のIssue分割ルール整備

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Product Owner + QA Owner
- Scope: `01_Plans/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0012`, `ADR-0019`, `04_Documentation/e2e_testing.md`, `01_Plans/issues/README.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- 要件定義フェーズで受入シナリオが先に固定されないと、Issueが実装タスク列挙に偏りやすい。
- `Expected verification level` は定義済みだが、要求粒度と検証粒度の対応表が不足している。
- 結果として「要件定義の完了」と「実装準備完了」の境界が曖昧になる。

## 2) 背景 / Context

- `ADR-0019` は結合品質ゲートとしてE2E方針を定義している。
- `01_Plans/issues/TEMPLATE.md` はAcceptance/Validation先出しを求めるが、シナリオ粒度の標準は未整備。
- docs-onlyタスクでも、将来のunit/integration/e2eへ接続可能な受入記述が必要。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 要件を行動可能なIssueへ変換し、価値実現までのリードタイムを短縮する。
- 安全（THREAT_MODEL / SafeMode）: 受入シナリオに安全境界を入れることで後工程の見落としを防ぐ。
- 企業・行政要件（enterprise_architecture）: 監査可能な検証記録の入口を要件定義で準備できる。
- 後方互換（schemas）: 互換性検証観点をシナリオに明示し、変更時の判定を容易にする。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（受入シナリオ先行型のIssue分割規約）。
- 変更の最小単位:
  - T1: 要求種別ごとの受入シナリオ最小セットを定義する。
  - T2: `Expected verification level` と要求粒度のマッピングを明文化する。
  - T3: 1Issue 1検証責務（docs-check/unit/integration/e2e）を原則化する。
- 非目標:
  - Playwrightテストや実装コードの追加。
  - CIワークフローの変更。

## 5) 受入条件 / Acceptance criteria

- [ ] 受入シナリオ記述の最小テンプレ（前提/操作/期待結果/除外）が定義される。
- [ ] 要求粒度と `Expected verification level` の対応ルールが定義される。
- [ ] 1Issueあたりの検証責務上限（複合しすぎない）が明文化される。
- [ ] 安全境界と互換境界の確認項目が受入シナリオに含まれる。
- [ ] docs-check コマンドで規約文書の整合を再現確認できる。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 受入シナリオ記述テンプレを作成する。
- [ ] T2: 要求粒度↔検証粒度マトリクスを作成する。
- [ ] T3: Issue分割基準（分割/統合の閾値）を定義する。
- [ ] T4: 既存Draft/Open issueの適用対象を棚卸しする。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-03|受入シナリオ|Expected verification level|分割基準" 01_Plans 04_Documentation`
- 期待結果:
  - issue memo validator が成功し、受入シナリオ規約の記述が追跡可能である。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` と目視で代替し、未実施理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存テンプレ運用のみで追加規約を作らない。
  - 却下理由: 受入記述の粒度差が残り、起票品質が安定しない。
- 代替案B: E2E中心で一律検証を要求する。
  - 却下理由: docs-only/設計タスクに過剰なコストとなる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 分割ルールが厳しすぎて起票速度が下がる。
- 影響範囲: Issue起票、レビュー、検証計画作成。
- ロールバック手順: 分割ルールを「推奨」に戻し、必須はAcceptance最小セットに限定する。

## 10) Additional context

- 要件定義フェーズの壁打ち成果を、実装前レビュー可能なIssue品質へ引き上げるための基盤。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. 検証粒度マッピングを全プロジェクト標準へ昇格する場合。
  2. 受入シナリオテンプレをCI検証対象にする場合。
