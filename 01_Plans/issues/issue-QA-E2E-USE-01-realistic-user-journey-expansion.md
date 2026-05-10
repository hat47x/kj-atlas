# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P0
- Owner: Stream F（QA専任）
- Scope: 本ファイルのみ（docs-only）
- Expected verification level: `e2e`
- Related: `01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`（境界判定を参照）

## Phase 1: Read Baseline（AC/DoD抽出 + 資産ギャップ）

### AC/DoD抽出（現行）
- AC: S1〜S3のMust判定軸が固定され、I18N境界が横断項目として組込済み。
- DoD: blocked時テンプレート・再開条件・3回上限停止条件が明示済み。

### テスト資産棚卸し
| Area | 現行 | 欠落 | 優先度 |
|---|---|---|---|
| Smoke | 起動/読込確認あり | 監査連携の根拠不足 | P2 |
| Core Journey | 部分的に存在 | 作成→編集→レビュー→安全共有の連結不足 | P0 |
| Boundary | SafeMode/readOnly一部あり | I18N境界と同時保証不足 | P0 |

### カバレッジギャップ（unit/integration接続観点）
- unitで検出した失敗系が、E2EシナリオS1〜S4へ追跡できる対応表が不足。
- integrationで担保すべきAPI契約失敗が、E2Eの「期待される遮断結果」と結びついていない。

## Phase 2: Plan（品質戦略）

### ADR（Context/Decision/Consequences）
#### Context
E2Eがsmoke中心のため、実利用で重要な連続操作（作成→レビュー→安全共有）の欠陥検知が不足している。

#### Decision
- 自動化対象: S1〜S3（Must）、S4（Should）をE2E自動化。
- 人間レビュー対象: 文言妥当性・業務受容性・監査判断。
- flaky許容ゼロ、再試行は最大3回、4回目相当は Stop。
- 段階ゲートは unit→integration→e2e の順に固定し、E2E単独合格を禁止。

#### Consequences
- 高リスクユーザージャーニーの欠陥流出を抑制。
- ただし、前段ゲート未達時にE2E着手を止める運用規律が必要。

### 段階ゲート定義（unit / integration / e2e）
| Gate | Entry | Exit（合格条件） |
|---|---|---|
| G1 Unit | 欠陥クラス定義済み | 失敗系・境界値・回帰点の観点充足 |
| G2 Integration | G1合格 | API契約/永続化断面の成功・失敗挙動が定義済み |
| G3 E2E | G2合格 | S1〜S3 Mustの期待結果が再現性をもって成立 |

### flakyリスク項目
- locale切替直後の非同期描画待機不足。
- readOnly/SafeMode切替の状態反映遅延。
- 外部環境（compose/network）依存での不安定化。
- シナリオ間データ汚染による順序依存。

## Phase 3: Execute（E2E拡張計画）

| Scenario | Priority | Flow | Done判定 |
|---|---|---|---|
| S1 Authoring Continuity | P0 | 作成→編集→再読込 | 欠損ゼロ/整合維持 |
| S2 Review Governance | P0 | 差分記録→人手昇格 | 自動昇格なし |
| S3 Safe Sharing Gate | P0 | 共有試行→条件充足→許可 | fail-closed維持 |
| S4 Import-to-Safe-Export | P1 | sanitize→共有境界確認 | 悪性reject/正常allow |

## I18N境界（QA-PUB-01横断チェック）
- `?locale=en` でも S1〜S3 が同一判定で成立する。
- `?readOnly=1` と locale 切替を併用しても禁止操作境界が維持される。
- `ja/en` のユーザージャーニー等価は自動化で判定し、翻訳妥当性は人間レビューで判定する。

## Phase 4: Verify（自己検証ルール）
- 失敗時は3回まで自己修復（再実行/待機調整/fixture確認）。
- 4回目相当は停止し、失敗分類を `test defect / product defect / environment limitation` で分離記録。
- 推測で期待結果を書き換えず、blockerとして記録する。

## Phase 5: Proceed（品質判定）
- AC-01: S1〜S3 Must判定軸が固定済み。
- AC-02: I18N境界（`locale` + `readOnly`）が横断項目として組込済み。
- AC-03: unit/integration/e2e 段階ゲートが定義済み。
- AC-04: flakyゼロ・再試行上限3回・4回目相当停止が明記済み。
- DoD-01: blocked時テンプレート・再開条件が明示済み。
- DoD-02: 依存未解決時に `Execution: Hold` を維持する条件が明示済み。

### blockers / 再開条件
- blocker: 上流仕様未確定、E2E環境不足、関連stream未反映。
- 再開条件: 上流仕様確定、E2E環境復旧、依存stream差分反映確認。


## Open readiness pack（AC/DoD/Validation plan 固定）

### AC（Open化判定用）
- AC-O1: S1〜S3（Must）と S4（Should）の優先境界が維持される。
- AC-O2: `locale + readOnly` のI18N境界が横断条件として残る。
- AC-O3: `unit -> integration -> e2e` の前段ゲート未達時は E2E Proceed しない。
- AC-O4: 失敗時の triage は `test defect / product defect / environment limitation` で固定される。

### DoD（Open公開品質）
- DoD-O1: 実装非実施（docs-only）が明示され、対象外変更を含まない。
- DoD-O2: Validation手順が再現可能で、判定語彙（pass/fail/blocked）が追跡可能。
- DoD-O3: 依存未確定・承認未了は `Pending` として保持し、推測確定しない。

### Validation plan（docs-check）
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|Pending|Execution: Hold" 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`
- `git diff --check -- 01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md`

### Pending approvals（未承認は保持）
- Pending-1: 実運用E2E環境での実行承認。
- Pending-2: QA-PUB-01 境界判定の最終レビュー承認。
