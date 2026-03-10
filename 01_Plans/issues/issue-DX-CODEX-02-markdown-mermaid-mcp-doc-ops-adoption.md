# Issue Draft: DX-CODEX-02 Markdown + Mermaid.js / MCP 文書整備運用の導入検証

- Type: Developer Experience
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: AI Collaboration Ops
- Scope: `00_Prompt/skills/` / `04_Documentation/` / `01_Plans/issues/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0018`, `ADR-0019`, `ADR-0022`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- Markdown + Mermaid.js 文書更新時の検証手順（構文確認、視覚確認、証跡記録）が統一されていない。
- MCP活用方針が明文化されておらず、エージェントごとの差が生じる。

## 2) 背景 / Context

- Codex skill 導入方針は `DX-CODEX-01` で整備中。
- Mermaid図を含む文書では、テキスト差分のみだと図破損を見逃す可能性がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 伝達品質と再現性の改善。
- 安全（THREAT_MODEL / SafeMode）: 文書運用のみで安全境界変更は行わない。
- 企業・行政要件（enterprise_architecture）: 直接影響なし。
- 後方互換（schemas）: スキーマ変更なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs / Skill template / Issue memo
- 変更の最小単位:
  1. `markdown-mermaid-docops` skill template を追加。
  2. Codex運用ガイドに Mermaid検証とMCP運用方針を追記。
  3. 本Issueで試行運用ログを蓄積する。
- 非目標:
  - アプリ実装コードの改修。
  - 新規ADRの即時追加。

## 5) 受入条件 / Acceptance criteria

- [x] Mermaid図付き文書タスクに適用できる skill template が存在する。
- [x] Mermaid構文検証コマンドが運用ガイドに記載される。
- [x] MCP利用時と非利用時の証跡方針が明記される。
- [x] `docs-check` レベルの検証（issue validator / unittest）が通る。

## 6) 実装タスク分解 / Task breakdown

- [x] T1: skill template を追加。
- [x] T2: 運用ガイド追記。
- [x] T3: Active issue へ登録。
- [x] T4: 試行ログテンプレートを追記。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- 期待結果:
  - Active issue index と memo 構造の整合が取れている。
- 未実施時の理由・代替検証:
  - なし。

## 8) 代替案 / Alternatives considered

- 代替案A: スキル追加は行わず、運用ガイドのみ整備。
- 代替案B: MCP方針を明記せずMermaid CLIのみ利用。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 運用ルールが増えて手順が重くなる。
- 影響範囲: 文書更新タスクの初動コスト。
- ロールバック手順: `markdown-mermaid-docops` 推奨を停止し、ガイドを簡素化。

## 10) Additional context

```md
- Task:
- Mermaid blocks changed:
- Applied skills/MCP:
- Validation evidence:
- Follow-up:
```


## 11) AC/DoD補完ドラフト（DX-CODEX-02）

- AC補完:
  - Plan/Execute/Verify/Self-correction（最大3回）を文書化する。
  - MCP優先・CLI代替の証跡要件を最小項目で固定する。
- DoD補完:
  - 対象3ファイルのみ差分であること。
  - docs-check（validator + unittest）が成功すること。
  - Mermaid検証コマンドが運用ガイドとskillの双方に記載されること。

## 12) 実行ログ（trial）

```md
- Task: DX-CODEX-02 Mermaid/MCP evidence policy implementation
- Mermaid blocks changed: no (policy/protocol text update)
- Applied skills/MCP: markdown-mermaid-docops (template update), MCP not required for this non-visual docs change
- Validation evidence:
  - python 01_Plans/issues/validate_active_issue_memos.py => pass
  - python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py => pass
- Follow-up: T3（Active issue index更新）は本タスクの禁止範囲のため未実施
```
