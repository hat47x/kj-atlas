# 01_Plans Issue Memo Index

このディレクトリは、GitHub Issue（正本）を補助する **短命メモ** を管理する。
Decisionは ADR、Action は issue memo で管理し、本ディレクトリは再開性の補助に限定する。

> Performance note for AI agents: issue memo が増えても全件を都度読む必要はない。対象Backlog ID/関連ADR/作業スコープに一致するメモのみ参照する。

## Scope

- 対象: Active な issue 補助メモ（Draft / Open / In Progress）
- 正本: 現在運用では issue memo を正本として扱う（GitHub Issues は未運用、将来再開は可能）
- ライフサイクル: Draft -> Open -> In Progress -> Done（Done (Local) は廃止）
- ライフサイクル定義は本READMEのみを正とする。個別issue memoには記載しない。
- Done メモは自動GCしない（手動削除のみ）

## Start here（人間 / 生成AI 共通）

1. `TEMPLATE.md` をコピーして起票草案を作成する。
2. `Type / Priority / Scope / Related ADR` を先に埋める。
3. `Expected verification level`（`docs-check` / `unit` / `integration` / `e2e`）を先に宣言する。
4. 受入条件（Acceptance criteria）と検証計画（Validation plan）を先に確定する。
5. `Source Issue` は運用状態に応じて記載する（未運用時は `N/A`、GitHub Issues運用時はURL）。

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
現在、Active issue memos はありません。

## Rules

1. 新規作成先は必ず `01_Plans/issues/`。
2. ファイル名は `issue-<BacklogID>-<short-title>.md` を推奨。
3. Done は本ディレクトリに継続保管し、自動削除しない。
4. 削除/アーカイブは人間の手動判断、または人間の明示指示がある場合のみ実施する。

## Completed issue memos

| Backlog ID | Memo | Status | Source Issue | Notes |
|---|---|---|---|---|
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
- GitHub Issues 未運用時は `Source Issue: N/A`、運用開始後はURL記載へ切替える。
- Done メモは自動GCせず、量が増えた場合も人間判断でのみ削除/整理する。
- ADR 側ステータス（例: `FB-RM-I18N-03`）は issue memo の実績に同期する。
