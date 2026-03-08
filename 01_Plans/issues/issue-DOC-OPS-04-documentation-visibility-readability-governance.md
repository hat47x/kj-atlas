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

- DOC-OPS-04 は複数レイヤ文書へ跨る恒久運用の検討論点を含むため、Issue本文だけで運用固定すると実質ADR化が発生する。
- 本タスクの目的は「ADR候補化前処理監査」に限定し、恒久ルールの断定は行わない。

## 2) 背景 / Context

- 既存論点（Information Architecture / Readability / Quality Gates / Governance）は、いずれも恒久ルール化候補である。
- したがって本Issueは、ADR起票可否を判断するための監査ログ（Context / Decision / Consequences）整備までを範囲とする。

## 3) 必須ワークフロー実施ログ（前処理監査）

### 3.1 Plan

#### 3.1.1 AC/DoD不足点

- AC不足1: 監査タスク完了条件と恒久運用条件が混在している。
- AC不足2: 暫定判断とADR確定事項の境界が曖昧だと、Issue本文での固定化リスクが残る。
- DoD不足1: 「Issue本文で恒久ルールを固定していないこと」の明示検証が必要。
- DoD不足2: 承認待ち停止時に残す判断材料（未解決論点・承認依頼）の定型が必要。

#### 3.1.2 補完ドラフト（本Issue内合意ログ）

- AC補完A: ADR候補A〜Dを監査粒度で `Context / Decision / Consequences` に分解する。
- AC補完B: 各Decisionに「暫定メモ範囲」と「ADRでのみ確定可能な範囲」を併記する。
- AC補完C: 各Consequencesに採用時・非採用時の影響を最低1件ずつ記録する。
- DoD補完A: docs-check相当（必須メタ・見出し整合・検証コマンド再現性）を確認する。
- DoD補完B: 恒久ルール不固定を文面で検証し、承認待ち停止状態を明記する。

#### 3.1.3 合意ログ

- 合意1（取得済み）: 補完ドラフトは前処理監査の完了判定にのみ適用し、恒久規約としては扱わない。
- 合意2（取得済み）: 実行フェーズはADR候補A〜Dの監査記録整理のみに限定する。
- 合意3（未取得・承認待ち）: 恒久ルール化の採否はADR起票後レビューで判断し、本Issueでは確定しない。

### 3.2 Execute

#### 3.2.1 適用境界の分離

- **承認後適用範囲（本Issueでは未適用）**: ADRで確定される恒久ルール。
- **暫定メモ範囲（本Issueで実施）**: 候補論点の棚卸し、影響評価、監査ログ整形。

#### 3.2.2 ADR候補A〜D 監査記録

##### ADR候補A: Documentation Information Architecture

- Context: 正本/解説/索引の責務分離が未確定で、文書追加時に重複正本が生じうる。
- Decision: 本Issueでは「責務分離が必要」という監査所見のみ記録し、責務定義はADRで審査・確定する（暫定）。
- Consequences: 採用時は責務境界の監査容易性が向上。非採用時は責務競合の再発リスクが残る。

##### ADR候補B: Documentation Readability Baseline

- Context: 読者前提・非目標・到達目標の記載粒度に文書間ばらつきがある。
- Decision: 本Issueでは「ベースライン候補の棚卸し」に留め、必須項目セットはADRで審査・確定する（暫定）。
- Consequences: 採用時は読解開始コストの低減が見込める。非採用時は品質の属人化が継続する。

##### ADR候補C: Documentation Quality Gates

- Context: docs-check運用はあるが、lint/link/metadataの必須化境界が統一されていない。
- Decision: 本Issueでは「候補ゲートの監査記録」に限定し、CI必須化範囲と例外条件はADRで審査・確定する（暫定）。
- Consequences: 採用時は回帰検知の自動化が進む。非採用時は目視依存による検知遅延が残る。

##### ADR候補D: Documentation Change Governance

- Context: 更新DoD・同期責務・承認責務の境界がIssue単位で再定義されやすい。
- Decision: 本Issueでは「ガバナンス論点の棚卸し」に留め、責務分離と承認段階はADRで審査・確定する（暫定）。
- Consequences: 採用時は説明責任と停止基準の明確化が期待できる。非採用時は運用判断の属人化が残る。

### 3.3 Verify

- 検証1: docs-check相当として、必須メタ項目と見出し整合をコマンドで確認する。
- 検証2: Decision記述に「確定」「必須化」「標準化」など恒久固定を宣言する文言がないことを確認する。
- 判定: 本Issueは暫定論点整理のみを実施し、恒久ルールを固定していない。

### 3.4 Proceed

- 現在状態: ADR候補A〜Dの前処理監査ログを作成済み。
- 停止理由: 本タスク範囲は暫定メモ整備までであり、恒久化判断はADR審査の責務。
- ADR起票可否判断材料:
  1. 未解決論点: 起票順序、レビュー体制、CI必須化境界、例外承認条件。
  2. 承認依頼事項: 4論点の優先順位と審査責任者の確定。

## 4) 受入条件 / Acceptance criteria（前処理監査限定）

- [x] AC-1: AC/DoD不足点を抽出し、補完ドラフトと合意ログを記録した。
- [x] AC-2: ADR候補A〜Dそれぞれに `Context / Decision / Consequences` を整理した。
- [x] AC-3: 承認後適用範囲と暫定メモ範囲を分離して記述した。
- [x] AC-4: Issue本文で恒久ルールを固定していないことを検証項目として明示した。
- [x] AC-5: ADR起票可否の判断材料（未解決論点・承認依頼事項）を残して停止条件を明記した。

## 5) Definition of Done（DoD: 前処理監査）

- [x] DoD-1: Plan / Execute / Verify / Proceed の4段ログが揃っている。
- [x] DoD-2: docs-check相当の検証コマンドを実行可能な形で記載している。
- [x] DoD-3: 恒久ルールをIssue本文で固定していないことを明示検証している。
- [x] DoD-4: 承認待ち停止時の未解決論点と承認依頼事項を記録している。
- [x] DoD-5: Self-Correction上限（3回）と未解消時の停止方針を記載している。

## 6) Self-Correction / Fail-safe

- 自律修正上限: 最大3回。
- 修正ステップ:
  1. 文面整合修正（最小差分）
  2. 監査ログ整形（Plan/Execute/Verify/Proceed）
  3. 境界表現修正（暫定/恒久の混在排除）
- 3回超で未解消の場合: 推測で進めず停止し、未解決論点を `Additional context` に列挙して人間判断待ちへ移行する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "^(#|##|###|####|#####)|^- (Type|Status|Lifecycle|Source Issue|Priority|Scope|Related ADR/Spec|Expected verification level):" 01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
  - `rg -n "確定|必須化|標準化" 01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- 期待結果:
  - issue memo必須メタと見出し整合に欠落がない。
  - 恒久固定を断定する文言は、Decision断定としては含まれない（本Issueは暫定記録）。

## 8) Additional context

- 承認待ち論点:
  1. ADR候補A〜Dの分離起票順序。
  2. ADRレビュー体制（審査責任者・承認段階）。
  3. docs-check必須化境界と例外承認条件。
- フェイルセーフ記録: 競合兆候・上位方針矛盾・恒久化境界の曖昧さが検出された場合は、推測実装せず停止する。
