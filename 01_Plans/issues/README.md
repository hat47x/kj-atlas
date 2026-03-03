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
| FB-RM-I18N-03 | `issue-FB-RM-I18N-03-ui-equivalence-e2e-smoke.md` | Done (Local) | TBD | 英語UI等価のsmoke/flow E2Eを追加し、SQLite代替経路で再実行を含む通過ログを記録。 |
| FB-RM-MID-05 | `issue-FB-RM-MID-05-structural-granularity-export.md` | Done (Local) | TBD | bundle export に overview/detail 粒度選択と manifest 出力を追加し、overview時のtrace抑止を unit test で固定。 |

## Done (Local) 運用ルール

`Done (Local)` は、**実装と検証は完了しているが GitHub Issue URL が未発行**のときだけ使う補助ステータス。

1. `Done (Local)` は Active issue memos には載せない。
2. `Done (Local)` は `Completed locally` セクションで管理する。
3. `Source Issue` が確定したら、メモへURLを追記し、必要に応じて `Done` へ更新する。
4. validator の機械検証対象は `Active issue memos` のみとし、`Completed locally` は対象外とする。


## ADR-0007 × issue memo 整合性突合（2026-03-03）

### Task Brief（固定）

- Scope:
  - `01_Plans/adr/ADR-0007-future-backlog.md` の `Roadmap統合バックログ` 状態と、`01_Plans/issues/*.md` の `Status` / 実績ログ（Done Local）を照合する。
  - 「実際に未完了のタスク」と「記録遅延タスク（実装完了だが記録未同期）」を分離して可視化する。
- Non-Goals:
  - 実装コードの有無を推測で断定しない。
  - Source Issue 未発行のまま `Done` へ強制変更しない。
- Acceptance:
  - 不整合を ID 単位で列挙し、各行に `status更新` / `根拠追記` / `別Issue化` のいずれかの必要アクションを付与する。
  - Verify で「次に誰が何を編集すれば閉じるか」を 1 行ずつ示す。
- Checks:
  - `rg -n '^| FB-RM-' 01_Plans/adr/ADR-0007-future-backlog.md`
  - `rg -n 'Status:|Related Backlog|Done \(Local\)' 01_Plans/issues/issue-*.md`
  - `rg -n 'Completed locally|FB-RM-' 01_Plans/issues/README.md`

### 不整合一覧（ADR-0007 vs issue memos）

| Backlog ID | ADR-0007 状態 | issue memo 状態/実績 | 判定 | 必要アクション | 備考 |
|---|---|---|---|---|---|
| FB-RM-I18N-03 | Planned | `issue-FB-RM-I18N-03-ui-equivalence-e2e-smoke.md`: Done (Local), E2E実行ログあり | 要確認（状態衝突） | **根拠追記**: ADR-0007 側へ「Done(Local)根拠リンク or 未達理由」を追記。**status更新**は根拠確認後のみ実施。 | 実装完了は断定せず、記録衝突として停止。 |
| FB-RM-PUB-01 | Planned | 対応 issue memo なし（本ディレクトリ内） | 実際に未完了（要起票） | **別Issue化**: `issue-FB-RM-PUB-01-*.md` を起票し、受入条件/検証計画を先に固定。 | 未着手タスクを可視化するための最小アクション。 |
| DOC-REL-01 | ADR-0007管理外 | `Completed locally` に Done(Local) として掲載 | 要確認（管理面） | **別Issue化**: ADR-0007 対象外で継続管理するなら、専用トラッキング（別ADR/issue index）へ分離。 | ADR-0007との突合対象外を明示する。 |

### 分離結果（可視化）

- 実際に未完了のタスク:
  - `FB-RM-PUB-01`（Planned かつ issue memo 不在）
- 記録遅延タスク:
  - `FB-RM-I18N-03`（ADR: Planned / issue memo: Done(Local) の衝突）
- 管理境界の要確認:
  - `DOC-REL-01`（ADR-0007対象外タスクが Completed locally に混在）

### Verify（次に誰が何を編集すれば閉じるか）

- **Backlog Owner（I18N）**: `ADR-0007` の `FB-RM-I18N-03` 行に、E2E実績を根拠として `Done` へ更新するか、未達DoDを追記して `Planned` 維持理由を明文化する。
- **Planning Maintainer**: `01_Plans/issues/README.md` の `Completed locally` と個別memoの `Status` を定期突合し、同種ドリフトの再発を防ぐ。
- **Planning Maintainer**: `FB-RM-PUB-01` の issue memo を新規作成し、`Source Issue`・受入条件・検証計画を先に固定する。
- **Docs/Planning Owner**: `DOC-REL-01` を ADR-0007突合対象から除外する運用注記（または別トラッキング先）を README に追記する。
