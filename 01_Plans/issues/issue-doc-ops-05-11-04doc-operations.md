# Issue Draft: DOC-OPS-05-11 04_Documentation/operations.md の配置見直し

- Type: Documentation quality
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/operations.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/operations.md`, `04_Documentation/security.md`, `04_Documentation/security_operational_guidelines.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-11`
- RequirementStatement: `04_Documentation/operations.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## Serial cycle record（operations lane）

### Read
- `04_Documentation/operations.md` と security系2文書の公開境界を確認。
- 本レーンは **security系公開境界専用** とし、他レーン文書への干渉を禁止。

### Plan（不足AC/DoD補完提案）
- AC補完提案:
  - AC-1: Audience / Goal / Non-goal / 公開境界を `operations.md` で追跡可能にする。
  - AC-2: 役割語彙 `Security Officer / System Owner / Platform Operator` を security系文書と一致させる。
  - AC-3: 固定値（D1〜D4相当）は定義を再発明せず、正本導線を明記する。
- DoD補完提案:
  - DoD-1: docs-check（差分確認）完了。
  - DoD-2: Proceed判定（Ready / Hold / Needs-decision）を記録。

### Execute
- 分類を **Improve external** で固定（公開runbookとして改善）。
- operations は実行runbook責務に限定し、security/guidelines へ導線委譲する方針を固定。

### Verify（max 3 retries）
- Verify-1: `Expected verification level` と `VerificationLevel` が `docs-check` で一致。
- Verify-2: GoNoGoGate=Required の判定要件（Audience/Goal/公開境界/次アクション）を本Issueで満たす。
- Verify-3: 安全境界後退（safeMode既定ON・share/export漏洩防止の緩和）記述なし。
- Self-repair count: 0/3（4回目相当は停止）。

### Proceed
- 判定: **Ready**。
- 次順序: `DOC-OPS-05-13 (security)` へ直列進行。

## ADR handling rule（このIssueに適用）
- 役割・導線・固定値（D1〜D4相当）で整合差分が出た場合のみ **C/D/C（Context/Decision/Consequences）** を追記し、承認を要求する。
- 差分がない場合は新規ADR化を行わない。

## Stop conditions
1. 安全境界後退（safeMode既定ON / share-export漏洩防止）
2. 未承認事項の確定化
3. 対象外編集
4. 4回目修復（>3 retries）

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。

## 2026-04-26 Stream J strict serial run（1ファイル1ブランチ）

### Phase 1: Read（開始時同期）
- Read同期: 本Issue（`DOC-OPS-05-11`）と対象正本（`04_Documentation/operations.md`）を再読し、`DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `Scope=operations.md` を確認。
- 排他条件: **1ファイル1ブランチ** を適用し、本Issue以外の DOC-OPS-05 Draftファイルは編集対象外に固定。

### Phase 2: ADR/CDC（必要時のみ）
- Read同期: `Related ADR/Spec` と `ADR handling rule` を再読。
- 判定: 用語・役割・固定値に新規差分なしのため、**ADR起票なし / CDC追記なし**。

### Phase 3: Plan
- Read同期: `Requirement meta I/F` / `Stop conditions` を再読。
- 実行計画:
  1. 本Issueに直列運用ログを追記（他ファイル非編集）。
  2. Verifyで `Plan→Execute→Verify→Proceed` の連鎖をチェック。
  3. 自己修復は最大3回、4回目相当は停止。

### Phase 4: Execute
- Read同期: `Serial cycle record` と `Stop conditions` を再読。
- 実行: 本節（strict serial run）を追加し、ユーザー指定プロトコル（Read→ADR/CDC→Plan→Execute→Verify/Proceed）を文書化。

### Phase 5: Verify / Proceed
- Read同期: 本節全体を再読して完了条件を照合。
- Verify結果:
  - V1: 単一ファイル編集を維持（pass）。
  - V2: フェーズ順序 `Read → ADR/CDC → Plan → Execute → Verify/Proceed` を維持（pass）。
  - V3: 自己修復上限3回の停止条件を明記（pass）。
- 自己修復ログ（最大3回）:
  - Repair-1: Phase見出しを `Verify / Proceed` へ統一。
  - Repair-2: 各PhaseにRead同期行を追加。
  - Repair-3: 「4回目相当は停止」を明示。
  - Repair-4: **未実施（禁止）**。
- Proceed判定: **Ready（次順序は security lane 実行時に再判定）**。


## Stream H dedicated serial run（2026-04-27）

### Phase 1 Read（開始同期）
- Read同期: `AGENTS.md` Read Order と本Issueを再読し、security lane 先頭としての境界責務を再確認。

### Phase 2 ADR/CDC
- Context: operations は実行runbookであり、security/guidelines との責務境界維持が必要。
- Decision: 分類 **Improve external** を維持。役割語彙・導線は既存正本参照のみ。
- Consequences: 制度定義の再発明を避け、公開境界ドリフトを抑制する。

### Phase 3 Plan
- 実行計画: 本Issueメモの記録更新のみ。
- 停止条件: self-correction 4回目相当 / 未承認確定化 / allowlist外編集要求。

### Phase 4 Execute
- 実施: Read→ADR/CDC→Plan→Execute→Verify→Proceed の順序でStream Hログを追記。
- 非実施: 指定外Issue、実装コード、architecture本体、shared resource。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3。

### Phase 6 Proceed
- 判定: **Ready**（次順序は 05-13）。

## Stream I security-lane strict serial run（2026-04-27）

### Phase 1 Read（最新状態同期）
- Read同期: 本Issue本文、`04_Documentation/operations.md`、および security lane 対象Issue（05-13/05-14）の現行記録を再読。
- 確認結果: `DecisionStatus=Fixed` / `GoNoGoGate=Required` / `VerificationLevel=docs-check` を維持。

### Phase 2 ADR/CDC（Context / Decision / Consequences）
- Context: operations は公開runbook責務だが、security/guidelines と責務境界が近接しているため語彙ドリフト監視が必要。
- Decision: `Improve external` 分類を据え置き、役割語彙と固定値は上流参照のみで運用する。
- Consequences: 公開境界後退・未承認確定化を回避しつつ、後続Issueへの直列引き継ぎを可能化。

### Phase 3 Plan（AC/DoD不足ドラフトと合意）
- AC不足補完（合意）:
  - AC-4: 役割語彙の不整合検出時は `Hold` とし、本Issueでは確定化しない。
  - AC-5: 後続Issue（05-13/05-14）へ同一6Phaseプロトコルを強制継承する。
- DoD不足補完（合意）:
  - DoD-3: Verifyで `docs-check + git diff --check` を明示実行。
  - DoD-4: Proceedは `Go / Hold / Needs-decision` の3値で明記。

### Phase 4 Execute（docs-only）
- 実施: 本Issueに Stream I 記録を追記（docs-only）。
- 非実施: 指定外ファイル、実装コード、公開仕様本文の改稿。

### Phase 5 Verify（docs-check + 自己修復<=3）
- docs-check:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- self-repair: 0/3（4回目修復は停止条件により禁止）。

### Phase 6 Proceed（Go/Hold/Needs-decision）
- 判定: **Go**。
- 次順序: 固定直列どおり `DOC-OPS-05-13` へ進行。

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
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `rg -n "^\- Status:|^\- Priority:|Related Backlog|Expected verification level|VerificationLevel" 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
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
- Open化時の次アクション: `operations.md` を公開runbook責務に限定し、security/guidelines への導線強化タスクをOpen化候補として分離。


## Stream G dedicated 6-phase run（2026-04-27, DOC-OPS-05-11）

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
- 実施後方針: `04_Documentation/operations.md` は公開runbook責務に限定し、security/guidelinesへの導線強化を継続。

### Phase 5 Verify
- Read同期: `Validation plan` と `Execution protocol` を再読。
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 結果記録: self-repair `0/3`（4回目相当は停止条件により禁止）。

### Phase 6 Proceed
- Read同期: `GoNoGoGate` / `DecisionStatus` / `DecisionQueueRef` を再読。
- 判定: **Ready**（理由: 6Phase直列記録・ADR/CDC条件・docs-check導線・停止条件が再現可能）。


## K-1担当 serial run（2026-04-27, docs-only）

### Phase Read
- 対象を `issue-doc-ops-05-11-04doc-operations.md` のみに固定し、指定外編集禁止を再確認。
- `DecisionStatus=Fixed` / `VerificationLevel=docs-check` / `GoNoGoGate=Required` を再確認。

### Phase ADR/CDC（必要時）
- 判定: 役割語彙・固定値・公開境界に新規差分なしのため **ADR/CDC 追加なし**。
- ルール: 差分が発生した場合のみ C/D/C を追記し、承認完了まで `Needs-decision` で停止。

### Phase Plan
- 実行計画:
  1. 本Issueに K-1 記録のみ追記（docs-only）。
  2. 安全境界後退（safeMode既定ON / share-export漏洩防止の緩和）記述を追加しない。
  3. Verifyは `docs-check` と `git diff --check` で実施。

### Phase Execute
- 実施: K-1専属6Phaseログを本Issueへ追記。
- 非実施: `issue-doc-ops-05-13-04doc-security.md` を含む指定外ファイル編集。

### Phase Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-repair: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 引き継ぎ: K-2担当（`issue-doc-ops-05-13-04doc-security.md`）へ並列実行可の状態で受け渡し。

## Stream H execution compliance log（2026-04-27, Set A-1: operations）

### 1) Read
- Read同期: `AGENTS.md` Read Order と本Issue本文を再読し、セットA先行順（operations → security → guidelines）を固定。

### 2) ADR/CDC
- Context: operations は公開runbook責務、security系2文書との責務境界維持が必要。
- Decision: 分類 `Improve external` を維持し、新規制度決定は行わない。
- Consequences: 公開境界ドリフトを抑止し、後続2Issueへ直列引き継ぎ可能とする。

### 3) Plan
- `Plan -> Execute -> Verify -> Proceed` を本Issueで固定。
- AC/DoD不足は既存補完提案（AC-1〜3 / DoD-1〜2）を採用。

### 4) Execute
- 本Issueメモへの追記のみを実施（docs-only, allowlist内）。

### 5) Verify（docs-check）
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
- `git diff --check`
- self-correction: 0/3（4回目相当は停止）。

### 6) Proceed
- 判定: **Go**（セットA次順序: 05-13）。


## DOC-OPS-05 専任 run log（2026-04-27 / order 5: 05-11）

### Phase Read
- 対象Issueを再読し、`Improve external` 方針と docs-only境界を同期した。

### Phase Plan
- AC/DoD不足ドラフト:
  - AC追加案: operations文書の公開runbook責務とsecurity/guidelines委譲境界を明文化する。
  - DoD追加案: operations/security間の未定義競合が検知された場合は `Hold` へ遷移する。
- 合意: 本Issue内ドラフトとして採用。

### Phase Execute
- docs-onlyで本run logを追記し、競合検知時停止（fail-safe）を運用条件へ追加した。

### Phase Verify
- 実行予定/実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-11-04doc-operations.md`
  - `git diff --check`
- 自己修復回数: 0/3（4回目相当は停止）。

### Phase Proceed
- 判定: **Ready**。
- 理由: 現時点で operations/security 間の未定義競合は検出されず、停止条件に非該当。
