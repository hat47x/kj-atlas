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

## Active issue memos

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| AUTH-E2E-01 | `issue-AUTH-E2E-01-authcontext-contract-level1-level2-regression.md` | Open | N/A |

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
| FB-RM-SEC-02 | `issue-FB-RM-SEC-02-worker-stabilization.md` | Done | N/A | worker化・fallback/cancel/progress 回帰固定済み。 |
| FB-RM-MID-02 | `issue-FB-RM-MID-02-manual-assisted-merge-decisions.md` | Done | N/A | merge判断記録の保存/再読込を実装済み。 |
| FB-RM-MID-01 | `issue-FB-RM-MID-01-deterministic-similar-card-candidates.md` | Done | N/A | deterministic候補生成と順序安定化を実装済み。 |
| FB-RM-MID-03 | `issue-FB-RM-MID-03-merge-decision-audit-export.md` | Done | N/A | merge監査エクスポートを実装済み。 |
| FB-RM-I18N-02 | `issue-FB-RM-I18N-02-locale-json-fallback-order.md` | Done | N/A | locale fallback順序を固定済み。 |
| FB-RM-I18N-03 | `issue-FB-RM-I18N-03-ui-equivalence-e2e-smoke.md` | Done | N/A | 英語UI等価 E2E smoke/flow を記録済み。 |
| FB-RM-MID-05 | `issue-FB-RM-MID-05-structural-granularity-export.md` | Done | N/A | export粒度とmanifest出力を実装済み。 |

## Status sync note (2026-03-03)

- 旧 `Done (Local)` は廃止し、完了はすべて `Done` として扱う。
- GitHub Issues 未運用時は `Source Issue: N/A` を維持し、PM/Triage の運用開始宣言を切替トリガーとしてURLへ一括移行する。
- AUTH系 issue memo は、開始宣言までは `N/A` を正とし、宣言後は次回更新PRでURLへ同期する（Active対象は `AUTH-E2E-01`、Done対象は次回メタ更新時に追随）。
- Done メモは自動GCせず、量が増えた場合も人間判断でのみ削除/整理する。
- ADR 側ステータス（例: `FB-RM-I18N-03`）は issue memo の実績に同期する。
