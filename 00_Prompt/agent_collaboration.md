# agent_collaboration — 三エージェント協働ガイド（Cowork / Claude Code / Codex）

本書は `ADR-0045` に基づく **エージェント間の責務分担と協働プロトコルの運用正本** です。

- 決定の背景・理由: `01_Plans/adr/ADR-0045-agent-division-of-labor-cowork-code-codex.md`
- 行動規範・概念制約: `00_Prompt/system_prompt.md` / `00_Prompt/domain.md`
- 実行順序・DoD: `00_Prompt/agent_handover.md`

複数エージェントが**同一ローカルワークツリーを共有して並行作業**する前提のため、衝突回避の git 規律（§3）を全エージェントが必ず守ること。

---

## 1. 各エージェントの得意分野

### Claude Cowork

- 対話的な企画・意思決定支援、上流文書（`00_Prompt` / `01_Plans`）の整理。
- 価値判断・トレードオフの言語化、仮想ステークホルダー合議（`00_Prompt/virtual_stakeholder_consensus.md`）。
- 「何を作るべきか」「なぜそう決めるか」を人間と詰める局面。

### Claude Code

- リポジトリ内の多ファイル横断の読解・検索・整合確認。
- ADR / issue の起票、計画の構造化、索引（AGENTS.md / value_traceability）の同期。
- 実装、テスト駆動の検証（tsc / vitest / pytest）、git 操作・差分管理・復旧。
- MCP 拡張により、ブラウザ実機の最小確認も補助可能（§4）。

### Codex（デスクトップアプリ版）

- 実装の高速な反復。
- **Chrome 操作によるアドホックな実機検証**（実際に画面を開いて挙動を確認）。
- 手早い試行錯誤と、その場での視覚確認が要る局面。

---

## 2. 責務分担（主担当 / 補助）

排他ではなく「主担当」。補助は主担当の不在時や負荷分散時に引き受ける。

| 領域 | 主担当 | 補助 |
| --- | --- | --- |
| 企画・価値判断・上流(00/01)整理・合議 | Cowork | Claude Code |
| ADR/issue 起票・多ファイル横断計画 | Claude Code | Cowork |
| 実装（frontend/backend）の高速反復 | Codex | Claude Code |
| テスト駆動の検証・回帰固定・git規律 | Claude Code | Codex |
| 実機アドホック検証（Chrome で画面確認） | Codex | Claude Code（MCP） |
| リリース判定・品質ゲート統合 | Claude Code | Cowork |

判断に迷う論点は人間（Maintainer）へエスカレーション（solo 段階は Maintainer 単独確定、`ADR-0039`）。

---

## 3. 協働プロトコル（衝突回避・必須）

過去に「作業中ブランチが他エージェントの checkout/pull で消える」「未コミット変更の喪失」「ADR 採番の重複（ADR-0035）」が発生した。再発防止のため全エージェントが守る。

- **CP-1 ブランチ専有**: 作業は専用フィーチャーブランチで行う。`main` で直接作業しない。他エージェントの作業中ブランチに `checkout` / `reset` / `rebase` しない。
- **CP-2 こまめな push**: 節目ごとに `git commit` → 即 `git push -u origin <branch>`。未コミット変更を長時間放置しない。
- **CP-3 採番の衝突回避**: 新規 ADR/issue 採番前に `git fetch`。`origin/main` と全リモートブランチの最大番号＋1 を採る。採番後すぐプレースホルダを commit & push して番号を確保。
- **CP-4 復旧手順**: ブランチが消えても reflog にコミット SHA は残る。`git cat-file -t <sha>` で生存確認 → `git branch <name> <sha>` で復活、または現行 main 上へ cherry-pick。未コミット退避は `git checkout -- .` ではなく `git stash`（破壊回避）。
- **CP-5 main 反映は PR 経由**: `main` 直 push は避け、フィーチャーブランチ → PR でマージ。
- **CP-6 範囲の明示**: 開始時に Scope（Docs/Frontend/Backend/Schema＋ブランチ名）を宣言。他者の主担当領域への割り込みは事前合意または別ブランチで。

> 補足（既知の環境事情）: `/mnt/d` 上のワークツリーは git 上で CRLF/LF の大量差分が出る。実差分は `git diff --ignore-all-space` で確認する。WSL 既定 node は古い（v12）ため frontend 作業は nvm node20 を使う（§4）。

---

## 4. Claude Code 拡張（MCP）の導入と再現性

Claude Code が実機検証等を補助できるよう、設定をリポジトリ `.claude/` に再現性ある形で置く。詳細・手順は `.claude/README.md` を正本とする。

### 4.1 frontend 検証の前提（全エージェント共通）

```bash
# WSL: node20 を使う（既定 v12 では Vite が動かない）
export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"; nvm use 20
cd 03_Implement/frontend
npm ci                              # 初回のみ（約35秒）
node ./node_modules/typescript/bin/tsc --noEmit          # 型
node ./node_modules/vitest/vitest.mjs run <path>         # 単体
node ./node_modules/vite/bin/vite.js build               # ビルド
npm run preview                     # http://127.0.0.1:4173 で実機確認
node ./node_modules/playwright/cli.js test <spec>        # e2e
```

### 4.2 役割境界

- **Codex**: Chrome 操作による自由なアドホック実機検証（主担当）。
- **Claude Code**: MCP（claude-in-chrome 等）が利用可能な環境では、preview（4173）に対する最小の確認（表示崩れ・主要導線の到達）を補助。MCP 不在時は e2e（Playwright）と source-string contract テストで代替する。
- どちらも `domain.md` の禁止事項（AIが保留を勝手に解消しない等）と SafeMode 既定ON を侵さない。

### 4.3 導入手順

`.claude/README.md` の手順に従う。`.claude/settings.json`（プロジェクト共有設定）はリポジトリ管理対象とし、個人トークン等の秘匿情報は含めない（含める場合は `.claude/settings.local.json` で git 管理外）。

---

## 5. 更新ルール

- 本書は `ADR-0045` の運用正本。責務分担・プロトコルの変更は ADR を先に更新してから本書へ反映する。
- 新しいエージェントや拡張を追加した場合は、`AGENTS.md` の Read Order / Project Map と本書を同期する。
