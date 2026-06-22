# Issue Draft: REQ-DEF-03 受入シナリオ先行型のIssue分割ルール整備

- Type: Process
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Product Owner + QA Owner
- Scope: `01_Plans/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0012`, `ADR-0019`, `04_Documentation/e2e_testing.md`, `01_Plans/issues/README.md`
- Dependencies: N/A
- Expected verification level: `docs-check`


## Requirement meta I/F（REQ-DEF共通キー）

> REQ-DEF-01/02/03 で共通利用する要求メタ項目。後続再編集競合を防ぐため、このキーセットを先に固定する。

- `RequirementID`
- `RequirementStatement`
- `PriorityClass`（Must / Should / Could）
- `RACI`（A/R/C/I）
- `ContractImpact`（schema/api/policy/ops: あり/なし）
- `AcceptanceScenario`（前提/操作/期待結果/除外）
- `VerificationLevel`（docs-check / unit / integration / e2e）
- `DecisionStatus`（Fixed / Pending）
- `DecisionQueueRef`（未確定時の参照先）

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

### 4.0 Plan（AC/DoD補完提案）

- AC補完提案:
  - AC-8: 各要求粒度（R0〜R3）に対して「許容される主検証責務」を1つに固定し、Issue分割基準と紐付ける。
  - AC-9: 複合検証が必要な場合の例外条件（契約境界を跨ぐ不可分変更のみ）と、分割不能理由の記録必須化を定義する。
  - AC-10: T1〜T4ごとに「完了条件」と「本文内の根拠節」を先に固定し、実行前にDone判定基準を凍結する。
- DoD補完提案:
  - DoD-1: `Requirement meta I/F` の `Verification level` が R0〜R3 の定義と矛盾しない。
  - DoD-2: `Validation plan` に主検証責務・未実施時の代替検証・残課題が記載される。
  - DoD-3: 1Issue 1検証責務を満たさない場合、`Decision Queue` に例外理由と解除条件を登録する。
  - DoD-4: T1〜T4の完了条件が事前定義され、実行後は全タスクが本文内証跡付きで完了に更新される。

### 4.0.1 AC/DoD不足の先出し確認（合意凍結）

- 合意事項A: AC-8〜AC-10 を REQ-DEF-03 の不足補完として採用し、Execute開始前に固定する。
- 合意事項B: DoD-1〜DoD-4 を Done判定の必須条件として採用し、後工程で緩和しない。
- 合意事項C: 本Issueは R0（docs-check）責務で完結させ、R1以上は派生Issueへ分割する。

### 4.1 Plan → Execute → Verify（独立実行プロトコル）

- Plan:
  - REQ-DEF-03 では「要求粒度↔検証粒度マッピング」の定義を単独成果物として固定し、他REQ本文改訂を伴わない。
  - 受入シナリオ最小テンプレ（前提/操作/期待結果/除外）に、安全境界・互換境界の確認観点を必須接続する。
- Execute:
  - Issue起票時に `Expected verification level` を宣言し、下表マッピングに従って受入シナリオを記述する。
  - 1 Issue 1 検証責務（主責務）を原則とし、複合責務は例外条件を明示した場合のみ許容する。
- Verify:
  - docs-check系コマンドでメタ項目と記述整合を確認し、宣言レベル未満の検証で完了扱いにしない。
  - 未実施検証がある場合は必ず理由・代替検証・残課題を `Validation plan` に記録する。

### 4.2 要求粒度 ↔ Verification level マッピング

| 要求粒度 | 代表対象 | Expected verification level（最小） | 補足 |
| --- | --- | --- | --- |
| R0: 記述規約/運用手順の明確化 | Issue template、運用文書、参照関係 | `docs-check` | 実装変更なし。リンク、用語、メタI/F整合を確認。 |
| R1: ロジック単位の仕様差分 | 関数/モジュール単位の仕様修正 | `unit` | docs-checkに加え、対象ロジックの単体検証を必須化。 |
| R2: 境界I/Fを跨ぐ仕様差分 | API/DB/worker/外部連携境界 | `integration` | unitに加え、境界契約の接続性を確認。 |
| R3: 利用者フロー到達性の保証 | UI/API連動、権限/公開導線 | `e2e` | integrationに加え、利用者視点の完遂フローを確認。 |

### 4.2.1 1Issue 1検証責務の運用境界

| 条件 | 判定 | 運用ルール |
| --- | --- | --- |
| 受入条件が単一の要求粒度（R0/R1/R2/R3）に収まる | 分割不要 | 主検証責務を1つだけ宣言して起票する。 |
| 受入条件が隣接粒度を跨ぐ（例: R1+R2） | 原則分割 | 上位粒度側を別Issueへ分離し、依存リンクで接続する。 |
| 境界契約が不可分で分割不能（例: API契約変更と最小統合確認が不可分） | 例外許容 | 主検証責務を高い方に固定し、低い方は補助検証として `Validation plan` に明記し、例外理由と解除条件を `Decision Queue` に登録する。 |
| E2E要件（R3）とdocs-only要件（R0）が同時に存在 | 必ず分割 | R0は docs-check Issue、R3は e2e Issue として分離する。 |

- 補助検証は許可されるが、完了判定は主検証責務の達成をもって行う。
- 主検証責務が未達の場合、他レベルが完了していてもDoneに遷移しない。

### 4.3 自己修復（最大3回）とフェイルセーフ停止

- 自己修復ループ（最大3回）:
  1. 検証失敗の原因を分類（記述欠落 / レベル不一致 / 参照不整合）。
  2. 最小修正を適用して再検証。
  3. 再失敗時は差分を縮小し、次ループで再検証。
- フェイルセーフ停止条件:
  - 3回実施しても `Expected verification level` 整合が満たせない場合は、範囲拡大せず停止する。
  - 停止時は未達条件、試行履歴、次アクション候補を `Validation plan` と `Decision Queue` に記録する。

## 5) 受入条件 / Acceptance criteria

- [x] 受入シナリオ記述の最小テンプレ（前提/操作/期待結果/除外）が定義される。
- [x] 要求粒度と `Expected verification level` の対応ルールが定義される。
- [x] 1Issueあたりの検証責務上限（複合しすぎない）が明文化される。
- [x] 安全境界と互換境界の確認項目が受入シナリオに含まれる。
- [x] docs-check コマンドで規約文書の整合を再現確認できる。
- [x] 要求粒度↔検証粒度マッピング（R0〜R3）が定義される。
- [x] Plan→Execute→Verify と自己修復3回/フェイルセーフ停止条件が明文化される。
- [x] 1Issue 1検証責務の運用境界（分割必須/例外許容）が定義される。

## 5.1 Definition of Done（REQ-DEF-03）

- [x] R0〜R3ごとに主検証責務（docs-check/unit/integration/e2e）が一意に定義されている。
- [x] 例外的に複合検証を許容する条件と記録先（`Validation plan` / `Decision Queue`）が定義されている。
- [x] Plan→Execute→Verify の実行手順と、自己修復最大3回・フェイルセーフ停止条件が本文に明記されている。
- [x] 本Issue本文のみの変更で完結し、他Issue・コード・CIを変更していない。

## 5.2 判定基準（acceptance-first 分割判定）

- 判定基準-1（連鎖整合）: `RequirementStatement` → `AcceptanceScenario` → `VerificationLevel` の3点が全要求で連結している。
- 判定基準-2（単一責務）: 主検証責務が1Issueにつき1つに固定され、例外は `Decision Queue` 記録済みである。
- 判定基準-3（曖昧語除去）: 「適宜」「必要に応じて」等の曖昧語を残さず、条件と除外を明記している。
- 判定基準-4（Fail-safe）: 価値定義と受入基準の不整合が残る場合は停止し、3回以内の自己修復後に未達を記録する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 受入シナリオ記述テンプレを作成する。
  - 完了条件: 「前提/操作/期待結果/除外」の最小テンプレが本文で独立参照可能である。
  - 証跡: `Requirement meta I/F` の `Acceptance scenario` 定義、および 4.1 Plan節のテンプレ明記。
- [x] T2: 要求粒度↔検証粒度マトリクスを作成する。
  - 完了条件: R0〜R3すべてが最小検証レベル付きで表形式に定義される。
  - 証跡: 4.2 要求粒度 ↔ Verification level マッピング。
- [x] T3: Issue分割基準（分割/統合の閾値）を定義する。
  - 完了条件: 1Issue 1検証責務の原則、分割必須条件、例外許容条件が表形式で定義される。
  - 証跡: 4.2.1 1Issue 1検証責務の運用境界。
- [x] T4: 既存Draft/Open issueの適用対象を棚卸しする。
  - 完了条件: Active issue群から「REQ-DEF-03規約を先行適用すべき対象」を本文に列挙し、適用理由を記載する。
  - 証跡: 6.1 適用対象棚卸し（Draft/Open）。

### 6.1 適用対象棚卸し（Draft/Open）

| Issue | 現在状態 | 適用優先度 | 適用理由（1Issue 1検証責務観点） |
| --- | --- | --- | --- |
| `issue-REQ-DEF-01-value-realization-requirements-baseline.md` | Open | High | REQ-DEF共通I/Fの定義源であり、R0（docs-check）責務を先に固定する必要がある。 |
| `issue-REQ-DEF-02-responsibility-boundary-and-contract-checkpoints.md` | Done | High | 契約影響（schema/api/policy/ops）を扱うため、R1〜R2境界の分割規約適用を実施済み。 |
| `issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md` | Done | High | 本文自体が規約正本のため、R0責務で完結させる適用サンプルとして機能する。 |
| `issue-DOC-OPS-04-documentation-visibility-readability-governance.md` | Draft | Medium | T1〜T4のdocs中心タスクが多く、複合検証を回避する分割基準の適用余地が大きい。 |

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-03|要求粒度|Verification level|1Issue 1検証責務|自己修復" 01_Plans/issues/issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md`
- 期待結果:
  - issue memo validator が成功し、受入シナリオ規約の記述が追跡可能である。
  - 宣言した `Expected verification level=docs-check` と、本文のR0主責務定義が矛盾しない。
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

## 9.1 非目標（明示）

- Playwright/E2Eシナリオそのものの実装追加。
- CIワークフロー変更や検証自動化ポリシー変更。
- REQ-DEF-01/02 の責務境界・契約判定の再定義。

## 10) Additional context

- 要件定義フェーズの壁打ち成果を、実装前レビュー可能なIssue品質へ引き上げるための基盤。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. 検証粒度マッピングを全プロジェクト標準へ昇格する場合。
  2. 受入シナリオテンプレをCI検証対象にする場合。


## Decision Queue（R3系 / 決定済み）

- R3-P1 (**Approved**): 要求粒度↔検証粒度マッピングを新規Issueで必須化（既存Activeは段階適用）。
- R3-P2 (**Approved Conditional**): 1Issue1検証責務を原則化し、例外は統合境界が2つ以上で分割不能の場合のみ許容。
- R3-P3 (**Approved Conditional**): 受入シナリオ最小テンプレは Process/実装系Issueで必須、Docs-onlyは任意（推奨）。

### R3-P1〜P3 補足説明と推奨

- R3-P1 推奨: **Approve（新規Issue必須）**
  - 背景: 要求粒度↔検証粒度が未固定だと完了判定が揺れる。
  - 効果: docs-check/unit/integration/e2e の過不足を抑制できる。
- R3-P2 推奨: **Approve（条件付き）**
  - 背景: 複合検証Issueは失敗時の切り分けが難しい。
  - 条件: 「統合境界が2つ以上で分割不能」の場合のみ例外許容し、理由を `Validation plan` と `Decision Queue` に記録。
- R3-P3 推奨: **Approve（条件付き）**
  - 背景: 受入シナリオの前提/操作/期待結果/除外の欠落を防ぐため。
  - 条件: Process/実装系は必須、Docs-onlyは任意（推奨）とする。

### Decision Record（確定）

- Context: REQ-DEF-03本体の検証規約はFixedであり、テンプレ必須化範囲と例外閾値の最終承認を実施した。
- Decision (Final): R3-P1をApprove、R3-P2/R3-P3をConditional Approveとして採択。
- Consequences: 分割粒度と検証責務の再現性が向上し、テンプレ/READMEへ制度化反映が可能。
- Approval status: Approved (mixed outcomes: Approve/Conditional Approve)

- Approval log: 2026-03-08 JST / Human decider / R3-P1 Approve, R3-P2 Conditional Approve, R3-P3 Conditional Approve

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## 11) ADR-style decision snapshot

### Context
- REQ-DEF-03 は「受入シナリオ先行」と「1Issue 1検証責務」の運用境界を定義する要求文書であり、実装詳細へ踏み込まない独立要件として維持する必要がある。
- 既存の `Expected verification level` 宣言のみでは、要求粒度（R0〜R3）との対応がレビュー時に揺れうる。

### Decision
- 要求粒度R0〜R3と主検証責務（docs-check/unit/integration/e2e）を一意対応で固定する。
- 複合検証は「境界契約が不可分で分割不能」の場合に限定し、`Validation plan` と `Decision Queue` に例外理由・解除条件を記録する。

### Consequences
- 要件の検証可能性が向上し、Done判定が主検証責務で再現可能になる。
- 例外運用は許容するが、記録コストが増えるため適用条件の継続監視が必要となる。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。


## 11) Stream H acceptance-splitting lock（2026-06-13）

- Classification: Open-ready planning rule; current memo remains Done and acts as the split-rule reference.
- Split order: RequirementStatement → AcceptanceScenario（前提/操作/期待結果/除外）→ VerificationLevel → Issue split.
- Mock-first rule: if a dependency can be severed with an A1 contract and A2 mock validation, A3 must remain an implementation plan until mock evidence is available.
- Stop condition: if an issue needs both real users and implementation changes, keep it Hold/Deferred and split planning from activation.
