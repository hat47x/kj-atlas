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
