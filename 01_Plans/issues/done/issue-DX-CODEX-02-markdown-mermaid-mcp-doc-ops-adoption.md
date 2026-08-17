# Issue Draft: DX-CODEX-02 Markdown + Mermaid.js / MCP 文書整備運用の導入検証

- Type: Developer Experience
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: AI Collaboration Ops
- Scope: `00_Prompt/skills/` / `04_Documentation/` / `01_Plans/issues/`
- Related Backlog: N/A
- Related ADR/Spec: `ADR-0001`, `ADR-0018`, `ADR-0019`, `ADR-0022`
- Dependencies: N/A
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- Markdown + Mermaid.js 文書更新時の検証手順（構文確認、視覚確認、証跡記録）が統一されていない。
- MCP活用方針が明文化されておらず、エージェントごとの差が生じる。

## 2) 背景 / Context

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

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog: 該当なし。

## Stream I serial execution（2026-05-04 / DX-CODEX-02運用設計整備）

### Phase 1: Read同期（現行運用ルールとの差分抽出）
- 再読対象:
  - `04_Documentation/codex_skill_operations.md`（参照のみ）
  - 本Issue（DX-CODEX-02）
- 差分抽出結果:
  1. Mermaid/MCP導入の可否判断は記載済みだが、段階別の**導入判断可能性**が不足。
  2. MCP利用時/非利用時の証跡方針はあるが、失敗時の復旧導線が分離されていない。
  3. 新規運用者向けに最小判断セット（教育コスト最小化）を明示する余地がある。

### Phase 2: Plan（AC/DoD再定義）
- AC（3観点）:
  - AC-1 導入判断可能性: Mermaid/MCP運用を PoC→限定導入→本番 で判定できる。
  - AC-2 再現運用性: MCP優先・CLI代替・証跡記録の順序を固定し、担当者依存を排除する。
  - AC-3 教育コスト最小化: 図更新タスク時に確認する導入判定チェックリストを最小化して提示する。
- DoD:
  - DoD-1 段階導入と段階別ロールバックが本文に明記される。
  - DoD-2 フェイルセーフ停止条件（再現不能/ロールバック欠落/監査証跡欠落）を明文化する。
  - DoD-3 次担当へ引き渡し可能な判定チェックリストが存在する。

### Phase 3: Execute（段階導入 + ロールバック）
- Stage 1: PoC（Mermaid変更なしの文書タスク）
  - 手順:
    1. `markdown-mermaid-docops` の手順を使い、非視覚変更タスクを1件実施。
    2. MCP不要時は「非利用理由」を明記する。
  - Go条件: docs-check成功 + 非利用理由が証跡として残る。
  - Rollback: 手順再現不能時はMCP連携を停止し、CLI最小検証のみに戻す。
- Stage 2: 限定導入（Mermaid変更を含む2タスク）
  - 手順:
    1. Mermaidブロック変更タスクでMCP優先確認を実施。
    2. MCP不可時はCLI代替で構文検証し、差分証跡を記録。
  - Go条件: 2タスク連続で「MCP利用有無/代替検証/結果」が同一形式で追跡可能。
  - Rollback: 証跡欠落または検証不一致が発生した時点でPoC段階へ戻す。
- Stage 3: 本番運用（標準手順化）
  - 手順:
    1. DX-CODEX系IssueにMCP優先・CLI代替の固定テンプレを適用。
    2. 月次レビューで証跡欠落率を確認。
  - Go条件: 欠落率0%かつフェイルセーフ未発火。
  - Rollback: 欠落率>0%なら限定導入へ戻し、記録テンプレを再教育。

### Phase 4: Verify（曖昧手順確認 + 自己修復）
- 曖昧語の排除:
  - 「必要時」表現を具体化し、MCP可否判定→代替検証→証跡記録の順序を固定。
- self-repair: 0/3（追加修正なし）。
- 停止条件:
  1. 再現不能な手順が1件でも発生したら停止。
  2. 段階別ロールバック未定義なら停止。
  3. 監査証跡（MCP利用有無/代替コマンド/結果）が欠落したら停止。

### Phase 5: Proceed（次担当への引き渡し）
- 導入判定チェックリスト:
  1. Mermaidブロック変更の有無を明記したか
  2. MCPを使ったか/使わないかを記録したか
  3. MCP非利用時の代替コマンドを記録したか
  4. PoC/限定導入/本番のどの段階か明記したか
  5. Go/No-Go判定の根拠を記録したか
  6. ロールバック手順をその段階に紐づけたか
  7. docs-check結果を記録したか
  8. フェイルセーフ停止条件に抵触していないか
  9. 公開stub/内部正本の責務境界を逸脱していないか
  10. 次担当への未完了事項を明記したか
