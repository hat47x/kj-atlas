# Codex RTK Token Saving Operations

対象読者: kj-atlas を Codex などの生成AIエージェントで作業するエージェント自身、およびその運用を確認する開発者。

目的: RTK（Rust Token Killer）を、Codex のシェル出力を短く保つ補助として使い、長時間作業でのコンテキスト消費を減らす。

範囲外: kj-atlas アプリ本体の実行時仕様、CI必須ツール化、RTK出力を監査証跡やテスト証跡の正本にすること。

## 1. 結論

RTK は本プロジェクトでは **Codexローカル作業の補助ツール** として使う。アプリ本体、CI、公開仕様、利用者向け文書の正本ではない。

Codex は次の原則で使い分ける。

- 冗長な確認は RTK 経由にする。
- 正確な全文が必要なときは通常コマンドに戻す。
- RTKで短くなった出力だけを根拠にせず、必要に応じて対象ファイルや生ログを再確認する。

## 2. この環境での配置

Windows Codex host では次の配置を正本とする。

| 項目 | 値 |
|---|---|
| RTK binary | `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.exe` |
| Codex-safe wrapper | `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd` |
| PATH shim | `C:\Users\yhata\AppData\Local\Microsoft\WindowsApps\rtk.cmd` |
| Config | `C:\Users\yhata\AppData\Roaming\rtk\config.toml` |
| History DB | `C:\Users\yhata\Documents\Codex\.rtk\history.db` |
| Tee directory | `C:\Users\yhata\Documents\Codex\.rtk\tee` |

Wrapper は `RTK_DB_PATH` と `RTK_TELEMETRY_DISABLED=1` を設定する。Codex からは、直接 `rtk` が使える場合でも wrapper と同じ動作であることを確認してから使う。

## 3. 作業開始時の確認

作業開始時または挙動が怪しいときは、次を短く確認する。

```powershell
rtk --version
rtk config
rtk telemetry status
rtk git status
rtk gain --history
```

期待値:

- `rtk --version` が表示される。
- `rtk config` が parse error なく表示される。
- telemetry は無効で、`RTK_TELEMETRY_DISABLED=1` が有効である。
- `rtk git status` が通常の `git status` より短い出力を返す。
- `rtk gain --history` に履歴が記録される。

## 4. 使うべき場面

次のコマンドは、正確な全文が不要なら RTK 経由を優先する。

| 場面 | 推奨コマンド |
|---|---|
| git状態確認 | `rtk git status` |
| 差分の粗い確認 | `rtk git diff` または `rtk diff <file>` |
| 履歴の粗い確認 | `rtk git log` |
| ファイル検索 | `rtk grep <pattern> <path>` または通常の `rg` |
| ディレクトリ確認 | `rtk ls` / `rtk tree` |
| テスト失敗だけ見たい | `rtk pytest ...` / `rtk vitest ...` / `rtk test ...` |
| TypeScript確認 | `rtk tsc ...` |
| lint確認 | `rtk lint ...` / `rtk ruff ...` |
| Docker確認 | `rtk docker ...` |
| JSONの形だけ見たい | `rtk json --keys-only ...` |
| 削減実績確認 | `rtk gain --history` |

通常の `rg` は高速であり、検索結果が多すぎない場合はそのまま使ってよい。出力が大きくなりそうな検索、ログ確認、テスト結果確認では RTK を優先する。

## 5. 通常コマンドに戻す場面

次の場面では RTK を使わない、または RTK後に通常コマンドで再確認する。

- 正確な全文、行番号、差分全体、スタックトレース全体が必要。
- テスト失敗の詳細を修正に使う。
- ファイル編集、削除、移動、git commit、git push など、実際に状態を変える操作。
- 対話的コマンド、shell builtin、PowerShell構文が複雑なコマンド。
- セキュリティ、秘密情報、監査、SafeMode境界に関わる確認。
- RTKが出力を削りすぎて判断できない。

状態変更を伴わないが shell 構文のまま履歴だけ取りたい場合は、次を使う。

```powershell
rtk proxy <command ...>
```

`proxy` はフィルタせずに実行し、RTK履歴だけを記録する。正確な出力が必要なら、最初から通常コマンドを使う。

## 6. Codexの判断ルール

Codex は各シェル実行前に、次を短く判断する。

1. 出力が長くなりそうか。
2. 要るのは要約か、全文か。
3. 失敗時に詳細ログへ戻れるか。
4. その結果をユーザに説明する必要があるか。

判断結果:

- 要約で足りる: RTKを使う。
- 失敗原因を読む必要がある: まずRTK、必要なら通常コマンドで詳細を読む。
- 証跡として正確性が必要: 通常コマンドを使う。
- 状態を変える: 通常コマンドを使う。

## 7. 記録と説明

RTKを使った場合でも、ユーザへ報告するときは「何を確認したか」と「結果」を明確に書く。RTKの短縮出力をそのまま貼る必要はない。

例:

- `rtk git status` で作業ツリーが clean であることを確認した。
- `rtk gain --history` で token saved を確認した。
- `rtk pytest ...` で失敗概要を確認し、詳細は通常pytestで再実行した。

## 8. ロールバック

RTKが作業を妨げる場合は、次の順で戻す。

1. そのコマンドだけ通常コマンドへ戻す。
2. `rtk proxy <command ...>` で履歴だけ取る。
3. `C:\Users\yhata\.codex\AGENTS.md` のRTK優先指示を一時的に無視する。
4. 恒久的に無効化する場合は `01_Plans/issues/issue-DX-CODEX-03-rtk-token-proxy-adoption.md` のロールバック手順を参照する。

## 9. 関連文書

- `AGENTS.md`
- `00_Prompt/codex_gsd_skill_ops.md`
- `01_Plans/issues/issue-DX-CODEX-03-rtk-token-proxy-adoption.md`
- `04_Documentation/codex_skill_operations.md`
