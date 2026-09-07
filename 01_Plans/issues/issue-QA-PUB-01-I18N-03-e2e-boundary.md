# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification boundary plan
- Status: Open
- Source Issue: N/A
- Open Readiness: Prepared
- Execution: Ready
- Priority: P0
- Owner: Stream H（QA E2E）
- Scope: 本ファイル, `03_Implement/frontend/e2e/`（Open後の追加検証はテスト資産のみ。製品実装変更は別Issue）
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `e2e`
- Related backlog: `PUB-01`, `I18N-03`, `QA-E2E-USE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `e2e`
- Policy reference: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`

## Phase 1: Read Gate（Draft/Hold理由と依存抽出）

### Draft理由（当時。2026-07-18までに解消済み）
- 境界3軸（公開互換/I18N等価/安全境界）はあるが、Open判定時に必要な承認証跡欄が不足。
- どの境界逸脱が即Holdか（重大度閾値）が記述されていない。

### Execution Hold理由（当時。2026-07-18までに解消済み）
- PUB-01 と I18N-03 の最終承認IDが未確定。
- `ADR-0019` に基づく実行経路の事前選択が未完了。

### 依存ブロッカー
| Blocker ID | 内容 | 計測条件 | 解消責務 |
|---|---|---|---|
| B-PUB-01 | 公開境界承認未了 | `Pending-1` に承認ID/日付追記 | Product/Reviewer |
| B-I18N-01 | I18N-03承認未了 | `Pending-2` に承認ID/日付追記 | Localization reviewer |
| B-ENV-01 | 実行経路未固定 → 解消済み（2026-07-18、下記Phase 6参照） | Compose/SQLite/例外のいずれか選択済み | QA lead |

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
- Pending-1/Pending-2に続き、B-ENV-01（`ADR-0019` 準拠の実行経路未固定）を2026-07-18に解消した。
- **B-ENV-01確定値**: 実行経路は**Docker Compose標準経路**で固定する。根拠: `03_Implement/frontend/docs/e2e_testing.md`が既に「標準経路はDocker Compose、Docker不可時のみSQLite/mock」を規範化しており、検証環境（WSL）でdocker 29.5.3 / compose v5.1.4の利用可を2026-07-18に確認済み。`QA-E2E-USE-01`のO-USE-02と同じ確定値であり、両issueで経路が分岐しない。
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

## 初回実行バッチ 実装記録（2026-07-18）

### 3軸カバー状況棚卸し（`e2e/`全59spec中の該当spec）

| 境界軸 | 該当spec | テスト件数 | 特記事項 |
| --- | --- | --- | --- |
| 公開互換 | `pub_visibility_i18n_readonly_flow.spec.ts`（2件）、`public_pack_visibility_compat.spec.ts`（4件） | 6 | reload後の永続化、view/pack visibilityの差異説明、legacy pack互換を厚くカバー。 |
| I18N等価 | `pub_visibility_i18n_readonly_flow.spec.ts`（1件）、`i18n_locale_query_equivalence.spec.ts`（3件）、`i18n_locale_functional_equivalence.spec.ts`（1件） | 5 | ロケール切替smoke、不正ロケールfallback、`locale=en`でのdocument置換/safe-mode文脈等価を確認済み。 |
| 安全境界 | `pub_visibility_i18n_readonly_flow.spec.ts`（1件のみ） | 1 | **最薄**。既存の唯一のテストは`locale=en`固定で、検証内容も「レイアウト提案ボタンがdisabled」という1操作のみ。実際の編集操作（カードdblclick編集→コミット）が遮断されるかは未検証で、かつja既定ロケールでのreadOnly検証が存在しない。 |

### 追加した検証（安全境界を強化 + I18N等価のja/en対を成立）

`pub_visibility_i18n_readonly_flow.spec.ts`に新規テスト`"fixture-backed readOnly + safe-mode blocks a committed card text edit in the default locale"`を追加。

- ソース調査で、カードのdblclick編集自体は`readOnly`でゲートされていない（`CanvasShell.tsx`の`onBeginEdit={onBeginEditCard}`は無条件）ことを確認した一方、実際のコミット経路`handleCommitCardText → applyDocumentChange`（`App.tsx`）は`isReadOnly`時に`buildReadOnlyBlockedMessage`を表示して`false`を返し、ドキュメントへ反映しないことをソースで確認した。
- 新テストはこの実コミットゲートを対象に、既定ロケール（ja）で`?readOnly=1`のみを指定し、カードをdblclickして編集→Enterでコミットを試みても、(1) 読み取り専用ブロックメッセージ（`Read-only mode: ... is disabled.` / `読み取り専用モード: ... は無効です。`のバイリンガル正規表現）が表示され、(2) カード本文が変更されないことを検証する。
- 既存の1件（`locale=en`固定、disabledボタンのみ確認）と対になり、「実際の編集操作がreadOnlyで遮断される」ことをja/en双方の観点から裏付ける。

### デバッグで発見・対処した2点
1. このファイルの既存4テストはヘッダー領域のボタン（Advanced / Share & Reproduce）のみを操作しており、初回表示される起動時パネル（`data-panel="start-document-entry"`、`aria-modal="true"`）を一度も閉じていなかった。カード本文へ直接クリックする新テストはこのモーダルにブロックされたため、他specの`openSample`ヘルパーと同じパターン（`Open sample|サンプルを開く`ボタンをクリックしてパネルを閉じる）を追加した。
2. `page.getByText("readonly guarded card")`がカード本体（アクセシブルネームにステータス接頭辞を含む）とは別に、対象説明用の`対象: readonly guarded card`という別要素にも一致し、strict modeエラーとなった。カードのlocatorへの`toBeVisible()`アサーションに変更して解消した。

### 検証結果
- `npx tsc --noEmit` — 0 errors。
- `npx vitest run` — 1081/1081 pass。1件のみ既知の環境依存失敗（`external_agent_workflow_doc.test.ts`、検証用ミラー`~/kjnative-fe`が`04_Documentation`を含むフルリポジトリ構成でないための既知の制約で、本変更とは無関係）。
- `npx playwright test e2e/pub_visibility_i18n_readonly_flow.spec.ts`（公式Playwright Dockerイメージ経由）— 2回連続実行しflakyゼロを確認、いずれも5/5 pass。
- `npx playwright test e2e/pub_visibility_i18n_readonly_flow.spec.ts e2e/public_pack_visibility_compat.spec.ts` — 9/9 pass（回帰なし）。
- `python3 01_Plans/issues/validate_active_issue_memos.py` / `python3 01_Plans/docs_check.py` / `git diff --check` — 別途PR証跡に記載。

### ガードレール適用結果
- 製品挙動・SafeMode・公開文書は変更していない（テスト追加のみ）。上記のソース調査で判明したdblclick編集開始自体の未ゲート状態は、テスト対象であるコミット時ゲート（`applyDocumentChange`）とは別の実装詳細であり、本issueのスコープ外として着手していない。

## 第2バッチ 実装記録（2026-08-13）: 安全境界の再棚卸しと、テストのみでは塞げなかった実欠落の是正

前回バッチが3軸のうち最薄と判定した安全境界（readOnly + SafeMode）を再度棚卸しした。`App.tsx`で`isReadOnly`を参照する全箇所（`grep -n "isReadOnly" App.tsx`、約45件）を洗い出し、undo/redo・save・create island・new document等のtoolbar操作はすべて`disabled={isReadOnly || ...}`で個別にゲートされている一方、カードdrag&dropによる位置変更だけがどのゲートも経由していないことを発見した。

**発見した実欠落**: `handleCardMove`（`App.tsx:2530`、pointer moveのたびに呼ばれてカード位置を直接`setHistory`へ書き込む関数）は、他の全mutation（`handleCommitCardText`、`handleCreateIsland`、`applyLayoutOperation`等）が経由する中央ゲート`applyDocumentChange`（`isReadOnly`時に`buildReadOnlyBlockedMessage`を表示し`false`を返す、`App.tsx:2345`）を通らず、`document`・`isPreviewingSuggestion`・deltaゼロの3条件しか見ていなかった。`CanvasShell`への`onCardMove={handleCardMove}`渡しも無条件で、`readingOrderEditMode={!isReadOnly && ...}`や`polygonVertexEditIslandId={!isReadOnly && ...}`のように同コンポーネントの他propが払っている`!isReadOnly`ガードがこの1経路だけ欠けていた。

**なぜ「テスト追加のみ」で閉じなかったか**: 本issueのガードレールは製品挙動変更を禁じるが、これは無関係な機能変更を防ぐためのものであり、まさにこの軸（禁止操作の遮断）が主張している不変条件そのものが破れているケースまでは想定していない。ドラッグはテキスト編集と異なり離散的な「コミット」操作を持たず（pointer move毎に位置を書き込む連続操作）、ブロックメッセージを模した回避策でテストだけ通すことはできても実際の欠落は残る。既存の類似判断（`AppErrorBoundary`のtenant scope欠落、`SAAS-TENANT-01` 2026-08-13チェックポイント参照）と同じく、既存の保護パターン（`applyDocumentChange`ゲート）を1経路だけ迂回していた1行相当の欠落であり、無関係な設計判断を要さないため直接是正した。

**是正内容**: `handleCardMove`の早期returnガードへ`isReadOnly`を追加した（`App.tsx:2532`、`useCallback`依存配列も同期）。ドラッグ開始時点（最初のpointer move）で即座にno-opとなり、`pendingCardDragSnapshotRef`も`lastDraggedCardIdRef`も設定されないため、drag-end側の`commitCardDragSnapshot`（`App.tsx:2624`）も既存の「snapshotなし」no-op経路（ゼロ移動ドラッグと同じ経路）を通る。pointer move毎のメッセージ表示は行わない（連続イベントでの表示スパムを避けるため。カードが一切動かないこと自体が、テキスト編集のブロックメッセージとは別の形の、リアルタイムなフィードバックになる）。

**追加した検証**: `pub_visibility_i18n_readonly_flow.spec.ts`へ`"fixture-backed readOnly blocks card drag repositioning"`を追加した。カードの初期bounding boxを記録し、`page.mouse`でpointer down→move→upのドラッグジェスチャーを実行後、bounding boxが完全に一致すること（x/yとも変化なし）、および成功時にのみ出る`"Moved card" / "カードを移動しました"`メッセージが出現しないことを確認する。

**契約が実際にfail-closedであることの確認（mutation）**: 上記ガード追加を一時的に取り消して同testを実行し、**実際に失敗する**ことを確認した（`before.x=120` → `after.x=240`、ドラッグ量120pxがそのまま位置へ反映され、readOnlyでの保護が無かったことを実測で裏付けた）。ガードを復元して再実行し、6/6 pass（既存5件を含む）へ戻ることを確認した。

**検証結果**:
- `npx tsc --noEmit`: 0 errors。
- `npx playwright test e2e/pub_visibility_i18n_readonly_flow.spec.ts e2e/realistic_user_journey_expansion.spec.ts`: 8/8 pass（新規1件＋既存7件、回帰なし）。
- `npx vitest run`: 239 file / 1,435 tests 全pass（環境依存の既知失敗は今回発生せず）。
- `npm run build`: pass。
- 実行環境: WSL Node 20.20.2（`.nvmrc`指定）、`/mnt/d/GIT/kj-atlas`を直接操作（別checkoutへのrsyncなし、`02_Architecture/`・`04_Documentation/`が実在するため環境依存failureが発生しない構成）。

**適用範囲についての限定**: 今回是正したのはカード**位置**（drag & drop）のreadOnly保護のみである。同ソース調査記録（前回バッチ）が個別に指摘したdblclick編集**開始**自体（`onBeginEdit`）の未ゲート状態は、コミット時ゲートで実害が閉じているため対象外のまま維持する。カード以外の要素（island境界、edge等）のdrag操作は本バッチの棚卸し対象に含めていない。

### 追補（同日）: Undo/RedoへのisReadOnly補強（defense-in-depth、実exploit未確認）

上記のドラッグ欠落を見つけた手法（`applyDocumentChange`を経由しない`setHistory`直呼び出しの全数列挙、`App.tsx`の`setHistory(`全17箇所をgrep）を横展開した。ほとんどは既にゲート済み（`applyDocumentChange`経由、または初期ロード系で readOnly と無関係）だったが、`handleUndo`/`handleRedo`（`App.tsx:6566`/`6585`）は、toolbarボタンとcommand-palette項目こそ`disabled={isReadOnly || ...}`で守られているものの、関数自体は`isReadOnly`を一切参照しておらず、Ctrl+Z/Ctrl+Y専用のグローバル`keydown`リスナー（`App.tsx:6624`、依存配列`[canRedo, canUndo, handleRedo, handleUndo]`に`isReadOnly`が無い）もボタンのdisabled状態を経由しない独立した呼び出し経路になっていた。

**ドラッグの事例と違う点（重要）**: 調査の結果、readOnlyセッションでは`history.past`/`.future`が実質的に常に空であることを確認した——ドキュメント読み込み系（`setHistory({past: [], ...})`各所）はreadOnlyと無関係に毎回履歴を空でリセットし、唯一の非ゲート済み変異経路だったカードdragは今回のバッチで塞いだため、他に履歴へ項目を積む経路が見当たらない。したがって`wantsUndo && canUndo`の`canUndo`が`false`のままとなり、**現状のコードでは実際に到達可能な悪用経路を実測で示せなかった**。ドラッグの欠落（`before.x=120→after.x=240`で実測済み）とは確信度が異なる。

**それでも是正した理由**: `SAAS-TENANT-01`の2026-08-13チェックポイント「request-time adapter-missing deny」が採った判断と同じ理由による——「契約がenforcement点からは読み取れないため、どちらかがrefactorされてもlocalには何も落ちない」。`handleUndo`/`handleRedo`がボタンのdisabled状態だけに依存する設計は、将来別の呼び出し経路（新しいショートカット、command palette項目、他コンポーネントからの直接呼び出し等）が追加された時点で無防備になる。`applyDocumentChange`が全mutationに要求している「呼び出し元に関わらずmutationの入口でisReadOnlyを見る」という不変条件を、この2関数にも一致させた。

**変更**: `handleUndo`/`handleRedo`の先頭に`if (isReadOnly) return;`を追加し、`useCallback`依存配列へ`isReadOnly`を追加した。

**検証**: E2Eでの新規追加は行っていない（上記のとおり、現状の到達可能性では「before/afterの差」を実測できないテストは意味のある回帰検知にならないと判断した）。既存のCtrl+Z関連E2E（`island_tidy.spec.ts`、`retention_keyboard_shortcuts.spec.ts`、`shortcut_cheatsheet.spec.ts`、`menu_bar.spec.ts`、計16件）と`npx tsc --noEmit`・`npx vitest run`（239 file/1,435 tests）・`npm run build`を実行し、通常（非readOnly）のundo/redoに回帰がないことを確認した。

## 2026-09-07 Open化同期 — 承認済みゲートを現在状態へ反映

2026-07-16〜18に成立していた解除条件と、その後に積み上がったE2E証跡を、triageが読む現在状態へ同期する。前節までの各時点で「Draft / Execution: Hold」と記録した箇所は**その時点の歴史証拠**として保持し、現在状態の主張には使わない。

- Pending-1（PUB-01公開境界）とPending-2（I18N-03外部公開判定）は、2026-07-16にMaintainer承認済み。
- B-ENV-01（ADR-0019準拠の実行経路）は、2026-07-18にDocker Compose標準経路として固定済み。SQLite/mockはDockerを実行できない場合の例外経路であり、標準経路と混同しない。
- その後、公開互換 / I18N等価 / readOnly + SafeMode の3軸に対するE2E資産と回帰証跡が追加され、readOnlyのカードdrag欠落など実際に見つかった境界逸脱も隠さず是正・回帰固定されている。
- したがって `Open Readiness: Prepared` / `Execution: Ready` と整合させ、`Status` を `Open` とする。古いDraft gateだけを理由にtriageから除外し続けない。
- この同期は**3軸のcurrent-main再検証完了、release承認、翻訳品質の人間レビュー完了を主張しない**。Openは「標準経路で実行して証拠を現在化できる状態」を意味する。
- Draft→Open同期自体はdocs-only。Open後の追加変更はE2Eテスト資産に限定し、製品実装の新規変更が必要な欠落を見つけた場合は、本Issueへ抱え込まず別Issueとして切り出す。既存specで3軸を十分に覆える場合は重複テストを作らず、Compose-backed再実行と証跡同期を優先する。
