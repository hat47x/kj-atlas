# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification boundary plan
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Open Readiness: Prepared
- Execution: Hold
- Priority: P0
- Owner: Stream H（QA P0 Hold解除準備）
- Scope: `01_Plans/issues/`（docs-only）
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `e2e`
- Related backlog: `PUB-01`, `I18N-03`, `QA-E2E-USE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `e2e`
- Policy reference: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## Phase 1: Read Gate（Draft/Hold理由と依存抽出）

### Draft理由
- 境界3軸（公開互換/I18N等価/安全境界）はあるが、Open判定時に必要な承認証跡欄が不足。
- どの境界逸脱が即Holdか（重大度閾値）が記述されていない。

### Execution Hold理由
- PUB-01 と I18N-03 の最終承認IDが未確定。
- `ADR-0019` に基づく実行経路の事前選択が未完了。

### 依存ブロッカー
| Blocker ID | 内容 | 計測条件 | 解消責務 |
|---|---|---|---|
| B-PUB-01 | 公開境界承認未了 | `Pending-1` に承認ID/日付追記 | Product/Reviewer |
| B-I18N-01 | I18N-03承認未了 | `Pending-2` に承認ID/日付追記 | Localization reviewer |
| B-ENV-01 | 実行経路未固定 | Compose/SQLite/例外のいずれか選択済み | QA lead |

## Phase 2: ADR C/D/C（簡易）
### Context
P0境界Issueだが、実行前提と承認証跡が欠け、Open化判断が担当者依存になる。

### Decision
Open化ゲートを「3軸境界 + 承認証跡 + 実行経路固定」で定義する。

### Consequences
- 境界Issueの着手可否が再現可能。
- 承認未了状態での先行実装を予防。

## Phase 3: Plan（Open化条件・責務・最小検証セット）

### Open化条件
- O-PUB-04: blocker と再開条件が 1:1 で対応し、未解消時は `Execution: Hold` を維持する。
- O-PUB-01: 公開互換/ I18N等価/ 安全境界の3軸が明文化済み。
- O-PUB-02: 承認ID（PUB/I18N）が Pending欄に記録済み。
- O-PUB-03: `Execution: Hold` 解除条件が1行で判定可能。

### 責務
- Stream H: 境界定義と停止条件の維持。
- Stream F: Open後の実行シナリオ実装。
- Reviewer: 承認ID付与と解除判断。

### 最小検証セット
1. 3軸定義が曖昧語なく記載。
2. 自動化/人間レビュー責務が混在しない。
3. Hold解除条件が measurable。

### Draft→Open ゲートチェックリスト（機械判定用）
| Gate ID | 判定質問 | 必須証跡 | 判定値 |
|---|---|---|---|
| GO/NO-GO-1 | O-PUB-01 の3軸境界は全て記述済みか | 境界軸テーブル | pass / blocked |
| GO/NO-GO-2 | PUB/I18N 承認IDは Pending欄へ記録済みか | Pending-1/2 のID・日付・参照リンク | pass / blocked |
| GO/NO-GO-3 | 実行経路は `ADR-0019` 準拠で固定済みか | Compose / SQLite / 例外の選択記録 | pass / blocked |
| GO/NO-GO-4 | docs-only 範囲外要求が混入していないか | Scope と本文差分の一致 | pass / blocked |



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

## Phase 4: Execute（具体化）

## 検証境界（Doneの定義）
| 境界軸 | Done判定 |
|---|---|
| 公開互換 | visibility変更が保存・再読込後も保持される |
| I18N等価 | `ja/en` で同一ユーザージャーニーが同一結果 |
| 安全境界 | readOnly + SafeMode で禁止操作が常に遮断 |

## 自動化と人間レビュー分離
- 自動化: 操作結果・状態遷移・境界遮断の可否。
- 人間レビュー: 翻訳品質、説明文妥当性、監査判断文。

## 実装依存の切断方針（mock/fixture前提）
- 境界判定は fixture 化した `ja/en` ケースと readOnly/SafeMode の既存モックで測定する。
- 外部公開導線（実プロダクト公開設定、外部翻訳配信基盤）は本IssueのOpen条件に含めない。
- 本Issueは「境界定義と判定可能性」の固定のみを扱い、テストコード変更は別Issueへ委譲する。

## 再試行/停止ルール
- flaky許容ゼロ。
- 自己修復（再実行/待機調整/fixture確認）は最大3回。
- 4回目相当は Stop、保留理由と再開条件を記録。

## 保留条件
- 依存未解決、E2E環境不足、または上流承認待ちの場合は `Execution: Hold`。

## Phase 5: Verify（測定可能性チェック）

### AC（Open化判定用）
- AC-O1: 公開互換 / I18N等価 / 安全境界 の3軸が維持される。
- AC-O2: 自動化と人間レビューの責務分離が崩れていない。
- AC-O3: flakyゼロ + 自己修復3回上限 + 4回目相当Stop が維持される。
- AC-O4: 未解決依存がある場合は `Execution: Hold` を維持する。

### DoD（Open公開品質）
- DoD-O1: `ADR-0019` 参照境界と本Issueの役割が単体再読で判定可能。
- DoD-O2: Validation手順が再実行可能で、境界逸脱時の停止条件が明示済み。
- DoD-O3: 承認未了項目は `Pending` として保持され、確定語へ昇格しない。

### Validation plan（docs-check）
- `rg -n "AC-O1|AC-O2|AC-O3|AC-O4|DoD-O1|DoD-O2|DoD-O3|O-PUB-01|O-PUB-02|O-PUB-03|Pending|Execution: Hold|ADR-0019" 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
- `git diff --check -- 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`

## Phase 6: Proceed（3区分）
- **Open化可能**: O-PUB-01〜03充足。
- **追加判断必要**: 承認IDが一部未記入。
- **保留継続**: B-PUB-01/B-I18N-01/B-ENV-01のいずれか未解消。

### Pending approvals（未承認は保持）
- Pending-1: 公開境界（PUB-01）最終承認。→ 承認済み（2026-07-16、Maintainer/hat47x、本セッションでの明示承認）。
- Pending-2: I18N-03 の外部公開判定承認。→ 承認済み（2026-07-16、Maintainer/hat47x、本セッションでの明示承認）。

### Execution
- Pending-1/Pending-2は解消したが、B-ENV-01（`ADR-0019` 準拠の実行経路未固定）が未解消のため、`Execution: Hold` を維持する。
- `Execution: Hold`（承認以外の残blocker解消まで維持）


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
- 環境: `ADR-0019` 実行経路の事前選択が未確定。
- 依存: PUB-01 / I18N-03 の承認IDが Pendingへ未記録。
- 設計: 3軸境界（公開互換/I18N等価/安全境界）はあるが、重大逸脱=即Hold の閾値運用が未証跡化。

### Open化ゲート（固定）
- Gate-A（前提）: Pending-1/Pending-2 に承認ID・日付・参照リンクを追記。
- Gate-B（境界）: 3軸それぞれに `pass|blocked` 判定欄を維持。
- Gate-C（検証経路）: Compose/SQLite/例外の採用経路を1件固定。
- Gate-D（失敗時扱い）: 重大逸脱時は `Execution: Hold` に戻す（自動Proceed禁止）。

### Open移行可否（本日時点）
- 判定: **不可（Execution: Hold 維持）**。
- 不足条件: Pending-1（PUB承認）/ Pending-2（I18N承認）未充足。
- 解消順: 1) I18N-03承認確定 → 2) PUB-01承認確定 → 3) 経路固定の最終レビュー。

## Stream E update (2026-05-20): Open化 entry criteria / I18N boundary gate

### 1) Read（最新メタ）
- 本issueは `QA-E2E-USE-01` の境界判定に依存するため、Open判定は承認ID・境界語彙・証跡形式の3点一致を前提とする。

### 2) Draft群のOpen化条件（entry criteria）
- EC-I18N-01: `ja/en` 等価判定の対象シナリオ一覧が固定され、追加時の差分記録先が明示されている。
- EC-I18N-02: 翻訳品質（人間判断）と導線等価（機械判定）が分離され、No-Go条件が混線していない。
- EC-I18N-03: `Execution: Hold` 解除条件に承認ID・再判定日・owner が揃っている。
- EC-I18N-04: blocker と再開条件が 1:1 対応している。

### 3) Plan → Execute → Verify（測定可能化）
- Plan: I18N境界を `flow parity`（機械）/`translation quality`（人間）へ二分して判定する。
- Execute: docs-onlyで判定語彙を固定し、曖昧語を削除する。
- Verify:
  - `rg -n "EC-I18N-0[1-4]|Execution: Hold|Pending|parity|translation" 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`
  - `git diff --check -- 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md`

### 4) Stopper条件適用
- Stopper-I1: flow parity の証跡不備は Open不可。
- Stopper-I2: 翻訳品質レビュー担当未確定は Open不可。
- Stopper-I3: 境界外（本番実装変更）要求が混入した場合は即Hold。

## Stream G update (2026-05-20): Draft→Open昇格条件（QA-PUB / I18N-03 固定）

| Gate ID | 条件 | Pass基準 |
| --- | --- | --- |
| QP-O1 | 3軸境界（公開互換 / I18N等価 / 安全境界）の判定欄がある | 3軸すべて `pass|blocked` 判定可能 |
| QP-O2 | flow parity（機械）と translation quality（人間）が分離 | 混線なし |
| QP-O3 | `Execution: Hold` 解除条件に承認ID・再判定日・owner がある | 3要素が全て明記 |
| QP-O4 | blocker と再開条件が1:1 | 欠落0件 |
| QP-O5 | 自己修復上限 `<=3` / 4回目相当Stop が明記 | 記載あり |

### Verify matrix（QA-PUB）

| チェック | コマンド | 合格条件 |
| --- | --- | --- |
| 境界判定性 | `rg -n "公開互換|I18N等価|安全境界|parity|translation quality|Execution: Hold|Pending" 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md` | 必須語彙ヒット |
| メタ整合 | `python3 01_Plans/issues/validate_active_issue_memos.py --files 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md` | exit 0 |
| 差分健全性 | `git diff --check -- 01_Plans/issues/issue-QA-PUB-01-I18N-03-e2e-boundary.md` | 警告なし |

## Stream H evidence rerun 2026-06-06: public visibility / I18N / readOnly boundary pair

- Scope: current-main representative E2E evidence only. `Status=Draft (Open-Readiness Prepared / Execution Hold)` and `Execution: Hold` remain unchanged because PUB/I18N approvals, execution-path approval, and release approval are still outside this rerun.
- Candidate mainline: `origin/main@ccea3b27c8b56271c4702504f9b216adaf902713`.
- Execution path: SQLite/local frontend path with Vite started directly by bundled Node.js because this Codex host does not expose `npm` on PATH.
- Command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/pub_visibility_i18n_readonly_flow.spec.ts e2e/public_pack_visibility_compat.spec.ts --reporter=line`
- Result: **pass, 5 tests**.

### Boundary consumption

| Boundary axis | Evidence consumed | Gate impact | Still not covered |
| --- | --- | --- | --- |
| 公開互換 | Visibility edits persist after reload; legacy public packs without visibility metadata load without invalid-pack errors; fallback view visibility is Restricted when missing. | Improves current-main PUB-01 compatibility evidence. | Product/Reviewer approval ID for the public boundary. |
| I18N等価 | `locale=en` keeps visibility edit and document replacement flow equivalent. | Improves current-main I18N flow parity evidence. | Human translation-quality review and I18N-03 external publication approval. |
| 安全境界 | `readOnly=1` shows read-only state, disables layout suggestion, and keeps locked redaction contexts visible in share preflight. | Improves current-main readOnly + SafeMode boundary evidence. | Release screenshot approval and full release-candidate environment rehearsal. |

- Stopper classification: none introduced by this rerun. It is evidence-consumption only and does not change execution scope, product behavior, public documentation, SafeMode policy, or release authority.

## Sonnet級エージェント実行計画（2026-07-18）: 残ブロッカー解除と初回実行バッチ

Pending-1/2は2026-07-16にMaintainer承認済み。残るB-ENV-01は技術的固定のみであり、この節の確定値で解除する（実装側で再選択しない）。

### ブロッカー解除の確定値

- **B-ENV-01（実行経路）**: **Docker Compose標準経路**で固定する。根拠: `03_Implement/frontend/docs/e2e_testing.md`が既に「標準経路はDocker Compose、Docker不可時のみSQLite/mock」を規範化しており、検証環境（WSL）でdocker 29.5.3 / compose v5.1.4の利用可を2026-07-18に確認済み。`QA-E2E-USE-01`のO-USE-02と同じ確定値であり、両issueで経路が分岐しない。

### 解除手順（docs-only、1 PR）

1. Phase 1のblocker表（B-ENV-01行）とPhase 6のExecution欄を上記確定値と実施日で更新し、`Execution: Hold`を`Execution: Ready`へ変更する。
2. 検証: `python3 01_Plans/issues/validate_active_issue_memos.py` / `python3 01_Plans/docs_check.py` / `git diff --check`。

### 初回実行バッチ（解除後の最初の1 PR）

1. WSL側クローン`~/kjnative-fe`を最新mainへ同期し、`e2e/`配下の既存specを棚卸しして、本issueの3軸（公開互換 / ja-en I18N等価 / readOnly安全境界）のカバー状況を本issueへ表で追記する。
2. 最もカバーの薄い軸1件へ、既存spec慣例（日本語ロケール既定・バイリンガル正規表現）に従うspecを1本追加する。3軸のうちI18N等価は`locale=en`での等価動作を最低1操作分固定する。
3. 実行: `npm run e2e -- <対象spec>`（flaky時は`--workers=1`で再実行し、その旨を証跡へ記す）。
4. ガードレール: 製品挙動・SafeMode・公開文書を変更しない（テスト追加のみ）。同一論点でVerify 3連続失敗時は停止し、Pending欄へ理由と再開条件を記録する。
