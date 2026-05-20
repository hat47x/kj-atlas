# Issue Draft: PRODUCT-QA-01 製品化リリース準備の品質ゲート定義

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: TBD
- Scope: `01_Plans/`, `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/`
- Related Backlog: `PRODUCT-QA-01`
- Related ADR/Spec: `01_Plans/issues/issue-MVP-EXIT-01-productization-readiness.md`, `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `01_Plans/adr/ADR-0031-productization-screen-information-architecture.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-QA-01
- RequirementStatement: MVP脱却時に必要な品質ゲートを、UI/UX、i18n、SafeMode、E2E、文書、リリース、診断の観点で定義し、リリース判断に使える状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=製品化候補のPRまたはリリース候補がある / 操作=品質ゲートを順に実行し、Go/No-Goを判定する / 期待結果=不足している検証、文書、画面設計課題が個別issueへ戻される / 除外=すべての将来機能の完了。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / import-sanitize / public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed (Open化可)
- DecisionQueueRef（未確定時の参照先）: `MVP-EXIT-01`

## 1) 課題 / Problem statement

- MVP脱却には、単一のテスト合格だけでなく、画面、文書、安全境界、公開範囲、運用、診断を横断したGo/No-Go基準が必要である。
- 現行のissue群は個別課題を扱っているが、製品化リリース候補を判定する横断チェックリストが未整備である。
- 一般公開向け文書、開発者向けE2E、内部issue/ADR、実装テストの境界をそろえないと、公開時に説明と実装がずれる。

## 2) 背景 / Context

- `MVP-EXIT-01` は製品化準備の親issueとして存在する。
- `QA-E2E-USE-01` は実利用ケースのE2E拡充を定義している。
- `ADR-0031` は製品化UIの画面情報設計を提案している。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 製品化の価値は、利用者が継続的に安心して使える品質で初めて実現する。
- 安全（THREAT_MODEL / SafeMode）: SafeMode、取り込み、共有、公開文書はリリース前に必ず照合する必要がある。
- 企業・行政要件（enterprise_architecture）: 組織導入では検証記録、障害時対応、公開範囲説明が求められる。
- 後方互換（schemas）: リリース判定では既存データの読み込みと旧導線の到達性を確認する。

## 3.1 依存関係 / Dependencies

- 直前依存: ADR-0031 の5領域定義。
- 連携先: PRODUCT-UX/QA 系issue（本ファイル内 Related ADR/Spec を参照）。
- ブロッカー条件: 上位ADRに矛盾がある場合は実装を開始しない。

## 3.2 非目標 / Non-goals（運用明示）

- 本issueの非目標は「4) 提案する解決策」の非目標節を正本とする。
- 非目標に該当する変更要求は、別issueまたはADRへ切り出す。

## 3.3 検証レベル / Verification level

- 本issueの検証レベルは Requirement meta I/F の `VerificationLevel` を正本とする。
- `e2e` 指定issueはPlaywright等の操作証跡を必須とし、`integration` 指定issueは横断ゲート記録を必須とする。



## 3.4 Stream J 依存切断メモ（2026-05-17）

- 本Issueは「ゲート定義」のみに限定し、UI/Backend実装チケットの完了待ちは **No-Go判定時の戻し先指定** のみで扱う。
- `PRODUCT-UX-*` および `PRODUCT-OPS-01` との関係は「参照依存」に統一し、同時完了を要求しない。
- Open化時点で必要なのは、各ゲートの判定手順と証跡形式があること（実装完了ではない）。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 製品化リリース準備チェックリスト。
  - CIまたは手動検証で確認するコマンド一覧。
  - E2Eユーザージャーニーと公開文書の照合。
  - SafeMode、share/export、import sanitize、public exposureのGo/No-Go基準。
- 変更の最小単位:
  - 既存issue群を参照するリリースゲートを `01_Plans` に定義する。
  - 必須ゲートと推奨ゲートを分ける。
- 非目標:
  - すべての品質改善を本Issueで実装すること。
  - 将来の認証・認可・共同編集をリリース必須にすること。

## 5) 受入条件 / Acceptance criteria

- [ ] 製品化リリース候補のGo/No-Go基準が、UI/UX、i18n、SafeMode、import/export、E2E、文書、診断で定義されている。
- [ ] 各ゲートに具体コマンド、手動確認、証跡の残し方がある。
- [ ] 未達の場合に戻す個別issueまたはADRが分かる。
- [ ] 公開文書と実装画面のスクリーンショットが一致していることを確認できる。
- [ ] 環境変数、SafeMode、共有、取り込み、公開範囲の説明が設計文書と矛盾しない。
- [ ] 既存データとレガシー導線の互換性確認が含まれる。

### 5.1 初期品質ゲート案

| Gate | 判定対象 | 必須/推奨 | Go条件 | No-Go条件 | 主な証跡 |
| --- | --- | --- | --- | --- | --- |
| G0 計画整合 | issue / ADR / 依存関係 | 必須 | 製品化対象が個別issueへ分かれ、ADR判断と実装作業が混在していない | 判断が必要な設計変更をissue本文だけで確定している | `validate_active_issue_memos.py`, `triage_actionable_plans.py` |
| G1 安全既定 | SafeMode / 取り込み / 共有 | 必須 | SafeMode既定ON、共有前確認、import sanitize が画面・文書・テストで一致 | SafeMode OFFや未レビュー情報共有を既定導線にしている | SharePanel test, acceptance screenshot |
| G2 主要操作 | 初回導線 / 選択 / 保存 / 表示 / 共有 | 必須 | マウスとキーボードで主要操作へ到達し、結果と戻り方が分かる | 選択対象の詳細が見えない、パネルを閉じられない、主要操作が見切れる | Playwright操作ログ, screenshots |
| G3 日本語UI | i18n / 表記 / 用語 | 必須 | 一般利用者向けUIに未翻訳・不自然な主要ラベルが残らない | 主要ボタンや警告に英語、内部略語、実装都合の語が残る | i18n tests, `rg` |
| G4 画面耐性 | 小画面 / 大きな文書 / 低速環境 | 必須 | 代表viewportで見切れず、待機・失敗・復帰導線が分かる | 共有前確認やSafeMode状態が見切れる | viewport matrix, diagnostics check |
| G5 公開文書 | public index / screenshots / link | 必須 | 公開文書が使い方に集中し、内部管理情報を含まない | 公開本文にプロジェクト管理・内部issue/ADR導線が混入する | public-doc forbidden-term search |
| G6 診断とサポート | エラー表示 / 診断 / SUPPORT | 推奨 | 保存失敗、API未接続、取り込み失敗時に次アクションが分かる | 利用者が機微情報を含む診断情報を共有しやすい | diagnostics docs, representative failure notes |
| G7 ビルドと回帰 | frontend / backend / docs | 必須 | typecheck、主要unit、E2Eまたは代替証跡、文書整形が通る | 既知の必須テスト失敗を未分類のまま残す | CI log, local command log |

### 5.2 価値実現ゲート

| Value Gate | 判定対象 | Go条件 | No-Go条件 | 戻し先issue |
| --- | --- | --- | --- | --- |
| V0/V1 初回価値実感 | 開始、サンプル、短いメモ、カード化、保留点 | 初回利用者が最初の意味ある配置へ到達できる | 文書を開けても、カードや保留点を作る次操作が分からない | `PRODUCT-VALUE-01` |
| V2 保留・違和感の作業化 | Hold / Critique / Evidence / Contradiction | 未確定、違和感、根拠不足を失敗ではなく作業状態として残せる | 未確定情報が削除、非表示、または確定情報のように扱われる | `PRODUCT-VALUE-02` |
| V3 人間レビュー中心 | proposal-only / reviewState / patch + approval | AI提案を比較、部分採用、保留、破棄できる | auto-apply、AIによる `human_reviewed` 昇格、直接確定がある | `PRODUCT-VALUE-02`, `CE-*` |
| V4 レビュー可能な成果物 | Narrative / Review Pack / SafeMode / source trace | 確定点、保留点、未レビュー情報、根拠への戻り方が共有物で分かる | 共有物が読みやすいだけで、根拠や未確定点へ戻れない | `PRODUCT-VALUE-03` |
| 横断 LLM任意性 | `KJ_ATLAS_LLM_PROVIDER=none` | 既定構成でも開始、外在化、構造化、共有前確認の主要価値が成立する | LLM接続がないと基本価値を体験できない | `PRODUCT-VALUE-01`, `PRODUCT-VALUE-02` |

### 5.3 Go/No-Go記録テンプレート

```md
## Productization Gate Record

- Candidate: <PR / release / commit>
- Date (JST): YYYY-MM-DD
- Reviewer:
- Scope:
- Gates:
  - G0 計画整合: Go / No-Go / N/A
  - G1 安全既定: Go / No-Go / N/A
  - G2 主要操作: Go / No-Go / N/A
  - G3 日本語UI: Go / No-Go / N/A
  - G4 画面耐性: Go / No-Go / N/A
  - G5 公開文書: Go / No-Go / N/A
  - G6 診断とサポート: Go / No-Go / N/A
  - G7 ビルドと回帰: Go / No-Go / N/A
- Value gates:
  - V0/V1 初回価値実感: Go / No-Go / N/A
  - V2 保留・違和感の作業化: Go / No-Go / N/A
  - V3 人間レビュー中心: Go / No-Go / N/A
  - V4 レビュー可能な成果物: Go / No-Go / N/A
  - 横断 LLM任意性: Go / No-Go / N/A
- Required follow-up issue:
- Decision: Go / Conditional Go / No-Go
```

## 6) 実装タスク分解 / Task breakdown

- [x] T1 製品化ゲートのカテゴリと必須/推奨を定義する。
- [x] T2 既存issue/ADRをゲートに紐付ける。
- [x] T3 自動テスト、手動Playwright確認、文書チェックの実行手順を定義する。
- [x] T4 Go/No-Go判定の記録形式を定義する。
- [x] T5 リリース前に不足した観点を個別issueへ戻す運用を決める。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run src/i18n/ui_hardcode_guard.test.ts src/ui/i18n_equivalence.integration.test.ts`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
  - `git diff --check`
- 期待結果:
  - 製品化リリース候補の品質ゲートを実行でき、未達項目が個別issueへ追跡できる。
- 未実施時の理由・代替検証:
  - 全E2Eが環境依存で実行できない場合は、対象scenario、失敗分類、再開条件を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 既存CI合格のみをリリース判定にする。文書・操作性・公開範囲のずれを拾えない。
- 代替案B: すべての将来機能完了を製品化条件にする。範囲が広すぎてMVP脱却の現実的な判断ができない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 品質ゲートが重すぎて、通常の改善PRが停滞する。
- 影響範囲: CI、E2E、リリース手順、公開文書。
- ロールバック手順: ゲートを必須/推奨へ再分類し、リリース阻害になっている項目を個別issueへ分離する。

## 10) Additional context

- ADR化が必要になる条件: リリース判定権限、公開配布方式、サポート範囲、公開配布のGo/No-Goをプロジェクト方針として固定する場合。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。

## 16) Stream E update (2026-05-19): Release/Quality/Env gate normalization

### Phase 1: Read
- `PRODUCT-QA-01` / `MVP-EXIT-01` / `ENV-CONFIG-DRIFT-01` の受入条件、`GoNoGoGate`、`VerificationLevel` を比較し、**integration レベルの単一ゲート定義**に統一した。
- 判定の曖昧語（「必要に応じて」「十分」）は、実行証跡（command log / gate record / follow-up issue）必須化で解消した。

### Phase 2: ゲート定義（固定）
- Release 判定は `G0..G7 + Value gates` を必須判定面として維持。
- Env 判定は `E1 Public key contract` / `E2 Runtime validation` / `E3 Compose consistency` を追加トレースし、No-Go時に `ENV-CONFIG-DRIFT-01` へ戻す。
- Conditional Go は「重大欠陥なし + 是正期限つきフォローアップ issue 発行済み」のときのみ許可。

### Phase 3: 検証設計
- 最低実施セット: issue metadata validator / frontend typecheck / backend settings tests / compose config / docs diff check。
- 失敗時判定基準:
  - **Blocker**: SafeMode境界破壊、公開契約キー不一致、主要導線E2E不能。
  - **Major**: UI主要操作の到達不能、公開文書と実装不一致、i18n重大欠落。
  - **Minor**: リリース阻害でない文言・体裁差分（follow-upで是正）。

### Phase 4: 監査テンプレ標準
- Gate record の必須項目を以下で固定:
  - Candidate / Date / Reviewer / Scope
  - Gate result (Go/No-Go/N/A)
  - Evidence links (command logs, screenshots, test report)
  - Escalation route (issue id, due date, owner)
  - Final decision (Go / Conditional Go / No-Go)

### Phase 5: 反映結果
- Stream E として本 issue を **release-quality ゲート正本**として再確認。
- Env契約逸脱の戻し先を `issue-ENV-CONFIG-DRIFT-01`、製品化親判断を `issue-MVP-EXIT-01` に固定。

### Fail-safe
- 判定曖昧さは本更新で解消済み。未解消論点は governance queue（ADR起票条件）へ送る。

## 17) Stream F update (2026-05-19): Release Readiness QA execution package

### Phase 1: Read（quality gate定義抽出）
- 判定対象は `G0..G7 + Value gates + E1..E3` とし、`GoNoGoGate=Required` / `VerificationLevel=integration` を固定する。
- `ADR-0019` と `frontend/docs/e2e_testing.md` に合わせ、証跡を「自動テスト結果 + 手動スモーク観測 + フォローアップissue」に分離する。

### Phase 2: Plan（Go/No-Go基準ドラフト）
- **Go**: Blocker=0 かつ Major=0。Minor は期限付き follow-up issue で許容。
- **Conditional Go**: Blocker=0 かつ Major>=1 だが、回避策・owner・due date・再判定日が同時に確定。
- **No-Go**: Blocker>=1、または証跡不備（コマンド結果/判定ログ欠落）、または SafeMode/share-export 境界不整合。

### Phase 3: Execute（受入条件反映）
- 受入条件に「判定結果を Gate Record に残す」「Conditional Go は是正期限と再判定日を必須化」「No-Go の戻し先 issue を明示」を追加適用する。

### Phase 4: Verify（測定可能性/再現性チェック）
- 測定可能性: 各ゲートに `result`, `evidence`, `owner`, `due` が存在すること。
- 再現性: 同一 candidate で同一コマンド集合を再実行した際、判定の差分理由を説明できること。
- 証跡最小セット:
  - issue metadata validator
  - frontend typecheck + regression guards
  - Playwright E2E（mock または実環境）
  - docs diff check / compose config check

### Phase 5: Proceed（リリース判定テンプレート）
```md
## Productization Release Decision Record
- Candidate:
- Decision date (YYYY-MM-DD):
- Reviewer:
- Scope:

### Gate Summary
- G0..G7:
- Value gates:
- E1..E3:
- Final: Go | Conditional Go | No-Go

### Evidence
- Command log links:
- Test report links:
- Screenshot links (if UI impact):

### Follow-ups
- Blocking issues:
- Conditional issues (owner / due):
- Re-decision date:

### Safety Confirmation
- SafeMode default ON: pass/fail
- share/export fail-closed: pass/fail
- public exposure checks: pass/fail
```

## 18) Stream E execution (2026-05-19): Product QA Gate 専任

### Phase1 Read（上流整合の確認）
- 参照正本を `ADR-0019` / `04_Documentation/acceptance_check.md` / `03_Implement/frontend/docs/e2e_testing.md` に固定し、公開利用者向け手動確認と開発者向け自動E2Eの境界を再確認した。
- 本Issueの `GoNoGoGate=Required` / `VerificationLevel=integration` を **P0品質ゲートの最上位条件** として維持し、Draft課題のOpen化条件をこのゲートに従属させる。

## 19) Stream F update (2026-05-20): Unified release readiness gate model

### Phase 1 Read（重複・矛盾抽出）
- `MVP-EXIT-01` と本Issueの判定条件を比較し、判定語彙・閾値・証跡要件のズレを抽出した。
- 矛盾点:
  - 判定カテゴリが「Gate一覧」中心と「Blocker/Critical/Major」中心で分離していた。
  - Conditional Go の必須条件（owner/due/re-decision date）が本文中で強度不一致だった。
  - 他ストリーム成果の受入時に必要な入力項目がテンプレート化されていなかった。

### Phase 2 Plan（共通ゲートモデル定義）
- `PRODUCT-QA-01` を Release Readiness 判定の正本とし、判定面を以下4カテゴリに統一する。
  - **Quality**: G2/G3/G4/G7 + Value gates（V0..V4）
  - **Security**: G1 + public exposure + SafeMode/share-export/import-sanitize整合
  - **Operability**: G6 + E1..E3（環境契約/実行整合）
  - **Documentation**: G0/G5 + 公開導線整合（`README.md`/`ROADMAP.md`/`public_index.md`）
- 判定式（必須）を固定:
  - Go: Blocker=0 かつ Critical=0 かつ Major=0 かつ 必須ゲート完了 かつ 証跡完備
  - Conditional Go: Blocker=0 かつ Critical=0 かつ Major>=1 かつ 是正計画（owner/due/re-decision date）登録済み
  - No-Go: Blocker>=1 または Critical>=1 または 必須証跡欠落

### Phase 3 Execute（受入条件テンプレ整備）
- 他ストリーム成果受入の最小テンプレートを追加し、判定入力を固定する。

```md
## Stream Deliverable Intake Template (PRODUCT-QA-01)
- Stream ID:
- Deliverable scope:
- Mapped gate category: Quality | Security | Operability | Documentation
- Target gates: (e.g., G3, V2, E2)
- Evidence bundle:
  - Command log:
  - Test report:
  - Screenshot / capture (UI影響時):
  - Docs diff / spec sync:
- Risk classification: Blocker | Critical | Major | Minor
- Follow-up requirement (if not Go):
  - issue id:
  - owner:
  - due:
  - re-decision date:
- Intake decision: Accepted | Accepted with condition | Rejected
```

### Phase 4 Verify（AC/DoD照合）
- AC照合観点を次で固定:
  1. 判定カテゴリが4分類へ正規化されている。
  2. Go/Conditional/No-Go 判定式が測定可能（数値・有無判定）である。
  3. 証跡要件が candidate 単位で追跡可能である。
  4. 未達時の戻し先 issue と再判定日が必須入力である。
- DoD観点:
  - `GoNoGoGate=Required` と `VerificationLevel=integration` を維持し、E2E未実施時の代替記録方針は `ADR-0019` 準拠。

### Phase 5 Proceed（Program受け渡し）
- Program親Issue（`MVP-EXIT-01`）への受け渡し入力は、次を必須化する。
  - Productization Gate Record（最新 candidate）
  - Stream Deliverable Intake Template（該当ストリーム分）
  - Conditional/No-Go の未解決一覧（owner/due/re-decision date）

### Phase2 Gate定義（P0固定）
- **P0 Gate-0（Evidence Completeness）**: Gate Record に `candidate/date/reviewer/scope/gate result/evidence/follow-up` が欠ける場合は即 No-Go。
- **P0 Gate-1（Safety Boundary）**: SafeMode既定ON、share/export前確認、import sanitize の3点が文書・操作・証跡で一致しない場合は No-Go。
- **P0 Gate-2（Execution Route）**: `ADR-0019` の Compose / SQLite代替 / 例外記録 のいずれかを事前固定し、未固定は No-Go。
- **P0 Gate-3（Recovery Routing）**: No-Go時に戻し先issue（例: `QA-*`, `MVP-EXIT-01`, `ENV-CONFIG-DRIFT-01`）と再判定日が無い場合は No-Go。

### Phase3 E2E/Unit境界定義（Draft Open化条件）
Draft QA issue（`issue-QA-*`）は、次の **Open化条件（AC/DoD/証拠）** を満たすまで Draft 維持とする。

- **AC-O1: Scope Boundary**
  - E2Eで確認する価値境界（UI導線/SafeMode/share-export/i18nのどれか）を1行で明示。
  - unit/integrationで担保する契約（変換/バリデーション/i18n guard など）を1行で明示。
- **AC-O2: DoD Boundary**
  - 完了条件に `pass条件` と `保留条件` を併記し、Execution: Hold解除条件を1行で判定可能にする。
- **AC-O3: Evidence Contract**
  - 最低証跡として `実行コマンド` / `結果` / `失敗分類(Blocker/Major/Minor)` / `follow-up issue` を持つ。
- **AC-O4: Route Selection**
  - Compose/SQLite/例外記録のいずれで検証するかを事前選択する。

DoDテンプレ（Draft→Open）
- DoD-O1: AC-O1〜O4が issue 本文に記載済み。
- DoD-O2: metadata validator で構文不整合がない。
- DoD-O3: No-Go時の戻し先と再開条件が 1:1 対応。

### Phase4 Verify（運用検証）
- Verify command set（最小）
  - `python3 01_Plans/issues/validate_active_issue_memos.py`
  - `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|Execution: Hold|Pending" 01_Plans/issues/issue-QA-*.md`
  - `git diff --check`
- 判定
  - Open化可能: AC/DoD/証跡が充足。
  - 追加判断必要: 証跡または実行経路固定が不足。
  - 保留継続: Blocker未解消、または安全境界が未確認。


## 18) Stream F update (2026-05-20): Gate Contract v1.0（固定）

### 18.1 Gate inventory（必須/推奨/将来）

- **必須（Release Blocking）**: G0, G1, G2, G3, G4, G5, G7, Value V0/V1, V2, V3, V4, 横断LLM任意性, E1, E2, E3
- **推奨（Conditional Go許容）**: G6（診断・サポート導線）
- **将来（MVP-EXIT以降）**: 長時間耐久、大規模データ負荷、企業専用運用プロファイルの深掘り

### 18.2 Severity contract（停止条件）

- **Blocker**: SafeMode/share-export/import-sanitize/public exposure 境界違反、証跡欠落、主要導線E2E不能。→ **即 No-Go**
- **Critical**: データ喪失リスク、保存復元失敗、公開文書と挙動の重大不一致。→ **No-Go（例外なし）**
- **Major**: 主要導線の到達不能/誤誘導、i18n主要ラベル欠落、操作復帰不能。→ **Conditional Go まで**（期限・Owner・再判定日必須）
- **Minor**: 表記・体裁・補助導線の軽微差分。→ **Go可**（follow-up issue必須）

### 18.3 Gate contract（再現可能判定）

| Gate | 目的 | 入力 | 実行コマンド/手順 | 合格基準 | 失敗時対応 |
| --- | --- | --- | --- | --- | --- |
| G0 計画整合 | 判定対象と依存を固定 | issue/ADR参照 | `python 01_Plans/issues/validate_active_issue_memos.py` | AC/DoD/戻し先issueが1:1で追跡可能 | `PRODUCT-QA-01` 本文差戻し |
| G1 安全既定 | SafeMode境界維持 | policy/docs/e2e証跡 | 手動smoke +安全境界確認 | SafeMode既定ON、共有前確認導線一致 | Blockerとして No-Go |
| G2 主要操作 | 操作可能性保証 | smoke手順/Playwright | `npm run e2e` または `npm run e2e:mock` | 開始→編集→保存→復帰が再現 | `QA-E2E-USE-01` へ戻す |
| G3 日本語UI | 主要UIの理解可能性 | i18n test | `npm run test:regression-guards` | 主要ラベルに未翻訳/内部語なし | `PRODUCT-UX-*` へ戻す |
| G4 画面耐性 | viewport崩れ防止 | 390/960/1280 観測 | 手動smoke viewport確認 | 主要操作が見切れない | `PRODUCT-UX-*` へ戻す |
| G5 公開文書 | 公開境界維持 | public docs | `git diff --check` + 公開文書目視 | 内部運用情報が公開文書に混入しない | `04_Documentation/*` 差戻し |
| G6 診断/サポート | 障害時初動 | diagnostics/support docs | 失敗時ログ採取手順確認 | 次アクションが利用者に伝わる | 推奨: follow-up |
| G7 回帰 | 技術回帰防止 | FE/BE/docs | `npm run typecheck` / backend test / diff check | 必須回帰失敗なし | Major以上は No-Go |
| E1 契約キー | Env公開契約 | runtime registry/docs | env keyの一致確認 | 公開契約キー逸脱なし | `ENV-CONFIG-DRIFT-01` |
| E2 実行時検証 | 起動時破綻防止 | settings test | backend settings test | 不正値fail-fast | Blocker |
| E3 Compose整合 | 配布時整合 | compose/env file | compose config check | compose/envの差分矛盾なし | `ENV-CONFIG-DRIFT-01` |

### 18.4 固定実行順（Runbook）

1. smoke（手動）
2. unit/regression（軽量）
3. integration（frontend/backend連動）
4. e2e（Playwright: compose優先、不可時mock）
5. release checks（docs/compose/env/public exposure）

各段で失敗した場合は次段へ進まない。自己修復は3回まで、4回目相当は Blocker一覧を作成して停止する。

### 18.5 Blocker一覧フォーマット（停止時）

- Blocker ID:
- Gate:
- Severity:
- 再現コマンド/手順:
- 影響範囲:
- 暫定回避策:
- エスカレーション先:
- 再開条件:

## Stream E update (2026-05-20): P0 release gate entry criteria / stopper application

### 1) Read（最新メタ）
- 本issueは `GoNoGoGate=Required` / `VerificationLevel=integration` の正本として扱う。
- 判定軸は `G0..G7 + Value gates + E1..E3` を維持し、Blocker/Major/Minor分類で決裁する。

### 2) Draft群のOpen化条件（entry criteria）
- EC-PROD-01: 各ゲートに `result/evidence/owner/due` の4項目が存在する。
- EC-PROD-02: Conditional Go の条件（期限付きfollow-up issue + 再判定日）が明文化されている。
- EC-PROD-03: No-Go 時の戻し先 issue（`MVP-EXIT-01`, `ENV-CONFIG-DRIFT-01` など）が固定されている。
- EC-PROD-04: SafeMode/share-export/import-sanitize/public-exposure の境界判定がゲート本文に含まれる。

### 3) Plan → Execute → Verify（測定可能化）
- Plan: release判定テンプレートを単一運用（Gate Record）として扱う。
- Execute: docs-onlyで証跡欄と戻し先導線の欠落を補完。
- Verify:
  - `rg -n "EC-PROD-0[1-4]|G0|G7|Value gates|E1|E2|E3|Conditional Go|No-Go" 01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
  - `git diff --check -- 01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md`

### 4) Stopper条件適用
- Stopper-P1: Blocker>0 で Go/Conditional Go を禁止。
- Stopper-P2: 証跡欠落（command log / gate result / follow-up issue）時は No-Go。
- Stopper-P3: SafeMode境界不整合は即No-Go。

## 18) Stream F update (2026-05-20): Release QA gate verification hardening

### Plan
- `Go/Conditional Go/No-Go` 判定を docs と tests の双方で追跡可能にする。
- Blocker/Major/Minor の分類語彙を regression 対象に固定する。

### Execute
- QA contract テストを追加し、Gate Record と判定語彙の欠落を CI 前段で検知可能にする。
- 実装コード変更なしで、品質ゲート定義のドリフト検知を優先する。

### Verify
- `python -m pytest 03_Implement/backend/tests/test_qa_e2e_doc_contract.py` を実行し、release gate 主要トークンの存在を確認する。
- metadata validator を併用し、issue memo 形式の逸脱を検知する。

### Proceed
- 判定語彙の逸脱が出た場合は No-Go とし、戻し先 issue を起票して是正期限を設定する。
