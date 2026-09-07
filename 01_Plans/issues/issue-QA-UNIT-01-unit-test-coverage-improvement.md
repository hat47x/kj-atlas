# Issue Plan: QA-UNIT-01 ユニットテスト拡充（欠陥検知能力ベース）

- Type: Process
- Status: In Progress
- Source Issue: N/A
- Open Readiness: Prepared
- Execution: Ready
- Priority: P0
- Owner: Stream H（QA P0 Hold解除準備）
- Scope: `01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`、初回実行バッチの`03_Implement/frontend/src/domain/view/hierarchy_level.ts`・同`.test.ts`・`App.tsx`、および2026-09-07第2バッチの`03_Implement/frontend/src/ui/TenantSessionRuntimeGate.test.ts`・`03_Implement/frontend/package.json`・`package-lock.json`。
- Out of Scope: CI設定変更、Vitest全体の`node`環境変更、テスト都合の製品挙動変更。第2バッチでは対象test fileだけにDOM環境を与え、`TenantSessionRuntimeGate.tsx`本体は変更しない。
- Expected verification level: `unit`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Policy reference: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## Phase 1: Read Gate（Draft/Hold理由と依存抽出）

### Draft理由
- 欠陥クラス基準は定義済みだが、Open判定に必要な依存解消チェックリストが未分離。
- G1/G2/G3 の順序はあるが、Hold解除条件の可測性が不足。

### Execution Hold理由
- 契約凍結・承認待ち・実行環境制約のいずれが支配的blockerか判定欄がない。
- 実装タスク起票承認（Pending-1）未了。

### 依存ブロッカー
| Blocker ID | 内容 | 計測条件 | 解消責務 |
|---|---|---|---|
| B-UNIT-01 | 実装タスク起票承認未了 | Pending-1 に起票ID追記 | QA lead |
| B-UNIT-02 | 上流契約凍結未反映 | Pending-2 に凍結参照ID追記 | Architecture owner |
| B-UNIT-03 | 環境制約 → 解消済み（2026-07-18、下記Phase 6参照） | unit実行プロファイルを選択済み | QA engineer |

## Phase 2: ADR C/D/C（簡易）
### Context
P0で優先度は高いが、実行前提未定義のため着手条件が不安定。

### Decision
Open化ゲートを「依存解消ID」「段階ゲート順序」「失敗分類語彙固定」で定義。

### Consequences
- 無理な先行実装を抑止し、実行可能性を向上。
- 第三者がHold維持/解除を機械的に判断可能。

## Phase 3: Plan（Open化条件・責務・最小検証セット）
### Open化条件
- O-UNIT-01: docs-only scope と non-goal が保持される。
- O-UNIT-02: `G1 Unit -> G2 Integration -> G3 E2E Traceability` が維持される。
- O-UNIT-03: `test defect / product defect / environment limitation` が単一語彙で維持される。
- O-UNIT-04: blocker と再開条件が 1:1 で対応づく。

### 責務
- Stream H: Open化条件の整備・曖昧語排除。
- Stream F: Open後の実行展開（テスト実装本体）。
- Reviewer: 承認ID検証と状態遷移判断。

### 最小検証セット
1. AC/DoD/O-UNIT の検索可能性。
2. blocker解消条件の可測性。
3. `Execution: Hold` の維持条件明示。

### Draft→Open ゲートチェックリスト（機械判定用）
| Gate ID | 判定質問 | 必須証跡 | 判定値 |
|---|---|---|---|
| GO/NO-GO-1 | O-UNIT-01〜04 は本文上で追跡可能か | O-UNIT節 + AC/DoD節 | pass / blocked |
| GO/NO-GO-2 | blocker と再開条件は 1:1 対応か | B-UNIT表 + Pending欄 | pass / blocked |
| GO/NO-GO-3 | G1→G2→G3 の順序と失敗分類は固定か | 段階ゲート定義テーブル | pass / blocked |
| GO/NO-GO-4 | docs-only 範囲外要求が混入していないか | Scope / Out of Scope の一致 | pass / blocked |

## Phase 4: Execute（具体化）

### 段階ゲート定義（unit / integration / e2e）
| Gate | Entry | Exit（合格条件） | 失敗分類 |
|---|---|---|---|
| G1 Unit | 対象欠陥クラス定義済み | P0/P1/P2観点数充足 + 期待値/失敗時挙動定義完了 | test defect / product defect / environment limitation |
| G2 Integration | G1合格 | 契約境界 + 永続化断面の失敗時挙動を定義済み | 同上 |
| G3 E2E Traceability | G2合格 | unit失敗を代表ジャーニーへ逆引き可能 | 同上 |

> 注: 本issueは docs-only のため、実テスト追加は別実行タスクで実施する。

### 実装依存の切断方針（mock/fixture前提）
- 欠陥クラスの網羅判定は既存 fixture と失敗注入モック（入力異常/契約境界/環境制約）を前提に定義する。
- 新規プロダクト挙動や新規テスト実装の有無を Open 条件に含めない。
- 実装タスクは Pending-1 承認後に別Issueで実施し、本Issueは計画品質の判定語彙を固定する。

## Phase 5: Verify（測定可能性チェック）
### AC（Open化判定用 / 推測確定禁止）
- AC-O1: Scope が docs-only（本ファイルのみ）として固定され、実装変更の要求が含まれない。
- AC-O2: Gate `G1 Unit -> G2 Integration -> G3 E2E Traceability` の順序が崩れていない。
- AC-O3: 失敗分類（`test defect / product defect / environment limitation`）が単一語彙で維持される。
- AC-O4: blocker と再開条件が 1:1 対応で記載され、未充足時は `Execution: Hold` を維持する。

### DoD（Open公開品質）
- DoD-O1: 第三者が本ファイル単体で「何を実装しないか（Non-goal）」を判定できる。
- DoD-O2: Validation plan がコマンド再現可能で、結果判定（pass/fail/blocked）が定義済み。
- DoD-O3: 承認未了項目は `Pending` のまま保持し、確定語（Done/Approved）へ昇格しない。

### Validation plan（docs-check）
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|O-UNIT-01|O-UNIT-02|O-UNIT-03|O-UNIT-04|Execution: Hold|Pending" 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
- `git diff --check -- 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`

## Phase 6: Proceed（3区分）
- **Open化可能**: O-UNIT-01〜04充足。
- **追加判断必要**: 承認IDが一部未記入。
- **保留継続**: B-UNIT-01/B-UNIT-02/B-UNIT-03のいずれか未解消。

### Pending approvals（未承認は保持）
- Pending-1: テスト拡張実行の着手承認（実装タスク起票）。→ 承認済み（2026-07-16、Maintainer/hat47x、本セッションでの明示承認）。
- Pending-2: 上流契約凍結の最終承認反映。→ 承認済み（2026-07-16、Maintainer/hat47x。参照する上流契約凍結は `DATA-CONTRACT-01`、Done）。

### Execution
- Pending-1/Pending-2に続き、B-UNIT-03（unit実行プロファイル未選択）を2026-07-18に解消した。
- **B-UNIT-03確定値**: 次の2本立てで固定する。
  1. frontend: `npm run test`（vitest全件、WSLクローン`~/kjnative-fe`で実行。DrvFs経由の`/mnt/c/...`では実行しない）。
  2. backend: `python3 -m pytest`（既定プロファイル。PostgreSQL roundtripテストは`KJ_ATLAS_RUN_PG_TESTS`未設定で自動スキップされ、CI既定と同一になる）。
  - 根拠: どちらもCIが実行するのと同一のプロファイルであり、追加インフラ・環境変数・外部依存を要求しない。PG roundtripが必要な変更では`KJ_ATLAS_RUN_PG_TESTS=1`のopt-in実行を証跡に追記する（プロファイルの置換ではなく追加実行として扱う）。
- `Execution: Ready`（承認・技術的ブロッカーはすべて解消。初回実行バッチは別PRで進める）


### 修復上限（共通）
- 自己修復は最大3回まで（再実行、記述補正、リンク補正）。
- 4回目相当は Stop。保留理由と再開条件を `Pending` 欄へ追記する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。



## Stream H Finalization (2026-05-20): Draft理由分解 / Open化ゲート固定

### Draft維持理由（分解）
- 環境: unit実行プロファイル（Compose/SQLite/例外）の採用理由が未記録。
- 依存: Pending-1（実装タスク起票承認）/ Pending-2（上流契約凍結承認）が未完了。
- 設計: G1→G2→G3 は定義済みだが、blocker解除証跡の責務分担が未入力。

### Open化ゲート（固定）
- Gate-A（前提）: B-UNIT-01〜03 の再開条件を Pending欄へ反映。
- Gate-B（AC）: AC-O1〜O4 が単一語彙で検索可能。
- Gate-C（DoD）: DoD-O1〜O3 が `pass|blocked` で第三者判定可能。
- Gate-D（失敗時扱い）: triage分類は `test defect / product defect / environment limitation` に固定。

### Open移行可否（本日時点）
- 判定: **不可（Execution: Hold 維持）**。
- 不足条件: Pending-1, Pending-2 の承認ID未記入。
- 解消順: 1) Pending-2（契約凍結承認）→ 2) Pending-1（起票承認）→ 3) unit profile確定。

## Stream E update (2026-05-20): Open化 entry criteria / unit gate normalization

### 1) Read（最新メタ）
- `Execution: Hold` 維持条件は `Pending-1/2` と `unit profile` 未確定であることを再確認。
- `G1→G2→G3` と triage語彙固定（`test defect / product defect / environment limitation`）をOpen判定の基準に据える。

### 2) Draft群のOpen化条件（entry criteria）
- EC-UNIT-01: O-UNIT-01〜04 が本文内で追跡可能（検索可能）である。
- EC-UNIT-02: `B-UNIT-01〜03` の各blockerに対応する再開条件が Pending欄に記録済み。
- EC-UNIT-03: 実行プロファイル（Compose / SQLite / 例外記録）を1件選択済み。
- EC-UNIT-04: 未充足時の Stopper分類（approval/contract/environment）が明示される。

### 3) Plan → Execute → Verify（測定可能化）
- Plan: Open判定は `GO/NO-GO-1..4` と `AC-O1..O4` の交差一致を要求。
- Execute: docs-onlyで不足メタ（承認ID、責務、判定語彙）を補完。
- Verify:
  - `rg -n "EC-UNIT-0[1-4]|O-UNIT-0[1-4]|Execution: Hold|Pending|test defect|product defect|environment limitation" 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`
  - `git diff --check -- 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md`

### 4) Stopper条件適用
- Stopper-U1: Pending-1/2 未解消のままOpen不可。
- Stopper-U2: triage語彙が増殖・揺れた場合はHold。
- Stopper-U3: docs-only範囲外の実装要求が混入した場合はStop。

## Stream G update (2026-05-20): Draft→Open昇格条件（QA-UNIT 固定）

| Gate ID | 条件 | Pass基準 |
| --- | --- | --- |
| QU-O1 | `O-UNIT-01..04` が本文で検索可能 | `pass` 判定可能 |
| QU-O2 | Blocker `B-UNIT-01..03` と再開条件が1:1対応 | 欠落0件 |
| QU-O3 | `G1->G2->G3` の順序固定 | 順序崩れなし |
| QU-O4 | triage語彙が `test defect / product defect / environment limitation` に固定 | 語彙差分なし |
| QU-O5 | 自己修復上限 `<=3` と4回目相当Stopが明記 | 記載あり |

### Verify matrix（QA-UNIT）

| チェック | コマンド | 合格条件 |
| --- | --- | --- |
| Gate可観測性 | `rg -n "O-UNIT-0[1-4]|B-UNIT-0[1-3]|G1 Unit|G2 Integration|G3 E2E Traceability|Execution: Hold" 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md` | 必須語彙が全件ヒット |
| メタ整合 | `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md` | exit 0 |
| 差分健全性 | `git diff --check -- 01_Plans/issues/issue-QA-UNIT-01-unit-test-coverage-improvement.md` | 警告なし |

（注: 上記のうち`validate_active_issue_memos.py --files`は現CLIが`--root`のみを受け付けるため、`python3 01_Plans/issues/validate_active_issue_memos.py`のデフォルト実行へ読み替える。`DX-E2E-08`で確認済み。）

## Sonnet級エージェント実行計画（2026-07-18）: 残ブロッカー解除と初回実行バッチ

Pending-1/2は2026-07-16にMaintainer承認済み。残るB-UNIT-03は技術的固定のみであり、この節の確定値で解除する（実装側で再選択しない）。

### ブロッカー解除の確定値

- **B-UNIT-03（unit実行プロファイル）**: 次の2本立てで固定する。
  1. frontend: `npm run test`（vitest全件、WSLクローン`~/kjnative-fe`で実行。DrvFs経由の`/mnt/c/...`では実行しない）。
  2. backend: `python3 -m pytest`（既定プロファイル。PostgreSQL roundtripテストは`KJ_ATLAS_RUN_PG_TESTS`未設定で自動スキップされ、CI既定と同一になる）。
  - 根拠: どちらもCIが実行するのと同一のプロファイルであり、追加インフラ・環境変数・外部依存を要求しない。PG roundtripが必要な変更では`KJ_ATLAS_RUN_PG_TESTS=1`のopt-in実行を証跡に追記する（プロファイルの置換ではなく追加実行として扱う）。

### 解除手順（docs-only、1 PR）

1. Phase 1のblocker表（B-UNIT-03行）とPhase 6のExecution欄を上記確定値と実施日で更新し、`Execution: Hold`を`Execution: Ready`へ変更する。
2. 検証: `python3 01_Plans/issues/validate_active_issue_memos.py` / `python3 01_Plans/docs_check.py` / `git diff --check`。

### 初回実行バッチ（解除後の最初の1 PR）

本issueの主旨は「欠陥検知能力ベース」の拡充であり、カバレッジ率を目標にしない。初回バッチは**直近の実バグの再発検知能力**を固定する:

1. `QA-MONKEY-10`（ラベルカリングによる見かけ喪失、Done）と`QA-MONKEY-12`（作業モードのボタン重なり）について、再発を検知するunit/domainテストが現存するかを棚卸しする（`03_Implement/frontend/src/canvas/`のculling系テスト、`visual_language.guard.test.ts`等をGrepで確認）。
2. 検知テストが欠けている実バグ1件へ、失敗3分類語彙（本issueのG1定義）に従うテストを追加する。
3. 実行: 上記確定プロファイル（`npm run test` / `python3 -m pytest`）で全件greenを確認し、証跡をG1欄へ記録する。
4. ガードレール: 製品挙動を変更しない（テスト追加のみ）。同一論点でVerify 3連続失敗時は停止し、Pending欄へ理由と再開条件を記録する。

### 初回実行バッチ 実装記録（2026-07-18）

**棚卸し結果**: `QA-MONKEY-10`（`label_culling.test.ts`の「keeps the active card over overlapping plain cards regardless of id order」で明示的に再発検知済み）と`QA-MONKEY-12`（`WorkModeTabs.test.ts`の「hides every tabpanel except the active one」で、根本原因である排他的タブ構造そのものを構造的に固定済み）は、いずれも**既にunit/domainレベルで再発検知テストが存在**しており、ギャップがなかった。

計画の想定（この2件のいずれかにギャップがある）と実際が異なったため、同issue群からより最近の実バグを追加調査し、`QA-MONKEY-13`（Alt+Shift+2構造レベルショートカット、2026-07-15解消）を検出した。この修正はフルE2Eスイート（165/165）でのみ検証されており、**unit/domainレベルの再発検知テストが存在しないこと**を確認した（`hierarchy_level.test.ts`の既存テストは純粋関数`maxDepthForHierarchyLevel`/`resolveHierarchyLevel`のみを対象とし、実際の欠陥箇所であった`App.tsx`内のeffect連鎖の相互作用は対象外だった）。

**追加した検知テスト**:
- `03_Implement/frontend/src/domain/view/hierarchy_level.ts`に`clampMaxDepthToAvailable(maxDepth, maxAvailableDepth)`を新規追加した。QA-MONKEY-13の根本原因だった`App.tsx`内のインライン条件（`if (maxDepth > maxAvailableDepth && maxAvailableDepth > 0)`）を同じロジックのまま純関数として抽出し、`App.tsx`側は抽出した関数を呼ぶだけに置き換えた（**製品挙動は変更していない**、既存条件のリファクタのみ）。
- `hierarchy_level.test.ts`に4 testsを追加した。中心の1件は「`maxAvailableDepth=0`のとき`maxDepth=1`（mid）を`0`へ切り詰めない」というQA-MONKEY-13の実際の再現条件そのものを検証する。

**なぜ抽出が必要だったか**: 欠陥の実体はReactのeffect連鎖の相互作用であり、`hierarchy_level.test.ts`の既存テストが対象としていた純粋関数のロジック自体は当時から正しかった（issueの「除外した仮説」で明示的に否定済み）。条件をインラインのままにすると、レンダリングやeffect実行を伴わないunitテストでは検知できない。純関数として抽出することで、E2Eを伴わない高速なunitテストが実際の製品コードパス（`App.tsx`が呼ぶのと同じ関数）を直接検証できるようになった。

### 検証結果（2026-07-18）

- `npm run typecheck`: 0 errors。
- `npx vitest run`: **1071/1071 pass**（新規4 testsを含む）。唯一失敗する`src/import/external_agent_workflow_doc.test.ts`は`~/kjnative-fe`検証用ミラーの環境固有の制約で、本変更と無関係（既知の事象）。
- QA-MONKEY-13を実際に発見した`e2e/header_toolbar_layout.spec.ts`（"modifier shortcuts update visible view and hierarchy state"を含む）を、Docker Desktop連携で`mcr.microsoft.com/playwright:v1.58.2-jammy`公式イメージを使い実行し、**9/9 pass**を確認した（リファクタによる回帰なし）。

G1（unit段階ゲート）欄への証跡: QA-MONKEY-13の再発は`clampMaxDepthToAvailable`のunitテストで即座に（E2E実行なしで）検知可能になった。

### 第2バッチ 調査記録（2026-07-19）: SaaS tenant runtime gateの分岐カバレッジ不足とテスト環境上の制約

**発見**: `03_Implement/frontend/src/ui/TenantSessionRuntimeGate.test.ts`は、初期loading状態の描画と、`main.tsx`が本componentを実際に配線していることの2点しか検証しておらず、component自身の中心的な分岐ロジック — `policyVerified`が`false`になった場合に`TenantSessionBlockedView`を表示すること、`true`になった場合に`TenantSessionBootstrapGate`へ正しくhand-offすること、`onRetry`が`attempt`を増分して`verifyTenantSessionRuntimePolicy`を再実行させること — を一切検証していない。

**着手し、着手不能と判断した理由**: この分岐は`useEffect`内の非同期処理（`verifyTenantSessionRuntimePolicy`の解決を待って`setPolicyVerified`する）に依存しており、React committment/再レンダリングを要する。本プロジェクトのfrontend単体テストは全ファイルが`react-dom/server`の`renderToStaticMarkup`（同期・DOM不要・effect未実行の1回限りの静的HTML化）のみで書かれている（`TenantSessionBootstrapGate.test.ts`を含む既存の類似gate componentテストも同じ制約下にあり、初期状態を1回描画するか、`TenantSessionBlockedView`等の提示専用subcomponentを個別に描画するかたちで検証しており、gate自身の状態遷移そのものを検証していない）。これは`03_Implement/frontend/vite.config.ts`が`test.environment: "node"`を明示しているためで、`jsdom`/`happy-dom`/`@testing-library/react`/`react-test-renderer`のいずれも`package.json`に存在しない。

このため、この分岐を実際にテストするには次のいずれかが必要であり、いずれも「テスト追加のみ」という本issueのガードレールを超える判断を要する:
1. `jsdom`または`happy-dom`を新規devDependencyとして追加し、当該テストファイルにvitestの`// @vitest-environment jsdom`指定を加える（プロジェクトの意図的なNode-only・最小依存方針との整合を要判断）。
2. componentの分岐ロジックを、React再レンダリングなしに検証可能な形へ再構成する（現状の3分岐自体は`policyVerified: boolean | null`を受ける純粋な条件分岐であり、抽出してもテスト価値は限定的で、本質的な検証対象である`useEffect`のasync解決・abort・再実行はcomponent構造を変えない限り分離できない）。

**Stopper分類**: `test defect`寄りだが、修復手段の選択自体が「テスト実行基盤（依存追加）の方針決定」という製品外の判断を要するため、本issueの自己修復ルール（最大3回）の対象にはせず、ここで停止する。

**再開条件**: プロジェクトのfrontend単体テストに、DOM/effectを伴うcomponent状態遷移を検証する手段（jsdom等の追加、または別のtest harness）を導入する方針が決定された場合に再開する。決定は`01_Plans/issues/`への新規Issueまたは本issueへの追記で記録する。

## 2026-09-07 current-state同期 / 第2バッチ再開

2026-07-16〜18にPending-1/2とB-UNIT-03は解消済みで、初回バッチも2026-07-18に実装・検証済みである一方、headerだけが`Status: Draft`に残っていたため、歴史節のDraft/Hold判定を改変せず、初回バッチ実行済みの現在状態を`In Progress`へ同期する。

2026-07-19の第2バッチで停止した理由は、`TenantSessionRuntimeGate`の中心的な状態遷移がReactのcommit/effectを必要とするのに、既存unit suiteがglobal `environment: "node"`＋SSR中心で、実componentを再レンダリングする局所harnessを持たなかったことだった。今回、この停止条件を次の最小境界で解除する。

- globalのVitest `environment: "node"` は変更しない。
- `TenantSessionRuntimeGate.test.ts`だけをVitestのfile-local environmentで`happy-dom`へ切り替える。
- Testing Library等の追加抽象層は導入せず、React 18の`createRoot`＋`act`で実componentをmountする。
- 製品側`TenantSessionRuntimeGate.tsx`をテスト都合で純関数化・分岐抽出しない。
- `policyVerified=false`のblocked表示、`true`の`TenantSessionBootstrapGate` hand-off、Retryによるpolicy再検証を実effect/state遷移として固定する。

### 判定境界

この変更は、2026-07-19に明記した**特定のtest-harness blockerを解消し、第2バッチの欠陥検知能力を増やすもの**である。QA-UNIT-01全体をDoneとはしない。今後も欠陥クラス基準で追加候補を選び、DOM環境を全testへ拡張することや、coverage率そのものを目的化することはしない。

依存追加はNode 20（repository `.nvmrc`）でengine-strict installが成立する版に固定し、対象test、frontend全suite、typecheck、planning/docs guardsが同一runでgreenになった場合だけmainline候補とする。
