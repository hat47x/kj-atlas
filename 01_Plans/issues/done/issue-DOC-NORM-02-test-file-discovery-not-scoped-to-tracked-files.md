# Issue: DOC-NORM-02 `test_norm_identifier_checks.py` のファイル探索が追跡ファイルに限定されていない

- Type: Bug / Process
- Status: Done
- Source Issue: `DOC-NORM-01`
- Priority: P3
- Owner: Maintainer
- Scope: `01_Plans/tests/test_norm_identifier_checks.py`
- Related ADR/Spec: `01_Plans/docs_check.py`（本番経路の対比）
- Expected verification level: `unit`

## 課題

- 現在の問題: `test_norm_identifier_checks.py` は `ROOT.rglob("*.md")` で対象ファイルを収集し、`{".git", "node_modules", "build"}` のみを除外している。本番の検証経路（`01_Plans/docs_check.py` → `contract_tracked_markdown_paths()`）は `git ls-files` で**追跡ファイルのみ**を対象にしているのに対し、テストは gitignore 対象や未追跡のローカル専用ディレクトリも素通りで拾う。

  実際に `.claude/worktrees/`（`.gitignore` で除外・Claude Codeのエージェントツールが使う一時ワークツリー）内に残っていた孤立した detached-HEAD ワークツリーの古いファイル（`02_Architecture/ai-prompt-core-redesign-2026-07-23.md`。禁止されている形式の行番号参照を含んでいた）を `test_baseline_has_no_line_number_references` が検出し、テストを失敗させた。このファイルは `main` にも `git ls-files` にも存在しない。

- 利用者または開発への影響: ローカルでテストを実行する開発者が、リポジトリの実際の状態とは無関係な「失敗」を見せられる。CIでは `.claude/worktrees/` 自体が存在しない（gitignore対象のため新規クローンに現れない）ので再現しないが、ローカル実行時の信頼性が下がり、「どうせローカルでは時々落ちる」という学習が起きる。

## 対応方針

- 実施すること:
  - `test_norm_identifier_checks.py` のファイル収集を、本番経路と同じ `git ls-files -z -- '*.md'`（または `01_Plans/docs_contract_checks.py` の `tracked_markdown_paths()` を直接再利用）へ揃える。
  - 直接再利用できない場合は、除外セットに `.claude` を追加する簡易対応でも良いが、根本対応は「本番と同じ発見方法を使う」こと。

- 実施しないこと:
  - `.claude/worktrees/` 配下の孤立ファイル自体の削除・整理（本issueのスコープ外。別途のワークツリー衛生の話であり、テストの発見方法とは独立）。

## 受入条件

- [x] `test_norm_identifier_checks.py` が `git ls-files` 相当の追跡ファイル一覧を使う（またはそれと同等の除外を行う）
- [x] `.claude/worktrees/` 配下に本規則へ違反するファイルを置いた状態でテストを実行しても、baseline系テストが失敗しない
- [x] 既存の12テスト全てが変更後も同じ意味で pass する（mutation系のprobeファイル配置場所は `01_Plans/`・`00_Prompt/` のままで良い——これらは追跡対象ディレクトリなので変更不要）

## 対応記録（2026-08-21）

`_markdown_paths()` を `docs_contract_checks.tracked_markdown_paths()`（`git ls-files -z -- '*.md'`）へ
置き換えた。ミューテーション系テストは全て探索結果へprobeパスを明示的に追加しているため、
`cls.md_paths`（baseline専用）の変更のみで影響が閉じる。

- 新規テスト `test_untracked_worktree_file_does_not_affect_the_baseline` を追加し、本issueが実際に
  観測した事象（`.claude/worktrees/`配下の孤立ファイルが禁止形式の行番号参照を含み、baselineを
  失敗させた）を再現・固定した。probeが実際にgitignore対象であることも`git check-ignore`で確認する。
- 変異検査: 修正前のロジック（`ROOT.rglob`）へ戻すと新規テストが失敗することを確認した。
- **実際に repo に残っていた本物の孤立ファイル**
  （`.claude/worktrees/eloquent-dhawan-42f2fa/02_Architecture/ai-prompt-core-redesign-2026-07-23.md`）を
  削除せずそのままにした状態で `python 01_Plans/docs_check.py` を実行し、**`docs-check passed`**
  （本セッションで初めてクリーンに通過）を確認した。
- 検証: `python -m pytest 01_Plans/tests/test_norm_identifier_checks.py`（17 passed）、
  `ruff check`（対象2ファイル）all passed、
  `03_Implement/backend/scripts/check_design_consistency.py`（0 errors, 0 warnings）。
