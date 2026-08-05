# Issue Draft: REQ-DEF-02 責任分界点と契約チェックポイントの要求定義

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Platform Architecture Owner + Security Officer
- Scope: `01_Plans/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0011`, `02_Architecture/architecture.md`, `02_Architecture/schemas.md`, `02_Architecture/enterprise_architecture.md`
- Dependencies: N/A
- Expected verification level: `docs-check`


## Requirement meta I/F（REQ-DEF共通キー）

> REQ-DEF-01/02/03 で共通利用する要求メタ項目。後続再編集競合を防ぐため、このキーセットを先に固定する。

- `RequirementID`
- `RequirementStatement`
- `PriorityClass`（Must / Should / Could）
- `RACI`（A/R/C/I）
- `ContractImpact`（schema / api / policy / ops : あり / なし）
- `AcceptanceScenario`（前提 / 操作 / 期待結果 / 除外）
- `VerificationLevel`（docs-check / unit / integration / e2e）
- `DecisionStatus`（Fixed / Pending）
- `DecisionQueueRef`（`DecisionStatus=Pending` の場合のみ必須）

### B-3. I/Fキー実装（本Issueの独立実行範囲）

> 独立実行可能理由: B-3のI/Fキーに RACI / Contract impact 判定を埋める専任タスクとして切り出し可能。

| Canonical key | このIssueでの確定値 | 備考 |
|---|---|---|
| `RequirementID` | `REQ-DEF-02` | 固定 |
| `PriorityClass` | `Must` | 監査説明責任の成立条件 |
| `RACI` | **A:** Platform Architecture Owner / **R:** Security Officer / **C:** Product Owner, Implementer / **I:** Reviewer, Operations | 要求定義時点で先に固定 |
| `ContractImpact` | **schema:** なし / **api:** なし / **policy:** あり / **ops:** あり | 契約判定を明示 |
| `VerificationLevel` | `docs-check` | 主検証責務は docs-check 固定 |
| `DecisionStatus` | `Fixed` | B-3は本Issueで確定 |
| `DecisionQueueRef` | N/A | `DecisionStatus=Fixed` のため不要 |

### AC/DoD補完提案（実施前確認）

- 不足候補1: `DecisionStatus=Fixed` なのに `DecisionQueueRef` を記載していたため、REQ-DEF-01の共通I/F条件（Pending時のみ必須）に合わせて補正する。
- 不足候補2: B-3独立実行の完了判定を明確化するため、DoDに「REQ-DEF-01共通I/Fとの整合確認」を追加する。
- 不足候補3: 主検証責務を `docs-check` 固定とし、validator + 文言追跡コマンドを必須ログ化する。
- 補完ドラフトA（AC）: RACI/ContractImpact/Go-No-Go の3項目が、RequirementStatement（R1/R2/R3）として相互参照なしで単独判読できる状態を合格条件とする。
- 補完ドラフトB（DoD）: Proceed宣言は「No-Goゼロ」かつ「docs-check相当コマンド成功ログあり」の同時充足時のみ可能とする。

## 要求定義の固定（RACI / ContractImpact / Go-No-Go）

### R-1: RACI固定（RequirementStatement）

- RequirementID: `REQ-DEF-02-R1`
- RequirementStatement: 要求定義時点で決定責務と承認責務を分離し、各要求に RACI を必須記載する。
- RACI: **A:** Platform Architecture Owner / **R:** Security Officer / **C:** Product Owner, Implementer / **I:** Reviewer, Operations

### R-2: ContractImpact判定固定（RequirementStatement）

- RequirementID: `REQ-DEF-02-R2`
- RequirementStatement: 各要求に対し schema/api/policy/ops の契約影響有無を「あり/なし」で明示する。
- ContractImpact: **schema:** なし / **api:** なし / **policy:** あり / **ops:** あり

### R-3: Go/No-Go判定固定（RequirementStatement）

- RequirementID: `REQ-DEF-02-R3`
- RequirementStatement: 要件未確定のまま実装Issueへ進まない停止条件を必須化する。

#### Go/No-Go matrix（要求定義ゲート）

| 判定項目 | Go条件 | No-Go条件 | エスカレーション先 |
|---|---|---|---|
| RACI | A/R/C/I が全要求に記載済み | 役割未記載または責務重複が未解消 | Platform Architecture Owner |
| ContractImpact | schema/api/policy/ops が「あり/なし」で判定済み | 1項目でも未判定 | Security Officer |
| 安全境界 | SafeMode既定ON・漏えい防止非改変が明記済み | 境界が未記載または緩和案のみ記載 | Product Owner + Security Officer |
| 検証計画 | docs-check コマンドと期待結果が記録済み | コマンドまたは期待結果が欠落 | Implementer |

> 判定ルール: **1つでも No-Go がある場合は Proceed せず停止**し、Decision Queueへ未確定項目を登録してから再判定する。

## 1) 課題 / Problem statement

- 要件定義フェーズで「誰がどこまで決めるか（責務境界）」が明示されないと、実装Issueで設計判断が再燃する。
- Architecture文書とOperations文書で責任分界の言い回しがずれると、受入判定責任が曖昧になる。
- 契約正本（schema/API/policy）と運用手順の境界が曖昧なままだと、後方互換判断が遅れる。

## 2) 背景 / Context

- AGENTS.md は上流整合（00〜02）を実装着手条件としている。
- `schemas.md` は互換性判断の単一正本であり、要件段階で変更有無を宣言する必要がある。
- `enterprise_architecture.md` は組織要件（役割分離/監査）の根拠であり、責任分界点の要求定義に必須。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Human-in-the-loop の成立には責任分界の可視化が前提。
- 安全（THREAT_MODEL / SafeMode）: 責務不明確は例外運用の拡大を招き、安全境界が緩む。
- 企業・行政要件（enterprise_architecture）: 監査説明責任を満たすため、決定権限を明文化する必要がある。
- 後方互換（schemas）: 契約変更の判定ゲートを要求定義で先に固定できる。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs only（責任分界点要求・契約チェックポイント定義）。
- 変更の最小単位:
  - T1: 役割別責務（Product/Architecture/Security/Implementer/Reviewer）を要求文脈で定義。
  - T2: 契約チェックポイント（Schema/API/SafeMode/Export）を要求テンプレに追加。
  - T3: 「要件確定前に実装へ進まない」停止条件を明文化。
- 非目標:
  - 認可ロジックやAPI仕様の変更。
  - CI設定や運用ツールの導入。

## 5) 受入条件 / Acceptance criteria

- [x] 役割ごとの決定責務と承認責務が要求文書で判読可能になる。
- [x] 契約チェックポイント（schema/API/policy/ops）が要求定義テンプレに追加される。
- [x] 各要求に「契約変更あり/なし」の判定欄がある。
- [x] SafeMode・漏えい防止・監査要件の境界が必須項目として保持される。
- [x] docs-check でメタ情報と参照整合を確認できる。

## 5.1 判定基準（責務境界・契約チェックポイント最小セット）

- 判定基準-1（責務境界）: `RACI` の A/R/C/I が全RequirementStatementに記載されている。
- 判定基準-2（契約境界）: `ContractImpact` の `schema/api/policy/ops` が全要求で `あり/なし` 判定済みである。
- 判定基準-3（停止条件）: Go/No-Go matrix のNo-Goが1件でもある場合、実装IssueへProceedしない。
- 判定基準-4（Fail-safe）: 価値定義（ADR-0001）と受入条件の整合が崩れた場合は停止し、Decision Queueへ登録する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 責任分界点のRACI表（要求定義向け）を作成する。
- [x] T2: 契約チェックポイントの定義表を作成する。
- [x] T3: 要件未確定時の停止基準（Go/No-Go）を作成する。
- [ ] T4: 後続Issueテンプレへ責任分界点項目を反映する。

### Plan → Execute → Verify（本実施ログ）

1. **Plan**
   - B-3のI/Fキーに `RACI` と `Contract impact` の確定値を埋める。
   - 許可スコープ外（REQ-DEF-01/03本文、運用文書）へは変更を拡張しない。
2. **Execute**
   - 本Issue内に B-3専用セクションを追加し、RACI/契約判定を表形式で固定。
   - T1〜T3の完了をこのIssue内でチェック済みに更新。
3. **Verify**
   - `validate_active_issue_memos.py` と unit test で体裁・必須項目整合を確認。
   - 文言追跡は `rg` で確認。
4. **Proceed**
   - Go/No-Go matrix を適用し、No-Goゼロ時のみ後続Issueへ進行する。
   - No-Go検出時は Decision Queue に登録して停止する。

### Verify結果（docs-check相当）

- `python 01_Plans/issues/validate_active_issue_memos.py` => `ok: validated 3 active issue memos`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` => `Ran 8 tests ... OK`
- `rg -n "REQ-DEF-02|責任分界|契約チェックポイント|Go/No-Go" 01_Plans/issues/issue-REQ-DEF-02-responsibility-boundary-and-contract-checkpoints.md` => R1/R2/R3 と Go/No-Go matrix の本文存在を確認

### Proceed判定（合格時のみ終了）

- 判定結果: **Proceed（合格）**
- 根拠: Go/No-Go matrix の No-Go 条件に該当なし、かつ docs-check相当の自己検証コマンドが全件成功。

### Execute確定ログ（B-3独立実行）

- RACI を `REQ-DEF-02-R1` へ固定し、A/R/C/I を本文に単一表記で統一。
- ContractImpact を `REQ-DEF-02-R2` へ固定し、`schema/api/policy/ops` の4面を「あり/なし」で確定。
- Go/No-Go を `REQ-DEF-02-R3` へ固定し、No-Go時の停止条件とエスカレーション先を維持。
- Decision Queue は「未確定事項のみ」へ限定し、B-3本体の `DecisionStatus=Fixed` と衝突しない状態へ補正。

### 自己修復ログ（最大3回）

- Attempt 1: validator実行（失敗時は不足項目を修正）。
- Attempt 2: unit test実行（失敗時はフォーマット/期待値差分を修正）。
- Attempt 3: `rg` によるキーワード存在確認（不足時は追記）。
- **Fail-safe停止条件**: 3回の自己修復で整合が回復しない場合は、変更を最小化して停止し未解決点を `Decision Queue` に記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "REQ-DEF-02|責任分界|契約チェックポイント|Go/No-Go" 01_Plans 02_Architecture 04_Documentation`
- 期待結果:
  - issue memo validator が成功し、責任分界点の要求が文書上で追跡できる。
- 未実施時の理由・代替検証:
  - Python未導入時は `rg` による存在確認で代替し、未実施理由を残す。

## 8) 代替案 / Alternatives considered

- 代替案A: 実装担当者の裁量で責任分界を都度決める。
  - 却下理由: 監査説明責任と再現性が確保できない。
- 代替案B: Architecture更新のみを先行し、Issueテンプレ更新を行わない。
  - 却下理由: 実務の起票時に責任分界点が抜け落ちる。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 責任分界点が細かすぎて運用負荷を上げる。
- 影響範囲: 要求定義作業、レビュー会運営、文書同期作業。
- ロールバック手順: 必須項目を最小セット（決定責務/承認責務/契約変更判定）へ縮退する。

## 9.1 非目標（明示）

- RACIを全Issueへ一律強制する運用決定（プロジェクト全体ポリシー化）。
- API/Schema実装の直接変更、およびCIゲート実装。
- REQ-DEF-01 canonical key の再定義。

## 9.2 分割戦略（下流適用）

- 分割方針:
  - `責務境界` と `契約影響` は本Issueで固定し、受入シナリオ詳細は REQ-DEF-03 へ委譲する。
  - 不可分論点（例: Go/No-Goと受入証跡）が発生した場合は、主責務を高リスク側（契約境界）へ固定して分割する。
- 引き渡し成果物（最小セット）:
  - `RACI` テーブル
  - `ContractImpact` 判定
  - Go/No-Go matrix

## 10) Additional context

- 実装前に責任分界点を固定することで、後工程の論点再燃を抑制する。
- ADR化が必要になる条件（トレードオフ閾値）:
  1. RACIを全フェーズ必須ルールとして固定する場合。
  2. 契約チェックポイントをCIゲートへ接続する場合。

## Definition of Done（DoD）

- [x] RACI が RequirementStatement（REQ-DEF-02-R1）として固定されている。
- [x] ContractImpact が RequirementStatement（REQ-DEF-02-R2）として固定されている。
- [x] Go/No-Go 判定が RequirementStatement（REQ-DEF-02-R3）として固定されている。
- [x] Plan → Execute → Verify → Proceed が本文ログとして追跡できる。
- [x] 未確定項目が Decision Queue（Pending-2 / Pending-3）へ接続されている。
- [x] REQ-DEF-01の共通I/F（canonical key / Pending時のみ `DecisionQueueRef` 必須）と不整合がない。


## Decision Queue（R2系 / 決定済み）

- R2-P1 (**Rejected**): `01_Plans/issues/TEMPLATE.md` へのRACI/責任分界点必須化は実施しない（要件削除）。
- R2-P2 (**Approved Conditional**): `Go/No-Go` 判定欄は合理的必要性があるIssueに限定して設置。
- R2-P3 (**Approved Conditional**): SafeMode/漏えい防止レビューゲートはセキュリティ境界影響Issueに限定して必須。

### Decision Record（確定）

- Context: REQ-DEF-02本体はFixedだが、テンプレ反映範囲（RACI/Go-No-Go/安全ゲート）の拘束度合いが未承認だった。
- Decision (Final):
  - R2-P1はReject（RACI・責任分界点要件は削除）。
  - R2-P2はApprove Conditional（必要IssueのみGo/No-Go欄を設置）。
  - R2-P3はApprove Conditional（セキュリティ境界影響Issueのみ安全ゲート必須）。
- Consequences: 低リスクIssueの運用負荷を抑えつつ、高リスクIssueに限定した安全レビュー導線を維持する。
- Approval status: Approved (mixed outcomes)
- Approval log: 2026-03-08 JST / Human decider

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。


## 11) ADR-style decision snapshot

### Context
- 責任分界が要求定義で固定されない場合、実装Issueで決定責務と承認責務が再燃し、監査説明責任が弱まる。
- 契約影響（schema/api/policy/ops）を要求段階で明示しないと、後方互換判断が後工程へ遅延する。

### Decision
- `REQ-DEF-02-R1`〜`R3` を正本として、RACI固定・ContractImpact固定・Go/No-Go停止条件をMust要求として維持する。
- `DecisionStatus=Fixed` の要求には `DecisionQueueRef` を要求せず、未確定項目のみQueue管理する。

### Consequences
- 進行可否の判定が要件段階で可能になり、未確定のまま実装へ進むリスクを低減できる。
- 条件付き承認項目（R2-P2/R2-P3）は運用判断が必要で、継続的なレビュー負荷が残る。


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


## 11) Stream H responsibility-boundary lock（2026-06-13）

- Classification: Open-ready planning rule; current memo remains Done unless contract-boundary drift is detected.
- Responsibility checkpoints: value owner, contract owner, verification owner, and SafeMode/share-export reviewer must be named or explicitly deferred to Maintainer in solo OSS/pre-release.
- Contract checkpoints: schema/api/policy/ops impact must be classified before issue split; if impact crosses layers, split or record an exception.
- Scope lock: planning-only; no `02_Architecture`, `03_Implement`, or `04_Documentation` edits are implied by this memo.
