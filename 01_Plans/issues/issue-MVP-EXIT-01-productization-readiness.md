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
- 実行コマンドログ（成功/失敗/未実施理由）
- 手動smoke観測（viewport含む）
- 未解決リスク台帳（owner/due date/escalation）

### Escalation/approval responsibility

- QA Lead: 判定取りまとめ・証跡整合確認
- System Owner: Conditional/Failの最終判断
- Platform Operator: 再現環境・実行ログ保証
- Security Officer: SafeMode/share-export/public exposure関連の最終承認
