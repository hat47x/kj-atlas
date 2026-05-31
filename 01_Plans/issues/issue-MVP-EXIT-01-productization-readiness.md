# Issue Draft: MVP-EXIT-01 MVP脱却に向けた製品化準備

- Type: Feature request
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0 (Program)
- Owner: Codex
- Scope: `00_Prompt/`, `01_Plans/`, `02_Architecture/`, `03_Implement/`, `04_Documentation/`
- Related Backlog: `MVP-EXIT-01`
- Related ADR/Spec: `README.md`, `ROADMAP.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0005-phase2-qualitative-integration.md`, `01_Plans/adr/ADR-0006-phase3-review-governance.md`, `02_Architecture/architecture.md`, `02_Architecture/enterprise_architecture.md`, `04_Documentation/public_index.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: MVP-EXIT-01
- RequirementStatement: kj-atlas をMVP扱いから、継続利用・公開配布・組織導入に耐える製品品質へ移行するための作業束を定義する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=現行アプリと公開候補文書が存在する / 操作=製品化に必要な品質・運用・UI/UX・公開導線を点検 / 期待結果=MVP表現、未完了の運用境界、UI/UXの主要リスクが個別issueへ分解される / 除外=本Issue単体で全機能を実装すること。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- UI、文書、運用手順にはMVP期の前提や内部管理視点が残っている。
- 一般利用者が自然に操作できるか、共有やAI提案を安全に扱えるか、公開文書から迷わず始められるかを横断的に確認する必要がある。
- MVP脱却には、単一の機能追加ではなく、製品名・導線・UI/UX・品質ゲート・公開文書・運用境界の束として扱う必要がある。

## 2) 背景 / Context

- `04_Documentation/public_index.md` は一般公開向け入口として整備済み。
- `04_Documentation/acceptance_check.md` に、利用者のマウス・キーボード操作を前提にした受け入れ確認を追加した。
- UIの未日本語化ラベルと右パネル見切れは、MVP期の作業密度が利用者体験に表れている例である。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 情報を整理し、判断を共有しやすくする価値は、初回利用と継続利用の動線が自然であるほど実現しやすい。
- 安全（THREAT_MODEL / SafeMode）: share/export とAI提案の安全境界が画面と文書で一致している必要がある。
- 企業・行政要件（enterprise_architecture）: 組織導入では文書体系、操作説明、監査、アクセス制御、障害時の初動が必要になる。
- 後方互換（schemas）: 製品化対応では既存データを壊さず、表示・操作・文書の改善を優先する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - UI/UX: 初回導線、右パネル、キーボード操作、未翻訳ラベル、フォーカス順序
  - 文書: 公開インデックス、受け入れ確認、設定、データ取り扱い、セキュリティ、開発者向け文書の分離
  - 運用: release、diagnostics、backup、rollback、障害時共有テンプレート
  - 品質: i18n、E2E、accessibility、responsive layout、large document performance
- 変更の最小単位:
  - 製品化テーマごとに `UX-*`、`DOC-*`、`QA-*`、`SEC-*` のissueへ分解する。
- 非目標:
  - 認証・SSO・連携先PDPなどの大規模実装を本Issueだけで完了させること。

## 5) 受入条件 / Acceptance criteria

- [ ] UI上の主要操作が日本語UIで一貫し、未翻訳ラベルが目立たない。
- [ ] マウスとキーボードで、作成、編集、保存、共有前確認、表示切替に自然に到達できる。
- [ ] MVP表現が、公開文書や通常画面の主要導線から除去または適切に置換される。
- [ ] 一般利用者向け文書と開発者向け文書が分離される。
- [ ] share/export、SafeMode、AI提案、監査ログの安全説明が画面・文書・実装で矛盾しない。
- [ ] 製品化に必要な残作業が個別issueへ分解され、ADR化が必要な判断だけADR候補として分離される。


## Stream J 再整列（2026-05-17）

### 優先度再整列
- 本Issueは製品化親Issueとして **P0 Program Gate** とし、個別実装Issueの先行条件（Open化判定）を担う。
- 実装を直接持たず、品質ゲート・依存切断・Open化条件の管理に限定する。

### 依存切断ポリシー
- `PRODUCT-UX-*` / `PRODUCT-QA-01` / `PRODUCT-OPS-01` は **相互待ち禁止** とし、本Issueからの一方向参照へ統一する。
- 依存は「仕様確定依存」と「実装依存」を分離し、仕様確定は docs-check 完了で解除可能とする。

### Open化条件（Definition of Ready for Open）
- [ ] 個別Issueが `DecisionStatus` / `GoNoGoGate` / `VerificationLevel` を埋めている。
- [ ] 受入条件に「安全境界」「回帰」「証跡」が含まれている。
- [ ] 非目標が明記され、UI実装変更をこのIssue本文で要求していない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 画面上のMVP表現、未翻訳ラベル、仮実装ラベルを棚卸しする。
- [ ] T2 マウス操作とキーボード操作の主要ユーザージャーニーを文書化し、自然でない箇所をissue化する。
- [ ] T3 公開文書から内部管理情報を除外し、開発者向け正本を別管理へ移す。
- [ ] T4 share/export と SafeMode の説明を画面、文書、テストで照合する。
- [ ] T5 大きなドキュメント、狭い画面、低速環境での利用体験を確認する。
- [ ] T6 release readiness checklist をMVP後の品質ゲートに更新する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test:i18n`
  - `npm run e2e`
  - `rg -n "MVP|04_Documentation|AGENTS.md|ADR-|内部管理" 04_Documentation`
- 期待結果:
  - UIの主要導線にMVP期の仮ラベルや未翻訳ラベルが残らない。
  - 公開文書は使い方の説明に集中している。
  - 製品化に必要な未解決項目が個別issueへ分かれている。

## 8) 代替案 / Alternatives considered

- 代替案A: 文書改善だけでMVP脱却とみなす。UI/UXと運用品質が残るため不十分。
- 代替案B: 大規模リデザインを先に行う。安全境界と既存操作の互換性を崩すリスクがあるため、課題分解を先に行う。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 製品化作業が大きすぎて、UI・文書・運用の変更が混在する。
- 影響範囲: frontend、公開文書、開発者向け文書、品質ゲート。
- ロールバック手順: 個別issue単位でPRを分け、問題のある変更だけ戻せるようにする。

## 10) Additional context

- ADR化が必要になる条件: ナビゲーション構造、公開配布方式、SafeMode既定値、認証・認可の製品方針を変更する場合。

### 2026-05-14 製品化分解メモ

- 画面設計の上位判断:
  - `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- 初回導線:
  - `01_Plans/issues/issue-PRODUCT-UX-01-first-run-document-entry.md`
- ワークスペース構造:
  - `01_Plans/issues/issue-PRODUCT-UX-02-workspace-information-architecture.md`
- 共有・エクスポート・レビューパック:
  - `01_Plans/issues/issue-PRODUCT-UX-03-safe-share-export-flow.md`
- 小画面・大規模文書・低速環境:
  - `01_Plans/issues/issue-PRODUCT-UX-04-responsive-large-document-operability.md`
- リリース品質ゲート:
  - `01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- サポート・診断・復帰導線:
  - `01_Plans/issues/issue-PRODUCT-OPS-01-support-diagnostics-error-recovery.md`

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。

## 11) Stream E update (2026-05-19): Program gate serialization

### Phase 1: Read
- 親Issueとしての役割を「実装タスク管理」ではなく「**Go/No-Go統治**」へ限定する方針を再確認した。

### Phase 2: ゲート定義
- 本Issueの Release判定入力は `PRODUCT-QA-01` の G0..G7 / Value gates を正本として参照する。
- Env整合の必須入力は `ENV-CONFIG-DRIFT-01` の E系ゲート判定結果とする。

### Phase 3: 検証設計
- Program判定に必要な最小証跡:
  1. Productization Gate Record（最新版）
  2. Env contract alignment result
  3. No-Go/Conditional Go の未解決フォローアップ一覧（owner + due）

### Phase 4: 監査テンプレ
- 判定ログは以下を必須化:
  - 判定日（YYYY-MM-DD）, 判定者, 対象 candidate
  - Gate summary（Go/Conditional Go/No-Go）
  - Escalation decision（継続/停止/再判定日）

### Phase 5: 反映
- 本Issueの `DecisionStatus` は **Pending 維持**（親Issueとして最終判定待ち）。
- 子Issueが No-Go の場合、本Issueは自動的に No-Go とし、条件付き解放は禁止。

### Fail-safe
- 判定基準が曖昧なままの場合は進行停止し、ADRまたは運用責任者承認を要求する。

## 12) Stream F update (2026-05-19): Program-level Go/No-Go handoff

### Phase 1: Read
- 親Issueの判定入力を `PRODUCT-QA-01`（G/V/Eゲート）に一本化し、本Issueは Program 判定のみを担当する。
- `ADR-0019` 準拠で、E2E未実施時は「未実施理由・再開条件・再判定日」を必須記録とする。

### Phase 2: Plan
- Program判定の閾値を固定:
  - Go: 子ゲートがすべて Go。
  - Conditional Go: 子ゲートに Conditional Go が残るが、期限付き是正計画が登録済み。
  - No-Go: 子ゲートに No-Go が1件以上、または証跡不備。

### Phase 3: Execute
- 本Issue受入条件へ次を反映:
  - Program 判定ログに `candidate/date/reviewer/final decision/escalation` を必須化。
  - Conditional Go は「解除条件」と「再判定日」が埋まらない限り出荷不可。
  - No-Go は自動的に本Issueも No-Go 扱いにする。

### Phase 4: Verify
- 測定可能性: Program判定ログから、どの子Issueが判定を規定したか追跡可能である。
- 再現性: 同一 candidate の再判定で、前回との差分理由（修正済み/未修正/新規リスク）を1行で説明できる。

### Phase 5: Proceed（Program判定テンプレート）
```md
## MVP-EXIT Program Gate Decision
- Candidate:
- Decision date:
- Reviewer:
- Input sources:
  - PRODUCT-QA-01 gate record:
  - ENV-CONFIG-DRIFT-01 result:

### Decision
- Final: Go | Conditional Go | No-Go
- Reason summary:
- Escalation route:

### Conditional controls
- Remaining risks:
- Owner:
- Due date:
- Re-decision date:
```

## 13) Stream H integration decision update (2026-05-20)

### Phase 1: Read & Intake
- A〜Gストリームの完了報告・検証ログは、`project-progress-dashboard` の最新同期（2026-05-19 rerun-77）を入力正本として採用した。
- 証跡不足として、以下を Program Gate の追加要求に分類した。
  1. `PRODUCT-QA-01` Gate Record の candidate単位の最新判定ログ（date/reviewer/final decision/escalation）
  2. `ENV-CONFIG-DRIFT-01` のE系ゲート最終結果
  3. Conditional/No-Go時の是正期限（owner/due/re-decision date）
- 入力鮮度は 2026-05-19 (UTC) を最新として確認し、これより古い判定は再評価対象とする。

### Phase 2: クリティカルパス再計算
- 真のクリティカルパス: `PRODUCT-QA-01 Gate確定 -> ENV-CONFIG-DRIFT-01整合 -> MVP-EXIT Program Gate最終判定`。
- モックで回避可能な依存: A2/A3実装前段のI/F整合確認（契約固定済み範囲）は継続可能。
- モックで回避不能な依存: Program Gate最終判定（Go/Conditional/No-Go）に必要な承認記録とGate結果。

### Phase 3: MVP Exit一次判定
- **一次判定: Conditional**
- 根拠:
  - Program判定テンプレートと判定閾値は整備済み。
  - 一方で最終Go判定に必要な最新Gate証跡（candidate単位）が本Issue本文で未確定。
- 是正条件:
  1. `PRODUCT-QA-01` と `ENV-CONFIG-DRIFT-01` の最新結果を Program Gate Decision テンプレートに転記。
  2. Conditional項目ごとに owner/due/re-decision date を必須入力。
  3. No-Go要因が1件でも残る場合は出荷判定を停止。

### Phase 4: 次サイクル実行計画（衝突ゼロ）
- Lane-H1（Program Gate証跡統合）: 本Issueのみ更新し、判定ログを確定する。
- Lane-H2（進捗可視化）: `project-progress-dashboard.md` のみ更新し、公開固定値・判定状態を同期する。
- Lane-H3（受入導線同期）: `04_Documentation/acceptance_check.md` の統合判定節のみ更新し、利用者向け確認導線を維持する。
- 停止条件: 証跡不足、allowlist外編集要求、判定式ドリフト、Verify 3回超過。

## Stream F update (2026-05-20): MVP Exit判定テンプレート固定

### Exit Decision Matrix

| 判定 | 条件 | 必須アクション |
| --- | --- | --- |
| Pass | Blocker=0 / Critical=0 / Major=0、必須ゲート完了、証跡完備 | リリース可 |
| Conditional | Blocker=0 / Critical=0、Major>=1 かつ是正計画確定 | 期限付きフォローアップ発行後に限定リリース可 |
| Fail | Blocker>=1 または Critical>=1、または証跡欠落 | リリース停止 |

### Required evidence pack

- Gate Record（G0..G7, V0..V4, E1..E3）

## Stream F update (2026-05-20): Program gate alignment with PRODUCT-QA-01

### Phase 1 Read（親子判定境界の明確化）
- 本Issueは Program 判定専任、`PRODUCT-QA-01` は Release Readiness 判定正本という責務分離を固定した。
- 判定不整合を避けるため、本Issueはゲート定義を再発明せず、`PRODUCT-QA-01` の結果を入力として受理する。

### Phase 2 Plan（Program判定式の統一）
- Program 判定式を `PRODUCT-QA-01` と同一ロジックへ統一する。
  - Go: 子ゲート判定が Go かつ必須証跡完備
  - Conditional Go: Blocker/Critical=0 で、Major残件に期限付き是正計画あり
  - No-Go: Blocker>=1 または Critical>=1 または証跡欠落
- Program判定カテゴリは次の4観点で集約する。
  - Quality
  - Security
  - Operability
  - Documentation

### Phase 3 Execute（受入条件テンプレート固定）
- 他ストリーム成果を Program 判定へ取り込む際の受入条件テンプレートを固定する。

```md
## Program Intake Acceptance Template (MVP-EXIT-01)
- Candidate:
- Source stream / issue:
- Category: Quality | Security | Operability | Documentation
- Referenced QA gate result: (G/V/E + verdict)
- Evidence completeness: pass/fail
- Risk class: Blocker | Critical | Major | Minor
- Intake result: Accept | Conditional Accept | Reject
- If conditional/reject:
  - Required follow-up issue:
  - Owner:
  - Due:
  - Re-decision date:
```

### Phase 4 Verify（判定可能性チェック）
- Program判定の必須入力:
  1. `PRODUCT-QA-01` の最新 Gate Record（candidate/date/reviewer/final）
  2. E系ゲート最終結果（E1..E3）
  3. Conditional/No-Go の未解決フォローアップ（owner/due/re-decision date）
- フェイルセーフ:
  - 上記いずれか未定義/欠落時は **判定停止（No-Go扱い）**。
  - 推測補完は禁止。

### Phase 5 Proceed（Program判定出力規約）
- Program判定ログは次を必須項目とする。
  - Candidate / Decision date / Reviewer
  - Final decision（Go | Conditional Go | No-Go）
  - Decision reason（1行要約）
  - Escalation route（継続/停止/再判定日）
  - External dependencies（未解決項目）
- 本Issueの完了条件は「製品実装完了」ではなく「判定枠組み確定 + 追跡可能な証跡様式確定」とする。
- 実行コマンドログ（成功/失敗/未実施理由）
- 手動smoke観測（viewport含む）
- 未解決リスク台帳（owner/due date/escalation）

### Escalation/approval responsibility

- QA Lead: 判定取りまとめ・証跡整合確認
- System Owner: Conditional/Failの最終判断
- Platform Operator: 再現環境・実行ログ保証
- Security Officer: SafeMode/share-export/public exposure関連の最終承認


## 14) Stream H release readiness framework update (2026-05-20)

### Phase 1: Read（Readyストリーム出口条件の収集）
- Ready入力を次の3系統へ固定する。
  1. `PRODUCT-QA-01` の Gate Record（G/V/E）
  2. `ENV-CONFIG-DRIFT-01` の E系最終判定
  3. `HIL-RS-02` delivery plan の Hold/Stop条件
- 収集対象は「candidate/date/reviewer/final decision/escalation」を必須キーとし、欠落時は `evidence-missing` 扱い。

### Phase 2: 統合判定フレーム（release readiness）
- Program統合判定は次の順序で直列評価する。
  - Step-1: Safety gate（safeMode / share-export / pending bypass）
  - Step-2: Quality gate（G0..G7 / V0..V4 / E1..E3）
  - Step-3: Evidence gate（candidate単位証跡の鮮度）
- 最終判定は `Go | Conditional | No-Go`。
  - `Go`: 3ゲートすべて通過。
  - `Conditional`: Safety通過、Quality/Evidenceに期限付き未解決が残る。
  - `No-Go`: Safety未通過、または証跡欠落。

### Phase 3: Plan→Execute→Verify（非依存統合観点）
- 本Issueで扱う作業を「統合判定ロジックの固定」と「証跡要求の明文化」に限定する。
- 他ストリーム実装の完了待ちはしない。未入力は `pending evidence` として保持し、判定式側だけを先に固定する。
- Verify観点: 判定式、入力必須キー、Stop条件が本文で相互矛盾しないこと。

### Phase 4: Stopper
- 下記が発生した場合は停止し、allowlist外編集を行わない。
  1. `PRODUCT-QA-01` / `ENV-CONFIG-DRIFT-01` 実ファイル更新を要求された場合
  2. Program判定に必要な証跡が候補単位で取得不能な場合
  3. 判定式の再定義要求（safeMode後退・No-Go緩和）

## Stream H update (2026-05-20): Program integration cadence and release decision SSOT

### Phase cadence（各Phase開始時 Read同期必須）
- 固定順序: `Read -> Plan -> Execute -> Verify -> Proceed`。
- Read同期対象（毎Phase冒頭）:
  1. `issue-MVP-EXIT-01-productization-readiness.md`（本ファイル）
  2. `issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
  3. `issue-REQ-DEF-01/02/03`
  4. `issue-PRODUCT-UX-*`, `issue-PRODUCT-VALUE-*`, `issue-PRODUCT-OPS-01`
- 差分検知時運用: AC/DoDまたはGate定義の齟齬を検知した場合は `draft proposal` を先に追加し、未合意事項は `Pending` として隔離する。

### Program-level AC/DoD補完（Stream H統合）
- Program AC:
  - [ ] PA-01: 全P0 issueで `GoNoGoGate` と `VerificationLevel` が整合している。
  - [ ] PA-02: release判定の最終式が `PRODUCT-QA-01` の Gate Record と矛盾しない。
  - [ ] PA-03: No-Go時の戻し先（REQ/PRODUCT/ENV）が候補ごとに一意に決まる。
- Program DoD:
  - [ ] PD-01: 判定ログ（candidate/date/reviewer/decision/follow-up）が埋まっている。
  - [ ] PD-02: `Conditional` は期限付きfollow-up issueがある場合のみ許可。
  - [ ] PD-03: self-repairは最大3回。4回目相当は停止報告（原因/影響/再開条件）。

### Release decision rule（統合判定）
- `Go`: Safety/Quality/Evidenceの全ゲート通過 + Blocker=0。
- `Conditional`: Safety通過 + Blocker=0 + Majorのみ残存 + 期限付き是正Issueあり。
- `No-Go`: Safety不通過、または証跡欠落、またはself-repair上限超過。


## Stream H Contract Finalization (2026-05-20)

### Scope confirmation
- Stream H dedicated; plan/ADR layer only; no implementation code edits.
- Target backlog: `MVP-EXIT-01` / `PRODUCT-VALUE-01..03` only.

### C/D/C lock (Context / Decision / Consequences)
| Context | Decision | Consequences |
| --- | --- | --- |
| MVP-EXIT-01 requires Open-ready contract quality before downstream execution. | AC/DoD/KPI/audit fields are locked for docs-only verification first. | Downstream streams can execute without re-interpreting value intent. |

### KPI + audit scorecard mapping
- KPI field quality gate: definition / formula / evidence / re-measurement must all exist.
- Audit field quality gate: `reviewer`, `date`, `artifact id`, `decision`, `re-decision condition` must be explicit.

### AC / DoD final lock
- [ ] AC-F1 Hypothesis→Action→Evidence→Decision chain is explicit.
- [ ] AC-F2 Go/No-Go rule is explicit and binary-decidable.
- [ ] AC-F3 KPI definitions are re-measurable by docs-only procedure.
- [ ] DoD-F1 No cross-stream implementation dependency is required for contract validation.
- [ ] DoD-F2 Safety boundary wording (SafeMode/share-export/review attribution) is consistent with ADR-0032.

### Verify (non-dependency)
- Result: Contract validation is executable without waiting for other stream code merges.
- Reason: Inputs are issue text completeness and evidence schema only.

### Self-correction (<=3)
1. Normalized gate terms to `Go / Conditional Go / No-Go`.
2. Removed ambiguous wording that implied implementation readiness was required at this phase.
3. Added explicit audit metadata requirements for approval traceability.

### Approval-wait packet
- This section + ADR-0032 Stream H block are the approval bundle for MVP-EXIT-01.

## MVP-EXIT Program Gate Decision 2026-05-23: PR #2251 evidence intake

- Candidate: PR #2251 `codex/current-project-risk-analysis-issues@771151d8dfcc3828ad6686418c38338e37d9a5a2`
- Decision date: 2026-05-23
- Reviewer: Codex
- Input sources:
  - PRODUCT-QA-01 gate record: `Productization Gate Record 2026-05-23: PR #2251 ready-for-review`
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated in this intake; no runtime env contract change in the final PR #2251 update.

### Decision

- Final: **Conditional Go for PR readiness / No-Go for full release shipment**
- Reason summary: PR #2251 has passing CI and candidate-specific planning/productization evidence, but full product shipment still requires release-candidate evidence across env contract gates, value gates, and remaining Draft product/UX issues.
- Escalation route: keep PR #2251 reviewable; do not treat it as final release approval. Re-run Program Gate after merge or release-candidate cut.

### Conditional controls

- Remaining risks:
  - E1..E3 environment contract evidence is not part of this final PR #2251 intake.
  - `PRODUCT-VALUE-*` and `PRODUCT-UX-*` Draft issues remain outside full release Go.
  - RTK adoption is local Codex DX evidence only and must not be mixed into application runtime readiness.
- Owner: Codex for evidence maintenance; System Owner / QA Lead required for release shipment decision.
- Due date: next release-candidate gate review.
- Re-decision date: when PR #2251 is merged or superseded, or when a release candidate is cut from `main`.

## MVP-EXIT Program Gate Decision 2026-05-23: PR #2253 draft-gate intake

- Candidate: PR #2253 `codex/product-value-ux-open-readiness@92ffa3320480c77d5b39027c4eb620dbbf4b8557`
- Decision date: 2026-05-23
- Reviewer: Codex
- Input sources:
  - PRODUCT-QA-01 gate record: `Productization Gate Record 2026-05-23: PR #2253 draft-gate readiness`
  - Draft child issue assessments:
    - `PRODUCT-VALUE-01..03`
    - `PRODUCT-UX-01..04`
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated in this intake; no runtime env contract change in PR #2253.

### Decision

- Final: **Conditional Go for planning-readiness evidence / No-Go for full release shipment**
- Reason summary: PR #2253 improves Program Gate traceability by recording why the seven product value and UX issues remain Draft, but the actual release decision still lacks owners, fixed E2E routes, and candidate-level value/UX evidence.
- Escalation route: keep PR #2253 reviewable as planning evidence. Do not count it as final release approval. Re-run Program Gate when child issue owners and evidence routes are fixed, or when a release candidate is cut.

### Conditional controls

- Remaining risks:
  - `PRODUCT-VALUE-01..03` still depend on ADR-0032 finalization, owner assignment, and value-specific E2E evidence.
  - `PRODUCT-UX-01..04` still depend on owner assignment and representative mouse/keyboard/viewport evidence.
  - E1..E3 environment contract evidence is not part of this PR #2253 intake.
  - SafeMode/share-export behavior is unchanged in this PR and still requires release-candidate smoke evidence before shipment.
- Owner: Codex for evidence maintenance; Productization Program Owner / QA Lead required for release shipment decision.
- Due date: next child-issue Open readiness review.
- Re-decision date: when child issue owners and evidence routes are fixed, or when a release candidate is cut from `main`.

## MVP-EXIT Program Gate Decision 2026-05-24: DATA-MAINT recovery evidence intake

- Candidate:
  - PR #2259 `codex/data-maint-sqlite-recovery-exercise@609a44576462e99e3c8031b9855beb04b098ee7c`
  - PR #2260 `codex/data-maint-postgres-recovery-docs@9c6abd0221971a90df676024c5eea29c7722a690`
  - PR #2261 `codex/data-maint-results-gate-sync@6ff535620ce461eee783fd445717f3b53f9d5154`
- Decision date: 2026-05-24
- Reviewer: Codex
- Input sources:
  - DATA-MAINT-02 SQLite recovery exercise: representative backend recovery evidence for `documents` and `merge_decision_logs`.
  - DATA-MAINT-02 PostgreSQL rehearsal boundary: PostgreSQL compose exercise is documented as not run locally because Docker is unavailable, with a restart condition retained.
  - DATA-MAINT-01 parent handoff: PR #2261 returns the recovery evidence to the parent issue without changing destructive admin-operation Stop conditions.
  - PRODUCT-QA-01 gate record: not updated in this slice; this intake only connects data-maintenance evidence to the Program Gate.
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated; no runtime environment variable or deployment contract changed.

### Decision

- Final: **Conditional Go for data-maintenance evidence / No-Go for full release shipment**
- Reason summary: The recovery evidence now covers a representative SQLite restore path and records the PostgreSQL real-environment rehearsal as an explicit remaining condition. This improves operational readiness traceability, but it is not sufficient for product shipment because the PostgreSQL compose exercise, release-candidate gate record, and major user-operation E2E evidence remain open.
- Escalation route: keep DATA-MAINT recovery work reviewable and mergeable as planning/verification evidence. Re-run Program Gate when the PostgreSQL rehearsal is completed or when a release candidate is cut from `main`.

### Conditional controls

- Remaining risks:
  - PostgreSQL restore has not been exercised in a real compose environment; DATA-MAINT-02 keeps the Docker restart condition.
  - Destructive admin operations, owner transfer, archive/delete policy, and support access to document bodies remain Stop conditions and require separate issue/ADR approval before implementation.
  - Full release shipment still requires candidate-level PRODUCT-QA gate evidence, especially SafeMode/share-export smoke coverage and representative mouse/keyboard user-operation E2E.
- Owner: Codex for evidence maintenance; Platform Operator / System Owner required for recovery rehearsal approval.
- Due date: next DATA-MAINT-02 restart window with Docker or equivalent PostgreSQL environment available.
- Re-decision date: after PostgreSQL compose recovery rehearsal, or when a release candidate is cut from `main`.

## MVP-EXIT Program Gate Decision 2026-05-25: DATA-MAINT executable recovery evidence refresh

- Candidate:
  - PR #2267 `codex/data-maint-02-recovery-exercise@f230ea6b9d86f46478c029290175d9f4e7d9cb74`
- Decision date: 2026-05-25
- Reviewer: Codex
- Input sources:
  - DATA-MAINT-02 executable recovery exercise: backend integration test for SQLite backup, restored DB readback, `Document.version`, card review flags, embedded merge suggestion decision, `merge_decision_logs` group/snapshot order, and SafeMode export block.
  - PostgreSQL representative rehearsal: WSL2 temporary PostgreSQL 16.14, `alembic upgrade head`, reusable `data_maintenance_pg_rehearsal.py`, `pg_dump -Fc`, `pg_restore` to `kj_atlas_restore`, and restored SQL readback all passed.
  - DATA-MAINT-01 handoff: PR #2267 records the parent handoff directly, so older PR #2261 is no longer the preferred parent evidence path.
  - PRODUCT-QA-01 gate record: PR #2267 adds the DATA-MAINT-02 recovery exercise gate record directly, so older PR #2263 should be closed or rebased if #2267 is merged first.
  - PROJECT-GOV-01 checkpoint: PR #2265 classifies #2267 as the primary canonical DATA-MAINT recovery evidence and #2261/#2263 as duplicate/superseded candidates after #2267.
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated; no runtime environment variable or deployment contract changed.

### Decision

- Final: **Go for representative data-maintenance recovery evidence / No-Go for full release shipment**
- Reason summary: PR #2267 now includes executable SQLite evidence, temporary PostgreSQL dump/restore rehearsal evidence, restored SQL readback, and CI success. Full release shipment remains No-Go because final release-candidate QA, representative user-operation E2E, and value/UX evidence are still open.
- Escalation route: prefer #2267 as the canonical DATA-MAINT recovery evidence for future Program Gate intake. Refresh or close older recovery-evidence PRs that duplicate #2267 before merging them.

### Conditional controls

- Remaining risks:
  - MVP-EXIT must not treat representative data recovery evidence as full release readiness. The release candidate still needs `PRODUCT-QA-01` final gate evidence and representative user-operation E2E.
  - Organization-specific backup retention, encryption, storage location, approval, RTO/RPO, and duty separation remain outside this decision and must not be fixed by implication.
  - Destructive admin operations, owner transfer, archive/delete policy, and support access to document bodies remain outside this decision and still require separate issue/ADR approval.
- Owner: Codex for evidence maintenance; Platform Operator / System Owner required only for organization-specific backup policy approval.
- Due date: next MVP-EXIT release-candidate Program Gate.
- Re-decision date: after #2267 is merged or rejected, or when a release candidate is cut from `main`.

## MVP-EXIT Program Gate Decision 2026-05-26: evidence lane merge resolution

- Candidate: `origin/main@1a8ecd575e830f5fa51e537b75875840c69c7096`
- Decision date: 2026-05-26
- Reviewer: Codex
- Input sources:
  - PROJECT-GOV-01 convergence checkpoint: #2261..#2267 are merged; current open PR set contains #2270 only.
  - PROJECT-BASELINE-01 governance-only delta: triage stopper none, `active_issues=47 / ready=18 / blocked=29`.
  - PRODUCT-QA-01 gate records: DATA-MAINT recovery evidence and representative user-operation evidence are recorded, but full release-candidate approval is still not granted.
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated in this delta; no runtime environment variable or deployment contract changed.

### Decision

- Final: **Go for evidence-lane convergence / No-Go for full release shipment**
- Reason summary: The previously open DATA/MVP/QA/OPS evidence lane has merged into `main`, removing the immediate branch-convergence risk. This does not equal a product release approval because the final release candidate still needs current SafeMode/share-export smoke evidence, representative user-operation E2E, value/UX evidence, and E1..E3 environment contract results.
- Escalation route: continue with product-release evidence collection through `PRODUCT-QA-01`. Treat #2270 as a DX-only rtk runbook PR and do not count it as application readiness evidence.

### Conditional controls

- Remaining risks:
  - Release-candidate Program Gate evidence has not been assembled for `origin/main@1a8ecd575e830f5fa51e537b75875840c69c7096`.
  - `PRODUCT-VALUE-*` and `PRODUCT-UX-*` child issues remain Draft and still need owner/evidence routes before full shipment.
  - Environment contract gates E1..E3 were not re-run in this convergence delta.
- Owner: Codex for evidence maintenance; Productization Program Owner / QA Lead required for shipment decision.
- Due date: next release-candidate Program Gate.
- Re-decision date: when a release candidate is cut from `main` or after the next material product/runtime change.

## MVP-EXIT Program Gate Decision 2026-05-26: release-candidate evidence refresh

- Candidate: `origin/main@1a8ecd575e830f5fa51e537b75875840c69c7096`
- Decision date: 2026-05-26
- Reviewer: Codex
- Input sources:
  - PRODUCT-QA-01 gate record: `Productization Gate Record 2026-05-26: release-candidate evidence refresh`
  - PROJECT-BASELINE-01 record: current main evidence refresh for planning, frontend, backend, browser E2E, build, and Compose config.
  - ENV-CONFIG-DRIFT-01 result: settings tests, public-key scan, production build, and WSL2 Compose config passed; full running Compose stack was not started.

### Decision

- Final: **Conditional Go for current release-candidate evidence / No-Go for full release shipment**
- Reason summary: The current `main` now has fresh evidence for planning metadata, frontend typecheck, full Vitest, backend pytest, production build, full Playwright browser E2E, SafeMode/share-export tested scope, and Compose config rendering. Full shipment remains No-Go because the product value and UX child issues still need assigned owners and explicit release-candidate evidence routes, and a full running Compose stack was not started in this run.
- Escalation route: treat this as a strong release-candidate evidence refresh, not a final shipment approval. Continue by opening or assigning the `PRODUCT-VALUE-*` and `PRODUCT-UX-*` Draft gates, then rerun Program Gate with owner and evidence route decisions.

### Conditional controls

- Remaining risks:
  - GitHub Actions CI run #9141 was blocked before checkout by a GitHub 403 account/repository operation error, but subsequent run #9143 passed checkout and all jobs. Treat `PROJECT-CI-01` as a closed transient incident unless the failure recurs.
  - `PRODUCT-UX-01..04` now have owner/evidence routes and can be executed as Open internal issues, but their implementation and release-candidate evidence are not complete.
  - `PRODUCT-VALUE-01..03` remain Draft because `ADR-0032` is still Proposed and value-specific fixtures/evidence locations are not fixed.
  - Compose was rendered successfully through WSL2, but full service startup was not executed in this evidence refresh.
  - Support diagnostics bundle policy remains a follow-up boundary and must not be implied by the passing recovery guidance E2E.
- Owner: Codex for evidence maintenance; Productization Program Owner / QA Lead required for final shipment decision.
- Due date: next product value/UX gate review.
- Re-decision date: after child issue owner/evidence routes are fixed, or after a material runtime/product change reaches `main`.

## MVP-EXIT Program Gate Decision 2026-05-27: product UX/value gate refinement

- Candidate: local branch `codex/project-gov-20260526-convergence@14bb45937243fb396e00eb597c3580625e4fbaab`
- Decision date: 2026-05-27
- Reviewer: Codex
- Input sources:
  - `PRODUCT-UX-01..04`: moved from Draft to Open with Codex stewardship, RACI, and fixed representative E2E/documentation evidence routes.
  - `PRODUCT-VALUE-01..03`: owner stewardship fixed, but Status remains Draft pending `ADR-0032` acceptance or explicit Productization Program Owner approval.
  - PRODUCT-QA-01 triage after local updates: `active_issues=47 / ready=22 / blocked=25 / actionable_adrs=1 / stopper=none`.
  - PR #2271 metadata: remote head still `5fd1a304` because local git push is blocked by credential-manager authentication; PR body records the local follow-up commits.

### Decision

- Final: **Conditional Go for product UX planning execution / No-Go for full release shipment**
- Reason summary: Product UX issues now have enough responsibility and evidence routing to proceed as executable internal issues. Product value gates remain intentionally Draft because accepting the value model would change the release decision basis and still needs ADR-0032 approval or an explicit program-owner decision.
- Escalation route: execute `PRODUCT-UX-01..04` evidence work through focused implementation/E2E slices. Keep `PRODUCT-VALUE-01..03` in Draft until `ADR-0032` is accepted or explicitly approved as a provisional value-gate baseline.

### Conditional controls

- Remaining risks:
  - UX Open status does not imply UI implementation completion, public documentation screenshot completion, or shipment approval.
  - Product value gates remain No-Go for full shipment until the first meaningful map, ambiguity/evidence workflow, and reviewable package fixtures are fixed.
  - Local commits must still be pushed to PR #2271 or recreated through another approved GitHub write path before merge.
- Owner: Codex for evidence maintenance; Productization Program Owner required for ADR-0032/value-gate approval.
- Due date: next value-gate approval review.
- Re-decision date: after `ADR-0032` status changes, after UX evidence PRs land, or after the local branch is successfully pushed.

## MVP-EXIT Program Gate Decision 2026-05-31: latest main evidence intake

- Candidate: `origin/main@b31dcbeaa05d30f9bf1f9f651d44a06166c51100`
- Related PR: draft PR #2278 `codex/project-baseline-20260531@eb045b7615e65434f3f0f6b7a43dc5438d4a704b`
- Decision date: 2026-05-31
- Reviewer: Codex
- Input sources:
  - PRODUCT-QA-01 gate record: `Productization Gate Record 2026-05-31: latest main evidence intake`.
  - PROJECT-BASELINE-01 preserved local full-evidence branch: `codex/project-baseline-20260531-full-local@f703bd24e88787bc9d983374230c0d776b23c789`.
  - PR #2278: draft PR containing the narrow CE3 Playwright locator fix only.
  - ENV-CONFIG-DRIFT-01 result: not re-evaluated in this intake; no runtime environment variable or deployment contract changed.

### Decision

- Final: **Conditional Go for latest-main evidence intake / No-Go for full release shipment**
- Reason summary: The latest-main baseline has strong local regression evidence across planning validation, frontend typecheck, Vitest, backend pytest, production build, and Playwright after the CE3 Japanese locator fix. This is still not a final product release approval because the evidence is partly local/preserved, PR #2278 is intentionally narrow and draft, the product UX evidence work is not complete, `PRODUCT-VALUE-01..03` remain Draft pending `ADR-0032`, and a full running Compose stack was not started.
- Escalation route: keep #2278 reviewable as a small E2E-locator correction. Continue the MVP exit program through product UX execution, value-model approval, and a full release-candidate gate rather than treating the preserved local baseline as shipment approval.

### Conditional controls

- Remaining risks:
  - The full PROJECT-BASELINE closeout memo is preserved locally but is not part of the remote #2278 branch.
  - Release-candidate screenshots and representative mouse/keyboard UX evidence are still required for `PRODUCT-UX-01..04`.
  - `PRODUCT-VALUE-01..03` remain Draft until `ADR-0032` is accepted or Productization Program Owner approval explicitly authorizes provisional value-gate execution.
  - Full Compose service startup was not executed in this intake; environment contract gates remain Conditional Go.
  - Public documentation was not republished as part of this gate decision.
- Owner: Codex for evidence maintenance; Productization Program Owner / QA Lead required for final shipment decision.
- Due date: next product UX/value gate review.
- Re-decision date: after #2278 is merged or rejected, after `ADR-0032` status changes, after UX evidence PRs land, or after a full running Compose rehearsal is completed.
