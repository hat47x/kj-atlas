# Issue: DOC-NORM-02 `test_norm_identifier_checks.py` のファイル探索が追跡ファイルに限定されていない

- Type: Bug / Process
- Status: Draft
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

- [ ] `test_norm_identifier_checks.py` が `git ls-files` 相当の追跡ファイル一覧を使う（またはそれと同等の除外を行う）
- [ ] `.claude/worktrees/` 配下に本規則へ違反するファイルを置いた状態でテストを実行しても、baseline系テストが失敗しない
- [ ] 既存の12テスト全てが変更後も同じ意味で pass する（mutation系のprobeファイル配置場所は `01_Plans/`・`00_Prompt/` のままで良い——これらは追跡対象ディレクトリなので変更不要）
