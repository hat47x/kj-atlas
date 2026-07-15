# codex_gsd_skill_ops — Get Shit Done 導入評価と運用ルール

## 1. 結論（本プロジェクトへの適用可否）

**結論: 条件付きで有用（導入推奨）**。

`kj-atlas` は `00〜04` の階層ドキュメントと ADR 中心で進める開発方式を採っており、
Get Shit Done（以下 GSD）の「milestone → phase → verify」の運用は、
以下の点で整合する。

- 単一タスク原則（`00_Prompt/agent_handover.md`）と GSD の phase 分割が一致する。
- 受入条件先出し（Acceptance 固定）と GSD の verify 運用が一致する。
- 中断/再開を前提とした継続進行（resume/pause）が、長期運用方針と整合する。

一方で、以下の**非適用ルール**を必須とする。

- GSD は「実行管理の補助」に限定し、仕様の正本にはしない。
- 要件・設計の正本は従来どおり `00_Prompt` / `01_Plans` / `02_Architecture` とする。
- SafeMode 既定ON、漏えい防止（share/export）を侵す提案は採用しない。

## 2. GPT-5.3-Codex における Skills 格納位置の調査結果

### 2.1 調査結果（正規のロード元）

本実行環境で Codex が自動認識する skill は次の2系統。

1. システム同梱: `/opt/codex/skills/.system/*`
2. ユーザー追加: `$CODEX_HOME/skills/*`（既定: `~/.codex/skills/*`）

したがって、`00_Prompt/skills/gsd-kj-atlas/SKILL.md` は
**リポジトリ内ドキュメント資産としては有効**だが、
**そのままでは Codex の実行時スキルとして自動ロードされない**。

### 2.2 既存配置の妥当性判定

- リポジトリ配置（`00_Prompt/skills/...`）: ✅ 妥当（配布元・レビュー対象として有効）
- 実行時配置（`$CODEX_HOME/skills/...`）: ❌ 未配置なら不十分（Codex は使えない）

## 3. 修正方針（不適切な場合に何を直すか）

### 3.1 最低限の修正

1. `SKILL.md` を配布元としてリポジトリに保持する（現状維持）。
2. 利用時は必ず `$CODEX_HOME/skills/gsd-kj-atlas/` に配置する。
3. AGENTS には「リポジトリ内 skill はテンプレートであり、実行時は `$CODEX_HOME/skills` が正本」と明記する。

### 3.2 導入手順（推奨）

```bash
mkdir -p "$HOME/.codex/skills"
cp -R 00_Prompt/skills/gsd-kj-atlas "$HOME/.codex/skills/gsd-kj-atlas"
```

> 注: 上流 `gsd-build/get-shit-done` は Codex skill 形式（`SKILL.md`）を直接提供していないため、
> そのまま `install-skill-from-github.py` で導入はできない。

## 4. 運用ルール（Codex）

### 4.1 起動条件（使うとき）

次の条件を満たすタスクで利用する。

1. 1回の作業で完了しない中〜大規模変更。
2. フェーズ分割（調査 / 実装 / 検証 / 文書同期）が必要。
3. 途中再開（resume）が想定される。

逆に、軽微な typo 修正や単一ファイル修正では利用しなくてよい。

### 4.2 実行順序（固定）

1. `AGENTS.md` で現在のタスクに必要な正本だけを確認。
2. `gsd-kj-atlas` で milestone / phase を起票。
3. 各 phase の受入条件を `agent_handover.md` のテンプレで固定。
4. 実装。
5. verify（tests/lint/差分確認）。
6. `00〜04` の該当文書を同期。

### 4.3 ガードレール

- GSD 上の計画が上位文書（00〜02）と矛盾する場合は、**実装を停止**して上位文書を先に改訂提案する。
- Docs-only タスクではコードを変更しない。
- Schema 変更時は `02_Architecture/schemas.md` を先に更新する。
- UI の視覚変更がある場合はスクリーンショットを取得する。

### 4.4 記録ルール

各 phase 完了時に最低限以下を残す。

- 変更ファイル一覧
- 実行した検証コマンド
- 未達の受入条件
- 次フェーズの開始条件

## 5. ロールバック方針

GSD 運用が過剰に重くなった場合は、
本ドキュメントを維持したまま「milestone 粒度を 1 つ下げる（phase を減らす）」ことで運用負荷を調整する。

GSD の導入自体を停止する場合も、
`00_Prompt/agent_handover.md` の DoD と安全ゲートは維持する。

## 6. 追加導入する補助 skill（2026-03）

GSD 運用を中核にしつつ、以下の curated skill を併用する。

- `doc`: docs-only / docs+code タスクで、差分説明と同期漏れ検知を補助。
- `security-threat-model`: SafeMode・公開境界・漏えい防止の脅威観点レビューを補助。
- `playwright`: UI変更時の検証フロー補助（E2E / screenshot）。

### 6.1 導入コマンド（curated）

```bash
python /opt/codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo openai/skills \
  --path skills/.curated/doc \
  --path skills/.curated/security-threat-model \
  --path skills/.curated/playwright
```

### 6.2 適用境界

- 仕様決定は従来どおり `00_Prompt` / `01_Plans` / `02_Architecture` が正本。
- 補助skillは「実施品質と検証密度の向上」のみに使う。

## 7. Markdown + Mermaid.js 文書整備への適用

- 文書タスクで Mermaid 図を伴う場合は `markdown-mermaid-docops` を併用し、
  `Scope / Non-Goals / Acceptance / Checks` を固定したうえで図表検証を行う。
- 視覚確認は MCP（browser/playwright）を優先し、不可時は Mermaid CLI のSVG生成ログを代替証跡とする。

### 7.1 導入コマンド（project template skill）

```bash
mkdir -p "$HOME/.codex/skills"
cp -R 00_Prompt/skills/markdown-mermaid-docops "$HOME/.codex/skills/markdown-mermaid-docops"
```


## 8. DX-CODEX-01 専任運用メモ（限定スコープ）

- 本タスクでは編集対象を次の3ファイルに限定する。
  - `00_Prompt/codex_gsd_skill_ops.md`
  - `04_Documentation/codex_skill_operations.md`
  - `01_Plans/issues/issue-DX-CODEX-01-codex-skill-adoption-and-validation.md`
- 次のファイルは更新しない。
  - `01_Plans/issues/README.md`
  - `01_Plans/project-progress-dashboard.md`
- docs-check は以下を必須実行する。
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`

