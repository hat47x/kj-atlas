# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (Open-Readiness Prepared / Execution Hold)
- Priority: P0
- Owner: Stream H（QA P0 Hold解除準備）
- Scope: 本ファイルのみ（docs-only）
- Expected verification level: `e2e`
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
