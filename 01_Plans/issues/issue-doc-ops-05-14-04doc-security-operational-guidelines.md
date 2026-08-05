# Issue Draft: DOC-OPS-05-14 04_Documentation/security_operational_guidelines.md の配置見直し

- Type: Documentation quality
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/security_operational_guidelines.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/security_operational_guidelines.md`, `04_Documentation/security.md`, `04_Documentation/operations.md`, `01_Plans/documentation_quality.md`
- Dependencies: `DOC-OPS-05`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-14`
- RequirementStatement: `04_Documentation/security_operational_guidelines.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

## Stream D drift-check update（2026-04-30）

- Phase 1 Read: `02_Architecture/design/strict_mode_exception_approval_flow.html` を起点に `operations.md -> security.md -> security_operational_guidelines.md -> e2e_testing.md` の導線を再確認。
- Phase 2 情報構造: 本文責務を維持（operations=runbook / security=基底方針 / guidelines=運用判断補助）。
- Phase 3 用語統一: `Security Officer / System Owner / Platform Operator`、状態語彙、D1〜D4固定値の一致を確認。
- Phase 4 品質ゲート: docs-check と `git diff --check` 前提、自己修復上限3回を維持。
- Phase 5 完了判定: 本更新は docs-only・allowlist 内で完結し、未承認事項の確定化は行わない。

## Serial cycle record（security operational guidelines lane）

### Read
- `04_Documentation/security_operational_guidelines.md` と、上流の security / operations との責務境界を確認。
- 本Issueは security系公開境界専用レーンの終点として扱う。

### Plan（不足AC/DoD補完提案）
- AC補完提案:
  - AC-1: 運用判断フローにおける公開情報と内部情報の分離基準を明記。
  - AC-2: 役割語彙（Security Officer / System Owner / Platform Operator）と責務分離（2者承認・実行分離）を一致。
  - AC-3: D1〜D4相当は上流仕様への導線を明示し、ガイド内で固定値を改変しない。
- DoD補完提案:
  - DoD-1: docs-only・対象3Issueのみ編集。
  - DoD-2: Verifyは最大3回まで自己修復、Proceed判定を明示。

### Execute
- 分類を **Improve external** で固定。
- guidelines は運用判断補助に限定し、制度定義の正本化は行わない（上流参照を維持）。

### Verify（max 3 retries）
- Verify-1: docs-check整合（Expected/VerificationLevel 一致）。
- Verify-2: GoNoGoGate=Required 条件（Audience/Goal/公開境界/次アクション）を満たす。
- Verify-3: 停止条件（安全境界後退・未承認確定化・対象外編集・4回目修復）非該当。
- Self-repair count: 0/3。

### Proceed
- 判定: **Ready**。
- security系公開境界レーン（operations → security → guidelines）の直列サイクル完了。

## ADR handling rule（このIssueに適用）
- 役割・導線・固定値（D1〜D4相当）で整合差分が出た場合のみ C/D/C を明文化し、承認を要求する。
- 差分がない場合は既存の承認済み方針を維持する。

## Stop conditions
1. 安全境界後退
2. 未承認確定化
3. 対象外編集
4. 4回目修復（>3 retries）

## 12) Stream F serial execution log（2026-04-26）

### Phase 1 Read
- 本Issue本文（Requirement meta I/F / Serial cycle record / Stop conditions）を再読し、対象が `DOC-OPS-05-14` 単票であることを確認。
- security lane の終点Issueとして、`operations → security → guidelines` の順序定義を再確認。

### Phase 2 Plan
- 実行範囲を **issue-doc-ops-05-14 のみ** に固定し、他Issueへの依存追加を禁止。
- 検証は `docs-check` のみ（差分整合と公開境界記録）を実施対象として明文化。

### Phase 3 Execute（ADRタスク必須 C/D/C + 承認記録）
- Context: guidelines は運用判断補助文書であり、公開可能情報と内部統制情報の境界が最重要。
- Decision: `DOC-OPS-05-14` は **Improve external** を維持し、固定値（D1〜D4相当）は上流参照のみで扱う。
- Consequences: 文書再配置の実行時に責務分離（2者承認・実行分離）を崩さず、公開境界を追跡可能にできる。
- Approval record: **Issueメモ内承認（Stream F運用合意）** として本C/D/Cを記録。未承認決定の確定化は行わない。

### Phase 4 Verify
- `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を確認。
- 自己修復回数を `0/3` で開始し、失敗時のみ最大3回まで。4回目相当は Stop conditions に従い停止。

### Phase 5 Proceed
- 判定: **Ready**。
- security系 lane（operations → security → guidelines）の Stream F 担当分を完了として記録。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: 上流Read Orderと本Issueを再読し、security系終点レーン責務を再確認。

### Phase 2 ADR/CDC
- Context: guidelines は運用判断補助として公開境界と責務分離の維持が要点。
- Decision: **Improve external** を維持し、D1〜D4相当は上流参照のみ。
- Consequences: 2者承認・実行分離を崩さず公開境界を追跡できる。

### Phase 3 Plan
- 実行計画: 本Issueメモのみ更新。
- 停止条件: self-correction 4回目相当 / 未定義競合 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Stream H 専属6Phaseログ追記（docs-only）。
- 非実施: 実装コード、architecture本体、shared resource、指定外Issue。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（security lane完了）。


## Stream G 共通ACテンプレ（合意・DOC-OPS-05）

- AC-1 Scope固定: docs-only（`03_Implement/**` 非編集）かつ allowlist 内の対象のみ更新する。
- AC-2 分類固定: 各対象で `Move internal` または `Improve external` を明記し、公開境界を維持する。
- AC-3 境界明示: Audience / Goal / Non-goal / Public boundary / Related を追跡可能にする。
- AC-4 ゲート整合: `GoNoGoGate=Required` を維持し、Go/No-Go 判定条件を本文で再現可能にする。
- AC-5 検証整合: `VerificationLevel=docs-check` と実行検証（`rg` / `git diff --check`）を一致させる。
- DoD-1 直列処理: mini-Phase 1..5（Read→Plan→Execute→Verify→Proceed）を記録する。
- DoD-2 失敗停止: 自己修復は最大3回。4回目相当、競合、allowlist外編集要求で `Hold` 停止。


## Stream G mini-Phase run（2026-04-27 / strict serial 1..5）

### Phase 1 Read
- 本Issueの `Requirement meta I/F` と対象Docの現行分類を再確認。
- 前提: docs-only / 指定allowlist / `VerificationLevel=docs-check` を固定。

### Phase 2 Plan
- 単一責務を「対象Docの公開境界維持と分類固定」に限定。
- 共通ACテンプレを本Issueに適用し、停止条件（3回上限・競合停止）を有効化。

### Phase 3 Execute
- 本Issueの `Status` を Ready 化し、共通ACテンプレと5Phase記録を追記。
- 指定外（`operations.md` / `security.md` / `e2e_testing.md` / `03_Implement/**`）は未編集。

### Phase 4 Verify
- docs-check: 対象Issueと対象Docで ACメタ（Audience/Goal/Public boundary/GoNoGo）を確認。
- `git diff --check` で体裁不整合がないことを確認。
- self-repair count: 0/3（この記録時点）。

### Phase 5 Proceed
- 判定: **Ready**。
- 次アクション: 同一方式で次の対象Issueへ直列進行。

## Stream I security-lane strict serial run（2026-04-27）

### Phase 1 Read（最新状態同期）
- Read同期: security（05-13）の Stream I Proceed=Go を確認後、本Issue本文と `04_Documentation/security_operational_guidelines.md` を再読。
- 確認結果: `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` を維持。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: guidelines は運用判断補助であり、公開境界と2者承認・実行分離の語彙整合が停止条件に直結する。
- Decision: `Improve external` を維持し、制度定義の新規確定は行わず上流導線を保持。
- Consequences: 役割語彙不整合・未承認確定化・公開境界後退の発生確率を抑制する。

### Phase 3 Plan（AC/DoD不足ドラフトと合意）
- AC不足補完（合意）:
  - AC-4: 公開可能情報と内部統制情報の境界を曖昧化しない。
  - AC-5: 停止条件（語彙不整合 / 公開境界後退 / 未承認確定化 / 4回目修復）をProceed直前に再点検する。
- DoD不足補完（合意）:
  - DoD-3: Verifyで `docs-check + git diff --check` を必須実行。
  - DoD-4: security lane 完了判定（Go/Hold/Needs-decision）を明記。

### Phase 4 Execute（docs-only）
- 実施: 本Issueに Stream I 記録を追記（docs-only）。
- 非実施: 指定外ファイル、実装コード、architecture本文、未承認事項の確定化。

### Phase 5 Verify（docs-check + 自己修復<=3）
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
  - `git diff --check`
- self-repair: 0/3（4回目修復は停止条件により禁止）。

### Phase 6 Proceed（Go/Hold/Needs-decision）
- 判定: **Go**（理由: 停止条件非該当、security lane 直列完遂）。
- 終了: 固定直列 `operations → security → guidelines` を完了。

## Stream H execution compliance log（2026-04-27, Set A-3: security operational guidelines）

### 1) Read
- Read同期: 本Issueと 05-13 Proceed=Go を確認し、セットA終点として境界責務を再確認。

### 2) ADR/CDC
- Context: guidelines は運用判断補助文書で、制度定義の正本ではない。
- Decision: 分類 `Improve external` を維持し、D1〜D4相当は上流参照のみ。
- Consequences: 2者承認/実行分離と公開境界追跡の整合を維持する。

### 3) Plan
- `Plan -> Execute -> Verify -> Proceed` を固定。
- AC/DoD不足は既存補完（AC-1〜3, DoD-1〜2）を適用。

### 4) Execute
- 本Issueメモ追記のみ実施（docs-only, allowlist内）。

### 5) Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- `git diff --check`
- self-correction: 0/3（4回目相当は停止）。

### 6) Proceed
- 判定: **Go**（セットA完了、セットBへ進行）。

## Stream J DOC-OPS-05 dedicated run (2026-04-27, Set2)

### Phase 1 Read
- Read Order 再確認後に本Issueを再読し、Scope/VerificationLevel/DecisionStatus を確認。
- SecurityGateImpact は `public-exposure` として維持。

### Phase 2 Plan
- 実行順序を `Read -> Plan -> Execute -> Verify -> Proceed` に固定。
- 変更対象を本Issueメモ単体に限定し、allowlist外編集を禁止。

### Phase 3 Execute
- Classification を **Improve external** で再確認し、公開境界の扱いを固定。
- public-exposure 観点として「公開可能情報のみ記載・内部情報を混在させない」を明記。

### Phase 4 Verify
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
  - `git diff --check`
- self-correction: 0/3（失敗時のみ最大3回、4回目相当は即停止）。

### Phase 5 Proceed
- 判定: **Go**（停止条件: セキュリティ導線矛盾 / 指定外編集 / self-correction上限超過 に非該当）。


## Stream G dedicated lane run（2026-04-28 / DOC-OPS-05 Security-docs専任）

## Stream E serial run（2026-04-29 / Doc-Ops Draft lane）

### Phase 1 Plan
- AC/DoD不足を補完して固定。
  - AC: 用語・責務・導線・固定値（D1〜D4）の同時整合。
  - DoD: docs-only、`docs-check`、Proceed判定記録。
- 設計起因の不整合は文書で解消せず停止報告する方針を再確認。

### Phase 2 Read同期
- 対象文書と関連正本（`02_Architecture/design/strict_mode_exception_approval_flow.html` / `security.md` / `operations.md` / `e2e_testing.md`）を再読。
- `Improve external` 分類と public-exposure 境界を維持。

### Phase 3 Execute
- `security_operational_guidelines.md` に Stream E の5Phaseログを追記（docs-only）。
- 実装・ADR本文・指定外ファイルは未編集。

### Phase 4 Verify
- `rg -n "Stream E serial update log|D1|D2|D3|D4|Security Officer|System Owner|Platform Operator" 04_Documentation/security_operational_guidelines.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- `git diff --check`
- self-repair: 0/3

### Phase 5 Proceed
- 判定: **Go**（停止条件非該当）。
- Issue status: **Done 維持**（Draft lane の追記同期を完了）。

### Phase 1 Read（開始同期）
- Read同期を実施し、Read Orderと本Issue本文、security lane固定順（operations → security → guidelines）を再確認。
- docs-only / allowlist内編集 / `VerificationLevel=docs-check` を再確認。

### Phase 2 ADR/CDC（C/D/C + 承認）
- Context: guidelines は公開運用判断の補助文書であり、公開境界・役割語彙固定・固定値参照専用が要件。
- Decision: 分類 **Improve external** を維持し、`Security Officer / System Owner / Platform Operator` の語彙固定、D1〜D4は参照専用を維持。
- Consequences: 公開境界の後退と語彙ドリフトを防ぎ、未承認事項の確定化を回避できる。
- Approval: **Issueメモ内運用承認（DOC-OPS-05 Stream G）** を記録。

### Phase 3 Plan（AC/DoD不足ドラフト提案）
- AC Draft:
  - AC-G-14-1: 公開可能情報と内部統制情報の境界を曖昧化しない。
  - AC-G-14-2: 役割語彙3点セットの一致を維持する。
- DoD Draft:
  - DoD-G-14-1: 6フェーズ直列記録。
  - DoD-G-14-2: self-correction 最大3回、超過時 `Hold`。

### Phase 4 Execute
- 実施: 本Issueメモ更新のみ（docs-only）。
- 非実施: 実装変更、上流固定値変更、未承認確定化。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Go**
- 理由: security/docs専任レーン条件を満たし、停止条件非該当。


## Stream G dedicated serial completion (2026-04-28)

### Phase 1 Read
- AC/Validationの再収集を実施し、`Requirement meta I/F`・`Acceptance criteria`・`Validation plan` の3点が本文に存在することを確認。
- フェイルセーフ確認: AC不在/検証不能/allowlist外編集要求は該当なし。

### Phase 2 Plan
- 難易度低→高の固定順を `01 → 03 → 08 → 10 → 04 → 09 → 12 → 14` としてロック。
- 本Issueの実行順は **8/8** とし、分類 `Improve external` を維持。

### Phase 3 Execute
- 変更を本Issueメモの最小差分に限定（docs-only / issue memo only）。
- 状態を `Done` に更新し、直列実行ログを追記。

### Phase 4 Verify
- docs-check基準で `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を再確認。
- 差分体裁は `git diff --check` で検証対象に含める。

### Phase 5 Proceed
- 判定: **Done**。
- クローズ条件: GoNoGoGate=Required の判定項目（Audience/Goal/Public boundary/Next action）を維持しつつ、直列5Phase完了を記録。


## Stream H DOC-OPS-05 serial update（2026-04-30）

### Phase 1 Read同期
- Read Order（00→02）と本Issue、対象Docを再読し、docs-only制約を確認。

### Phase 2 章ごとのAC定義
- AC固定: Audience / Goal / Non-goal / Public boundary / Related / GoNoGoGate / VerificationLevel(docs-check)。

### Phase 3 章単位更新（直列）
- 本Issueに対応する章のみを更新対象として直列処理し、未承認事項の確定化は行わない。

### Phase 4 docs-check / link-check
- `git diff --check` と `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md` を実行対象とする。
- 自己修復回数: 0/3（4回目相当はHold停止）。

### Phase 5 issue更新
- 判定: **Ready**（停止条件非該当、docs-only維持）。

## Stream I dedicated run（2026-05-02 / DOC-OPS-04-05 security lane）

### Phase 1: Read
- `AGENTS.md` の Read Order と本Issueを再確認し、対象を docs-only（issue + 04_Documentation）に限定。
- `04_Documentation/security_operational_guidelines.md` の役割語彙（Security Officer / System Owner / Platform Operator）と導線を再確認。

### Phase 2: ADR/仕様明文化（Context / Decision / Consequences）
- Context: security lane の最終文書として、公開境界と責務分離の説明が drift しやすい。
- Decision: 既存分類 `Improve external` を維持し、制度値の再定義は行わず参照導線を優先する。
- Consequences: 未承認事項の確定化を防ぎつつ、運用判断補助としての責務を維持できる。

### Phase 3: Plan
- 変更単位: 本Issueに 6Phase 実行記録を追記する最小差分。
- 整合ルール: 用語統一（3役割）・GoNoGoGate=Required・VerificationLevel=docs-check の一致を維持。

### Phase 4: Execute
- 実施: 本セクション追記のみ（docs-only）。
- 非実施: backend/frontend 実装、architecture本文、指定外issue。

### Phase 5: Verify（max 3 repairs）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase 6: Proceed
- 判定: **Go**（停止条件非該当、docs-only 完結）。
- 次アクション: security lane の drift-check を次サイクルで再確認。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-14-04doc-security-operational-guidelines.md` | `04_Documentation/security_operational_guidelines.md` | 既存本文の Decision / Proposed classification を継承 |

### Phase 2: Plan（AC / DoD 統一テンプレ）
- AC（統一）
  - 読者タスク完遂性: Audience / Goal / Non-goal が追跡可能。
  - 用語統一: 役割語彙と判定語彙（Move internal / Improve external / GoNoGo）を統一。
  - 参照導線: Related ADR/Spec と対象04文書の相互参照を明記。
- DoD（統一）
  - 相互参照が明記される。
  - 品質ゲート（`docs-check` + `git diff --check`）が明記される。
  - 更新責務（Issue整備担当 / 04_Documentation改稿担当の分離）が明記される。

### Phase 3: Execute（標準セクション）
- 目的: DOC-OPS-05対象Issueを、公開境界を崩さず運用できる品質に正規化する。
- 範囲: 本Issue本文（`01_Plans/issues`）のみ。
- 非対象: `04_Documentation/**` 本文改稿、`03_Implement/**`、shared統合3ファイル。
- 検証観点: メタ項目充足 / 優先度矛盾なし / リンク表記整合 / docs-check一致。
- 停止条件: scope逸脱検知、自己修復4回目相当、未承認確定化要求。
- 並行実行可能フラグ: **No (security-lane serial)**。

### Phase 4: Verify（重複・矛盾・リンク）
- 重複Issue: 既存DOC-OPS-05連番内で対象重複なし（本Issue固有対象）。
- 優先度矛盾: `Priority=P2` 系列で整合（高優先度との衝突なし）。
- リンク切れ: Related ADR/Spec は既存記載を継承し、解決不能リンクは本パスでは未検出。
- 自己修復: 0/3（本更新時点）。

### Phase 5: Proceed（04_Documentation改訂担当への引継ぎ）
- 引継ぎメモ: 本Issueは「本文改稿を行わず、品質ゲートと参照導線を固定」済み。
- 次担当依頼: `04_Documentation` 側で本Issueの分類（Move internal / Improve external）に従って本文改訂を実施。
- ゲート条件: 改訂後は `docs-check` を再実行し、Issue側の分類・用語・導線と一致確認すること。

## Stream H serial completion log（2026-05-18）

### Phase 1: Read
- 本Issueと対応する `04_Documentation` 文書を再読し、docs-only と allowlist 制約を再確認。

### Phase 2: Plan
- 共通契約（Audience / Goal / Non-goal / Public boundary / Related）と品質ゲート（可読性・検証可能性・保守性）を適用。

### Phase 3: Execute
- 章構造・用語・相互リンク規約を統一し、各文書に「運用手順 / 判断基準 / 失敗時対応」を必須化。

### Phase 4: Verify
- `git diff --check` と issue memo validator（対象ファイル）を検証対象とする。
- self-correction: 0/3（4回目相当は Hold）。

### Phase 5: Proceed
- 判定: **Ready**（DOC-OPS-05 直列処理対象として継続可能）。

## 16) Open readiness gate（DOC-OPS-05 machine-check）

- Batch: `C (11-14)`
- GateStatus: `Conditional`（現時点のIssue StatusはDraftのため、Open化は本ゲートの充足を条件とする）
- DraftReasonClass: `open-trigger-not-executed`
- BlockingIssueIDs: `none`
- OpenTrigger:
  1. `Status` を Draft から Open へ変更。
  2. `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
  3. `GoNoGoGate=Required` に対する判定条件（Ready/Hold/Needs-decision）が本文中で一意。
  4. `DecisionStatus=Fixed` の場合、`DecisionQueueRef` は `N/A` であること。
- MechanicalChecks:
  - `rg -n "^- Status:|Expected verification level|VerificationLevel|GoNoGoGate|DecisionStatus|DecisionQueueRef" 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
  - `rg -n "Open readiness:|状態分類:|Phase 5: Proceed" 01_Plans/issues/issue-doc-ops-05-14-04doc-security-operational-guidelines.md`
  - `git diff --check`
- Proceed verdict (Phase 6): `Open可能（条件付き）`

## Stream G documentation/public boundary pass (2026-06-13)

### Plan
- 対象: `security operational guidelines`。
- Scope: Docs-only。`03_Implement/` と `02_Architecture/` は編集しない。
- Acceptance: 公開/保守/開発者/内部計画の分類が追跡でき、SafeMode・share/export・AI提案レビューの安全境界が後退しない。

### Execute
- RequirementID `DOC-OPS-05-14` の公開境界を再確認。
- Decision: security_operational_guidelines は公開可能な判断観点に限定し、組織固有の承認者名・期限・監査証跡を含めない境界を明記した。

### Verify
- docs-check 対象として issue memo metadata、Markdown整形、リンク導線、公開不可情報の混入有無を確認する。
- Self-correction budget: 0/3 から開始し、4回目相当は停止する。

### Proceed
- 判定: Ready for verification。
- 残課題: 実ファイル移動や開発者向け正本の再配置が必要な場合は、別PRで allowlist と移動先を明示して扱う。
