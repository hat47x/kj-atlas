# Issue Draft: CE1 ContextQuery/ContextBundle foundation

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: Backend/Frontend Team
- Scope: `03_Implement/backend/`, `03_Implement/frontend/`, `04_Documentation/`
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）
- RequirementID: `CE1-CONTEXT-FOUNDATION`
- RequirementStatement: ContextQuery/Bundleを決定論で生成し、Query Preview必須導線を実装する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE0完了 / 操作=同一Queryを再実行 / 期待結果=bundleHash一致 / 除外=自動適用
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: integration
- DecisionStatus: Fixed
- DecisionQueueRef: `UNC-VSC-CE-01-02`

## 1) 実装対象（具体）

- Backend:
  - `POST /context/query`（Query validation）
  - `POST /context/bundle`（deterministic bundle + bundleHash）
- Frontend:
  - Query Previewパネル（送信前に `scope/depth/reviewFilter/safeMode` を表示）
  - Preview未通過時は送信ボタン無効。

## 2) 受入条件 / Acceptance criteria

- [ ] ContextQuery必須フィールド未入力時に400（fail-fast）となる。
- [ ] 同一Queryを10回実行してbundleHash一致率100%。
- [ ] safeMode ON + reviewedOnly=true で未レビュー本文がbundleに含まれない。
- [ ] Query PreviewをバイパスするUI/API導線がない。
- [ ] 監査ログに `queryId`, `bundleHash`, `excludedReason` が記録される。

## 3) 実装タスク分解 / Task breakdown

- [ ] T1: Query/BundleのPydanticスキーマ定義。
- [ ] T2: deterministic sort/filter/truncationの実装。
- [ ] T3: Query Preview UI + バリデーション実装。
- [ ] T4: integration test（API + UI）追加。

## 4) 検証計画 / Validation plan

- 実行コマンド:
  - `pytest -q 03_Implement/backend/tests -k "context_query or context_bundle or deterministic"`
  - `npm --prefix 03_Implement/frontend test -- --runInBand --testNamePattern "Query Preview|bundleHash"`
- 期待結果:
  - 決定論・safeMode制約・preview必須がすべて緑。

## 5) リスクとロールバック / Risks & rollback

- 失敗モード: bundleHash不安定でCE-2以降の比較不能。
- ロールバック: truncation/orderingロジックを直前安定版へ戻し、fixture固定で再検証。
