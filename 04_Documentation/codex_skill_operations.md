# Codex Skill Operations Guide

> DOC-OPS-05 Classification: **Move internal**
> Audience: AIエージェント運用担当者（内部）
> Goal: Codex skill運用手順を内部ガイドへ統合する。
> Public boundary: 04では最小参照のみ残し、運用詳細は00_Prompt/01_Plansへ集約予定。
> Next action: DOC-OPS-05 issueの分類固定に従い、Move internal は移設PR、Improve external は公開品質改善PRを後続で実施。


## Purpose

本書は、`kj-atlas` プロジェクトで Codex skill を安全に導入・運用するための実務ガイドである。
仕様正本（`00_Prompt` / `01_Plans` / `02_Architecture`）を維持したまま、skill を **実行補助** として活用する。
公開文書品質の確認は `01_Plans/documentation_quality.md` を参照する。

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

### Plan / Execute / Verify protocol (Mermaid docs task)

Mermaidを含む docs タスクは次の順序を固定する。

1. **Plan**: Scope / Non-Goals / Acceptance / Checks（DoD）を先に確定。
2. **Execute**: Mermaid block・本文・見出し導線を同時更新。
3. **Verify**: docs-check と Mermaid構文検証を実施。
4. **Self-correction**: 修正→再検証を最大3回。3回超過時は停止し、前提崩壊/競合を報告。

### Mermaid validation command (recommended)

Mermaid図を含むドキュメント変更では、次のコマンドで構文検証する。

```bash
npx -y @mermaid-js/mermaid-cli -i /tmp/diagram.mmd -o /tmp/diagram.svg
```

### docs-check commands (issue memo)

```bash
python 01_Plans/issues/validate_active_issue_memos.py
python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py
```

### MCP usage / evidence policy

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

## Quality gate (Phase 1〜6, Doc-Ops-05 Set 2)

このガイド更新時は、次の品質ゲートを適用する。

1. **Phase 1: Scope固定**
   - Skill運用手順のみを更新し、仕様正本（00〜02）の内容を上書きしない。
2. **Phase 2: 文書メタ確認**
   - Audience / Goal / Public boundary が冒頭で判別可能であることを確認する。
3. **Phase 3: 用語統一**
   - `reviewed / unreviewed`、`SafeMode`、`share/export` の語彙を既存正本に合わせる。
4. **Phase 4: 導線確認**
   - `AGENTS.md` Read Order と `00_Prompt/codex_gsd_skill_ops.md` への参照整合を確認する。
5. **Phase 5: 検証確認**
   - docs-check / Mermaid検証 / 代替証跡のいずれかを記録可能な形で残す。
6. **Phase 6: 完了判定**
   - docs-only 原則と安全境界（SafeMode既定ON）を損なっていないことを確認する。

失敗時は **最大3回まで修復して再判定** し、3回超過時は作業を停止して `01_Plans/issues/` にブロッカーを記録する。

## Related

- `00_Prompt/codex_gsd_skill_ops.md`
- `01_Plans/documentation_quality.md`
- `04_Documentation/codex_skill_operations.md`（本書）
