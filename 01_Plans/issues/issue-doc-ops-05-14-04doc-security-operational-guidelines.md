# Issue Draft: DOC-OPS-05-14 04_Documentation/security_operational_guidelines.md の配置見直し

- Type: Documentation quality
- Status: Ready
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `04_Documentation/security_operational_guidelines.md`
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `04_Documentation/security_operational_guidelines.md`, `04_Documentation/security.md`, `04_Documentation/operations.md`, `01_Plans/documentation_quality.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-14`
- RequirementStatement: `04_Documentation/security_operational_guidelines.md` を「内部文書へ移動」または「対外文書として改善」のどちらかに分類し、実行計画を固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=`04_Documentation` の文書分類を棚卸し済み`; 操作=対象文書の読者・目的・配置先を判定する; 期待結果=分類結果と次の変更方針が issue と関連文書に残る; 除外=本文の全面改稿や実装修正`
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

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

## Authoring Checklist（人間/生成AI 共通）

- [ ] `Source Issue` が運用状態と整合している（未運用時は `N/A`、運用時はURL）。
- [ ] `Related ADR/Spec` が最低1件ある。
- [ ] 受入条件に「安全」「互換」「検証」が含まれる。
- [ ] `Validation plan` に具体コマンドがある。
- [ ] 非目標が明記されスコープ逸脱を防いでいる。

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
