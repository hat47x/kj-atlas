# AIエージェント失敗事例ログ

区分: Internal / Log（`agent_failure_lessons.md` の実記録）

Updated: 2026-08-03

記録形式・対象・参照タイミングは `01_Plans/agent_failure_lessons.md` を参照。末尾へ追記する。

## 2026-08-03: CI trailing whitespace check が複数回失敗（CRLF行末混入）

- 事象: `git diff --check` が、コミットしたPython/TypeScriptファイルの「追加行」に trailing whitespace があるとしてCIが失敗。`models_context.py`・`test_context_bundle_routes.py`・`issue-DOMAIN-EXPR-01` の3回発生。
- 原因: WSL上の作業でCRLF→LF変換が走る際、行末に空白が残った。日本語長文のissue更新時は、編集ツール由来の行末空白が入りやすい。
- 対応: `sed -i 's/[[:space:]]*$//'` で該当ファイルの末尾空白を一括除去し、`git diff -U0 | grep '^+'` で追加行だけを検査してからコミット。
- 再発防止: コミット前に必ず `git diff --check`（または追加行のみの末尾空白grep）を実行する。日本語長文の編集後は特に行末を確認する。

## 2026-08-02: esbuild version mismatch で vitest が起動不能

- 事象: `vitest run` が `Cannot start service: Host version "0.28.1" does not match binary version "0.21.5"` で起動失敗。i18nテスト・対象モジュールテストが実行不能になった。
- 原因: pnpm移行がrevert（`DX-CI-PNPM-01`）された後に残った `.pnpm/` 配下の古い `esbuild@0.28.1` エントリと、アクティブな `esbuild@0.21.5` の混在。`.pnpm/esbuild@0.28.1` のバイナリが欠落していた。
- 対応: `rm -rf node_modules/.pnpm/esbuild@0.28.1 node_modules/.pnpm/@esbuild+win32-x64@0.28.1` で古いエントリを除去 → vitest正常起動（233 files / 1372 tests pass）。
- 再発防止: esbuild系の起動エラーはまず `.pnpm/` 配下のバージョン重複を確認する。pnpm関連ファイルがrevertされた後のnode_modules操作には注意する。

## 2026-08-02: 作業ディレクトリ依存のgit pathspecエラー

- 事象: `git add 03_Implement/frontend/...` が `warning: could not open directory '03_Implement/frontend/03_Implement/frontend/'` で失敗。作業ディレクトリが `03_Implement/frontend/` にある状態でリポジトリルート基準のパスを渡した。
- 原因: 前のコマンドで `cd` したディレクトリが残っており、相対パスが二重化した。
- 対応: `git -C /mnt/d/GIT/kj-atlas` でリポジトリルートを明示するか、ルート基準の相対パスを使う。
- 再発防止: git操作は `git -C /mnt/d/GIT/kj-atlas` 形式で統一する。cd後の相対パスgitコマンドは避ける。

## 2026-07-30: 手動マージ後のtest-results/ が未追跡で残る

- 事象: Playwright実行の `test-results/` ディレクトリがuntrackedとして残り、毎回 `git status` を汚した。
- 原因: `.gitignore` に `**/test-results/` が無かった。
- 対応: `.gitignore` に `**/test-results/` を追加（`.claude/worktrees/` も同時に追加）。
- 再発防止: 実行成果物（テスト結果、キャッシュ、一時ファイル）は生成時に.gitignoreへ追加する。

## 2026-07-20: roundブランチのマージでindex.lock残存による失敗

- 事象: `git merge` が `Unable to write index` で失敗し、`index.lock` が残って後続のgit操作が全て失敗した。
- 原因: 並行プロセス（別エージェントのgit操作）との競合、または中断されたマージの残骸。
- 対応: `rm -f .git/index.lock` でロックを除去してから再試行。マージ中は連続で複数ブランチをマージしない。
- 再発防止: git操作が `Unable to write index` / `index.lock` で失敗したら、まずロックファイルを確認・除去する。複数ブランチの連続マージは1つずつ確認しながら進める。
