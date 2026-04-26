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
