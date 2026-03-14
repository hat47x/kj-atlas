# 01_Plans Issue Memo Index

このディレクトリは、GitHub Issue（正本）を補助する **短命メモ** を管理する。
Decisionは ADR、Action は issue memo で管理し、本ディレクトリは再開性の補助に限定する。

> Performance note for AI agents: issue memo が増えても全件を都度読む必要はない。対象Backlog ID/関連ADR/作業スコープに一致するメモのみ参照する。

## Scope

- 対象: Active な issue 補助メモ（Draft / Open / In Progress）
- 正本: 現在運用では issue memo を正本として扱う（GitHub Issues は**未運用**、将来再開は可能）
- ライフサイクル: Draft -> Open -> In Progress -> Done（Done (Local) は廃止）
- ライフサイクル定義は本READMEのみを正とする。個別issue memoには記載しない。
- Done メモは自動GCしない（手動削除のみ）

## Start here（人間 / 生成AI 共通）

1. `TEMPLATE.md` をコピーして起票草案を作成する。
2. `Type / Priority / Scope / Related ADR` を先に埋める。
3. `Expected verification level`（`docs-check` / `unit` / `integration` / `e2e`）を先に宣言する。
4. 受入条件（Acceptance criteria）と検証計画（Validation plan）を先に確定する。
5. `Source Issue` は運用状態に応じて記載する（未運用時は `N/A`、GitHub Issues運用時はURL）。


## DOC-OPS-02 同期チェック（実行前に確認）

- 用語: `正本 / 暫定メモ / 決裁入力 / 例外承認` を `ADR-0022` と一致させる。
- 役割: AUTH系（`Security Officer / System Owner / Platform Operator`）と DOC系（`Platform Architecture Owner / Plan Owner / Architecture Owner`）の責務境界を分離する。
- 導線: `02_Architecture/strict_mode_exception_approval_flow.md` → `04_Documentation/operations.md` / `04_Documentation/security.md` → `01_Plans/issues/README.md` / `01_Plans/project-progress-dashboard.md` の順に同期する。
- 固定値（D1〜D4）: `承認順序=Security Officer先行 + 承認TTL=4h / scope=tenant最大2h / 代理承認なし / 48hレビュー + 15m一次 + 60m二次` を変更しない。

## Source Issue 運用基準（Traceability）

### 現在の運用判定（2026-03-03 時点）

- 判定: **GitHub Issues 正本運用は未開始**。
- 根拠: 本READMEの `Scope` に「GitHub Issues は未運用」と明記され、`Active issue memos` の `Source Issue` が `N/A` で統一されている。
- 実務ルール: PM/Triage の開始宣言が行われるまで、`Source Issue` は `N/A` を維持する。

### `Source Issue: N/A` を継続できる条件

- GitHub Issues を正本としてまだ運用開始していない（本READMEの `Scope` と一致）。
- 対象タスクが issue memo 内で完結し、外部トラッカー参照を必須としていない。
- `Active issue memos` 表の `Source Issue` 列が `N/A` で統一管理されている。

### GitHub Issues URL に移行する条件

- PM/Triage が「GitHub Issues を正本として運用開始」と明示した時点。
- 既存 `Open / In Progress` メモを更新するタイミングで、`Source Issue` を対応するURLへ置換する。
- 新規メモは起票時からGitHub Issue URLを必須とし、`N/A` は使用しない。

### GitHub Issues 正本運用の開始宣言ドラフト（PM/Triage）

> 本節はドラフトであり、実際の宣言時に日時とリンクを確定して使用する。

```md
[開始宣言] GitHub Issues 正本運用を開始します

- 宣言日時（JST）: 2026-03-XX XX:XX
- A（Accountable）: Platform Architecture Owner
- R（Responsible）: PM/Triage
- 告知先:
  1. `01_Plans/issues/README.md`（本ファイル）
  2. GitHub Discussions: `#project-ops`（運用告知スレッド）
  3. 対象移行PR本文（RACI-I記録付き）

本宣言以降、Active issue memo の `Source Issue: N/A` は次回更新PRで GitHub Issue URL へ移行する。
```

> 停止条件: A または R が未確定（役割が未割当）の場合、宣言を出さずに `N/A` を維持し、未確定項目を `Additional context` に記録して停止する。

### Active memo `Source Issue: N/A` → URL 移行Runbook（手順1〜6）

1. **開始宣言の確定**
   - 上記ドラフトの `宣言日時` を確定して README に追記し、RACI-I通知を1回記録する。
2. **URL対応表の作成**
   - Active issue memo ごとに `Backlog ID -> GitHub Issue URL` の1:1対応表を作成する。
3. **置換コミット（memo本体）**
   - Active memo の `Source Issue: N/A` を URL に置換する。
   - 同一コミットで `Status` / `Owner` / `Acceptance criteria` / 本文タスクは変更しない。
4. **置換コミット（index同期）**
   - `Active issue memos` 表の `Source Issue` 列を同一URLへ同期する。
5. **検証コマンド実行**
   - `python 01_Plans/issues/validate_active_issue_memos.py`
   - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
   - `rg -n "^- Source Issue: N/A$|\|[^|]*\|[^|]*\|[^|]*\| N/A \|" 01_Plans/issues`
6. **完了記録と通知**
   - 完了判定（`N/A`残存ゼロ + validator成功）をPR本文に記録し、RACI-I通知を確定する。

### RACI-I通知テンプレートと実施順序（誰がいつ通知するか）

- **A（Accountable）**: Platform Architecture Owner（最終承認・開始宣言確定）
- **R（Responsible）**: PM/Triage（実作業実行・通知送信）
- **C（Consulted）**: 各Issueの実行Lead
- **I（Informed）**: QA Lead

通知テンプレート（固定）:

```md
[RACI-I] Backlog=<Backlog ID> / Change=<Source Issue N/A→URL または開始宣言> / By=<role> / Memo=<memo path> / Source=<issue URL>
```

実施順序（固定）:

1. **R（PM/Triage）** が開始宣言案を作成して A に提示する（宣言前）。
2. **A（Platform Architecture Owner）** が開始宣言を確定し、READMEへ反映する（宣言時点）。
3. **R（PM/Triage）** が `Source Issue` 置換PRを作成し、テンプレで I（QA Lead）へ通知する（置換コミット作成時）。
4. **A（Platform Architecture Owner）** が検証結果と監査チェックを承認し、最終通知を確定する（マージ直前）。

### 置換コミット監査ルール（`Source Issue` 以外を変更しない）

チェックリスト:

- [ ] 置換対象ファイルは Active issue memo と `01_Plans/issues/README.md` の `Active issue memos` 表のみ。
- [ ] `git diff --word-diff` で `Source Issue` 行以外に差分がない。
- [ ] `Status` / `Owner` / `Priority` / `Acceptance criteria` / `Task breakdown` の差分が0件。
- [ ] 置換後URLは `https://github.com/<org>/<repo>/issues/<number>` 形式。
- [ ] validator と unit test が成功している。

監査コマンド（例）:

- `git diff -- 01_Plans/issues/README.md 01_Plans/issues/issue-*.md`
- `git diff --word-diff -- 01_Plans/issues/README.md 01_Plans/issues/issue-*.md | rg -n "Source Issue|Status|Owner|Priority|Acceptance criteria|Task breakdown"`

### ロールバック条件（宣言延期時の N/A 維持ルール）

- A または R が未確定（役割が未割当）の場合、開始宣言を延期し、`Source Issue: N/A` を維持する。
- URL対応表が Active memo と1:1対応しない場合、置換を中断して `N/A` 維持へ戻す。
- validator 失敗または監査チェック未達の場合、置換コミットをrevertし `N/A` を維持する。
- 延期時は理由・未確定項目・次回確認期限を `Additional context` またはPR本文に残す。

### 移行完了判定（Done条件）

- Active issue memos と対象memo本体の `Source Issue: N/A` が **残存ゼロ** である。
- `python 01_Plans/issues/validate_active_issue_memos.py` が成功する。
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` が成功する。

### URL移行の実施手順（運用開始後）

1. PM/Triage が「GitHub Issues 正本運用開始」を宣言し、開始日と告知先を本READMEへ追記する。
2. Active memo ごとに GitHub Issue を1:1で紐付け、`Source Issue` にURLを記載する。
3. 置換コミットは **`Source Issue` のみ変更**（`Status`/`Owner`/`Acceptance criteria` は同一コミットで変更しない）。
4. `Active issue memos` 一覧の `Source Issue` 列も同一PR内でURLへ同期する。
5. `python 01_Plans/issues/validate_active_issue_memos.py` を実行し、index/memo不整合がないことを確認する。
6. RACI-I通知を1回記録し、`Backlog ID` ごとに参照先URLが追跡可能であることを確認する。

### 運用手順（N/A維持 / URL移行）

1. **N/A維持フェーズ（現行）**
   - 新規 issue memo は `Source Issue: N/A` で作成する。
   - `Status` は `Draft/Open/In Progress` のみを使用し、`Active issue memos` 表と一致させる。
   - 外部トラッカー参照が必要になった時点で、`Additional context` に移行要求を記録する。
2. **URL移行フェーズ（将来）**
   - PM/Triage の運用開始宣言日を `README.md` に追記する。
   - Active な全 memo について、`Source Issue: N/A` を対応URLへ同一PRで置換する。
   - 置換PRでは `Status` を変えず、`Source Issue` だけを更新して監査差分を最小化する。
3. **移行完了判定**
   - `Active issue memos` 表に `N/A` が残っていないこと。
   - `python 01_Plans/issues/validate_active_issue_memos.py` が成功すること。

> 安全装置: 運用開始時期や移行責任者が未確定な場合、`N/A` のまま固定しない。該当メモの `Additional context` に確認事項として記録し、`Status` は `Draft` または `Open` で停止する。

## ステータス更新責任（Open → In Progress → Done）

| 遷移 | 更新責任者 | 更新タイミング（固定） |
|---|---|---|
| Draft → Open | **A**（Platform Architecture Owner） | 受入条件・Validation plan・RACIが揃い、着手可能と判断した時 |
| Open → In Progress | **R**（各Issueの実行Lead） | 最初の実作業コミット/PR/文書差分を開始する直前 |
| In Progress → Done | **A**（Platform Architecture Owner） | `Acceptance criteria` 完了と `Validation plan` 実施結果が確認できた時 |

- R は更新提案（ステータス変更PR/コミット）を行い、A が最終確定する。
- 責任者が未確定（R/Aの指名なし）の場合は遷移させず、確認事項として停止する（推測で確定しない）。

## RACI-I 通知ルール（PM/Triage, QA Lead）

- 通知対象（I）: `PM/Triage`, `QA Lead`。
- 通知トリガー（固定）:
  - `Status` 変更時（Open化 / In Progress化 / Done化）
  - `Source Issue` の `N/A ↔ URL` 切替時
  - `Owner` または `Expected verification level` を変更した時
- 通知内容（最小）: `Backlog ID` / 変更項目（StatusまたはSource Issue等）/ 更新者 / 参照リンク（issue memo + Source Issue）。
- 通知手段: PR本文または関連スレッドに同一フォーマットで1回記録し、重複通知しない。
- 記録フォーマット（推奨）:
  - `[RACI-I] Backlog=<ID> / Change=<Status Open→In Progress> / By=<name> / Memo=<path> / Source=<N/A or URL>`

### RACI-I 記録例（Source Issue 切替時）

- `[RACI-I] Backlog=AUTH-IMPL-01 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/123 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-IMPL-01-user-identity-schema-migration-implementation.md / Source=https://github.com/<org>/<repo>/issues/123`
- `[RACI-I] Backlog=AUTH-API-02 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/124 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-API-02-strict-provisioning-contract-and-admin-api.md / Source=https://github.com/<org>/<repo>/issues/124`
- `[RACI-I] Backlog=AUTH-E2E-01 / Change=Source Issue N/A→https://github.com/<org>/<repo>/issues/125 / By=platform-architecture-owner / Memo=01_Plans/issues/issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md / Source=https://github.com/<org>/<repo>/issues/125`

## Required fields（最低必須）

issue補助メモには、最低でも次の項目を含める。

- Meta: `Type`, `Status`, `Source Issue`, `Priority`, `Scope`
- Quality gate: `Expected verification level`
- Traceability: `Related Backlog`, `Related ADR/Spec`
- Execution: `Proposed solution`, `Acceptance criteria`, `Task breakdown`, `Validation plan`
- Safety/Compatibility: 安全影響・互換影響・非目標


## Expected verification level（運用ガイド）

`Expected verification level` は「最低限どこまで検証するか」の宣言です。
上位レベルを選んだ場合は、下位レベルの検証を内包して実施します。

| Level | 最低実施内容 | 代表コマンド例 |
|---|---|---|
| `docs-check` | 参照リンク・整形・必須メタ検査 | `rg -n ...` / `git diff --check` |
| `unit` | `docs-check` + 対象モジュール単体テスト | `pytest <target>` / `npm test -- <target>` |
| `integration` | `unit` + サービス間結合検証 | `docker compose ...` / API結合テスト |
| `e2e` | `integration` + ユーザーフロー検証 | `playwright test ...` |

> 詳細なE2E運用は `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md` と
> `04_Documentation/e2e_testing.md` を正本とする。

## Quality checklist（レビュー観点）

- これは **Action** を記述しており、Decision（方針固定）はADRへ分離されているか。
- AGENTS.mdの4判断軸（価値/安全/企業行政/後方互換）で優先度を説明できるか。
- 実装者が「次の1手」を迷わない粒度（再開可能タスク）になっているか。
- テスト・検証がコマンド単位で書かれているか。
- `Expected verification level` と `Validation plan` が矛盾していないか。
- Done時に削除/ADR昇格/CHANGELOG反映の出口条件が明記されているか。

## Template

- 作成雛形: `01_Plans/issues/TEMPLATE.md`
- 機械検証: `python 01_Plans/issues/validate_active_issue_memos.py`
- ユニットテスト: `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`


## Human decision support

- `../project-progress-dashboard.md`: プロジェクト進捗サマリ / Active issue集約 / 判断待ちキューの単一ダッシュボード（Plan→Execute→Verify→Proceed と Self-Correction上限を含む運用入口）。
- ダッシュボード更新原則: `project-progress-dashboard.md` は ADR / issue memo の決定事項を統合表示する参照レイヤとし、直接更新を起点にしない。必ず先に ADR または issue memo の正本を更新してから統合反映する。
- `decision-pack-2026-03-human-judgement.md`: ActiveなDraft issueのうち、人間判断待ちの高優先項目と選択肢を集約。
- REQ-DEF運用状態: R2-P1〜P3 / R3-P1〜P3 は決定済み。`TEMPLATE.md` の必須化ルール（R3-P1必須、R3-P2/R3-P3条件付き）を適用する。
- DOC-OPS-04ゲート状態: ADR-A（`ADR-0022-doc-ops-04-documentation-information-interface.md`）と ADR-B/C/D（`ADR-0023/0024/0025`）は `Accepted`。旧 `ADR-0022-documentation-*` 3件は `Superseded`。
- DOC-OPS-04統合境界: B/C/D作業中は統合ファイル3点（`issues/README.md` / `project-progress-dashboard.md` / `issue-DOC-OPS-04...md`）の同時更新を禁止し、必要時はB/C/Dを停止して統合フェーズ専用コミットへ切り出す。
- DOC-OPS-04停止/再開条件: 停止= A不整合 / 統合ファイル更新必要 / SoD違反 / Self-Correction 3回超過。再開= A再承認+Deciders再確認完了 + 統合フェーズ修正完了 + 役割分離再検証ログ追記 + validator/unittest成功。
- DOC-OPS-04次アクション: 後続改訂は ADR-0023/0024/0025 の境界を維持し、必要時のみ追加ADRを起票する。

## Active issue memos

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| HIL-RS-01 | `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` | Open | N/A |
| HIL-RS-01-A1 | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | Open | N/A |

### HIL-RS-01 実行順序と競合回避（Stream D 統合基準）

- 依存順は **A1 → A2 → A3** の直列を固定し、A1完了報告が揃うまで A2/A3 は着手しない。
- Stream A/B/C の完了報告が揃うまで、共有リソース（`issues/README.md` / `project-progress-dashboard.md`）は更新しない。
- 共有リソースの更新は Stream D 統合フェーズに集約し、単一コミットで Active表・決定ログ・次アクション・件数集計を同期する。
- 2026-03-11時点で Stream A/B/C の完了報告を受領済みとし、Stream D が共有リソース同期の最終更新を実施する。

### Stream F 統合スナップショット（2026-03-14 JST, rerun-17）

- 件数: issue memo 全量監査=43（Open=8 / In Progress=1 / Blocked=2 / Draft=7 / Done系=25）、運用上の集約表示=27（Active=2 / Done=25）。
- Active一覧: `HIL-RS-01`, `HIL-RS-01-A1`（いずれも Open / Source Issue=N/A）。
- 依存順序: **A1 → A2 → A3** を固定（A1完了報告前はA2/A3着手禁止）。
- Decision Queue: `DQ-HIL-EXEC-01` は Ready、`DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` は Open（Ready=1 / Open=2）。
- 決定済み項目の扱い: `DQ-HIL-A1-01` / `DQ-HIL-A1-02` は `project-progress-dashboard.md` の決定ログ（`DR-HIL-A1-01` / `DR-HIL-A1-02`）へ集約し、Queueから除外済み。
- 再監査: `validate_active_issue_memos.py` / `unittest` / `rg` による整合チェックを実施し、件数・状態・依存順の不整合0件を再確認。
- Stream D再検証（同日追補）: A/B/C完了報告受領済み状態を維持し、共有リソース2点の同期値（27/2/25、Decision Queue: Ready=1/Open=2、A1→A2→A3）を再確認。
- Stream D Phase 1再確認（2026-03-13）: Stream A/B/C 完了報告受領済み・契約リンク固定済み・共有リソース更新範囲3ファイル固定を再確認。
- Stream D再同期（2026-03-13）: validator/unittest/rg を再実行し、件数・状態・依存順に加えて Decision Queue（Ready=1 / Open=2）と決定ログ集約済み項目の整合維持を確認。
- Stream D Phase 2 Proceed（2026-03-13）: Stream A/B/C 完了報告受領済みゲートを再確認し、共有リソース同期（Active=2 / Done=25 / Decision Queue: Ready=1/Open=2 / A1→A2→A3）を更新してクローズ。
- Stream D Phase 3監査（2026-03-13）: issue memo総数43件（Open=8 / Draft=7 / Done系=25 / In Progress=1 / Blocked=2）を再計算し、Decision Queue未決=2（Ready=1 / Open=2）・停止条件違反0件を確認。
- Stream D Phase 4公開（2026-03-13）: 再開判定チェックリストを1行確定（未固定箇所=0 / 契約リンク確定 / Queue未決は`DQ-FB-P2C-01`,`DQ-OPS-SOURCE-01` / 停止条件違反なし）。
- Stream D Phase 3 Verify追補（2026-03-13）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、dashboard/README/decision-packの件数・Queue（Ready=1/Open=2）・再開判定の整合維持を確認。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-2）: Read Gate（A/B/C完了報告・契約リンク固定・検証ログ受領）を前提に、3共有ファイル同時同期後の validator/unittest/rg 成功を再確認。
- Stream D Phase 2 Gate判定（2026-03-13, FB-P2C下流）: Gate 0未承認を再確認し、`FB-P2C-01-A2` / `A3` は Blocked 維持、Decision Queue は `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open` に同期。
- Stream D Phase 4 Proceed（2026-03-13 rerun-4）: 再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を再確定。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-5）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 4 Proceed（2026-03-13 rerun-6）: 再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を再確定し、共有3ファイルの同期をクローズ。
- Stream D Phase 3 Verify追補（2026-03-13 rerun-6）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 3 Verify追補（2026-03-14 rerun-9）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream D Phase 3 Verify追補（2026-03-14 rerun-10）: Stream A/B/C完了報告と決定リンク固定（`DR-HIL-A1-01` / `DR-HIL-A1-02` / `DL-HIL-01` / `DR-REQ-DEF-02` / `DR-REQ-DEF-03`）を再確認後、`python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg` を再実行し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行の一致を維持。
- Stream F Phase 1-4最終同期（2026-03-14 rerun-11）: Read Sync→同期反映→validator/unittest/`rg`検証→Closeout を直列で再実施し、件数43・Active2・Done25・Decision Queue Ready=1/Open=2・再開判定1行・停止条件違反0件の一致を確定。
- Stream D Phase 4 Publish（2026-03-14 rerun-8）: Plan→Execute→Verify→Proceed を再完了し、共有統合3ファイルを単一コミット対象で同期。未解決Queueは `DQ-FB-P2C-01` / `DQ-OPS-SOURCE-01` の2件を維持、再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / 停止条件違反なし）を確定。

- Stream A Phase 1-4同期（2026-03-14）: Read Gate再読で A1→A2→A3依存・Queue（Ready=1/Open=2）・停止条件違反0件を確認し、A1契約レビュー（ADR追加不要）→DQ運用点検（`DQ-HIL-EXEC-01` Ready維持、`DQ-FB-P2C-01`/`DQ-OPS-SOURCE-01` Open期限管理）→共有2ファイル同期を同一コミットで実施。
- Stream D Phase 4 Publish（2026-03-14 rerun-11）: human_judgementメタプロンプト再適用で Decision Queue 3件をGate再判定（暫定）し、rerun-12で最終状態を `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open` に再同期。
- Stream F Phase 3 Verify追補（2026-03-14 rerun-12）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md` を再実行し、Queue表示の同期を確認。
- Stream F Phase 5 Proceed（2026-03-14 rerun-12）: 再開判定チェックリストを更新し、他レーン公開値（Ready=1/Open=2、次アクション=Ready監査1件+Open期限管理2件、停止条件違反0件）を共有。
- Stream F Phase 3 Verify追補（2026-03-14 rerun-13）: Phase 1 Read Sync→Phase 2 Plan→Phase 3 Execute（単一変更セット）後に `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数43・Queue Ready=1/Open=2・再開判定1行の整合を確認。
- Stream F Phase 5 Proceed（2026-03-14 rerun-13）: 再開判定チェックリストを更新し、公開値（Ready=1/Open=2、次アクション=Ready監査1件+Open期限管理2件、停止条件違反0件、未承認決定混入なし）を共有。
- Stream H Phase 1-4 最終同期（2026-03-14）: A〜G完了報告・Queue状態・依存順をRead同期し、共有3ファイルで Active=2 / Done=25 / 件数43 / Decision Queue Ready=1/Open=2 を再反映。
- Stream H Phase 3 Verify（2026-03-14）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数・Queue・再開判定1行の一致を確認。
- Stream E Phase 1 Read同期（2026-03-14 final）: Stream A/B/C/D完了報告受領、依存順 `A1→A2→A3`、Decision Queue（Ready=1/Open=2）、shared resource以外の未マージ差分なしを再確認。
- Stream E Phase 2-3 統合/実行（2026-03-14 final）: shared resource 3ファイルのみを単一変更セットで更新し、件数43・Active2・Done25・Queue Ready=1/Open=2・次アクション（Ready監査1件 + Open期限管理2件）を同期。
- Stream E Phase 4-5 Verify/Proceed（2026-03-14 final）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` 成功を確認し、再開判定チェックリスト1行（未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし）を公開ログ化。
- Stream F Phase 1-5 最終同期（2026-03-14 rerun-14）: A〜E完了報告受領・依存順 `A1→A2→A3`・Decision Queue（Ready=1/Open=2）・shared resource freeze解除をRead Gateで再確認し、共有3ファイルの同期対象（件数43 / Active=2 / Done=25 / 次アクション=Ready監査1件+Open期限管理2件）を宣言後に単一変更セットで反映した。
- Stream F Phase 4 Verify（2026-03-14 rerun-14）: `python 01_Plans/issues/validate_active_issue_memos.py` / `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py` / `rg -n "Decision Queue|Ready=|Open=|再開判定チェックリスト|A1→A2→A3" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/issues/decision-pack-2026-03-human-judgement.md` を再実行し、件数43・Queue Ready=1/Open=2・再開判定1行・停止条件違反0件の一致を再確定。
- Stream F Phase 1-5 再同期（2026-03-14 rerun-15）: A〜E完了報告受領・依存順 `A1→A2→A3`・Decision Queue（Ready=1/Open=2）をRead Gateで再確認し、shared resource 3ファイルの単一変更セット更新後に validator/unittest/rg を再実行して件数43・Active2・Done25・再開判定1行・停止条件違反0件の一致を維持。
- Stream E Phase 1-4 同期（2026-03-14 rerun-16）: Read同期（A/B/C/D完了報告）→件数/状態/Decision Queue反映→参照リンク/件数/依存順監査→再開判定チェックリスト1行確定を直列実行し、shared resource 3ファイルの公開値を `件数43 / Active2 / Done25 / Queue Ready=1 Open=2 / A1→A2→A3 / 停止条件違反0件` で再固定。
- Stream F Phase 1-5 最終再同期（2026-03-14 rerun-17）: Read Gate（A〜E完了報告と証跡）→Plan（3ファイル限定）→Execute（単一変更セット）→Verify（validator/unittest/rg）→Proceed（再開判定チェックリスト1行固定）を実施し、件数43・Active2・Done25・Queue Ready=1/Open=2・依存順A1→A2→A3・停止条件違反0件を維持。

## Rules

1. 新規作成先は必ず `01_Plans/issues/`。
2. ファイル名は `issue-<BacklogID>-<short-title>.md` を推奨。
3. Done は本ディレクトリに継続保管し、自動削除しない。
4. 削除/アーカイブは人間の手動判断、または人間の明示指示がある場合のみ実施する。

## Completed issue memos

| Backlog ID | Memo | Status | Source Issue | Notes |
|---|---|---|---|---|
| DX-CODEX-01 | `issue-DX-CODEX-01-codex-skill-adoption-and-validation.md` | Done | N/A | Codex skill導入手順・役割分担・正本/補助境界・試行ログテンプレートを整備。 |
| DX-CODEX-02 | `issue-DX-CODEX-02-markdown-mermaid-mcp-doc-ops-adoption.md` | Done | N/A | markdown-mermaid-docops skill運用とMermaid/MCP証跡方針を標準化。 |
| AUTH-ARCH-01 | `issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md` | Done | N/A | AuthContext/JIT境界、strict責務、承認記録を確定。 |
| AUTH-SCHEMA-01 | `issue-AUTH-SCHEMA-01-identity-schema-planning.md` | Done | N/A | identity schema比較、403契約、expand/contract前提を確定。 |
| AUTH-IMPL-01 | `issue-AUTH-IMPL-01-user-identity-schema-migration-implementation.md` | Done | N/A | users / user_identities migration 実装・検証を完了。 |
| AUTH-API-02 | `issue-AUTH-API-02-strict-provisioning-contract-and-admin-api.md` | Done | N/A | strict provisioning 契約と admin API 実装・検証を完了。 |
| FB-RM-RS-02 | `issue-FB-RM-RS-02-structural-metrics.md` | Done | N/A | 実装/検証完了済み。 |
| DOC-REL-01 | `issue-DOC-REL-01-spec-source-doc-consistency-audit.md` | Done | N/A | 文書整合監査完了。 |
| ENV-ARCH-01 | `issue-ENV-ARCH-01-global-env-prefix-migration.md` | Done | N/A | 一括移行（Option B/C）の実装・検証を完了し、旧キー非互換を確定。 |
| AUTH-OPS-03 | `issue-AUTH-OPS-03-strict-mode-exception-relaxation-runbook-plan.md` | Done | N/A | strict mode例外運用の固定値・責務・停止条件を01/02/04で同期完了。 |
| DOC-OPS-02 | `issue-DOC-OPS-02-cross-document-improvement-plan-from-human-decisions.md` | Done | N/A | 文書横断ドリフト（用語/役割/導線/D1〜D4）を解消。 |
| DOC-OPS-03 | `issue-DOC-OPS-03-project-progress-dashboard-planning.md` | Done | N/A | dashboard運用プロトコルと競合停止条件を固定。 |
| DOC-OPS-04 | `issue-DOC-OPS-04-documentation-visibility-readability-governance.md` | Done | N/A | ADR-0023/0024/0025 を直列処理し、統合同期と検証を完了。 |
| REQ-DEF-02 | `issue-REQ-DEF-02-responsibility-boundary-and-contract-checkpoints.md` | Done | N/A | R2-P1 Reject, R2-P2/R2-P3 Conditional Approve を確定し運用方針へ反映。 |
| REQ-DEF-03 | `issue-REQ-DEF-03-acceptance-scenarios-and-issue-splitting.md` | Done | N/A | R3-P1 Approve, R3-P2/R3-P3 Conditional Approve を確定しテンプレ運用へ反映。 |
| REQ-DEF-01 | `issue-REQ-DEF-01-value-realization-requirements-baseline.md` | Done | N/A | REQ-DEF共通I/F正本とDecision Queue連携を最終固定。 |
| FB-RM-SEC-02 | `issue-FB-RM-SEC-02-worker-stabilization.md` | Done | N/A | worker化・fallback/cancel/progress 回帰固定済み。 |
| FB-RM-MID-02 | `issue-FB-RM-MID-02-manual-assisted-merge-decisions.md` | Done | N/A | merge判断記録の保存/再読込を実装済み。 |
| FB-RM-MID-01 | `issue-FB-RM-MID-01-deterministic-similar-card-candidates.md` | Done | N/A | deterministic候補生成と順序安定化を実装済み。 |
| FB-RM-MID-03 | `issue-FB-RM-MID-03-merge-decision-audit-export.md` | Done | N/A | merge監査エクスポートを実装済み。 |
| FB-RM-I18N-02 | `issue-FB-RM-I18N-02-locale-json-fallback-order.md` | Done | N/A | locale fallback順序を固定済み。 |
| FB-RM-I18N-03 | `issue-FB-RM-I18N-03-ui-equivalence-e2e-smoke.md` | Done | N/A | 英語UI等価 E2E smoke/flow を記録済み。 |
| FB-RM-MID-05 | `issue-FB-RM-MID-05-structural-granularity-export.md` | Done | N/A | export粒度とmanifest出力を実装済み。 |
| QA-PUB-01 | `issue-QA-PUB-01-I18N-03-e2e-boundary.md` | Done (SQLite fallback path) | N/A | SQLite fallback の E2E 境界検証ログを固定し、将来の本番同等検証との差分前提を明文化。 |

| AUTH-E2E-01 | `issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md` | Done | N/A | Level1/Level2運用固定、fixture回帰、PR記録テンプレを確定。 |

## Status sync note (2026-03-03)

- 旧 `Done (Local)` は廃止し、完了はすべて `Done` として扱う。
- GitHub Issues 未運用時は `Source Issue: N/A` を維持し、PM/Triage の運用開始宣言を切替トリガーとしてURLへ一括移行する。
- AUTH系 issue memo は、開始宣言までは `N/A` を正とし、宣言後は次回更新PRでURLへ同期する（Active対象は `AUTH-E2E-01`、Done対象は次回メタ更新時に追随）。
- Done メモは自動GCせず、量が増えた場合も人間判断でのみ削除/整理する。
- ADR 側ステータス（例: `FB-RM-I18N-03`）は issue memo の実績に同期する。
- 2026-03-11 Stream D統合フェーズで Active/Done 集計と dashboard の Decision Queue / Next actions を再監査し、不整合ゼロを確認。
- Stream D Phase 5 Proceed（2026-03-13 rerun-3）: 5ファイル再読→共有リソース同期→Verifyを再実施し、Decision Queueは `DQ-HIL-EXEC-01=Ready` / `DQ-FB-P2C-01=Open` / `DQ-OPS-SOURCE-01=Open`、依存順序は A1→A2→A3 を維持。
- Stream F Phase 5 Proceed（2026-03-14 rerun-15）: 再開判定チェックリスト公開値を `未固定箇所=0 / 契約リンク確定 / Queue未決2件 / 停止条件違反なし` で再確認し、再開判定を維持。
