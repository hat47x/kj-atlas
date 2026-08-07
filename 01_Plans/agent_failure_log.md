# AIエージェント失敗事例ログ

区分: Internal / Log（`agent_failure_lessons.md` の実記録）

Updated: 2026-08-03

## 2026-08-06: WSL backend pytest runner unavailable

- 事象: `python3 -m pytest` で Inquiry bundle backend tests の実行を試みたが、`No module named pytest` で開始できなかった。
- 原因: 現在利用可能な WSL Python 環境に backend の test extra が導入されていない。Windows 側の Python launcher も実体環境を提供していない。
- 対応: `~/kj-backend-venv` の既存仮想環境を発見し、そこで対象テストを実行する経路へ切り替えた。
- 再発防止: backend の検証開始前に `python3 -m pytest --version` と既存仮想環境を確認し、依存がなければ未実行として明記する。

## 2026-08-06: 新migration追加後のAlembic head固定テスト失敗

- 事象: Inquiry bundle migration追加後、`test_alembic_has_single_head` が旧head `20260720_0013` を期待して失敗した。
- 原因: migration graphは線形のまま新headへ進んだが、テストの固定期待値を追随していなかった。
- 対応: 期待headを `20260806_0014` へ更新して対象テストを再実行する。
- 再発防止: 新migration追加時はAlembic lineage testのhead期待値を同じ変更単位で確認する。

## 2026-08-06: 新規repository testのruff未使用import

- 事象: Inquiry bundle repository testに `Session` の未使用importがあり、ruffが失敗した。
- 原因: test fixtureの型注釈を簡略化した後にimportだけが残った。
- 対応: 未使用importを削除し、対象ファイルのruffを再実行する。
- 再発防止: テスト追加後は対象Pythonファイルにruffを実行する。

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
- **再発（2026-08-03）**: 同じ `.pnpm/esbuild@0.28.1` が再生成されており再発。pnpm installが走るたびに0.28.1が復活する可能性が高い。除去コマンドはその場で再実行する。根本解決は `node_modules` をクリーンに再構築するか、pnpm移行を正式に完了するか、`.pnpm` 配下のesbuildを0.21に固定する運用の検討が必要。
- **根本原因の特定（2026-08-07）**: `node_modules` が npm/pnpm混在状態（`.pnpm/` 74エントリ + `.modules.yaml`）であることを確認。`issue-DX-ENV-01-mixed-npm-pnpm-node-modules-state.md` として起票し、クリーン再構築を推奨。
- **ビルドも壊れる（2026-08-07）**: stale `.pnpm/rollup@4.62.3` が `vite build` を `Source phase import "vite/modulepreload-polyfill" must be external` で失敗させる。`rm -rf node_modules/.pnpm/rollup@4.62.3 ...` で解消。混在node_modulesはesbuild（vitest）だけでなくrollup（vite build）も壊すため、`vite build` 実行前に `.pnpm/` 配下のrollup/esbuild重複を確認する。

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

## 2026-08-06: 削除対象コードを `src/` だけで検索して統合テストの参照を見落とした

- 事象: `deterministic_tiebreak_worker_adapter.ts` を「未使用」と判定して削除。実際は `tests/tiebreak/deterministic_tie_break.integration.test.ts` が参照しており、`npx vitest run --config tests/tiebreak/vitest.config.tiebreak.ts` が壊れるところだった。
- 原因: デッドコード判定のgrepを `src/` 配下に限定した。このadapterは `tests/tiebreak/vitest.config.tiebreak.ts`（`include: ["tests/tiebreak/**/*.test.ts"]` の別設定）で実行される統合テストだけが参照しており、通常の `vitest run` には現れなかった。作業ツリー上に残っていた別worktreeのテストが検出の手掛かりになった。
- 対応: `git show 62dca731~1:<path>` から復元し、`tests/tiebreak/vitest.config.tiebreak.ts` で3 tests passを確認。DX-CLEANUP-08（番号衝突のため08へ再番号、旧07）を「参照源がsrc外に偏在」の検討対象として訂正した。
- 再発防止: 「削除対象か」の判定は **`src/` だけでなく `tests/`・`e2e/`・別vitest設定・build設定を含めたリポジトリ全体** で参照を検索する。特に `vitest.config.*.ts` が複数ある場合は、別設定のテストがどのファイルを include するかを確認してから削除判断する。コミット前に `git grep` をリポジトリルート基準で実行する。
