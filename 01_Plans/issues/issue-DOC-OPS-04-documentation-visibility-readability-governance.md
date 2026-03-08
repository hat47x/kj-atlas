# Issue Draft: DOC-OPS-04 設計文書の俯瞰統合アーキテクチャと可読性改善プログラム

- Type: Documentation quality
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + Documentation Maintainers
- Scope: `AGENTS.md`, `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0002`, `ADR-0008`, `ADR-0018`, `ADR-0019`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `02_Architecture/api.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- プロジェクト規模拡大に伴い、設計文書の参照経路が多段化し、初見読者・新規実装者が「どの文書をどの順で読めば判断できるか」を即時把握しにくくなっている。
- 00〜04階層の規律はあるが、意思決定を横断的に俯瞰する「上位統合ビュー」が不足し、仕様の全体像・依存関係・優先順位が分断されて見える。
- 個別文書ごとに求められる前提知識レベルが高く、読解コストが高止まりしている。結果として、設計判断の再現性・オンボーディング速度・レビュー効率が低下しうる。

## 2) 背景 / Context

- 現状は `AGENTS.md` の Read Order と Project Map が入口として機能しているが、「読んだあとにどう統合理解するか」を担う文書が不足している。
- `02_Architecture/` は単一文書ごとの正本性が高い一方、文書間の依存関係（先に読むべき章、同時参照すべき契約、更新同期単位）が暗黙知化しやすい。
- `01_Plans/issues/` には文書改善タスクが散在しており、短期修正は進むが、中長期の文書情報設計（Information Architecture）としての統制計画が未固定。

## 2.5) ADR候補化前処理（DOC-OPS-04限定）

本Issueでは、DOC-OPS-04 全体実装には進まず、**ADR候補化の前処理のみ**を実施する。

### 2.5.1) 一次判定（Context / Decision / Consequences）

| 観点 | 要約 | 判定への影響 |
|---|---|---|
| Context | 対象は `AGENTS.md` / `01_Plans` / `02_Architecture` / `04_Documentation` を横断し、Read Order・正本導線・更新責務を再設計する。 | 既存運用を跨ぐ恒久ルール化が発生しうるため、ADR候補化の必要性が高い。 |
| Decision | **一次判定: ADR候補化を必須（Yes）**。ただし本Issue内で恒久ルールを固定せず、候補論点を `Context / Decision / Consequences` 形式で分離起票準備する。 | Issue本文のみで恒久方針を凍結しない。DecisionはADRへ昇格して確定する。 |
| Consequences | 先にADR候補化することで、上位統合文書の責務・品質ゲート・例外運用の固定範囲が監査可能になる。未実施の場合、Issueメモが実質ADR化し重複正本を生みやすい。 | ADR未分離のまま恒久ルールを追記する変更を禁止する。 |

### 2.5.2) AC/DoD不足の提案（ADR候補化前処理向け）

以下を **追加提案（合意対象）** とし、前処理の受入条件に限定して扱う。

- AC提案A: ADR候補A〜Dそれぞれに `Context / Decision / Consequences` を独立記述する。
- AC提案B: 各 `Decision` に「Issue内の暫定扱い」と「ADRで固定すべき範囲」を分離して明記する。
- AC提案C: 各 `Consequences` に採用時・非採用時の影響を最低1件ずつ記載する。
- DoD提案A: docs-check（メタ必須項目、リンク、候補間の一貫性）を再現可能コマンドで記録する。
- DoD提案B: 本更新で恒久運用ルールを増設しない（Issue本文で固定しない）ことを差分で確認する。

### 2.5.3) ADR候補A-D（Context / Decision / Consequences）

#### ADR候補A: Documentation Information Architecture

- Context: 文書の正本/解説/索引責務が分散し、参照開始点と契約正本への導線が読者依存になっている。
- Decision: Issue内では「責務分離が必要」という論点定義に留める。正本/解説/索引の恒久定義と配置規約はADRで固定する。
- Consequences: 採用時は文書責務が監査可能になり、正本重複を抑止できる。非採用時は文書追加時に責務競合が再発し、DOC-OPS系Issueで都度再解釈が必要になる。

#### ADR候補B: Documentation Readability Baseline

- Context: 対象読者・前提・非目標・到達目標の記載粒度が文書ごとに不均一で、読み順と理解負荷が安定しない。
- Decision: Issue内では「可読性ベースライン項目の候補列挙」に限定する。必須項目セットと適用範囲（全体/一部）はADRで固定する。
- Consequences: 採用時は新規参画者の読解開始コストを下げ、レビュー観点を定型化できる。非採用時は文書品質が執筆者依存のままとなり、更新時の判断再現性が低下する。

#### ADR候補C: Documentation Quality Gates

- Context: docs-checkの運用は存在するが、lint/link/metadata validator の必須化レベルと適用境界が未統一である。
- Decision: Issue内では「品質ゲート対象の候補」を整理する。CI必須化の範囲・失敗時ポリシー・例外承認条件はADRで固定する。
- Consequences: 採用時は文書変更の回帰検知が機械化され、差分レビューの検査漏れを抑制できる。非採用時は目視依存が継続し、リンク切れやメタ欠落の検出が遅延する。

#### ADR候補D: Documentation Change Governance

- Context: 文書更新DoD、同期対象、レビュー責務、例外承認の境界がIssue単位で都度定義されやすい。
- Decision: Issue内では「ガバナンス論点の棚卸し」に留め、恒久運用フロー（責務分離・承認段階・監査証跡）はADRで固定する。
- Consequences: 採用時は変更時の説明責任と停止基準が明確化し、ドキュメントドリフトを抑制できる。非採用時は運用判断が属人化し、重大変更時に合意形成コストが上がる。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 仕様判断を人間中心で追跡可能にするため、文書間の意味接続（Context -> Decision -> Implementation）を明示する必要がある。
- 安全（THREAT_MODEL / SafeMode）: 読解ミスで SafeMode や漏えい防止ポリシーの優先順位を誤ると、実装・運用の安全逸脱が発生する。
- 企業・行政要件（enterprise_architecture）: 監査説明責任が要求される環境では、参照可能な設計トレーサビリティと判断経路の明確化が必須。
- 後方互換（schemas）: 文書構造改編時に契約正本（schemas/api/runtime parameter）の所在が曖昧になると、互換運用が破綻するため明示的ガードが必要。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（設計文書の情報設計・可読性・運用規約を再編）。
- 変更の最小単位（再開可能タスク）:
  - 文書レイヤA（俯瞰）: 全体像・依存関係・更新責務を定義する上位統合文書（仮称: `02_Architecture/documentation_architecture.md`）を新設。
  - 文書レイヤB（個別品質）: 各設計文書に「対象読者 / 先に読む文書 / 本文の到達目標 / 非目標 / 更新トリガー」をテンプレ化して追記。
  - 文書レイヤC（運用）: 変更時チェックリスト（構造・可読性・難易度・リンク整合）を `01_Plans/issues/README.md` か `04_Documentation/operations.md` に固定。
  - 文書レイヤD（継続監査）: docs lint（メタ項目欠落・リンク切れ・必須セクション欠落）を段階導入する。
- 非目標:
  - アプリ機能仕様そのものの変更。
  - API/Schema の契約変更。
  - Frontend/Backend 実装変更。

### 4.0 事前設計ドキュメント作成方針（Pre-coding gate）

実装（03_Implement）へ着手する前に、対象機能に応じて次の設計文書を `02_Architecture/` 配下へ先行作成する。

- ER図（必要なデータモデル変更がある場合）
- 業務フロー（利用者・運用者の主要フロー）
- 画面遷移図（UI変更がある場合）
- 機能一覧（対象スコープの機能境界）
- ファイル定義（永続化・import/exportファイル）
- 入出力定義（API/Worker/CLIを含むI/F契約）

作図・表現ルール:

- GitHubでレンダリング可能な Markdown + Mermaid.js のみを使用する。
- 図だけで完結させず、各図の直後に「目的」「前提」「非目標」「更新トリガー」を明記する。
- 仕様正本は図単体ではなく本文契約（schema/api/parameter registry）であり、図は理解支援と依存可視化を担う。


### 4.0A 上流工程ドキュメントの詳細評価（取り込み判断）

上流工程で候補となる設計ドキュメントを評価し、DOC-OPS-04 の対象に **取り込む / 段階導入 / 今回は対象外** を明確化する。

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

`documentation_architecture.md` のような上位統合文書を導入する場合、次のガードを **必須** とする。

- 上位統合文書は「索引・依存関係・更新責務」のみを記述し、仕様値・契約本文・規定値を再定義しない。
- 契約本文（正本）は既存の `schemas.md` / `api.md` / `runtime_parameter_registry.md` / 各ADR に限定し、上位統合文書は該当見出しへのリンク参照のみを行う。
- 上位統合文書に正本内容を引用する場合は、要約の先頭に `非正本（参照用）` と明記し、同段落内に正本へのリンクを必須化する。
- 正本へ未リンクの断定記述（MUST/SHALL/既定値）を検出した場合は、自己修復プロトコルへ移行し、3回で解消できなければフェイルセーフ停止する。

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

- [ ] 設計文書の上位統合文書（俯瞰・依存・更新責務）を1つ新設し、Read Order/Project Map から到達可能になっている。
- [ ] `02_Architecture` 主要文書に、最低限の可読性メタ（対象読者、先行読書、到達目標、非目標、更新トリガー）が追加される方針が固定されている。
- [ ] 実装前に作成すべき設計成果物（ER図、業務フロー、画面遷移図、機能一覧、ファイル定義、入出力定義）が方針として明文化され、適用条件が定義されている。
- [ ] 図表現は GitHub 対応 Markdown + Mermaid.js を標準とし、記法制約と更新責務が明記されている。
- [ ] 上流工程ドキュメントの取り込み判断（必須/条件付き/対象外）が表形式で定義され、変更種別ごとの適用条件が明確化されている。
- [ ] `Expected verification level` と上流ドキュメント要求（特に受入試験観点表）の対応ルールが定義されている。
- [ ] 「要求技術レベル緩和」の施策（多層導線・要点先出し・図表化方針）が文書規約として明文化されている。
- [ ] docs-check 検証（issue memo validator、リンク/メタ確認）が再現可能コマンドで記録されている。
- [ ] SafeMode・漏えい防止・契約正本の優先順位を弱めないことが明記されている。
- [ ] 上位統合文書における「正本重複禁止ガード」（非正本明記 + 正本リンク必須 + 再定義禁止）が運用ルールとして明文化されている。
- [ ] ADR候補化の一次判定結果（Context/Decision/Consequences）が記録され、恒久ルールはADR分離で確定する方針が明記されている。
- [ ] 自己修復3回ルール（差分修正→再検証）と、未解消時のフェイルセーフ停止条件が定義されている。

## 5.5) Definition of Done（DoD）補完

- [ ] DoD-1: AC項目がすべて満たされ、未達項目は理由・再開条件・担当を記録している。
- [ ] DoD-2: docs-checkコマンド結果（成功/失敗）を1つの検証ログとして残している。
- [ ] DoD-3: 上位統合文書に正本重複がないことを差分レビューで確認している。
- [ ] DoD-4: ADR候補化が必要な論点は `Context / Decision / Consequences` 形式で切り出し済みである。
- [ ] DoD-5: SafeMode・漏えい防止・契約正本優先の3原則を弱める変更がない。

## 5.6) 自己修復プロトコル（最大3回）とフェイルセーフ停止

文書変更中に検証不一致・重複正本・リンク不整合を検出した場合は、次の順序を固定する。

1. **自己修復1回目**: 不整合箇所を最小修正し、docs-checkを再実行。
2. **自己修復2回目**: 依存文書を含めて同期修正し、docs-checkを再実行。
3. **自己修復3回目**: 章構成を縮退（索引化/要約化）して再検証。

停止条件（フェイルセーフ）:

- 3回目終了時点で不整合が残る場合は **それ以上の拡張編集を禁止** し、未解消論点・影響範囲・暫定回避策を `Additional context` へ記録して停止する。
- フェイルセーフ停止時は「正本側を変更しない」「新規正本を作らない」を必須条件とする。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: 現行設計文書の情報設計監査（重複、欠落、依存不明、読者不一致）を実施し、監査結果を残す。
- [ ] T2: 上位統合文書（仮称 `documentation_architecture.md`）の章立て・責務境界・正本参照ルールを草案化する。
- [ ] T3: 個別文書テンプレ（対象読者/前提/非目標/更新トリガー）を定義し、主要文書へ段階適用する。
- [ ] T3.5: pre-coding設計成果物テンプレ（ER/業務フロー/画面遷移/機能一覧/ファイル定義/入出力定義）と Mermaid記法ガイドを作成する。
- [ ] T3.6: 上流工程ドキュメントの詳細評価結果（必須/条件付き/対象外）を運用ルール化し、適用判断チェック項目を追加する。
- [ ] T4: 難易度緩和施策（3層ガイド、読む順の短縮導線）を AGENTS.md と関連文書へ反映する。
- [ ] T5: docs-check 自動検証の拡張方針（lint/validator/link checker）を確定する。
- [ ] T6: 上記実施中に仕様決定が必要な論点を ADR 候補として切り出す。
- [ ] T7: 上位統合文書に対する「正本重複禁止ガード」チェック項目を docs-check 手順へ追加する。
- [ ] T8: 自己修復3回プロトコルとフェイルセーフ停止条件を運用手順として明文化する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "^# |^- (Type|Status|Lifecycle|Source Issue|Priority|Scope|Related ADR/Spec|Expected verification level):" 01_Plans/issues/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- 期待結果:
  - issue memo の必須メタが欠落なく、active index と整合している。
  - docs-check レベルの検証が再現可能である。
- 未実施時の理由・代替検証:
  - Python実行不可環境では `rg` + 目視レビューで代替し、未実施理由を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存文書を都度改善し、上位統合文書を作らない。
  - 却下理由: 改善の局所最適化が続き、全体整合と学習コスト低減が進まない。
- 代替案B: 新規文書だけ作り、既存文書へメタ情報を追加しない。
  - 却下理由: 実際に参照される個別文書の理解負荷が残り、効果が限定的。
- 代替案C: 図表を外部ツールで管理し、リポジトリには画像のみ置く。
  - 却下理由: 差分追跡・レビュー再現性・テキストベース保守性が低下する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード:
  - 俯瞰文書が重複正本化し、逆に矛盾源になる。
  - 可読性改善の名目で文書が冗長化し、保守負荷が増える。
- 影響範囲:
  - `AGENTS.md`, `01_Plans/adr/*`, `02_Architecture/*`, `04_Documentation/*` の参照関係。
- ロールバック手順:
  - 上位統合文書を「索引・依存図」に限定し、仕様本文は既存正本へ戻す。
  - 過剰メタ項目は最小セット（対象読者/非目標/更新トリガー）に縮退する。

## 10) Additional context

- 関連Issue/PR/議論ログ: `DOC-OPS-02`, `DOC-OPS-03`。
- 上流工程ドキュメント評価は、特定手法名を記載せずに「実務上の必要成果物」として統合管理する。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. 文書情報設計（正本/解説分離、上位統合文書の責務）を恒久ルールとして固定する必要がある場合。
  2. 文書品質ゲート（lint/validator）をCI必須化し、プロジェクト標準運用へ格上げする場合。
  3. AGENTS Read Order を段階読書モデルへ変更し、開発フローの標準手順を更新する場合。
  4. `02_Architecture` の分割・再編に伴い、文書ID/参照ポリシーの互換契約を定義する必要がある場合。
  5. Mermaid/Markdown 図表標準を組織ルールとして固定し、例外条件（画像埋め込み許容範囲）を決裁する必要がある場合。

### ADR候補（起票予備リスト）

- ADR候補A: Documentation Information Architecture（前処理済み: Context/Decision/Consequences 記載）。
- ADR候補B: Documentation Readability Baseline（前処理済み: Context/Decision/Consequences 記載）。
- ADR候補C: Documentation Quality Gates（前処理済み: Context/Decision/Consequences 記載）。
- ADR候補D: Documentation Change Governance（前処理済み: Context/Decision/Consequences 記載）。
