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

## Source Issue 運用基準（Traceability）

### `Source Issue: N/A` を継続できる条件

- GitHub Issues を正本としてまだ運用開始していない（本READMEの `Scope` と一致）。
- 対象タスクが issue memo 内で完結し、外部トラッカー参照を必須としていない。
- `Active issue memos` 表の `Source Issue` 列が `N/A` で統一管理されている。

### GitHub Issues URL に移行する条件

- PM/Triage が「GitHub Issues を正本として運用開始」と明示した時点。
- 既存 `Open / In Progress` メモを更新するタイミングで、`Source Issue` を対応するURLへ置換する。
- 新規メモは起票時からGitHub Issue URLを必須とし、`N/A` は使用しない。

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
- 通知トリガー: `Status` 変更時（Open化 / In Progress化 / Done化）と、`Source Issue` の `N/A ↔ URL` 切替時。
- 通知内容（最小）: `Backlog ID` / 新ステータス / 更新者 / 参照リンク（issue memo + Source Issue）。
- 通知手段: PR本文または関連スレッドに同一フォーマットで1回記録し、重複通知しない。

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
| AUTH-ARCH-01 | `issue-AUTH-ARCH-01-authcontext-jit-provisioning-data-boundary.md` | Open | N/A |
| AUTH-SCHEMA-01 | `issue-AUTH-SCHEMA-01-identity-schema-planning.md` | Open | N/A |

## AUTH-ARCH-01 / AUTH-SCHEMA-01 実行比較（1ページ）

### RACI（簡易）

| Issue | R | A | C | I |
|---|---|---|---|---|
| AUTH-ARCH-01 | Auth Architecture Lead（Security/Identity） | Platform Architecture Owner | Backend Lead, Compliance/Security Officer | PM/Triage, QA Lead |
| AUTH-SCHEMA-01 | Data Schema Lead（Backend/DB） | Platform Architecture Owner | Auth Architecture Lead, Backend Lead, Compliance/Security Officer | PM/Triage, QA Lead |

### 着手条件 / ブロッカー / 完了条件 比較

| Issue | 着手条件（Start） | ブロッカー（Blockers） | 完了条件（DoD） |
|---|---|---|---|
| AUTH-ARCH-01 | ADR-0020基準化、現行差分棚卸し、RACI合意 | 監査属性保存要否、IAP差異preset、strict時の管理導線責任 | 属性境界文書化、マッピング規則収束、AUTH-SCHEMA-01へ前提引き渡し |
| AUTH-SCHEMA-01 | AUTH-ARCH-01境界定義レビュー済み、対象章確定、RACI合意 | マッピング未確定、strict運用責任未承認、移行ポリシー未承認 | `02_Architecture/*` 同期更新、ADR-0020参照整合、migration前提明文化 |

### Expected verification level と Validation plan の整合

| Issue | Expected verification level | Validation plan | 判定 |
|---|---|---|---|
| AUTH-ARCH-01 | `docs-check` | `rg` による参照整合確認 + `validate_active_issue_memos.py` | 整合（コード実装を要求していない） |
| AUTH-SCHEMA-01 | `docs-check` | `rg` による参照整合確認 + `validate_active_issue_memos.py` | 整合（Architecture同期確認に一致） |

### 依存関係グラフ（実行順）

```text
AUTH-ARCH-01 (AuthContext/JIT 境界定義)
    └─理由: 保存属性境界・マッピング規則が未確定だと
           AUTH-SCHEMA-01 で一意制約/API契約を固定できない
        ↓
AUTH-SCHEMA-01 (identity schema 反映・同期)
```

### 実行順（1日以内タスク / 決裁待ちタスク）

1. **即着手（1日以内）**
   - AUTH-ARCH-01: T1 `reviewerRef/ownerRef/AuthContext` 参照棚卸し。
   - AUTH-ARCH-01: T2 属性分類表（persist/transient/forbidden）草案。
   - AUTH-SCHEMA-01: T1 `02_Architecture/*` の identity 記述差分抽出。
2. **決裁待ち（承認が必要）**
   - AUTH-ARCH-01: `amr/acr/aal/auth_time` 保存方針の最終承認（Compliance含む）。
   - AUTH-ARCH-01: `ALLOW_JIT_PROVISIONING=false` 時の管理導線（API/CLI）責任境界承認。
   - AUTH-SCHEMA-01: provider+subject 一意制約への tenant 境界含有と移行ポリシー承認。
3. **承認後に実施**
   - AUTH-ARCH-01: T3/T4 マッピング案収束 + ADR追記要否判定。
   - AUTH-SCHEMA-01: T2/T3/T4 スキーマ案確定 + architecture 同期PR。

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
