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

## 2. 導入した Codex スキル

- Skill 名: `gsd-kj-atlas`
- 配置（リポジトリ）: `00_Prompt/skills/gsd-kj-atlas/`
- 配置（ローカルCodex）: `$CODEX_HOME/skills/gsd-kj-atlas`（既定 `~/.codex/skills/gsd-kj-atlas`）

## 3. 運用ルール（Codex）

### 3.1 起動条件（使うとき）

次の条件を満たすタスクで利用する。

1. 1回の作業で完了しない中〜大規模変更。
2. フェーズ分割（調査 / 実装 / 検証 / 文書同期）が必要。
3. 途中再開（resume）が想定される。

逆に、軽微な typo 修正や単一ファイル修正では利用しなくてよい。

### 3.2 実行順序（固定）

1. `AGENTS.md` の Read Order を先に確認。
2. `gsd-kj-atlas` で milestone / phase を起票。
3. 各 phase の受入条件を `agent_handover.md` のテンプレで固定。
4. 実装。
5. verify（tests/lint/差分確認）。
6. `00〜04` の該当文書を同期。

### 3.3 ガードレール

- GSD 上の計画が上位文書（00〜02）と矛盾する場合は、**実装を停止**して上位文書を先に改訂提案する。
- Docs-only タスクではコードを変更しない。
- Schema 変更時は `02_Architecture/schemas.md` を先に更新する。
- UI の視覚変更がある場合はスクリーンショットを取得する。

### 3.4 記録ルール

各 phase 完了時に最低限以下を残す。

- 変更ファイル一覧
- 実行した検証コマンド
- 未達の受入条件
- 次フェーズの開始条件

## 4. ロールバック方針

GSD 運用が過剰に重くなった場合は、
本ドキュメントを維持したまま「milestone 粒度を 1 つ下げる（phase を減らす）」ことで運用負荷を調整する。

GSD の導入自体を停止する場合も、
`00_Prompt/agent_handover.md` の DoD と安全ゲートは維持する。
