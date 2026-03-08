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

**合意取得（実行前ゲート）**

- 合意1（取得済み）: 上記補完案は「前処理監査の完了判定」にのみ適用し、恒久ルールとしては扱わない。
- 合意2（取得済み）: 実行フェーズでは ADR候補A〜D の監査ログ補完に限定し、横断文書更新・規約固定は実施しない。
- 合意3（未取得・承認待ち）: 恒久ルール化の可否は ADR 起票後レビューで判断する（本Issueでは確定しない）。

### 3.2 Execute: ADR候補A〜Dの監査記録（Context / Decision / Consequences）

### 3.2.1) 適用境界（承認後のみ適用 vs 暫定メモ）

- **承認後にのみ適用する範囲**: ADR候補A〜Dで確定する恒久ルール（情報設計責務、可読性必須メタ、品質ゲート必須化、変更ガバナンス）。
- **暫定メモ範囲（本Issue内）**: 候補論点の整理、選択肢、影響評価、docs-check観点の確認ログ。
- 本Issueは **ADR起票前の準備メモ** として扱い、恒久ルールの正本化は `01_Plans/adr/` 承認後に限定する。

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
- ADR起票可否判定: **条件付きで起票可**（候補A〜Dの Context/Decision/Consequences が監査可能な粒度で揃っているため）。
- 未解決論点: 候補A〜Dの起票順序、レビュー体制、CI必須化境界、例外承認条件の4点。
- 次に必要な承認: 「ADR分離起票の優先順位」と「恒久ルール化の審査責任者」を Human reviewer が確定すること。

## 4) 受入条件 / Acceptance criteria（前処理監査限定）

- [x] AC-1: AC/DoD不足点を抽出し、補完案を明記している。
- [x] AC-2: ADR候補A〜Dそれぞれに `Context / Decision / Consequences` の監査記録がある。
- [x] AC-3: 各Decisionに暫定/恒久の境界が明記されている。
- [x] AC-4: 恒久ルールをIssue本文で固定していないことを明示確認している。
- [x] AC-5: 承認待ち記録を残し、前処理範囲で停止している。

## 5) Definition of Done（DoD: 前処理監査）

| 区分 | ドキュメント | 判断 | 理由 / 適用条件 |
|---|---|---|---|
| 必須（取り込む） | 要求一覧（機能要求・非機能要求） | 取り込む | 仕様境界を先に固定し、実装スコープ逸脱を防止する。 |
| 必須（取り込む） | 機能一覧（Feature Inventory） | 取り込む | 画面/API/データ定義との対応軸を作る。 |
| 必須（取り込む） | 業務フロー（As-Is/To-Be） | 取り込む | 操作順序と運用責務の合意を先行させる。 |
| 必須（取り込む） | 画面遷移図 | 取り込む | UI変更時の回帰範囲を特定しやすくする。 |
| 必須（取り込む） | 入出力定義（API/Worker/CLI） | 取り込む | I/F契約をコード前に確定し、結合バグを抑制する。 |
| 必須（取り込む） | ファイル定義（import/export/manifest） | 取り込む | 互換性・監査・移行戦略の前提になる。 |
| 条件付き（段階導入） | ER図 / データモデル図 | 条件付き | 永続化モデル変更があるタスクで必須化する。 |
| 条件付き（段階導入） | 状態遷移図（State Machine） | 条件付き | 非同期処理・承認フロー・モード遷移がある場合に必須化。 |
| 条件付き（段階導入） | 例外/エラー設計（失敗モード一覧） | 条件付き | 外部連携・入力検証・運用影響が大きい領域で必須化。 |
| 条件付き（段階導入） | 受入試験観点表（Requirements→Test） | 条件付き | `Expected verification level` が `integration/e2e` の場合に必須化。 |
| 今回は対象外 | 工数見積り・体制計画文書 | 対象外 | DOC-OPS-04 は文書情報設計品質を主目的とし、PM計画文書は別Issueで扱う。 |

導入順序（固定）:

1. **最小必須セット**（要求一覧/機能一覧/業務フロー/画面遷移/入出力定義/ファイル定義）を標準化。
2. 変更種別に応じて条件付きドキュメント（ER図/状態遷移/エラー設計/受入観点表）を追加適用。
3. docs-check で「作成要否判定」と「未作成時の理由記録」を検証可能にする。

### 4.2 上位統合文書導入時の「正本重複禁止ガード」

`documentation_architecture.md` のような上位統合文書を導入する場合、次のガードを **ADR候補（承認後適用）** として扱う。

- 上位統合文書は「索引・依存関係・更新責務」のみを記述する案とし、仕様値・契約本文・規定値の再定義は禁止候補として ADR で審査する。
- 契約本文（正本）は既存の `schemas.md` / `api.md` / `runtime_parameter_registry.md` / 各ADR に限定する案とし、上位統合文書は該当見出しリンク参照のみを許可する方針を ADR で確定する。
- 上位統合文書に正本内容を引用する場合は、`非正本（参照用）` 明記と正本リンク同段落記載を必須候補として ADR で判断する。
- 正本へ未リンクの断定記述（MUST/SHALL/既定値）を検出した場合の自己修復移行（最大3回）も、運用固定ではなく ADR で採否判断する。

### 4.1 取りうる対策の網羅整理（実行候補）

1. 俯瞰・統合（Information Architecture）
   - 設計文書群の地図化（目的別ナビゲーション: 新規参加者向け / 実装者向け / 運用者向け / 監査向け）。
   - 依存グラフ化（どの文書変更時にどこへ追従更新が必要か）。
   - 「正本」と「解説」の二層化（Normative vs Explanatory）を明示。

2. 可読性・品質向上（Writing Quality）
   - 各文書冒頭へ 5行サマリ + 想定読者 + 想定所要時間を追加。
   - 長文節へ「要点先出し」「決定事項」「根拠」「実装影響」の固定見出しを導入。
   - 用語の表記揺れを抑制する辞書（domain.md 参照）を文書校正ルール化。
   - 長大文書の分割基準（行数/責務/変更頻度）を明文化。

3. 要求技術レベル緩和（Onboarding / Accessibility）
   - Beginner/Practitioner/Expert の3層読みガイドを追加。
   - 「まずここだけ読む」最短導線（30分 / 2時間 / 1日）を提示。
   - 図表化（依存関係図・判断フロー）を追加し、文章依存を軽減。

4. 運用・ガバナンス強化（Maintenance）
   - 文書更新のDefinition of Done（DoD）に「関連文書同期確認」を追加。
   - PRテンプレに docs impact セクションを追加し、設計変更時の同期漏れを防止。
   - 四半期ごとの「文書負債レビュー」（obsolete節/重複/矛盾）を定例化。

5. 自動化・検証（Tooling）
   - issue memo validator を拡張して、必須メタ（対象読者/非目標/更新トリガー）を検査。
   - Markdown lint + link check + 用語検査（禁止語/揺れ語）の導入。
   - 変更差分から関連文書未更新を警告する簡易スクリプトの導入。

## 5) 受入条件 / Acceptance criteria

- [ ] （承認後適用）設計文書の上位統合文書（俯瞰・依存・更新責務）を1つ新設し、Read Order/Project Map から到達可能にする。
- [ ] （承認後適用）`02_Architecture` 主要文書に、最低限の可読性メタ（対象読者、先行読書、到達目標、非目標、更新トリガー）を追加する。
- [ ] （承認後適用）実装前に作成すべき設計成果物（ER図、業務フロー、画面遷移図、機能一覧、ファイル定義、入出力定義）を方針化し、適用条件を定義する。
- [ ] （承認後適用）図表現は GitHub 対応 Markdown + Mermaid.js を標準候補とし、記法制約と更新責務をADRで確定する。
- [ ] （承認後適用）上流工程ドキュメントの取り込み判断（必須/条件付き/対象外）を表形式で定義し、変更種別ごとの適用条件を明確化する。
- [ ] （承認後適用）`Expected verification level` と上流ドキュメント要求（特に受入試験観点表）の対応ルールを定義する。
- [ ] （承認後適用）「要求技術レベル緩和」の施策（多層導線・要点先出し・図表化方針）を文書規約へ昇格する。
- [ ] docs-check 検証（issue memo validator、リンク/メタ確認）が再現可能コマンドで記録されている。
- [ ] SafeMode・漏えい防止・契約正本の優先順位を弱めないことが明記されている。
- [ ] （承認後適用）上位統合文書における「正本重複禁止ガード」（非正本明記 + 正本リンク必須 + 再定義禁止）を運用ルール化する。
- [ ] ADR候補化の一次判定結果（Context/Decision/Consequences）が記録され、恒久ルールはADR分離で確定する方針が明記されている。
- [ ] 自己修復3回ルール（差分修正→再検証）と、未解消時のフェイルセーフ停止条件が定義されている。

## 5.5) Definition of Done（DoD）補完

- [ ] DoD-1: AC項目がすべて満たされ、未達項目は理由・再開条件・担当を記録している。
- [ ] DoD-2: docs-checkコマンド結果（成功/失敗）を1つの検証ログとして残している。
- [ ] DoD-3: 上位統合文書に正本重複がないことを差分レビューで確認している。
- [ ] DoD-4: ADR候補化が必要な論点は `Context / Decision / Consequences` 形式で切り出し済みである。
- [ ] DoD-5: SafeMode・漏えい防止・契約正本優先の3原則を弱める変更がない。

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
