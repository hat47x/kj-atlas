# Issue Draft: DOC-OPS-05-13 04_Documentation/security.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/security.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/security.md`, `04_Documentation/operations.md`, `04_Documentation/security_operational_guidelines.md`, `THREAT_MODEL.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-13`
- RequirementStatement: `04_Documentation/security.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## Serial cycle record（security lane）

### Read
- `04_Documentation/security.md` を基点に operations / security_operational_guidelines との境界を確認。
- 直列順を `operations → security → security_operational_guidelines` で固定。

### Plan（不足AC/DoD補完提案）
- AC補完提案:
  - AC-1: 公開境界（Public）と非公開境界（Private）を明文化。
  - AC-2: 役割語彙 `Security Officer / System Owner / Platform Operator` を統一。
  - AC-3: D1〜D4相当は fixed values として参照導線を明示（値の再定義はしない）。
- DoD補完提案:
  - DoD-1: 本Issueは docs-only（対象3Issueのみ編集）を満たす。
  - DoD-2: Verify結果と Proceed判定を記録する。

### Execute
- 分類を **Improve external** で固定。
- security は基底方針（公開可能な原則・境界）に限定し、運用詳細は guidelines へ委譲。

### Verify（max 3 retries）
- Verify-1: docs-check整合（`Expected verification level=docs-check` と `VerificationLevel=docs-check`）。
- Verify-2: GoNoGoGate=Required 条件の記録（Audience/Goal/公開境界/次アクション）を確認。
- Verify-3: 安全境界後退・未承認確定化・対象外編集の不在を確認。
- Self-repair count: 0/3（4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次順序: `DOC-OPS-05-14 (security_operational_guidelines)` へ直列進行。

## ADR handling rule（このIssueに適用）
- 役割・導線・固定値（D1〜D4相当）で整合差分が発生した場合のみ C/D/C を明文化し、承認を要求する。
- 差分なしの場合は既存方針維持（新規承認要求なし）。

## Stop conditions
1. 安全境界後退
2. 未承認確定化
3. 対象外編集
4. 4回目修復（>3 retries）

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。

## 12) Stream F serial execution log（2026-04-26）

### Phase 1 Read
- 本Issue本文（Requirement meta I/F / Serial cycle record / Stop conditions）を再読し、対象が `DOC-OPS-05-13` 単票であることを確認。
- 参照正本は `04_Documentation/security.md`・`04_Documentation/operations.md`・`04_Documentation/security_operational_guidelines.md` に限定。

### Phase 2 Plan
- 実行範囲を **issue-doc-ops-05-13 のみ** に固定し、相互依存は manifest（Related ADR/Spec）参照のみに制限。
- 受入観点を `Audience / Goal / 公開境界 / 次アクション` と `docs-check` 一致確認に固定。

### Phase 3 Execute（ADRタスク必須 C/D/C + 承認記録）
- Context: security 文書は公開原則を示すが、運用詳細との境界が曖昧だと過不足ある公開につながる。
- Decision: `DOC-OPS-05-13` は **Improve external** を維持し、制度定義の再発明は行わず上流導線を優先する。
- Consequences: 後続の docs-only 更新は公開境界の明確化に集中でき、実装/設定変更を誘発しない。
- Approval record: **Issueメモ内承認（Stream F運用合意）** として本C/D/Cを記録。未承認の新規決定は追加しない。

### Phase 4 Verify
- `Expected verification level=docs-check` と `VerificationLevel=docs-check` の一致を確認。
- 自己修復回数を `0/3` で開始し、失敗時のみ最大3回まで。4回目相当は Stop conditions に従い停止。

### Phase 5 Proceed
- 判定: **Ready**。
- 次順序: `DOC-OPS-05-14` を同一プロトコル（Read → Plan → Execute → Verify → Proceed）で処理する。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: Read Order上流と本Issueを再読し、security lane（operations→security→guidelines）順序を確認。

### Phase 2 ADR/CDC
- Context: security は公開可能な基底方針に限定し、運用詳細は guidelines へ委譲する必要がある。
- Decision: **Improve external** を維持し、役割語彙・固定値は参照専用で運用。
- Consequences: 安全境界後退や未承認確定化を回避できる。

### Phase 3 Plan
- 実行計画: 本Issueメモ追記のみ（docs-only）。
- 停止条件: self-correction 4回目相当 / 未承認確定化 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Stream H 専属6Phaseログを追記。
- 非実施: 実装コード、architecture本体、shared resource、指定外Issue。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（次順序 05-14）。

## Stream I security-lane strict serial run（2026-04-27）

### Phase 1 Read（最新状態同期）
- Read同期: operations（05-11）の Stream I Proceed=Go を確認後、本Issue本文と `04_Documentation/security.md` を再読。
- 確認結果: `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` を維持。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: security は公開原則の基底文書であり、guidelines への委譲境界が曖昧だと公開境界後退リスクが増す。
- Decision: `Improve external` を維持し、役割語彙・固定値（D1〜D4相当）は再定義せず参照導線で統一。
- Consequences: 用語不整合と未承認確定化を抑止し、guidelines 側での運用詳細化を安全に継続できる。

### Phase 3 Plan（AC/DoD不足ドラフトと合意）
- AC不足補完（合意）:
  - AC-4: 公開境界が後退する記述追加を禁止し、検出時は `Hold`。
  - AC-5: 役割語彙の揺れ（Security Officer / System Owner / Platform Operator）検知時は差分記録のみで承認待ち。
- DoD不足補完（合意）:
  - DoD-3: `docs-check + git diff --check` をVerify必須化。
  - DoD-4: Proceed判定理由を1行で明文化。

### Phase 4 Execute（docs-only）
- 実施: 本Issueに Stream I 記録を追記（docs-only）。
- 非実施: 指定外ファイル、実装変更、承認未了事項の確定化。

### Phase 5 Verify（docs-check + 自己修復<=3）
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
  - `git diff --check`
- self-repair: 0/3（4回目修復は停止条件により禁止）。

### Phase 6 Proceed（Go/Hold/Needs-decision）
- 判定: **Go**（理由: 停止条件非該当、公開境界後退なし）。
- 次順序: 固定直列どおり `DOC-OPS-05-14` へ進行。

## Stream K gate-prep run（2026-04-27）

### Phase 1 Read（Draft gate条件の明示）
- 本Issueを最新状態で再読し、`Status=Draft` / `Priority=P2` / `Related Backlog=DOC-OPS-05` / `Expected verification level=docs-check` を確認。
- Draft gate条件を次の4点に固定: (1) 必須メタ（Status/Priority/Related/Validation）欠落なし、(2) Classificationが明示済み、(3) Proceed判定が `Ready/Hold/Needs-decision` で記録可能、(4) docs-only範囲を逸脱しない。

### Phase 2 ADR確認（CDC起票・承認前確定禁止）
- Context: DOC-OPS-05 Draft群は公開境界の分類判定を安全にOpen化するための事前整備。
- Decision: 本Issueの分類方針 `Improve external` を維持し、新規の制度変更は追加しない。
- Consequences: 追加Decisionが必要になった場合は **Issue内CDCを新規起票し、承認完了まで `Needs-decision` で停止**（確定化しない）。

### Phase 3 Plan（Open化に必要な AC / DoD / Validation 定義）
- AC:
  1. Audience / Goal / 公開境界 / 次アクションが本文で追跡可能。
  2. `GoNoGoGate=Required` の判定導線が本文にある。
  3. `DecisionStatus` と `DecisionQueueRef` の整合（FixedならN/A）が保たれる。
- DoD:
  1. docs-onlyで当該Issueファイルのみ更新。
  2. Verifyで必須メタ整合チェックを通過。
  3. Proceedで `Ready/Hold/Needs-decision` を理由付きで記録。
- Validation plan:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
  - `rg -n "^\- Status:|^\- Priority:|Related Backlog|Expected verification level|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
  - `git diff --check`

### Phase 4 Execute（Draft→Open移行条件の文書整備のみ）
- 実施内容: 本Stream Kセクションを追記し、Draft gate / CDC運用 / AC-DoD-Validation / Proceed判定条件を明文化。
- 非実施: 共有ファイル（`project-progress-dashboard.md` / `issues/README.md`）および実装コードの変更。

### Phase 5 Verify（必須メタ整合 + 失敗時3回修復）
- Verify結果: 1回目チェックで必須メタ（Status/Priority/Related/Validation）整合を確認。
- 修復回数: 0/3（不整合未検知）。4回目相当は停止し `Hold` へ遷移。

### Phase 6 Proceed（Open化可否判定）
- 判定: **Ready**。
- 根拠: Draft gate条件・CDC運用条件・AC/DoD/Validationが本文で再現可能。
- Open化時の次アクション: `security.md` を公開可能な基底方針に限定し、運用詳細のguidelines委譲を明示するOpenタスクを分離。


## Stream G dedicated 6-phase run（2026-04-27, DOC-OPS-05-13）

### Phase 1 Read
- Read同期: 本Issue本文を再読し、`Status` / `Scope` / `Priority` / `Expected verification level` を確認。
- 差分確認: 前回記録との差分は **なし**（`Status=Draft`, `Priority=P2`, `VerificationLevel=docs-check` を維持）。

### Phase 2 ADR/CDC
- Read同期: `Related ADR/Spec` と `ADR handling rule` を再読。
- Context: DOC-OPS-05 Draft整備は公開境界の安全な固定が目的で、未承認事項の確定化を禁止する。
- Decision: 分類 `Improve external` を維持し、新規仕様差分は起票しない（差分発生時のみ C/D/C を追記）。
- Consequences: docs-only の分類整備を継続し、仕様正本（00〜02）の改変を回避する。

### Phase 3 Plan
- Read同期: `Requirement meta I/F` / `Acceptance criteria` / `Stop conditions` を再読。
- 実行計画:
  1. 本Issueに6Phase直列記録を追記（allowlist内のみ）。
  2. AC/DoD不足はドラフト提案として本文に残す。
  3. Verify失敗時は自己修復を最大3回、4回目相当は停止（Hold）。

### Phase 4 Execute
- Read同期: `Scope` / `Proposed solution` / `Non-goal` を再読。
- 実施: 本セクションを追加して6Phase手順を明文化。
- 実施後方針: `04_Documentation/security.md` は公開可能な基底方針に限定し、運用詳細はguidelinesへ委譲。

### Phase 5 Verify
- Read同期: `Validation plan` と `Execution protocol` を再読。
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
  - `git diff --check`
- 結果記録: self-repair `0/3`（4回目相当は停止条件により禁止）。

### Phase 6 Proceed
- Read同期: `GoNoGoGate` / `DecisionStatus` / `DecisionQueueRef` を再読。
- 判定: **Ready**（理由: 6Phase直列記録・ADR/CDC条件・docs-check導線・停止条件が再現可能）。


## K-2担当 serial run（2026-04-27, docs-only）

### Phase Read
- 対象を `issue-doc-ops-05-13-04doc-security.md` のみに固定し、指定外編集禁止を再確認。
- `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を再確認。

### Phase ADR/CDC（必要時）
- 判定: 役割語彙・固定値・公開境界に新規差分なしのため **ADR/CDC 追加なし**。
- ルール: 差分が発生した場合のみ C/D/C を追記し、承認完了まで `Needs-decision` で停止。

### Phase Plan
- 実行計画:
  1. 本Issueに K-2 記録のみ追記（docs-only）。
  2. 安全境界後退（safeMode既定ON / share-export漏洩防止の緩和）記述を追加しない。
  3. Verifyは `docs-check` と `git diff --check` で実施。

### Phase Execute
- 実施: K-2専属6Phaseログを本Issueへ追記。
- 非実施: `issue-doc-ops-05-11-04doc-operations.md` を含む指定外ファイル編集。

### Phase Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 引き継ぎ: K-1担当（`issue-doc-ops-05-11-04doc-operations.md`）と並列実行可の状態を維持。

## Stream H execution compliance log（2026-04-27, Set A-2: security）

### 1) Read
- Read同期: 本Issueと 05-11 Proceed=Go を確認し、セットA直列順を維持。

### 2) ADR/CDC
- Context: security は公開原則の基底文書で、運用詳細はguidelinesへ委譲すべき。
- Decision: 分類 `Improve external` を維持し、役割語彙/固定値は参照専用とする。
- Consequences: 未承認確定化と公開境界後退を防止する。

### 3) Plan
- `Plan -> Execute -> Verify -> Proceed` を固定。
- AC/DoD不足は既存補完（AC-1〜3, DoD-1〜2）を適用。

### 4) Execute
- 本Issueメモ追記のみ実施（docs-only, allowlist内）。

### 5) Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-13-04doc-security.md`
- `git diff --check`
- self-correction: 0/3（4回目相当は停止）。

### 6) Proceed
- 判定: **Go**（セットA次順序: 05-14）。
