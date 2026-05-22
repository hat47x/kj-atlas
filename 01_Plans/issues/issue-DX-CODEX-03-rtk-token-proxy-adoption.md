# Issue Draft: DX-CODEX-03 RTK token proxy adoption for Codex IDE

- Type: Developer Experience
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: AI Collaboration Ops
- Scope: `Codex local environment` / `01_Plans/issues/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0018`, `ADR-0019`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- Codex IDE の長時間作業では、`git status`、`git diff`、テスト実行、ビルドログなどの冗長なシェル出力がコンテキストを消費しやすい。
- RTK（Rust Token Killer）はシェル出力を圧縮する CLI proxy として導入候補になるが、Codex で透明な自動リライトが保証されるか、Windows/WSL2 環境で実用になるかを確認する必要があった。
- 本環境では Codex の integrated terminal が `wsl` に設定されている一方で、エージェントプロセスから見る WSL distribution が未導入であり、WSL 前提の hook 運用は成立しなかった。

## 2) 背景 / Context

- RTK 公式 README は Codex 向けに `rtk init -g --codex` を案内しているが、Codex 連携は `AGENTS.md + RTK.md` による instructions 方式で、hook による強制リライトではない。
- RTK 公式の supported agents guide でも、Codex CLI は prompt-level instructions であり、transparent rewrite は N/A とされている。
- OpenAI の Codex IDE 説明では、IDE が開いているファイルや選択中コードなどの文脈を使えるため短いプロンプトで進めやすい一方、長い作業や大きい文脈では消費が増え得る。

参照:

- `https://github.com/rtk-ai/rtk`
- `https://github.com/rtk-ai/rtk/blob/master/docs/guide/getting-started/supported-agents.md`
- `https://github.com/openai/codex/issues/19001`
- `https://developers.openai.com/learn/docs-mcp`
- `https://openai.com/index/introducing-upgrades-to-codex/`

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 長時間の調査・実装作業でコンテキスト消費を抑え、継続性とレビュー可能性を高める。
- 安全（THREAT_MODEL / SafeMode）: アプリ本体の SafeMode や share/export 境界には影響しない。RTK telemetry は opt-in であるが、本環境では wrapper で `RTK_TELEMETRY_DISABLED=1` を固定する。
- 企業・行政要件（enterprise_architecture）: 製品運用要件ではなく開発端末の効率化であり、監査対象のアプリ仕様には含めない。
- 後方互換（schemas）: スキーマ変更なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Local Codex environment / Issue memo
- 変更の最小単位:
  1. RTK v0.40.0 Windows binary を checksum 検証後に `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.exe` へ配置する。
  2. Codex sandbox から書ける履歴 DB を使う wrapper `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd` を作成する。
  3. `C:\Users\yhata\.codex\AGENTS.md` に、冗長なコマンドで RTK wrapper を優先する短い指示を追加する。
  4. `C:\Users\yhata\AppData\Roaming\rtk\config.toml` に DB/tee/telemetry/hooks 設定を作成する。
- 非目標:
  - アプリ本体コード、CI、公開ドキュメントの変更。
  - WSL distribution のインストール。
  - Codex 側に hook API がない状態での強制的な透明リライト実装。

## 5) 受入条件 / Acceptance criteria

- [x] RTK の入手元と checksum が確認される。
- [x] `rtk --version` 相当で RTK v0.40.0 が確認できる。
- [x] Codex sandbox から `rtk gain` が失敗しない。
- [x] `rtk git status` で通常の `git status` よりコンパクトな出力と履歴記録を確認できる。
- [x] telemetry が opt-in されておらず、wrapper 側でも無効化されている。
- [x] WSL2 の制約と、Codex では prompt-level instructions であることを明記する。
- [x] ADR 化が必要な条件が明記される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: 既存環境で `rtk` 未導入であることを確認する。
- [x] T2: RTK v0.40.0 Windows release と `checksums.txt` を取得し、SHA-256 一致を確認する。
- [x] T3: RTK binary、wrapper、RTK config、Codex global instructions を配置する。
- [x] T4: `rtk config` / `rtk telemetry status` / `rtk git status` / `rtk gain --history` で動作確認する。
- [x] T5: WSL distribution 不在のため full hook support は未導入として記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `wsl.exe --list --verbose`
  - `where rtk`
  - `rtk --version`
  - `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd config`
  - `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd telemetry status`
  - `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd git status`
  - `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd gain --history`
- 期待結果:
  - RTK v0.40.0 が表示される。
  - `rtk config` が parse error なく設定を表示する。
  - telemetry は `enabled: no` かつ env override により blocked になる。
  - `rtk git status` が履歴 DB に記録され、token saved が表示される。
- 未実施時の理由・代替検証:
  - WSL hook support は WSL distribution 未導入のため未実施。代替として Windows native binary + Codex global instructions + wrapper 方式を採用した。

## 8) 代替案 / Alternatives considered

- 代替案A: `rtk init -g --codex` をそのまま実行する。
  - 不採用理由: Codex sandbox では RTK default DB path が書けず、また `@RTK.md` 参照や Windows/WSL 周辺の既知課題があるため、wrapper と直接指示の方が再現性が高い。
- 代替案B: WSL distribution を導入して Linux 版 RTK を使う。
  - 不採用理由: 本タスクの範囲をローカル開発支援の導入に限定し、OS distribution 追加はユーザ端末の管理判断を要する。
- 代替案C: 導入せず運用ルールだけでコマンド出力を短くする。
  - 不採用理由: `rtk git status` で command-level savings が確認でき、限定導入の価値がある。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード:
  - Codex が RTK 指示を常に守るとは限らない。
  - RTK filter が必要な詳細出力を落とす可能性がある。
  - PATH shim は実ユーザ環境では見えるが、Codex sandbox では見えない場合がある。
- 影響範囲:
  - Codex のローカル開発作業のみ。アプリ本体・CI・公開仕様には影響しない。
- ロールバック手順:
  1. `C:\Users\yhata\.codex\AGENTS.md` から RTK 指示を削除する。
  2. `C:\Users\yhata\.codex\RTK.md` を削除する。
  3. `C:\Users\yhata\AppData\Local\Microsoft\WindowsApps\rtk.cmd` を削除する。
  4. `C:\Users\yhata\AppData\Roaming\rtk\config.toml` を削除または退避する。
  5. `C:\Users\yhata\Documents\Codex\tools\rtk\` と `C:\Users\yhata\Documents\Codex\.rtk\` を削除する。

## 10) Additional context

- 実導入結果（2026-05-23 JST）:
  - RTK binary: `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.exe`
  - Codex-safe wrapper: `C:\Users\yhata\Documents\Codex\tools\rtk\rtk.cmd`
  - RTK config: `C:\Users\yhata\AppData\Roaming\rtk\config.toml`
  - RTK history DB: `C:\Users\yhata\Documents\Codex\.rtk\history.db`
  - Codex global instruction: `C:\Users\yhata\.codex\AGENTS.md`
- 検証結果:
  - `rtk 0.40.0`
  - `rtk config` parse error なし。
  - `rtk telemetry status`: consent never asked / enabled no / `RTK_TELEMETRY_DISABLED=1` blocked。
  - `rtk gain --history`: `rtk git status` 2回で `Saved: 58` を確認。global aggregate は後続の `rtk read` などで母数が増えるため、command-level savings を確認単位とする。
- ADR 化が必要になる条件:
  - RTK を kj-atlas の標準開発環境、CI、レビューゲート、または contributor 必須ツールに昇格する場合。
  - RTK filter の結果をテスト証跡や監査証跡の正本として扱う場合。
  - WSL distribution 導入や Windows hook workaround をプロジェクト標準に含める場合。
