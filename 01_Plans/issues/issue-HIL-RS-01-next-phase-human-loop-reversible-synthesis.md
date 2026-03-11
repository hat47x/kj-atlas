# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner
- Scope: `01_Plans/`, `02_Architecture/`, `03_Implement/frontend/`, `04_Documentation/`
- Related Backlog: HIL-RS-01
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/review_attribution.md`
- Expected verification level: `docs-check`

## 1) 課題 / Problem statement

- `ENV-ARCH-01` は Close 判定済みだが、次フェーズの作業起点（Backlog/依存順序/停止条件）が未固定だと再開時に手戻りが発生する。
- プロジェクト目的（意味の保留・単一正解の否定・可逆性）に直結する次タスクを、再開可能な粒度で固定する必要がある。

## 2) 背景 / Context

- `phase-exit-evaluation-ENV-ARCH-01-2026-03-11.md` で、次Backlog IDの Open 化が引き継ぎ条件として明示されている。
- `ADR-0001` では P-01/P-02/P-04 が価値軸として固定され、HIL反復が要求される。
- `domain.md` は AI が単一正解を断定しないこと、保留状態を勝手に解消しないことを拘束する。

### このIssueが保持する内容（実行管理SSOT）

- 次フェーズ（HIL-RS-01）の実行順序と依存関係
- AC達成状況
- 検証コマンドと結果

## 3) 提案する解決策 / Proposed solution

- 変更対象: docs/plans（契約先行）
- 実行パッケージ:
  - A1: Architecture契約起票（Critique入力・再提案差分・レビュー帰属）
  - A2: Frontend実装起票（候補比較/入力/差分可視を分離）
  - A3: Documentation同期起票（操作手順・制約・検証手順）
- 非目標:
  - LLM provider 抽象の再設計
  - SafeMode既定ONを緩める変更
  - 単一スコア/ランキング提示

## 4) 受入条件 / Acceptance criteria

- [ ] `ADR-0026` と本issueで、目的/非目標/停止条件が一致している。
- [ ] A1→A2→A3 の依存順序が明示され、各タスクが再開可能粒度で定義されている。
- [ ] 安全制約（SafeMode既定ON、share/export漏えい防止を弱めない）が明記されている。
- [ ] docs-check の結果が再現可能コマンドで記録される。
- [ ] `issues/README.md` と `project-progress-dashboard.md` の Active 状態が同期される。

## 5) 実装タスク分解 / Task breakdown

- [x] T1: `ADR-0026` の status を Decider判断に応じて確定（Proposed→Accepted/Rejected）する。
- [x] T2: A1用 issue（Architecture最小I/F定義）を作成し、契約境界を固定する。
- [ ] T3: A2用 issue（Frontend分割実装）を作成し、UI変更時の screenshot方針を含む検証計画を付与する。
- [ ] T4: A3用 issue（Documentation同期）を作成し、運用手順と制約を更新する。
- [ ] T5: `phase-exit-evaluation-HIL-RS-01-<date>.md` の評価テンプレを用意する。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "HIL-RS-01|ADR-0026|Active:|次フェーズ" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`
- 期待結果:
  - HIL-RS-01 が Active issue として index / dashboard の双方で確認できる。
- 未実施時の理由・代替検証:
  - docs-check が実行不能な場合は `rg` 出力で同期箇所を手動照合する。

## 7) 代替案 / Alternatives considered

- 代替案A: ENV-ARCH系の微修正を継続して次フェーズ定義を後ろ倒しする。
  - 却下理由: 価値直結機能（HIL反復）への着手が遅れる。
- 代替案B: ADRなしで実装先行する。
  - 却下理由: 00〜02優先の階層ルールに反し、スコープドリフトを招く。

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: タスク分解が粗く、再開時に優先順位が曖昧化する。
- 影響範囲: plan/architecture/frontend/documentation の同期運用。
- ロールバック手順: HIL-RS-01 を Draft に戻し、`ADR-0026` の Decision 節を縮小して再承認する。

## 9) Additional context

- 関連Issue/PR/議論ログ: N/A
- ADR化が必要になる条件: 安全制約または保留/可逆性の定義変更が必要になった場合。
