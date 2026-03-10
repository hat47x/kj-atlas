---
name: markdown-mermaid-docops
description: Markdown + Mermaid.js ドキュメント更新時に、構造化編集・図表検証・MCPスクリーンショット確認を標準化する補助スキル。
---

# markdown-mermaid-docops

## Purpose

Markdown文書とMermaid図を更新するタスクで、
再現可能な検証（lint / parse / preview）を揃えて品質を安定化する。

## Use this skill when

- `*.md` に Mermaid 図（` ```mermaid `）を追加・修正する。
- ドキュメント変更で図と本文の整合確認が必要。
- MCP（browser/playwright）で視覚確認が必要。

## Mandatory constraints

1. 仕様の正本は `00_Prompt` / `01_Plans` / `02_Architecture`。
2. 本skillは文書編集と検証手順の補助のみを行う。
3. 安全制約（SafeMode既定ON、漏えい防止）に反する記述を提案しない。

## Workflow

1. **Plan**: 対象Markdownの Scope / Non-Goals / Acceptance / Checks（DoD）を先に固定する。
2. **Execute**: Mermaidブロックを追加/編集し、見出しと参照導線を同期する。
3. **Verify**: `npx -y @mermaid-js/mermaid-cli -i <input.mmd> -o <output.svg>` で構文検証する。
4. **Verify(visual)**: 必要に応じて MCP browser/playwright で描画確認する。
5. **Record evidence**: 検証コマンド・結果・artifact path（またはCLIログ）を記録する。
6. **Self-correction**: 検証失敗時は修正→再検証を最大3回まで実施し、3回超過時は停止条件として報告する。

## Evidence policy (Mermaid/MCP)

- 優先証跡: MCP browser/playwright のスクリーンショット artifact。
- 代替証跡: Mermaid CLI のSVG生成成功ログ（環境制約でMCP不可の場合）。
- 記録最小項目:
  - 対象ファイル
  - Mermaid block の変更有無
  - 実行コマンド
  - 成否（pass/fail）
  - 生成物パス（artifact / svg）
  - 再試行回数（self-correction count）

## Checks

- Mermaid構文エラーがない。
- Markdown見出しレベルとリンクが壊れていない。
- 図と本文の語彙が一致している。
- MCP利用時は artifact path が残っている、非利用時は代替証跡理由が残っている。
