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
