# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Open Readiness: Prepared
- Execution: Hold
- Priority: P0
- Owner: Stream H（QA P0 Hold解除準備）
- Scope: 本ファイルのみ（docs-only）
- Expected verification level: `e2e`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Related: `01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`（境界判定を参照）
- Policy reference: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## Phase 1: Read Gate（Draft/Hold理由と依存抽出）

### Draft理由（現状）
- S1〜S3（Must）/S4（Should）の判定軸は定義済みだが、Open化の最終判断に必要な「依存充足の証跡欄」が未固定。
- unit/integration/e2e 段階ゲートは定義済みだが、どの依存がどのゲートを解放するかの対応が曖昧。

### Execution Hold理由（現状）
- `ADR-0019` が要求する実行経路（Compose優先、代替経路、例外記録）のどれで進めるか未確定。
- 実環境実行承認（Pending-1）と I18N境界最終承認（Pending-2）が未了。

### 依存ブロッカー（測定可能化）
| Blocker ID | 内容 | 計測条件（解消判定） | 解消責務 |
|---|---|---|---|
| B-USE-01 | 実運用E2E環境承認未了 | 承認記録リンクが `Pending-1` に追記済み | QA Lead |
| B-USE-02 | I18N境界最終承認未了 | `QA-PUB-01` の承認記録IDが記載済み | Reviewer |
| B-USE-03 | ゲート解放証跡欄未固定 | G1/G2/G3 各欄に entry/exit 証跡欄が記入可能 | Stream H |

## Phase 2: ADR C/D/C（簡易）

### Context
P0だが、実行前提（承認・環境・境界証跡）が不足し、Execution Holdのままでは着手可否を客観判定できない。

### Decision
Open化ゲートを次の3カテゴリで固定する。
1. **Prerequisite Gate**: 承認ID、実行経路（Compose/SQLite/例外）の明示。
2. **Environment Gate**: `ADR-0019` のヘルス確認経路をどれで実施するかを事前固定。
3. **Scope Gate**: 本Issueは docs-only であり、実装変更要求を含めない。

### Consequences
- 実行可能性が上がり、Open/Hold判断を第三者が再現可能。
- 前提未充足のままE2E拡張実装へ進む誤着手を防止。

## Phase 3: Plan（Open化条件・責務・最小検証セット）

### Open化条件
- O-USE-04: blocker と再開条件が 1:1 で対応し、未解消時は `Execution: Hold` を維持する。
- O-USE-01: B-USE-01/B-USE-02 が両方解消済み。
- O-USE-02: `ADR-0019` 準拠の実行経路（Compose/SQLite/例外）が1つ指定済み。
- O-USE-03: G1→G2→G3 の entry/exit 判定欄が埋められる構成である。

### 責務
- Stream H: Open化ゲート文面維持、曖昧語排除、Hold条件の更新。
- Stream F: Open後の実行計画具体化とテスト拡張実装。
- Reviewer: 承認ID付与と Hold解除可否の最終判定。

### 最小検証セット（docs-only）
1. AC/DoD/O-USE 条項が単一語彙で再検索可能。
2. blocker と再開条件が 1:1 対応。
3. `Execution: Hold` 維持条件が明示。

### Draft→Open ゲートチェックリスト（機械判定用）
| Gate ID | 判定質問 | 必須証跡 | 判定値 |
|---|---|---|---|
| GO/NO-GO-1 | B-USE-01 と B-USE-02 は解消済みか | Pending欄の承認ID + 日付 + 参照リンク | pass / blocked |
| GO/NO-GO-2 | 実行経路は `ADR-0019` 準拠で1つ固定済みか | Compose / SQLite / 例外の選択記録 | pass / blocked |
| GO/NO-GO-3 | G1→G2→G3 の entry/exit 証跡欄は埋められるか | Gate表の entry/exit 欄 | pass / blocked |
| GO/NO-GO-4 | docs-only 範囲外要求が混入していないか | Scope / Non-Goals の一致 | pass / blocked |



## Phase 3.5: テスト設計境界（Stream E）

### 目的
- QA Monkey群とE2E境界を**テスト資産のみ**で整備し、実装コード変更を前提にしない。

### 分離方針（契約 / スモーク / E2E）
- 契約テスト: fixtureベースで API/状態遷移の契約を固定し、回帰差分の一次検知を担う。
- スモーク: 主要導線と fail-closed 境界を手動で短時間確認する。
- E2E: 実利用シナリオの再現と境界回帰の自動化を担う。

### 非目標
- `src/ui` / `src/canvas` の機能変更による問題解決。
- 本番データ接続や外部公開環境を前提にした検証。

### flaky対策と停止条件
- mock/fixture 優先。
- 自己修復上限は3回。4回目相当は Stop、`Pending` に再開条件を追記。

## Phase 4: Execute（Draft本文の具体化）

### シナリオ定義（実行本体は別Issue）
| Scenario | Priority | Flow | Done判定 |
|---|---|---|---|
| S1 Authoring Continuity | P0 | 作成→編集→再読込 | 欠損ゼロ/整合維持 |
| S2 Review Governance | P0 | 差分記録→人手昇格 | 自動昇格なし |
| S3 Safe Sharing Gate | P0 | 共有試行→条件充足→許可 | fail-closed維持 |
| S4 Import-to-Safe-Export | P1 | sanitize→共有境界確認 | 悪性reject/正常allow |

### I18N境界（横断）
- `?locale=en` でも S1〜S3 が同一判定で成立する。
- `?readOnly=1` と locale 切替を併用しても禁止操作境界が維持される。
- `ja/en` のユーザージャーニー等価は自動化で判定し、翻訳妥当性は人間レビューで判定する。

### 実装依存の切断方針（mock/fixture前提）
- 本Issueで定義するシナリオ妥当性は、既存 fixture とモック化済み外部依存（認証/共有境界/永続化失敗）で判定する。
- 新規実装依存（新API・新UI・本番データ接続）を Open 条件に含めない。
- 実環境との差分は「Execution Hold解除後の実行Issue」で検証し、本Issueでは依存一覧を固定する。

## Phase 5: Verify（測定可能性チェック）

### Open readiness pack（AC/DoD/Validation plan 固定）

#### AC（Open化判定用）
- AC-O1: S1〜S3（Must）と S4（Should）の優先境界が維持される。
- AC-O2: `locale + readOnly` のI18N境界が横断条件として残る。
- AC-O3: `unit -> integration -> e2e` の前段ゲート未達時は E2E Proceed しない。
- AC-O4: 失敗時の triage は `test defect / product defect / environment limitation` で固定される。

#### DoD（Open公開品質）
- DoD-O1: 実装非実施（docs-only）が明示され、対象外変更を含まない。
- DoD-O2: Validation手順が再現可能で、判定語彙（pass/fail/blocked）が追跡可能。
- DoD-O3: 依存未確定・承認未了は `Pending` として保持し、推測確定しない。

#### Validation plan（docs-check）
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|O-USE-01|O-USE-02|O-USE-03|Execution: Hold|Pending" 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
- `git diff --check -- 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`


## Phase 5.1: Verify Evidence (2026-05-20, Stream E)

- 実施経路: SQLite/ローカル検証（Compose未使用）。
- 判定: **Execution: Hold 維持**（Pending-1 / Pending-2 未解消のため）。

### 再現コマンドと結果
- `npm run test:regression-guards`（frontend）: pass（97 tests）。
- `python3 01_Plans/issues/validate_active_issue_memos.py` : pass（active memo検証OK）。
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|O-USE-01|O-USE-02|O-USE-03|Execution: Hold|Pending" 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` : pass（条項抽出可能）。

### 失敗/制約の記録
- `validate_active_issue_memos.py --files ...` は未対応引数のため失敗。再実行時は `--root` またはデフォルト実行を使用する。
- 自己修復回数: 1/3（コマンド修正で復旧）。

## Phase 6: Proceed（3区分）
- **Open化可能**: O-USE-01〜03が全充足。
- **追加判断必要**: O-USE-02は充足、承認IDが一部未反映。
- **保留継続**: B-USE-01/B-USE-02 のいずれか未解消。

### Pending approvals（未承認は保持）
- Pending-1: 実運用E2E環境での実行承認。
- Pending-2: QA-PUB-01 境界判定の最終レビュー承認。

### Execution
- `Execution: Hold`（Pending解消まで維持）


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
- 環境: `ADR-0019` 準拠の実行経路（Compose / SQLite / 例外記録）が candidate 単位で未固定。
- 依存: Pending-1（実運用E2E承認）と Pending-2（I18N境界最終承認）が未解消。
- 設計: Gate証跡欄（G1/G2/G3 entry/exit）の入力責務と判定語彙は定義済みだが、承認ID未記入。

### Open化ゲート（固定）
- Gate-A（前提）: Pending-1/Pending-2 に承認ID・日付・参照リンクを記録。
- Gate-B（検証経路）: `ADR-0019` の実行経路を1つ選択し、未選択経路は「未採用理由」を残す。
- Gate-C（AC/DoD）: AC-O1〜O4 / DoD-O1〜O3 が `pass|blocked` で判定可能。
- Gate-D（失敗時扱い）: `test defect / product defect / environment limitation` の3分類以外を使用しない。

### Open移行可否（本日時点）
- 判定: **不可（Execution: Hold 維持）**。
- 不足条件: Pending-1, Pending-2 の承認証跡。
- 解消順: 1) Pending-2（I18N境界）→ 2) Pending-1（実運用E2E承認）→ 3) Gate表の最終記入確認。

## Stream E update (2026-05-20): Open化 entry criteria / P0 gate measurableization

### 1) Read（最新メタ）
- `Status=Draft (Open-Readiness Prepared / Execution Hold)` を維持し、Open判定は `Pending-1/2` と `Execution path` の充足でのみ判断する。
- `Expected verification level=e2e` を根拠に、Open条件は **実行可否の事実**（承認ID、経路固定、証跡欄）へ限定する。

### 2) Draft群のOpen化条件（entry criteria）
- EC-USE-01: `B-USE-01` と `B-USE-02` が解消済み（承認ID・日付・参照リンクを Pending 欄へ記録）。
- EC-USE-02: `ADR-0019` 準拠の実行経路（Compose / SQLite / 例外記録）を1つ固定し、変更時の更新責務者を明記。
- EC-USE-03: `G1/G2/G3` それぞれに entry/exit 証跡欄（command / result / evidence link）を記入可能。
- EC-USE-04: 未充足時は `Execution: Hold` を維持し、Stopper分類（approval/env/scope）を1件以上記録。

### 3) Plan → Execute → Verify（測定可能化）
- Plan: `GO/NO-GO-1..4` を Open判定の唯一ゲートとして運用する。
- Execute: docs-only 範囲で、承認ID・実行経路・証跡欄の欠落を補完する（実装変更は禁止）。
- Verify:
  - `rg -n "EC-USE-0[1-4]|Execution: Hold|Pending|GO/NO-GO" 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
  - `git diff --check -- 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`

### 4) Stopper条件適用
- Stopper-S1（Approval）: 承認ID未記入のままOpenへ遷移しない。
- Stopper-S2（Environment）: 実行経路未固定ならOpen不可。
- Stopper-S3（Scope）: docs-only範囲外要求が混入した時点で更新停止し、Hold理由として記録。

## Stream F update (2026-05-20): QA専任実行パッケージ（tests/docs/issues限定）

### Plan
- Scope は `03_Implement/frontend/tests/**` `03_Implement/backend/tests/**` `03_Implement/frontend/docs/e2e_testing.md` `01_Plans/issues/issue-QA-*` に限定。
- 実装本体の変更は行わず、契約トークン検証を unit 化して回帰入口を固定する。

### Execute
- `test_qa_e2e_doc_contract.py` を追加し、`Execution: Hold` / `AC-O*` / `DoD-O*` / Gate語彙の存在を自動検証対象へ昇格。
- 未確定依存は mock/fixture 境界で保持し、Open条件の前倒し確定を禁止。

### Verify
- 追加テスト pass を前提に、`Execution: Hold` 維持条件（Pending-1/2 未解消）を再確認。
- 自己修復上限は3回、4回目相当は Stop を維持。

### Proceed
- Pending-1/2 解消までは本Issueの状態遷移を行わず、証跡更新のみ継続する。

## Stream G update (2026-05-20): Draft→Open昇格条件（QA-E2E-USE 固定）

| Gate ID | 条件 | Pass基準 |
| --- | --- | --- |
| QE-O1 | 代表ユーザージャーニー（smoke/core/safety）が境界別に列挙 | 3系統すべて記載 |
| QE-O2 | 実行経路（Compose / SQLite / 例外記録）が事前選択 | 1経路以上が固定 |
| QE-O3 | 失敗分類が `test defect / product defect / environment limitation` へ正規化 | 語彙ゆれなし |
| QE-O4 | No-Go時の戻し先issueと再開条件が1:1 | 欠落0件 |
| QE-O5 | 自己修復上限 `<=3` / 4回目相当Stop が明記 | 記載あり |

### Verify matrix（QA-E2E-USE）

| チェック | コマンド | 合格条件 |
| --- | --- | --- |
| 境界列挙 | `rg -n "smoke|core|safety|Compose|SQLite|例外記録|Execution: Hold" 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` | 必須語彙ヒット |
| メタ整合 | `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` | exit 0 |
| 差分健全性 | `git diff --check -- 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` | 警告なし |

## Stream H update (2026-05-25): 代表ユーザ操作証跡レーン

### 目的
- `Execution: Hold` を解除せず、PRODUCT-QA-01 の G2 主要操作 / Value gates が消費できる「代表ユーザ操作の一次証跡」を固定する。
- マウス操作とキーボード操作を同じ価値境界で扱い、片方だけで成立する操作を release-ready と誤判定しない。
- Playwright 実行前に壊れやすい入口（選択、文脈パネル、閉じる、フォーカス復帰、共有前確認）を軽量に検知する。

### 実行経路（本更新で固定する一次証跡）
- Path-USE-A: `03_Implement/frontend/src/ui/ux_operability_regression.test.ts` を `npm run test:regression-guards` に含める。
- Path-USE-B: 手動 smoke では標準サンプルまたは新規文書を使い、秘密情報や顧客データを入力しない。
- Path-USE-C: release candidate では `npm run e2e` または `npm run e2e:mock` の Playwright 証跡で Path-USE-A/B を補強する。

### シナリオ別操作証跡

| Scenario | マウス操作 | キーボード操作 | 一次証跡 | G/V gate mapping |
| --- | --- | --- | --- | --- |
| S1 Authoring Continuity | カード作成、カード移動、保存、再読込 | `Tab` 到達、`Enter` / `Space` 選択、保存導線到達 | `test:regression-guards` + 手動smoke | G2, V0/V1 |
| S2 Review Governance | レビュー対象選択、文脈パネル確認、明示操作で状態確認 | 選択対象へ `Tab`、`Enter` / `Space`、選択後の文脈導線確認 | `ux_operability_regression.test.ts` | G2, V2, V3 |
| S3 Safe Sharing Gate | `共有と再現` を開く、SafeMode表示、共有前確認、`Escape` 閉鎖 | 共有トリガーへ `Tab`、`Enter`、`Escape`、フォーカス復帰 | `ux_operability_regression.test.ts` + SharePanel系テスト | G1, G2, V4 |
| S4 Import-to-Safe-Export | import後にsanitize結果を確認し、共有前確認へ進む | import結果から主要導線へ `Tab` で戻れることを確認 | `test:regression-guards` + release candidate E2E | G1, G2, G7, V4 |

### Gate entry/exit 欄（PRODUCT-QA転記用）

| Gate | Entry evidence | Exit evidence | 判定語彙 |
| --- | --- | --- | --- |
| G1 安全既定 | SafeMode既定ON、SharePanel文言、import sanitizeテスト | SafeMode/share-export境界の失敗がない | pass / blocked / fail |
| G2 主要操作 | `ux_operability_regression.test.ts` が regression guards に含まれる | pointer/keyboard双方で主要導線へ到達し、閉じる/戻るが確認できる | pass / blocked / fail |
| G3 日本語UI | i18n guard と UI hardcode guard | 主要ラベルに未翻訳・内部語が残らない | pass / blocked / fail |

### Hold条件の扱い
- Pending-1 / Pending-2 が未解消のため、本Issueの状態は **Draft / Execution: Hold 維持**。
- Path-USE-A は Open解除ではなく、PRODUCT-QA-01 が G2 の不足を分類するための一次証跡として扱う。
- Playwright または実運用E2Eで失敗した場合は、`test defect / product defect / environment limitation` のいずれかに分類し、戻し先を `QA-E2E-USE-01` または該当 `PRODUCT-UX-*` issue へ固定する。

### 追加Verify
- `cd 03_Implement/frontend && npm run test:regression-guards`
- `cd 03_Implement/frontend && node .\node_modules\vitest\vitest.mjs run src/ui/ux_operability_regression.test.ts`
- `python3 01_Plans/issues/validate_active_issue_memos.py`
- `git diff --check -- 03_Implement/frontend/package.json 03_Implement/frontend/docs/e2e_testing.md 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`

## Stream H evidence rerun 2026-06-06: first-value user operation pair

- Scope: current-main representative E2E evidence only. `Status=Draft (Open-Readiness Prepared / Execution Hold)` and `Execution: Hold` remain unchanged because Pending-1 / Pending-2 and release approval are still outside this rerun.
- Candidate mainline: `origin/main@762aad281792a508034d0ba9715c77d2432d84b2`.
- Execution path: SQLite/local frontend path with Vite started directly by bundled Node.js because this Codex host does not expose `npm` on PATH.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/keyboard_release_candidate_flow.spec.ts e2e/first_meaningful_map_mouse_flow.spec.ts --reporter=line`
- Result: **pass, 2 tests**.

### Gate consumption

| Scenario | Evidence consumed | Gate impact | Still not covered |
| --- | --- | --- | --- |
| S1 Authoring Continuity | Mouse path opens the first-value sample, selects two cards, creates `Island 1`, and verifies the selected island context. | Improves G2 / V0 / V1 evidence on current `main`. | Human product-value acceptance and release screenshot bundle. |
| S2 Review Governance | Keyboard path selects a card, reaches critique input, enters a critique note, and preserves focus after share panel close. | Improves G2 / V2 / V3 operability evidence. | Physical keyboard acceptance by UX reviewer. |
| S3 Safe Sharing Gate | Keyboard path opens share preflight and verifies `セーフモード: ON`. | Improves G1 / G2 / V4 safety-entry evidence. | Full release-candidate share/export screenshot and program approval. |

- Stopper classification: none introduced by this rerun. It is evidence-consumption only and does not change execution scope, product behavior, or public documentation.

## Stream H evidence rerun 2026-06-06: S1-S3 realistic journey

- Scope: current-main representative E2E evidence only. `Status=Draft (Open-Readiness Prepared / Execution Hold)` and `Execution: Hold` remain unchanged because Pending-1 / Pending-2, Compose approval, and release approval are still outside this rerun.
- Candidate mainline: `origin/main@cf6f74cddce0f3c04c70b3d88f0bbc82a9a15a43`.
- Execution path: SQLite/local frontend path with Vite started directly by bundled Node.js because this Codex host does not expose `npm` on PATH.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/realistic_user_journey_expansion.spec.ts --reporter=line`
- Result: **pass, 1 test**.

### Gate consumption

| Scenario | Evidence consumed | Gate impact | Still not covered |
| --- | --- | --- | --- |
| S1 Authoring Continuity | Deterministic fixture import replaces the current document and verifies three cards remain visible. | Improves current-main G2 / S1 evidence. | Full persistence/reload rehearsal and release screenshot bundle. |
| S2 Review Governance | Read-only mode is entered and layout suggestion is disabled while the read-only indicator is visible. | Improves current-main S2 boundary evidence. | Human UX acceptance and broader review-state transition proof. |
| S3 Safe Sharing Gate | Share preflight opens in read-only mode and shows locked redaction contexts for Share / Review Pack. | Improves current-main G1 / G2 / S3 evidence. | Full share/export screenshot approval and Compose-backed release rehearsal. |

- Stopper classification: none introduced by this rerun. It is evidence-consumption only and does not change execution scope, product behavior, public documentation, SafeMode policy, or release authority.

## Stream H evidence rerun 2026-06-16: S1-S3 realistic journey after Advanced UI

- Scope: current-main representative E2E evidence only. `Status=Draft (Open-Readiness Prepared / Execution Hold)` and `Execution: Hold` remain unchanged because Pending-1 / Pending-2, Compose approval, release approval, and human acceptance are still outside this rerun.
- Candidate mainline: `origin/main@6a6db549fc76ff4f5a53c3c3c32f6829fb66d0f6`.
- Trigger: `Advanced UI` now keeps non-essential first-run controls out of the default surface. The realistic journey needed to verify the read-only `Suggest layout` boundary through the advanced control path instead of assuming that the control is visible immediately after entering read-only mode.
- Execution path: SQLite/local frontend path with Vite started directly by bundled Node.js because this Codex host does not expose `npm` on PATH.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/realistic_user_journey_expansion.spec.ts --reporter=line`
- Result: **pass, 1 test**.
- CI reference: GitHub Actions run `9602` for PR `#2411` completed successfully before merge.

### Gate consumption

| Scenario | Evidence consumed | Gate impact | Still not covered |
| --- | --- | --- | --- |
| S1 Authoring Continuity | Deterministic fixture import still replaces the current document and keeps the three expected cards visible after the first-run UI decluttering change. | Refreshes current-main G2 / S1 evidence after the Advanced UI merge. | Full persistence/reload rehearsal and release screenshot bundle. |
| S2 Review Governance | Read-only mode is entered, the share panel is closed, `Advanced UI` is opened, and the disabled `Suggest layout` control is verified through the visible advanced path. | Refreshes current-main S2 boundary evidence for the post-MVP default surface. | Human UX acceptance, physical keyboard review, and broader review-state transition proof. |
| S3 Safe Sharing Gate | Share preflight still opens in read-only mode and shows locked redaction contexts for Share / Review Pack before the advanced-control assertion. | Refreshes current-main G1 / G2 / S3 evidence without changing SafeMode policy. | Full share/export screenshot approval and Compose-backed release rehearsal. |

- Stopper classification: none introduced by this rerun. It is evidence-consumption only and does not change execution scope, product behavior, public documentation, SafeMode policy, or release authority.
