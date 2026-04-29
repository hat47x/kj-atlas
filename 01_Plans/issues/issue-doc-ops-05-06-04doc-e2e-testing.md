# Issue Draft: DOC-OPS-05-06 04_Documentation/e2e_testing.md のOpen化準備

- Type: Documentation quality
- Status: Draft
- Lifecycle: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Stream E
- Scope: `04_Documentation/e2e_testing.md`（※本Issueではメモ整備のみ）
- Related Backlog: `DOC-OPS-05`
- Related ADR/Spec: `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `04_Documentation/e2e_testing.md`, `04_Documentation/operations.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `DOC-OPS-05-06`
- RequirementStatement: E2E運用文書の公開改善方針を維持しつつ、Open化判定に必要な情報を不足なく固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: E2E運用方針はADR-0019を正本として維持。
  - 操作: 公開改善（Improve external）方針、検証、Proceed判定を明記。
  - 期待結果: Open化審査で追加確認なしに着手可否が判断できる。
  - 除外: `04_Documentation/e2e_testing.md` の本文改稿。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A（DecisionStatus=Fixed）

## 1) 課題 / Problem statement

- 既存メモが長文化し、Improve external方針とOpen readiness判定が埋もれている。
- 5Phase記録が重複し、監査時に最終状態を取り出しにくい。

## 2) 背景 / Context

- e2e_testingは対外運用説明の主要導線であり、公開品質改善が必要。
- ただし本Issueはメモ整備限定であり、実文書改稿は後続Issueで行う。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 公開品質改善タスクの着手判断を早める。
- 安全（THREAT_MODEL / SafeMode）: 公開運用情報の誤記載リスクを低減。
- 企業・行政要件（enterprise_architecture）: 運用手順の説明責務を保持。
- 後方互換（schemas）: 実装・データ互換への影響なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象: Docs（Issue memo only）
- 分類方針: **Improve external（維持）**
- 非目標: 対象文書本体の編集、shared resources更新、他Issue編集。
- 作業プロトコル: **Read → Plan → Execute → Verify → Proceed** を固定適用する。
- 他ストリーム干渉禁止: 本メモ以外の変更を行わない。

## 5) 受入条件 / Acceptance criteria

- [x] Improve external 判定と根拠（公開runbook品質向上）が明記される。
- [x] GoNoGoGate=Required の判定条件（ADR-0019整合、公開境界）が明記される。
- [x] Validation plan が `docs-check` と一致する。
- [x] Proceed判定（三値）が記録される。
- [x] 5Phase実行記録が1セットで維持される。
- [x] ADR論点は CD&C（Claim/Decision/Constraint）で明文化し、承認必須である旨を記録する。
- [x] 検証失敗時の自己修復は最大3回で停止するルールを記録する。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 重複ログを整理し、最終判定情報を単一化。
- [x] T2 AC/DoD不足を補完してOpen化基準を固定。
- [x] T3 Verify結果を記録。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check`
  - `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - 体裁崩れなし。
  - active memo検証に副作用なし。
- 未実施時の理由・代替検証:
  - N/A
- 修復ポリシー:
  - 検証失敗時は原因切り分け→最小修正→再検証を行う。
  - 自己修復は最大3回までとし、4回目は停止して承認待ちへ移行する。

## 8) リスクとロールバック / Risks & rollback

- 失敗モード: 判定根拠が過度に簡略化される。
- ロールバック: 当該メモのみrevertし、根拠節を復元。

## 9) ADR論点（CD&C）

- Claim: E2E文書の公開改善方針は「Improve external」を維持し、Open化判断の入力情報を不足なく揃える。
- Decision: ADR-0019整合と公開境界（public-exposure）をGoNoGoGate=Requiredとして固定する。
- Constraint: 本Issueではメモ整備のみに限定し、`04_Documentation/e2e_testing.md` 本文改稿は行わない。
- Approval required: 上記CD&CはOpen化着手前の承認を必須とする。

## 10) Phase execution record（Stream E, Single Pass）

### Phase 1 Read
- Read同期対象: `00_Prompt/system_prompt.md` → `00_Prompt/domain.md` → `00_Prompt/handoff.md` → `00_Prompt/agent_handover.md` → `00_Prompt/codex_gsd_skill_ops.md` → `00_Prompt/ai_cognitive_externalization_requirements.md` → `01_Plans/adr/ADR-0001-value-to-requirements.md` → `02_Architecture/architecture.md` → 本Issue。
- 同期結果: 上位文書との矛盾なし。対象スコープを本メモ単体に固定。

### Phase 2 Plan
- Plan固定: Read → Plan → Execute → Verify → Proceed。
- 想定差分: 重複記録の圧縮、AC/DoD補強、CD&C明文化、検証上限ルール追記。
- 差分整合: 想定外差分なし（他ファイル非編集）。

### Phase 3 Execute
- 実施内容: 本メモのみ再構成し、AC達成状態・CD&C・修復上限・Proceed判定枠を追加。
- スコープ監査: 指定外ファイルは未編集。
- Read再同期: 実施後に本Issue再読し、Planとの差分一致を確認。

### Phase 4 Verify
- 実行: `git diff --check`。
- 実行: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- 結果: いずれも成功。
- 自己修復回数: 0/3。

### Phase 5 Proceed
- Proceed判定: **Ready（Go）**。
- 理由: AC充足、GoNoGoGate条件明記、CD&C承認必須を明文化、docs-check成功。
- Blocker: なし。
- Needs decision: あり（CD&C承認）。


## Stream E phase run（2026-04-29）

### 1) Read（Draft gate条件抽出）
- Draft gate条件を確認: `Improve external`、`GoNoGoGate=Required`、`VerificationLevel=docs-check`。

### 2) Context / Decision / Consequences
- Context: E2E手順は対外導線の主要文書でADR-0019整合が必須。
- Decision: 分類は **Improve external 維持**。
- Consequences: Open化は可能だが、本文改稿タスクでADR完全整合を担保する必要。

### 3) AC/DoD・Open化条件の明文化
- Open化条件: ADR-0019との受入基準・代替経路・実行コマンドの一致を確認後に `Ready`。
- DoD: 三値Proceedと自己修復上限（<=3）を維持。

### 4) Plan→Execute→Verify（自己修復）
- Plan/Execute: 本Issueメモのみ追記。
- Verify: docs-check方針維持、自己修復 0/3。

### 5) Proceed
- 判定: **Ready**。
- 理由: Open化審査に必要な条件が本文で再現可能。
