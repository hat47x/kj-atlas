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
| FB-RM-MID-02 | `issue-FB-RM-MID-02-manual-assisted-merge-decisions.md` | Done (Local) | TBD | merge候補ごとの accept/partial/reject/defer 記録と保存再読込を実装。 |
| FB-RM-MID-01 | `issue-FB-RM-MID-01-deterministic-similar-card-candidates.md` | Done (Local) | TBD | 非AI deterministic heuristic による merge candidate 生成と順序安定テストを追加。 |
| FB-RM-MID-03 | `issue-FB-RM-MID-03-merge-decision-audit-export.md` | Done (Local) | TBD | bundle export に `merge_decision_audit.json` を追加し、representative/source 追跡情報を監査用に出力。 |
| FB-RM-I18N-02 | `issue-FB-RM-I18N-02-locale-json-fallback-order.md` | Done (Local) | TBD | locale JSON契約と fallback順序（requested->ja->key）を実装し、unit/typecheckで固定。 |
| FB-RM-MID-05 | `issue-FB-RM-MID-05-structural-granularity-export.md` | Done (Local) | TBD | bundle export に overview/detail 粒度選択と manifest 出力を追加し、overview時のtrace抑止を unit test で固定。 |


## Done(Local) Source Issue TBD 解消 実行計画

### 1) Task Brief（固定）

- **Scope**: `Completed locally (Source Issue pending)` に掲載された8件の issue補助メモのみを対象とし、`Source Issue: TBD` を解消する。コード実装や仕様変更は行わない。
- **Acceptance**:
  1. 対象8件すべてで、既存GitHub Issueの有無が確認される。
  2. 未存在のものは新規GitHub Issueを起票し、URLを確定する。
  3. 各メモの `Source Issue` をURLへ更新し、`Status` / `Lifecycle` と矛盾しない状態遷移を実施する。
  4. `Completed locally` 表の `Source Issue` が全件URL化される。
- **Checks**:
  - `Source Issue` に推測URLを書かない（確認できたURLのみ記載）。
  - 命名規則（`issue-<BacklogID>-<short-title>.md`）またはLifecycle規則（Draft -> Open -> In Progress -> Done -> GC、Local exception含む）と矛盾を検知した場合は、その時点で更新を停止し、確認依頼を行う。
  - 更新後に `git diff --check` で文書整合を確認する。

### 2) 対象一覧と3段階手順

以下の各メモについて、必ず **A. 既存Issue探索 → B. 未存在なら起票 → C. URL反映と状態遷移** の順で処理する。

1. `FB-RM-SEC-02` (`issue-FB-RM-SEC-02-worker-stabilization.md`)
2. `FB-RM-MID-03` (`issue-FB-RM-MID-03-merge-decision-audit-export.md`)
3. `FB-RM-MID-05` (`issue-FB-RM-MID-05-structural-granularity-export.md`)
4. `FB-RM-RS-02` (`issue-FB-RM-RS-02-structural-metrics.md`)
5. `FB-RM-I18N-02` (`issue-FB-RM-I18N-02-locale-json-fallback-order.md`)
6. `FB-RM-MID-02` (`issue-FB-RM-MID-02-manual-assisted-merge-decisions.md`)
7. `FB-RM-MID-01` (`issue-FB-RM-MID-01-deterministic-similar-card-candidates.md`)
8. `DOC-REL-01` (`issue-DOC-REL-01-spec-source-doc-consistency-audit.md`)

#### A. 既存 GitHub Issue 探索（共通）

- 検索キー: `Backlog ID`、メモタイトル主要語、関連ADR番号。
- 一致条件:
  - Issue本文またはタイトルに同一Backlog IDがある。
  - 受入条件/スコープがメモと実質一致する。
- 一致しない場合: 「未特定」と記録し、Bへ進む。

#### B. 未存在なら新規 Issue 起票（共通）

- 起票元: 当該メモを正本下書きとして使用。
- タイトル規約: `<Backlog ID>: <short title>`。
- 本文最小要素: Problem / Proposed solution / Acceptance criteria / Validation plan / Related ADR。
- 起票後: 発行されたIssue URLを取得して記録。

#### C. URL反映後の状態遷移（共通）

- 各メモの `Source Issue` を `TBD` から確定URLへ更新。
- 実装と検証が完了済みであるため、`Status` は原則 `Done` に更新（`Done (Local)` 例外を終了）。
- `01_Plans/issues/README.md` の `Completed locally` から該当行を除去し、必要に応じて `Done` 扱いの記録（archive/CHANGELOG運用）へ引き渡す。

### 3) Verification（完了条件）

- 完了判定は次を全て満たすこと。
  1. `Completed locally (Source Issue pending)` の全行で `Source Issue != TBD`。
  2. 対象8メモの `Source Issue` がすべて有効なGitHub Issue URL。
  3. `Done (Local)` が残る場合は、URL未確定ではなく運用上の例外理由が明示されている。
  4. Lifecycle矛盾（`Done (Local)` のままURL確定済み等）がない。

### 4) Record（優先度・担当ロール）

安全影響が高い順で以下の担当を割り当てる。

| Priority Order | Backlog ID | Safety impact rationale | Primary role | Support role |
|---|---|---|---|---|
| 1 | FB-RM-SEC-02 | worker化・fallback/cancel/progressの回帰固定は安全運用に直結 | Security Owner | Frontend Owner |
| 2 | FB-RM-MID-03 | 監査エクスポートは説明責任/漏えい統制に影響 | Governance Reviewer | Frontend Owner |
| 3 | FB-RM-MID-05 | export粒度とtrace抑止は漏えい最小化に関与 | Frontend Owner | Security Owner |
| 4 | FB-RM-RS-02 | diagnostics健全性指標は運用上の早期異常検知に寄与 | Frontend Owner | QA |
| 5 | FB-RM-I18N-02 | locale fallback不備は誤表示リスク（中） | Frontend Owner | QA |
| 6 | FB-RM-MID-02 | merge判断記録は監査補助（中） | Product/Review Ops | Frontend Owner |
| 7 | FB-RM-MID-01 | deterministic候補は品質改善寄り（中〜低） | Product/Review Ops | QA |
| 8 | DOC-REL-01 | 文書整合監査は直接の安全影響は低い | Docs Owner | Governance Reviewer |

> 実行中に命名規則・Lifecycle・メモ内容とIssueの対応関係で矛盾を検知した場合は、誤った紐付けを防ぐため即時停止し、確認後に再開する。

## Done (Local) 運用ルール

`Done (Local)` は、**実装と検証は完了しているが GitHub Issue URL が未発行**のときだけ使う補助ステータス。

1. `Done (Local)` は Active issue memos には載せない。
2. `Done (Local)` は `Completed locally` セクションで管理する。
3. `Source Issue` が確定したら、メモへURLを追記し、必要に応じて `Done` へ更新する。
4. validator の機械検証対象は `Active issue memos` のみとし、`Completed locally` は対象外とする。
