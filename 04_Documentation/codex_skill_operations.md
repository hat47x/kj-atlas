# Codex Skill Operations Guide

## Purpose

本書は、`kj-atlas` プロジェクトで Codex skill を安全に導入・運用するための実務ガイドである。
仕様正本（`00_Prompt` / `01_Plans` / `02_Architecture`）を維持したまま、skill を **実行補助** として活用する。

## Codex skill loading specification (confirmed)

- Codex が自動ロードする skill の配置先は次の2系統。
  1. システム同梱: `/opt/codex/skills/.system/*`
  2. ユーザー追加: `$CODEX_HOME/skills/*`（既定: `~/.codex/skills/*`）
- リポジトリ内 `00_Prompt/skills/*` は配布テンプレートとして扱い、実行時に使うには `$CODEX_HOME/skills` への配置が必要。

## Recommended skill set for kj-atlas

本プロジェクトでの優先導入対象を次の4つとする。

1. `gsd-kj-atlas`（repo template）
   - 複数phase運用・再開性・Acceptance先出しを標準化。
2. `doc`（curated）
   - ドキュメント起点タスクの整理・更新品質を補助。
3. `security-threat-model`（curated）
   - 脅威モデル観点（SafeMode / leak防止）を点検。
4. `playwright`（curated）
   - UI変更時のE2E/スモーク確認を補助。

## Installation procedure

### 1) Curated skills installation

```bash
python /opt/codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo openai/skills \
  --path skills/.curated/doc \
  --path skills/.curated/security-threat-model \
  --path skills/.curated/playwright
```

### 2) Project template skill installation

```bash
mkdir -p "$HOME/.codex/skills"
cp -R 00_Prompt/skills/gsd-kj-atlas "$HOME/.codex/skills/gsd-kj-atlas"
```

### 3) Verification

```bash
ls "$HOME/.codex/skills"
```

導入後は **Codex を再起動**して skill を再読込する。

## Usage protocol (Plan -> Execute -> Verify)

1. `AGENTS.md` Read Order を確認。
2. `gsd-kj-atlas` で Scope / Non-Goals / Acceptance / Checks を固定。
3. 実装時は仕様正本（00〜02）を参照し、skillは判断補助に限定。
4. `security-threat-model` で safeMode / share-export 境界を確認。
5. Docs変更を含む場合は `doc` を使って 04_Documentation と導線を同期。
6. UI変更時は `playwright` で回帰確認・必要に応じてスクリーンショット取得。

## Guardrails

- skill は仕様の正本ではない。仕様追加は ADR/Architecture 経由で行う。
- SafeMode既定ON、漏えい防止（share/export）の制約を破る提案は不採用。
- Docs-only task ではコード変更を行わない。


## Markdown + Mermaid.js / MCP adoption

### Added project skill (template)

- `00_Prompt/skills/markdown-mermaid-docops/SKILL.md` を配布テンプレートとして追加。
- 実行時は以下で `$CODEX_HOME/skills` に配置する。

```bash
mkdir -p "$HOME/.codex/skills"
cp -R 00_Prompt/skills/markdown-mermaid-docops "$HOME/.codex/skills/markdown-mermaid-docops"
```

### Mermaid validation command (recommended)

Mermaid図を含むドキュメント変更では、次のコマンドで構文検証する。

```bash
npx -y @mermaid-js/mermaid-cli -i /tmp/diagram.mmd -o /tmp/diagram.svg
```

### MCP usage policy

- 図やUI導線の視覚確認は MCP の browser/playwright ツールを優先する。
- 画像証跡が必要な場合は artifact path を記録し、Issue/PRへ添付する。
- ブラウザ利用不可時は代替として Mermaid CLI のSVG生成ログを検証記録に残す。


## DX-CODEX-01 scoped execution notes

- この運用更新は docs-only で実施し、編集対象を以下の3ファイルへ限定する。
  - `00_Prompt/codex_gsd_skill_ops.md`
  - `04_Documentation/codex_skill_operations.md`
  - `01_Plans/issues/issue-DX-CODEX-01-codex-skill-adoption-and-validation.md`
- `01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` は本タスクの更新対象外。
- docs-check は validator / unittest の2本を実行し、Issue memo に結果を記録する。

