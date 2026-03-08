# Issue Draft: DOC-OPS-04 設計文書の俯瞰統合アーキテクチャと可読性改善プログラム（ADR候補化前処理監査）

- Type: Documentation quality
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: DOC-OPS-04 監査専任エージェント
- Scope: `01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md` のみ（本Issue更新に限定）
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0002`, `ADR-0018`, `ADR-0019`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- DOC-OPS-04 は本来、複数レイヤ文書へ跨る恒久運用の検討論点を含むため、Issue本文だけで恒久ルールを固定すると「実質ADR化」が発生する。
- 本タスクは「ADR候補化前処理」の監査に限定されるため、実装計画・横断反映・運用固定の切り分けを明確化する必要がある。

## 2) 背景 / Context

- 既存のDOC-OPS-04論点（Information Architecture / Readability / Quality Gates / Governance）は、いずれも恒久ルール化の可能性を含む。
- したがって本Issueで行うべき作業は、ADR候補化に必要な監査記録（Context / Decision / Consequences）を整える前処理までに限定する。

## 3) 必須ワークフロー実施ログ（本監査タスク）

### 3.1 Plan: AC/DoD不足点の抽出と補完案

**不足点（監査観点）**

- AC不足1: 「前処理タスクの完了条件」が恒久運用条件と混在し、監査終了判定が曖昧。
- AC不足2: 「Decisionにおける暫定/恒久の境界」が明文化されないとIssue本文での固定化リスクが残る。
- DoD不足1: 「Issue本文で恒久ルールを固定していないこと」の明示検証項目が必要。
- DoD不足2: 「承認待ちで停止する状態」の記録フォーマットが必要。

**補完案（本Issueでの合意対象）**

- AC補完A: ADR候補A〜Dの各項目に `Context / Decision / Consequences` を独立記述する。
- AC補完B: 各 `Decision` に「Issue内の暫定扱い」と「ADRで確定すべき範囲」を併記する。
- AC補完C: 各 `Consequences` に採用時/非採用時の影響を最低1件ずつ記録する。
- DoD補完A: docs-check観点（メタ必須項目・見出し整合・監査ログ再現）をコマンドで確認する。
- DoD補完B: 「恒久ルール不固定」を差分・文面の両方で確認し、承認待ち状態を明記する。

### 3.2 Execute: ADR候補A〜Dの監査記録（Context / Decision / Consequences）

#### ADR候補A: Documentation Information Architecture

- Context: 正本/解説/索引の責務分離が未確定で、文書追加時の重複正本リスクが残る。
- Decision: 本Issueでは「責務分離が必要」という監査所見のみを記録し、責務定義・配置規約はADRで確定する（暫定扱い）。
- Consequences: 採用時は責務境界の監査可能性が向上する。非採用時は文書増加に伴う責務競合が再発する。

#### ADR候補B: Documentation Readability Baseline

- Context: 読者前提・非目標・到達目標の記載粒度が文書ごとにばらついている。
- Decision: 本Issueでは「ベースライン候補の棚卸し」に限定し、必須項目セットと適用範囲はADRで確定する（暫定扱い）。
- Consequences: 採用時は読解開始コストとレビューばらつきが低減する。非採用時は品質の属人化が継続する。

#### ADR候補C: Documentation Quality Gates

- Context: docs-check運用はあるが、lint/link/metadata検査の必須化境界が統一されていない。
- Decision: 本Issueでは「候補ゲートの監査記録」に留め、CI必須化範囲・例外承認条件はADRで確定する（暫定扱い）。
- Consequences: 採用時は回帰検知が機械化される。非採用時は目視依存で欠陥検知が遅延する。

#### ADR候補D: Documentation Change Governance

- Context: 更新DoD、同期責務、承認責務の境界がIssueごとに再定義されやすい。
- Decision: 本Issueでは「ガバナンス論点の棚卸し」までに限定し、責務分離・承認段階・監査証跡はADRで確定する（暫定扱い）。
- Consequences: 採用時は説明責任と停止基準が明確化する。非採用時は運用判断の属人化が継続する。

### 3.3 Verify: 恒久ルール不固定の確認

- 確認結果: 本Issue本文では、いずれの候補でも「確定」「必須化」「標準運用化」を宣言していない。
- 確認結果: すべてのDecisionは「暫定扱い」として記載し、恒久化はADR分離後の承認に委譲している。
- 判定: **Issue本文で恒久ルールを固定していない（適合）**。

### 3.4 Proceed: 承認待ち記録

- 現在状態: ADR候補A〜Dの前処理監査を完了。
- 次アクション: Human reviewer による ADR候補化可否の承認待ち。
- 停止理由: 本タスクは「前処理監査」に限定されるため、広域文書反映は実施しない。

## 4) 受入条件 / Acceptance criteria（前処理監査限定）

- [x] AC-1: AC/DoD不足点を抽出し、補完案を明記している。
- [x] AC-2: ADR候補A〜Dそれぞれに `Context / Decision / Consequences` の監査記録がある。
- [x] AC-3: 各Decisionに暫定/恒久の境界が明記されている。
- [x] AC-4: 恒久ルールをIssue本文で固定していないことを明示確認している。
- [x] AC-5: 承認待ち記録を残し、前処理範囲で停止している。

## 5) Definition of Done（DoD: 前処理監査）

- [x] DoD-1: 必須ワークフロー（Plan/Execute/Verify/Proceed）をすべて記録した。
- [x] DoD-2: docs-check観点の最低限検証（メタ項目・見出し・構造）を再現可能コマンドで確認した。
- [x] DoD-3: 恒久ルール不固定の確認結果を明文化した。
- [x] DoD-4: 承認待ちで停止する旨を記録し、広域反映を実施していない。

## 6) Self-Correction / Fail-safe

- 自律修正上限: 最大3回。
- 修正ルール:
  1. 1回目: 文面不整合の最小修正。
  2. 2回目: 監査ログ構造（Plan/Execute/Verify/Proceed）の再整列。
  3. 3回目: 暫定/恒久境界表現の縮退修正。
- フェイルセーフ停止条件:
  - 競合兆候（既存規約との衝突）または未定義ルールを検知した場合、推測実装を行わず停止する。
  - 停止時は「判断待ち」へ遷移し、未解消論点を `Additional context` に記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "^(#|##|###)|^- (Type|Status|Lifecycle|Source Issue|Priority|Scope|Related ADR/Spec|Expected verification level):" 01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- 期待結果:
  - issue memo 必須メタの欠落なし。
  - 監査用セクション（Plan/Execute/Verify/Proceed）の存在確認。

## 8) Additional context

- 承認待ち論点:
  1. ADR候補A〜Dを分離起票する順序。
  2. 候補ごとの暫定DecisionをADRへ昇格する際のレビュー体制。
- フェイルセーフ記録: 現時点で競合兆候は未検出。未定義ルールの新規固定は実施していない。
