# Issue Draft: REQ-DEF-03 受入シナリオ先行型のIssue分割ルール整備

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Product Owner + QA Owner
- Scope: `01_Plans/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0012`, `ADR-0019`, `04_Documentation/e2e_testing.md`, `01_Plans/issues/README.md`
- Expected verification level: `docs-check`


## Requirement meta I/F（REQ-DEF共通キー）

> REQ-DEF-01/02/03 で共通利用する要求メタ項目。後続再編集競合を防ぐため、このキーセットを先に固定する。

- Requirement ID
- Requirement statement
- Priority class（Must / Should / Could）
- RACI（A/R/C/I）
- Contract impact（schema/api/policy/ops: あり/なし）
- Acceptance scenario（前提/操作/期待結果/除外）
- Verification level（docs-check / unit / integration / e2e）
- Decision status（Fixed / Pending）
- Decision queue ref（未確定時の参照先）

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
| 境界契約が不可分で分割不能（例: API契約変更と最小統合確認が不可分） | 例外許容 | 主検証責務を高い方に固定し、低い方は補助検証として `Validation plan` に明記する。 |
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
| `issue-REQ-DEF-01-requirement-metadata-schema.md` | Open | High | REQ-DEF共通I/Fの定義源であり、R0（docs-check）責務を先に固定する必要がある。 |
| `issue-REQ-DEF-02-requirement-traceability-and-contract-impact.md` | Open | High | 契約影響（schema/api/policy/ops）を扱うため、R1〜R2境界の分割規約適用が必須。 |
| `issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md` | Open | High | 本文自体が規約正本のため、R0責務で完結させる適用サンプルとして機能する。 |
| `issue-DOC-OPS-04-documentation-visibility-readability-governance.md` | Draft | Medium | T1〜T4のdocs中心タスクが多く、複合検証を回避する分割基準の適用余地が大きい。 |

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-03|要求粒度|Verification level|1Issue 1検証責務|自己修復" 01_Plans/issues/issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md`
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


## Decision Queue（残る未確定）

- Pending-1: 要求粒度↔検証粒度マッピングを全Issue必須にする適用開始時期。
- Pending-2: 1Issue1検証責務ルールの例外許容条件（統合検証を許す閾値）。
- Pending-3: 受入シナリオ最小テンプレを `01_Plans/issues/TEMPLATE.md` へ必須昇格する範囲。
