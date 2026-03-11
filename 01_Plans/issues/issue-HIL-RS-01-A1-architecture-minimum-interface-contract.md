# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定（Critique/再提案差分/レビュー帰属）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner
- Scope: `01_Plans/`, `02_Architecture/`
- Related Backlog: `HIL-RS-01`
- Related ADR/Spec: `ADR-0026`, `ADR-0001`, `00_Prompt/domain.md`, `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `HIL-RS-01-A1`
- RequirementStatement: Critique入力/再提案差分/レビュー帰属の最小I/F契約を固定し、A2/A3が契約参照のみで着手可能な状態にする。
- PriorityClass: Must
- AcceptanceScenario: 前提=A1着手時点でADR-0026がAccepted、操作=I/F契約と非目標・検証計画を文書化、期待結果=A2/A3が契約未確定待ちなしで着手可能、除外=実装コード変更
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) 課題 / Problem statement

- HIL-RS-01の実行順でA1契約が未固定だと、A2（Frontend実装）とA3（Documentation同期）が同一論点を重複解釈して競合する。
- Critique入力/再提案差分/レビュー帰属の境界を最小契約として確定しない限り、下流で「実装先行→仕様後追い」の逆流が発生する。

## 2) 背景 / Context

- `ADR-0026` D2は契約先行を明示し、A1を最初の実行タスクとして起票することをProceedに定義している。
- `domain.md` と `ADR-0001` は、保留維持・単一正解の否定・Human-in-the-loop反復を価値軸として拘束する。
- レビュー帰属は `review_attribution` 系仕様と整合させる必要がある。

## 3) 提案する解決策 / Proposed solution

- 変更対象: Docs/Architecture（契約定義のみ）
- 契約最小単位:
  1. Critique入力I/F（入力必須項目、任意項目、禁止事項）
  2. 再提案差分I/F（差分単位、可逆操作、トレースキー）
  3. レビュー帰属I/F（人間承認フラグ、承認者識別、タイムスタンプ）
- 非目標:
  - LLM Provider再設計
  - Frontendコンポーネント実装
  - SafeMode既定ONの緩和

## 4) 受入条件 / Acceptance criteria

- [ ] Critique入力/再提案差分/レビュー帰属の3契約が、必須/任意/禁止を含めて記述されている。
- [ ] 安全条件（SafeMode既定ON、share/export漏えい防止の後退禁止）が契約制約として明記されている。
- [ ] A2/A3が参照する契約IDと参照先ファイルを明示し、契約未固定箇所が0件である。
- [ ] A2/A3の並列可能条件（編集境界分離、共有リソース同時編集禁止）が明文化されている。
- [ ] Validation planにdocs-check 3コマンドが記載され、再現可能である。

## 5) DoD（Definition of Done）

- [ ] A1 issue本文にAC/非目標/停止条件/検証計画が揃っている。
- [ ] `issues/README.md` Active issue memosにA1が追加されている。
- [ ] `project-progress-dashboard.md` の Active/Decision Queue/Next actionsにA1が反映されている。
- [ ] docs-check（validator + unittest + rg確認）が成功している。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: A1 issue本文に契約3点の境界定義を記述する。
- [ ] T2: A2/A3並列条件（可能条件/禁止条件）を本文に固定する。
- [ ] T3: 共有リソース同期（README/dashboard）を単一フェーズで実施する。
- [ ] T4: docs-checkを実行し、結果を記録する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `rg -n "HIL-RS-01|ADR-0026|A1|Active issue memos|Decision Queue" 01_Plans/issues/README.md 01_Plans/project-progress-dashboard.md 01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`
- 期待結果:
  - A1がActive issueとしてREADME/dashboardに反映され、ADR-0026 Acceptedとの整合が確認できる。
- 未実施時の理由・代替検証:
  - 実行環境制約でpython実行不可の場合、`rg`出力と差分レビューで同期状態を手動確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: A2実装を先行し、I/Fは実装差分から逆算する。
  - 却下理由: 00〜02先行ルール違反となり、契約ドリフトを誘発する。
- 代替案B: A1とA3を統合して単一issueにする。
  - 却下理由: 設計契約と運用同期の責務境界が曖昧化する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 契約粒度が粗く、A2/A3が再度判断待ちになる。
- 影響範囲: `01_Plans/`, `02_Architecture/`, `04_Documentation/` の同期運用。
- ロールバック手順: A1をDraftへ戻し、契約境界を再分割して再起票する。

## 10) Additional context

- 関連Issue: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- A2/A3並列可能条件:
  1. A2はA1契約IDのみ参照し、共有ファイル（README/dashboard）を編集しない。
  2. A3は運用文書更新に限定し、A2と同一ファイルを編集しない。
  3. 共有リソース更新は統合フェーズ専用コミットに集約する。
