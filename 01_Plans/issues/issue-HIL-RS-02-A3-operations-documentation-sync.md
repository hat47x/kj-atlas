# Issue Draft: HIL-RS-02 A3 Operations/Documentation 同期

- Type: Documentation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: TBD
- Priority: P2
- Owner: Operations Owner
- Scope: `04_Documentation/`, `01_Plans/`
- Related Backlog: `HIL-RS-02`
- Related ADR/Spec: `ADR-0027`, `ADR-0019`, `04_Documentation/operations.md`, `04_Documentation/security.md`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Expected verification level: `docs-check`

## 1) 背景

- A2をインターフェース前提として先行しても、A3運用文書を同期しないと検証・監査手順が実装想定と乖離する。
- AUTH-OPS-03 の固定語彙（役割、状態、D1〜D4）が運用文書間でズレると、監査時に同一事象を別状態として解釈してしまう。

## 2) 目的

- 可逆統合フローの運用手順、異常時ロールバック、監査証跡採取を運用文書へ反映し、A3の運用責務を矛盾なく固定する。

## 3) スコープ

- operations/security/e2e_testing の必要差分更新。
- project-progress-dashboard の A3 同期ログ更新。

## 4) 非スコープ

- 認証認可モデルの新規設計。
- backend API仕様変更。
- A1/A2 issue 本体変更。

## 5) 受入条件（AC）

- AC-1: 新運用手順が既存手順と矛盾しない。
- AC-2: ロールバック手順が明記される。
- AC-3: strict mode例外の状態遷移（`Requested/ApprovalPending` -> `Approved` -> `ExceptionActive/ActiveException` -> `RollbackPending` -> `Closed`、未確定時 `StoppedForClarification`）と2者承認責務が operations/security で一致している。
- AC-4: D1〜D4固定値（承認TTL=4h、最大2h、代理承認なし、48hレビュー+15m/60m）が operations/security 双方で一致している。
- AC-5: docs-checkが通過する。
- AC-6: dashboard に A3 同期証跡（Read/Plan/Execute/Verify/Proceed）が1行以上残る。

## 6) DoD（A3運用同期）

- DD-1: `operations.md` と `security.md` の責務語彙が一致（Security Officer / System Owner / Platform Operator）。
- DD-2: 状態語彙の差分（architecture canonical と運用 runbook alias）を明示し、意味差分ゼロを保証。
- DD-3: `e2e_testing.md` に docs-check 観点（相互リンク、用語一致、固定値一致）を反映。
- DD-4: `project-progress-dashboard.md` に Stream F A3 同期記録を残す。

## 7) ADR CDC（新規ADRは作成しない）

- Context:
  - 実装側の状態語彙と運用文書語彙がズレると、例外運用の停止/復旧判断が監査で分断される。
  - A2未完了でもA3文書同期を先行し、運用責務を固定する必要がある。
- Decision:
  - 同期対象は `operations.md` / `security.md` / `e2e_testing.md` / `project-progress-dashboard.md`。
  - 同期順序は `02_Architecture`（参照） -> `04_Documentation`（operations -> security -> e2e） -> `01_Plans`（dashboard）とする。
  - 固定語彙は役割3種、状態遷移、D1〜D4固定値を AUTH-OPS-03 準拠で統一する。
- Consequences:
  - 監査容易性（同一語彙・同一固定値）が向上する。
  - 文書変更時の同時同期コスト（cross-doc更新）が増える。

## 8) docs-check観点（明示）

1. 相互リンク: operations <-> security <-> e2e の参照導線が途切れていない。
2. 用語一致: 役割（Security Officer/System Owner/Platform Operator）、状態（StoppedForClarification等）が一致。
3. 固定値一致: D1〜D4（4h / 2h / no delegate / 48h + 15m/60m）が一致。

## 9) フェーズ進行ログ（Stream F）

### Phase 1: Read
- Plan: A3 issue + operations/security/e2e + dashboard を再読し、語彙・責務・状態・D1〜D4差分を抽出する。
- Execute: 対象5ファイルと `strict_mode_exception_approval_flow.md` を参照して差分棚卸し。
- Verify: `rg` で状態語彙/固定値/役割の出現位置を抽出し、ズレ候補を特定。
- Proceed: 差分候補を Plan入力として固定。

### Phase 2: Plan
- Plan: AC/DoD不足を補完し、docs-check観点（相互リンク・用語一致・固定値一致）をタスク化。
- Execute: AC-6 と DoD を追記し、検証コマンド群を整理。
- Verify: AC/DoD と検証手順が1対1に対応することを確認。
- Proceed: CDC明文化へ移行。

### Phase 3: ADR CDC明文化
- Plan: 新ADRを作らず、A3 issue 内に Context/Decision/Consequences を固定する。
- Execute: 本Issue 7章へ CDC を追記。
- Verify: Context=乖離リスク、Decision=同期対象/順序/固定語彙、Consequences=監査容易性向上+更新コスト増 を満たす。
- Proceed: 文書実更新へ移行。

### Phase 4: Execute
- Plan: operations/security/e2e/dashboard を同一語彙・責務・固定値へ同期。
- Execute: 役割分離語彙、状態遷移語彙、固定値チェック導線を更新。
- Verify: 4文書間の表記揺れ・固定値差分がゼロであることを確認。
- Proceed: docs-check実行へ移行。

### Phase 5: Verify
- Plan: docs-check、キーワード照合、差分整合を実施。
- Execute: validator + `rg` を実行し、必要なら自己修復（最大3回）。
- Verify: 失敗ゼロならProceed、未解消ならフェイルセーフ条件で停止。
- Proceed: 同期結果をA3 issueへ記録。

### Phase 6: Proceed
- Plan: 同期結果・未解決項目・次アクションを記録。
- Execute: 実行結果を本Issueとdashboardに反映。
- Verify: AC/DoD証跡が参照可能であることを確認。
- Proceed: 乖離が残る場合は停止して追加判断要求。

## 10) 検証方法

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `rg -n "StoppedForClarification|RollbackPending|Closed|Requested|ApprovalPending|Approved|ExceptionActive|ActiveException|Security Officer|System Owner|Platform Operator" 04_Documentation/operations.md 04_Documentation/security.md`
- `rg -n "承認TTL=4h|最大2h|代理承認なし|48h|15m|60m|D1|D2|D3|D4" 04_Documentation/operations.md 04_Documentation/security.md 04_Documentation/e2e_testing.md`

## 11) 依存関係

- `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md` はインターフェース前提として参照し、A3文書同期は独立実行する。

## 12) リスク / フェイルセーフ

- リスク: 運用文書の同期遅延で現場手順が旧仕様のまま残る。
- 停止条件:
  1. 3回修復失敗
  2. 用語統一不能
  3. 固定値不一致が解消不能
  4. 未定義競合
- 停止時は「失敗条件 / 影響文書 / 必要な人間判断」を記録して保留する。

## 13) 同期結果（Stream F 実行記録）

- operations/security/e2e/dashboard を同時同期し、役割・状態・固定値の整合を確認。
- 未解決項目: なし（本更新時点）。
- 次アクション: AUTH-OPS-03 更新時は 4.4 固定順序（Architecture -> Documentation -> Plans -> AGENTS）で再同期する。
