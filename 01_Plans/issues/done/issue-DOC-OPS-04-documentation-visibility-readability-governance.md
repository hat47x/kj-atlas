# Issue Draft: DOC-OPS-04 設計文書の俯瞰統合アーキテクチャと可読性改善プログラム（ADR候補化前処理監査）

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: DOC-OPS-04 監査専任エージェント
- Scope: `01_Plans/issues/` / `01_Plans/adr/` / `01_Plans/project-progress-dashboard.md`（計画レイヤ同期のみ）
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0002`, `ADR-0018`, `ADR-0019`, `ADR-0022`
- Dependencies: N/A
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

#### 3.2.3 ADR起票前の決裁情報（暫定固定: Phase 2）

> 注記: 本節は **ADR起票前の審査入力** を記録する。恒久ルールの断定はADR本文でのみ行う。

1) **ADR起票順序（暫定）**
- Context: A（情報設計I/F）が未確定だと、B/C/Dの用語・判定メタ参照先が分岐しやすい。
- Decision: 起票順序は **A → (B/C/D)** とし、B/C/DはAのI/F語彙を前提に審査する（暫定）。
- Consequences: 先行I/Fにより後続ADRの差分比較が容易化する一方、Aの承認遅延が全体着手順序のクリティカルパスになる。

> 状態同期注記（Phase 2）:
> - **A承認済み**: `ADR-0022-doc-ops-04-documentation-information-interface.md=Accepted`。旧 `ADR-0022-documentation-*` 3件は `Superseded`。B/C/Dは編集境界と同時更新禁止を維持して実編集可能。
> - **B/C/D開始条件**: A（情報I/F ADR）=`Accepted`、編集境界ルールが有効、かつ統合ファイル同時更新禁止が維持されていること。

2) **レビュー責任体制（暫定）**
- Context: DOC-OPS系は `01_Plans` / `02_Architecture` / `04_Documentation` の横断影響があり、単独レビューでは見落としが出る。
- Decision: 一次レビューを Plan Owner、二次レビューを Architecture Owner、最終承認を Platform Architecture Owner とする三層レビュー案を審査入力として記録する（暫定）。
- Consequences: 監査可能性は上がるが、レビュー待機時間が増えるため、各ADRで承認SLAの要否判断が必要になる。

3) **docs-check/CI必須化境界（暫定）**
- Context: 文書更新の全件で同一ゲートを課すと、軽微修正の待機コストが増える可能性がある。
- Decision: `01_Plans` の Decision文書（ADR/issue meta）と `project-progress-dashboard.md` 更新は docs-check必須、CI拡張（link/metadata strict）はCで判断する前提を記録する（暫定）。
- Consequences: 最低限の回帰防止を維持しつつ、CI強制境界はCへ分離できる。

4) **例外承認条件（暫定）**
- Context: docs-check失敗時に即時停止しかないと、復旧作業の優先順序が曖昧になる。
- Decision: 例外は「緊急復旧」「依存ツール障害」「上位判断待ち」の3類型のみ候補とし、適用時は理由・期限・フォローアップIssueを必須記録する案を審査入力として保持する（暫定）。
- Consequences: 例外乱発を抑制できる一方、期限管理が未実装だと形骸化するためDで統治責務を確定する必要がある。




#### 3.2.4 次段並列化準備（Phase 4 出力）

- 編集許可スコープ（ファイル単位）:
  - ADR-B: `01_Plans/adr/ADR-0023-doc-ops-04-readability-baseline.md`（新規のみ）
  - ADR-C: `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`（新規のみ）
  - ADR-D: `01_Plans/adr/ADR-0025-doc-ops-04-change-governance.md`（新規のみ）
  - 統合フェーズ専用: `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` / `01_Plans/issues/done/issue-DOC-OPS-04-documentation-visibility-readability-governance.md`
- 競合禁止ルール:
  1. B/C/D実行中は `README.md` と dashboard を更新しない（統合フェーズ1本化）。
  2. B/C/Dは相互ADR本文を直接編集しない（参照はTraceabilityリンクのみ）。
  3. Aの用語I/F変更が発生した場合は、B/C/Dを停止しA再承認を先行する。
- Proceed条件:
  - A（情報I/F ADR）=`Accepted` を維持する。AのI/F語彙に変更兆候が出た場合は B/C/D を停止し、A再承認後に再開する。


### 3.2.5 状態同期確認（Phase 2 / 統合前）

- 同期対象: Active issue / `project-progress-dashboard.md` / `decision-pack-2026-03-human-judgement.md`
- 同期結果（2026-03-09 JST）:
  1. `A承認済み`（`ADR-0022-doc-ops-04-documentation-information-interface.md=Accepted`）を3文書で一致させた。
  2. B/C/D開始条件（A（情報I/F ADR）=`Accepted`、編集境界、統合ファイル同時更新禁止）を3文書で一致させた。
  3. 不一致検出時は self-correction を最大3回まで許容し、未解消時は停止する運用を確認した。

### 3.2.6 ADR承認運用の最終ゲート（Phase 3: 実装前合意）

- 共通テンプレート（並列プロンプト引き渡し用・改変禁止領域を含む）:

```md
[DOC-OPS-04 ADR Parallel Handover Template / Locked]
- Target ADR: <ADR-0023|ADR-0024|ADR-0025>
- Scope Lock: このテンプレートは `Context / Decision / Consequences / Verify` の見出し名を変更しない。
- Non-editable region:
  1) A（ADR-0022-doc-ops-04-documentation-information-interface.md）I/F語彙定義
  2) 統合ファイル同時更新禁止ルール
  3) 停止/再開条件（A再承認必須）

## Context
- A I/Fとの差分理由（逸脱有無）
- 影響範囲（01/02/04）

## Decision
- 採用案（1つ）
- 非採用案（理由付き）

## Consequences
- 採用時の効果
- 非採用時のリスク

## Verify
- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- docs-check相当（見出し/メタ/参照整合）
```

- 運用指示: B/C/DのADR実編集前に、各ADRで `Context / Decision / Consequences` の3要素を承認プロトコルとして明文化する。
- 固定ルール: 上記テンプレートの Non-editable region は統合フェーズまで改変しない。



### 3.2.7 統合フェーズ実行ログ（Phase 3）

- 対象共有リソース: `issues/README.md` / `project-progress-dashboard.md` / `issue-DOC-OPS-04...md`
- 実施内容:
  1. Active/Done と Gate状態の同期を3文書で再確認した。
  2. B/C/D承認統合入力（Context / Decision / Consequences）を「統合済み・起票待ち」状態へ更新した。
  3. 停止/再開条件と次アクション（ADR-0023/0024/0025直列起票）を明記した。
- 判定: A=`Accepted` 維持、競合シグナルなし、統合ファイル同時更新禁止は統合フェーズ内でのみ解除して適用。

### 3.2.8 直列実行エージェント監査ログ（2026-03-09）

- Plan:
  1. Phase 1で A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）の `Accepted` 維持とI/F固定語彙を再監査する。
  2. Phase 2で B/C/D 実行境界（個別ADRのみ編集、統合ファイル更新禁止）を再固定する。
  3. Phase 3で統合ファイル3点の状態同期を最小差分で確認する。
- Execute:
  - 監査対象を `ADR-0022-doc-ops-04-documentation-information-interface.md` / `project-progress-dashboard.md` / `issues/README.md` / 本Issueに限定し、B/C/D個別ADR本文は未着手のままとした。
  - B/C/D 実行順序を `ADR-0023 → ADR-0024 → ADR-0025` の直列キューとして再配布し、統合ファイル更新は統合フェーズ専用コミットへ切り出す運用を確認した。
  - AC/DoD不足の有無を再点検し、追加ドラフトは不要（既存AC/DoDでゲート判定可能）と記録した。
- Verify:
  - Phase 1ゲート判定チェック:
    - [x] A=`Accepted`（`ADR-0022-doc-ops-04-documentation-information-interface.md`）
    - [x] 固定I/F（用語/見出し/判定メタ）を契約として再確認
    - [x] 停止/再開条件を統合ファイル3点で一致確認
  - Phase 2境界チェック:
    - [x] B/C/D作業中に統合ファイル3点を更新しない制約を明示
    - [x] 統合更新が必要な場合は停止→統合フェーズ専用コミットへ切出す手順を明示
  - 判定: 不一致なし。Self-Correctionは0回。
- Proceed:
  - 直列実行境界を維持したまま、次作業は `ADR-0023` 起票・審査へ進む。
  - フェイルセーフ条件（A I/F変更兆候・統合ファイル同時更新必要・想定外競合）を継続監視する。

### 3.3 Verify

- 検証1: docs-check相当として、必須メタ項目と見出し整合をコマンドで確認する。
- 検証2: Decision記述に「確定」「必須化」「標準化」など恒久固定を宣言する文言がないことを確認する。
- 判定: 本Issueは暫定論点整理のみを実施し、恒久ルールを固定していない。

### 3.4 Proceed

- 現在状態: ADR候補A〜Dの前処理監査ログに加えて、統合フェーズでの状態同期を完了。
- 停止条件（維持）: A I/F語彙変更兆候、統合ファイル同時更新の必要発生、想定外競合。
- 次アクション:
  1. `ADR-0023`（B）を起票し、Context / Decision / Consequences を承認審査へ投入。
  2. `ADR-0024`（C）を起票し、docs-check/CI境界を承認審査へ投入。
  3. `ADR-0025`（D）を起票し、変更統治・例外承認を承認審査へ投入。

## 4) 受入条件 / Acceptance criteria（前処理監査限定）

- [x] AC-1: AC/DoD不足点を抽出し、補完ドラフトと合意ログを記録した。
- [x] AC-2: ADR候補A〜Dそれぞれに `Context / Decision / Consequences` を整理した。
- [x] AC-3: 承認後適用範囲と暫定メモ範囲を分離して記述した。
- [x] AC-4: Issue本文で恒久ルールを固定していないことを検証項目として明示した。
- [x] AC-5: ADR起票可否の判断材料（未解決論点・承認依頼事項）を残して停止条件を明記した。
- [x] AC-6: ADR起票前の4論点（順序/責任体制/CI境界/例外条件）を暫定記録として固定した。
- [x] AC-7: B/C/D並列化に向けた編集境界と競合禁止ルールを記録した。

## 5) Definition of Done（DoD: 前処理監査）

- [x] DoD-1: Plan / Execute / Verify / Proceed の4段ログが揃っている。
- [x] DoD-2: docs-check相当の検証コマンドを実行可能な形で記載している。
- [x] DoD-3: 恒久ルールをIssue本文で固定していないことを明示検証している。
- [x] DoD-4: 承認待ち停止時の未解決論点と承認依頼事項を記録している。
- [x] DoD-5: Self-Correction上限（3回）と未解消時の停止方針を記載している。
- [x] DoD-6: ADR-A承認チェックポイント（A逸脱時は次Phase停止）を明示している。

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
  1. ADR-A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）のAccepted維持と、I/F変更時の再承認要否。
  2. B/C/D並列着手後の承認SLA監視と統合タイミング。
  3. docs-check必須化境界と例外承認条件の恒久化（ADR-C/D審査対象）。
- フェイルセーフ記録: 競合兆候・上位方針矛盾・恒久化境界の曖昧さが検出された場合は、推測実装せず停止する。


## 9) DOC-OPS-04直列実行 完了ログ（2026-03-09）

### Phase 0: 前提確認

- ADR-A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）が `Accepted` 維持であることを確認。
- B/C/D作業中の統合ファイル3点同時更新禁止を再確認。
- 停止条件（A語彙I/F変更兆候、統合ファイル同時更新必要化）を明示。

### Phase 1〜3: ADR-0023/0024/0025 直列処理

- 実行順序を `0023 → 0024 → 0025` で固定し、各ADRで Plan → Execute → Verify → Proceed を完了。
- AC/DoD不足は各ADR内で補完提案を明記し、既存合意ログと整合確認。
- Self-Correction は各Phaseとも 0回（上限超過なし）。

### Phase 4: 統合同期

- 統合ファイル3点（`issues/README.md` / `project-progress-dashboard.md` / 本Issue）の状態を Done/Accepted に同期。
- validator と unittest を実行し、整合性を確認。

### 完遂判定

- DOC-OPS-04 は完了（Done）。
- 未解決ADR（0023/0024/0025）は解消（Accepted）。
- 競合・停止条件該当なし。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `visibility/readability governance`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-04` の公開境界を再確認。
- Decision: 04文書冒頭に公開区分を追加し、公開入口には内部Issue/ADR詳細を混ぜない読みやすさ境界を確認した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
