# 01_Plans Issue Memo Index

このディレクトリは、GitHub Issue（正本）を補助する **短命メモ** を管理する。
Decisionは ADR、Action は GitHub Issue で管理し、本ディレクトリは再開性の補助に限定する。

## Scope

- 対象: Active な issue 補助メモ（Draft / Open / In Progress）
- 正本: GitHub Issues
- ライフサイクル: Draft -> Open -> In Progress -> Done -> GC(削除)

## Start here（人間 / 生成AI 共通）

1. `TEMPLATE.md` をコピーして起票草案を作成する。
2. `Type / Priority / Scope / Related ADR` を先に埋める。
3. 受入条件（Acceptance criteria）と検証計画（Validation plan）を先に確定する。
4. `Source Issue` に GitHub Issue URL を記入してから実装着手する。

## Required fields（最低必須）

issue補助メモには、最低でも次の項目を含める。

- Meta: `Type`, `Status`, `Lifecycle`, `Source Issue`, `Priority`, `Scope`
- Traceability: `Related Backlog`, `Related ADR/Spec`
- Execution: `Proposed solution`, `Acceptance criteria`, `Task breakdown`, `Validation plan`
- Safety/Compatibility: 安全影響・互換影響・非目標

## Quality checklist（レビュー観点）

- これは **Action** を記述しており、Decision（方針固定）はADRへ分離されているか。
- AGENTS.mdの4判断軸（価値/安全/企業行政/後方互換）で優先度を説明できるか。
- 実装者が「次の1手」を迷わない粒度（再開可能タスク）になっているか。
- テスト・検証がコマンド単位で書かれているか。
- Done時に削除/ADR昇格/CHANGELOG反映の出口条件が明記されているか。

## Template

- 作成雛形: `01_Plans/issues/TEMPLATE.md`

## Active issue memos

| Backlog ID | Memo | Status | Source Issue |
|---|---|---|---|
| FB-RM-RS-02 | `issue-FB-RM-RS-02-structural-metrics.md` | Draft | TBD |
| DOC-REL-01 | `issue-DOC-REL-01-spec-source-doc-consistency-audit.md` | Draft | TBD |

## Rules

1. 新規作成先は必ず `01_Plans/issues/`。
2. ファイル名は `issue-<BacklogID>-<short-title>.md` を推奨。
3. Done/Close 後は `git rm` を標準とし、一覧から削除する。
4. 例外保存が必要な場合のみ `archive/` へ移し、`Retention Reason` / `Review Due` / `Source Issue` を先頭に記載する。
