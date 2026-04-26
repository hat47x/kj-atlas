# Issue Draft: DOC-OPS-05-14 04_Documentation/security_operational_guidelines.md の配置見直し

- Type: Documentation quality
- Status: Draft
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
