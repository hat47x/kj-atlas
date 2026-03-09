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
- `decision-pack-2026-03-human-judgement.md`: ActiveなDraft issueのうち、人間判断待ちの高優先項目と選択肢を集約。
- REQ-DEF運用状態: R2-P1〜P3 / R3-P1〜P3 は決定済み。`TEMPLATE.md` の必須化ルール（R3-P1必須、R3-P2/R3-P3条件付き）を適用する。
- DOC-OPS-04ゲート状態: ADR-A（`ADR-0022`）と ADR-B/C/D（`ADR-0023/0024/0025`）はすべて `Accepted`。
- DOC-OPS-04統合境界: B/C/D作業中は統合ファイル3点（`issues/README.md` / `project-progress-dashboard.md` / `issue-DOC-OPS-04...md`）の同時更新を禁止し、必要時はB/C/Dを停止して統合フェーズ専用コミットへ切り出す。
- DOC-OPS-04停止/再開条件: 停止= A（`ADR-0022`）I/F語彙の変更兆候または統合ファイル同時更新の必要発生。再開= A再承認完了 + 統合フェーズ修正完了 + validator/unittest成功。
- DOC-OPS-04次アクション: 後続改訂は ADR-0023/0024/0025 の境界を維持し、必要時のみ追加ADRを起票する。

## Active issue memos

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|

## Rules

1. 新規作成先は必ず `01_Plans/issues/`。
2. ファイル名は `issue-<BacklogID>-<short-title>.md` を推奨。
3. Done は本ディレクトリに継続保管し、自動削除しない。
4. 削除/アーカイブは人間の手動判断、または人間の明示指示がある場合のみ実施する。

## Completed issue memos

| Backlog ID | Memo | Status | Source Issue | Notes |
|---|---|---|---|---|
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

| AUTH-IMPL-01 | `issue-AUTH-IMPL-01-user-identity-schema-migration-implementation.md` | Done | N/A | users/user_identities migration と段階移行検証を完了。 |
| AUTH-API-02 | `issue-AUTH-API-02-strict-provisioning-contract-and-admin-api.md` | Done | N/A | strict provisioning契約と管理APIの統合検証を完了。 |
| AUTH-E2E-01 | `issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md` | Done | N/A | Level1/Level2運用固定、fixture回帰、PR記録テンプレを確定。 |

## Status sync note (2026-03-03)

- 旧 `Done (Local)` は廃止し、完了はすべて `Done` として扱う。
- GitHub Issues 未運用時は `Source Issue: N/A` を維持し、PM/Triage の運用開始宣言を切替トリガーとしてURLへ一括移行する。
- AUTH系 issue memo は、開始宣言までは `N/A` を正とし、宣言後は次回更新PRでURLへ同期する（Active対象は `AUTH-E2E-01`、Done対象は次回メタ更新時に追随）。
- Done メモは自動GCせず、量が増えた場合も人間判断でのみ削除/整理する。
- ADR 側ステータス（例: `FB-RM-I18N-03`）は issue memo の実績に同期する。
