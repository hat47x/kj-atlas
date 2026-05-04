# Issue Draft: DOC-OPS-05-05 01_Plans/documentation_quality.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream I
- Scope: `01_Plans/documentation_quality.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/documentation_quality.md`, `01_Plans/adr/ADR-0024-doc-ops-04-quality-gates-boundary.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Dependencies: `DOC-OPS-05`, `DOC-OPS-05-06`, `DOC-OPS-05-07`
- Dependency status: `未確定（DOC-OPS-05 の Open gate 判定待ち）`
- Expected verification level: `docs-check / unit / integration / e2e（期待レベル固定。実行義務はdocs-checkのみ）`

## Requirement meta I/F（共通キー / Stream L統一）
- RequirementID: `DOC-OPS-05-05`
- RequirementStatement: 内部品質基準文書としての扱いを固定し、Open化審査に必要な判断情報を揃える。
- PriorityClass: Must
- AcceptanceScenario: 前提=3Issueの品質ゲート統一; 操作=分類方針/品質ゲート/検証計画を明示; 期待結果=Open可否を単体判定; 除外=実装改修
- GoNoGoGate: Required
- SecurityGateImpact: public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A（DecisionStatus=Fixed）

## ADR-style 明文化
### Context
- DOC-OPS-05 系Draftの判定メタは存在するが、3Issue横断で期待検証レベルの記述ゆれがあり、Open昇格判定を一本化しにくい。

### Decision
- 本Issueは **Move internal** を維持し、3Issue共通の品質ゲート定義（docs-check/unit/integration/e2eの期待レベル固定）を採用する。
- docs-onlyタスクとして、実行義務は `docs-check` のみ。unit/integration/e2e は「非目標かつ実装依存なしで進める検証項目」として定義固定する。

### Consequences
- Open化判定の比較軸が3Issueで一致し、Proceed/Hold/Stop 判定の恣意性を低減できる。
- 実装依存の検証を誤って要求しないため、docs-only範囲を逸脱しない。

## Open gate判定情報（Fixed）
### Classification（Move internal / Improve external）
- Decision: **Move internal（固定）**
- Classification basis:
  1. Audience: 文書執筆者・レビュアー向け内部品質統制。
  2. Goal: 公開文書品質を担保する内部審査の運用基準化。
  3. Public boundary: 対外説明本文ではなく内部統制基準書。

### GoNoGoGate=Required（判定条件）
- Go条件（全件必須）:
  1. 3Issueで共通メタ項目（Context/Decision/Consequences, AC, Validation, Non-goals）が一致。
  2. docs-check の実行結果が記録され、self-correction が `<=3`。
  3. `DOC-OPS-05` 依存確定証跡（日時・承認者・対象・判断）が追跡可能。
- NoGo/Hold条件:
  - 上記いずれか未達。
- Stop条件:
  - self-correction が `4回目` 相当に到達。
- Gate verdict: **NoGo（現時点）**

## Validation（共通定義）
- docs-check: **必須**
- unit: **期待レベル定義のみ（非目標）**
- integration: **期待レベル定義のみ（非目標）**
- e2e: **期待レベル定義のみ（非目標）**
- Planned checks:
  - `git diff --check -- 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-doc-ops-05-05-04doc-documentation-quality.md`
- Result summary: pass
- Self-correction budget: `0/3`

## Non-goals（共通定義）
- `03_Implement/**` の実装変更
- `04_Documentation/**` 本文改稿
- unit/integration/e2e 実行結果の新規作成

## Proceed tri-state
- ProceedDecision: **Hold**
- Alternatives: `Proceed` / `Hold` / `Stop`
- Reason: `DOC-OPS-05` 依存未確定。

## Open化 AC / DoD（統一）
- [ ] AC-Open-1: Classification / Gate / Validation / Proceed が本Issue単体で再読可能。
- [ ] AC-Open-2: docs-check pass と self-correction `<=3` を記録。
- [ ] AC-Open-3: 依存確定証跡（日時・承認者・対象・判断）を記録。
- [ ] AC-Open-4: docs-only制約を維持。
- [ ] DoD-Open-1: 3Issue横断で品質ゲート定義が一致。
- [ ] DoD-Open-2: 未解消項目がある場合は Hold/Stop へ遷移。
- [ ] DoD-Open-3: 次工程への引継ぎに「実装禁止解除条件」を1文で含む。

## Stream L execution log（2026-05-04）
### Phase 1: 共通テンプレ適合チェック
- 05/06/07 を同時再読し、メタ項目・AC・Validation・Non-goals の差分を抽出。

### Phase 2: ADR-style 明文化
- Context/Decision/Consequences を本Issueへ明示。
- docs-check/unit/integration/e2e の期待レベルを固定。

### Phase 3: 依存・競合整理
- 参照整合: `ADR-0019`, `documentation_quality.md`, `ADR-0024`。
- 実装依存なし検証項目: docs-check + メタ整合確認。

### Phase 4: 実行
- Open昇格可能粒度へ AC/DoD を再編。
- 検証計画をコマンド単位で固定。

### Phase 5: Verify/Stop
- 3Issue横断の品質ゲート一致を確認。
- 未解消: 依存確定証跡不足のため **Hold** 維持。


## Stream E preparation addendum（2026-05-04 / Draft→Open昇格準備）

### Phase 1: Read
- DOC-OPS-05-05/06/07 の3Issueを再照合し、品質ゲート記述（docs-check必須、他は期待レベル定義のみ）の一致を確認。

### Phase 2: Plan（AC/DoD不足補完）
- AC補完: `Approval Record`（日時/承認者/対象/判断/evidence）記録をOpen必須条件に固定。
- DoD補完: self-correction `<=3` を維持し、4回目相当は `Stop`。

### Phase 3: Execute（proposal-only）
- メモ整備のみ実施。`03_Implement/**` と `04_Documentation/**` 本文は非変更。

### Phase 4: Verify
- 3Issue横断のGate/Validation/Proceed三値が矛盾なく再読可能であることを確認。

### Phase 5: Proceed
- 判定: **Hold**（`DOC-OPS-05` 依存確定待ち）。
- Open昇格提案条件: 依存確定証跡 + docs-check pass + self-correction上限内。
- 未定義競合/4回目相当修復は **Stop**。

## Open化最終整備（proposal-only / 2026-05-04）

### Read→ADR/CDC→Plan→Execute→Verify→Proceed（固定運用）
1. **Read**: 上位根拠（ADR / schemas / 関連Issue）との差分を再読して語彙ドリフトを検知する。
2. **ADR/CDC**: Context / Decision / Consequences を本Issue内で閉じる（外部依存で確定しない）。
3. **Plan**: Open判定の AC / DoD / Validation / Stop 条件を先に固定する。
4. **Execute**: **blocker明文化・Open化条件定義・AC/DoD整備のみ** 実施し、実装化は行わない。
5. **Verify**: docs-check を基準に、自己修復は最大3回（4回目相当は Stop）で運用する。
6. **Proceed**: 依存確定と Approval Record が充足した場合のみ Proceed、それ以外は Hold/Stop。

### Blocker明文化（Open不可時の固定理由）
- 依存ステータス未確定、または承認証跡（日時/承認者/対象/判断/evidence）の欠落。
- proposal-only 契約（実装禁止 / auto-*禁止 / fail-closed）に抵触する要求の混入。
- Verify再試行が3回を超過、または未定義競合（契約衝突・責務分離崩壊）の検知。

### Open化条件（proposal-only gate）
- [ ] 条件1: 本Issue単体で Context/Decision/Consequences・AC・DoD・Validation・Proceed tri-state が再読可能。
- [ ] 条件2: docs-check の pass 記録と self-correction `<=3` が記録済み。
- [ ] 条件3: 依存確定証跡と Approval Record の最小項目が充足。
- [ ] 条件4: 実装タスク化を行わず、未承認依存を確定扱いしていない。

### Verify失敗時 Self-Correction ルール
- Attempt 1: 文言矛盾・欠落メタの修正。
- Attempt 2: Gate条件と Stop条件の再整列。
- Attempt 3: 依存/承認証跡の未充足を Hold理由へ明示。
- 4回目相当: **Stop**（超過または依存崩壊として終了）。


## Stream G normalization pass（2026-05-04）

### Phase 1: Read同期（Issue ↔ 04_Documentation 対応表）
| Issue | Target 04_Documentation | Current classification |
| --- | --- | --- |
| `issue-doc-ops-05-05-04doc-documentation-quality.md` | `04_Documentation/documentation_quality.md` | 既存本文の Decision / Proposed classification を継承 |

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
- 並行実行可能フラグ: **Yes**。

### Phase 4: Verify（重複・矛盾・リンク）
- 重複Issue: 既存DOC-OPS-05連番内で対象重複なし（本Issue固有対象）。
- 優先度矛盾: `Priority=P2` 系列で整合（高優先度との衝突なし）。
- リンク切れ: Related ADR/Spec は既存記載を継承し、解決不能リンクは本パスでは未検出。
- 自己修復: 0/3（本更新時点）。

### Phase 5: Proceed（04_Documentation改訂担当への引継ぎ）
- 引継ぎメモ: 本Issueは「本文改稿を行わず、品質ゲートと参照導線を固定」済み。
- 次担当依頼: `04_Documentation` 側で本Issueの分類（Move internal / Improve external）に従って本文改訂を実施。
- ゲート条件: 改訂後は `docs-check` を再実行し、Issue側の分類・用語・導線と一致確認すること。


## Stream I phase run (2026-05-04)
### 1. Read（最新同期）
- 3Issueの現行Draftを再読し、Classification / GoNoGo / Validation / Proceed tri-state の整合を確認。

### 2. ADR明文化（Context/Decision/Consequences）
- Context: Open判定に必要なメタは存在するが、依存確定証跡が未充足。
- Decision: 既存分類（Move internal / Improve external）を維持し、docs-check必須・他検証は期待レベル定義のみを固定。
- Consequences: docs-only範囲を維持したまま、Open可否を単体再判定できる。

### 3. Plan（AC/DoD不足補完）
- AC/DoD に `Approval Record` と self-correction上限（<=3）を必須条件として維持。
- 依存未確定時の Proceed 抑止（Hold/Stop）を明文化。

### 4. Execute（Draft品質向上のみ）
- 実施: 本Issueメモの整合性強化（phase運用・gate・stop条件の再確認）。
- 非実施: `03_Implement/**` と `04_Documentation/**` 本文改稿。

### 5. Verify（3回まで自己修復）
- 実行結果: docs-check系コマンドで整形・メタ不整合なし。
- Self-correction: `1/3`（初回検証で固定、4回目相当はStop）。

### 6. Stop（gate未確定なら停止）
- 判定: **Hold/Stop ready**。`DOC-OPS-05` の依存確定証跡が揃うまで Proceed しない。
