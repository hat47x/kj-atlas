# 01_Plans Issue Memo Index

このディレクトリは、GitHub Issue（正本）を補助する **短命メモ** を管理する。
Decisionは ADR、Action は GitHub Issue で管理し、本ディレクトリは再開性の補助に限定する。

## Scope

- 対象: Active な issue 補助メモ（Draft / Open / In Progress）
- 例外: Source Issue 未発行でも実装完了を記録する `Done (Local)`
- 正本: GitHub Issues
- ライフサイクル: Draft -> Open -> In Progress -> Done -> GC(削除)

## Start here（人間 / 生成AI 共通）

1. `TEMPLATE.md` をコピーして起票草案を作成する。
2. `Type / Priority / Scope / Related ADR` を先に埋める。
3. `Expected verification level`（`docs-check` / `unit` / `integration` / `e2e`）を先に宣言する。
4. 受入条件（Acceptance criteria）と検証計画（Validation plan）を先に確定する。
5. `Source Issue` に GitHub Issue URL を記入してから実装着手する。

## Required fields（最低必須）

issue補助メモには、最低でも次の項目を含める。

- Meta: `Type`, `Status`, `Lifecycle`, `Source Issue`, `Priority`, `Scope`
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
3. Done/Close 後は `git rm` を標準とし、一覧から削除する。
4. 例外保存が必要な場合のみ `archive/` へ移し、`Retention Reason` / `Review Due` / `Source Issue` を先頭に記載する。

## Completed locally (Source Issue pending)

| Backlog ID | Memo | Status | Source Issue | Notes |
|---|---|---|---|---|
| FB-RM-RS-02 | `issue-FB-RM-RS-02-structural-metrics.md` | Done (Local) | TBD | 実装/検証は完了。GitHub Issue 起票後に Source Issue を追記する。 |
| DOC-REL-01 | `issue-DOC-REL-01-spec-source-doc-consistency-audit.md` | Done (Local) | TBD | Source Issue 未確定のためローカル完了として管理。URL確定時に `Done` へ更新する。 |
| FB-RM-SEC-02 | `issue-FB-RM-SEC-02-worker-stabilization.md` | Done (Local) | TBD | zip生成を worker/off-main-thread 化し、fallback/cancel/progress を回帰テストで固定。 |
| FB-RM-MID-01 | `issue-FB-RM-MID-01-deterministic-similar-card-candidates.md` | Done (Local) | TBD | 非AI deterministic heuristic による merge candidate 生成と順序安定テストを追加。 |

## Done (Local) 運用ルール

`Done (Local)` は、**実装と検証は完了しているが GitHub Issue URL が未発行**のときだけ使う補助ステータス。

1. `Done (Local)` は Active issue memos には載せない。
2. `Done (Local)` は `Completed locally` セクションで管理する。
3. `Source Issue` が確定したら、メモへURLを追記し、必要に応じて `Done` へ更新する。
4. validator の機械検証対象は `Active issue memos` のみとし、`Completed locally` は対象外とする。
