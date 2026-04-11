# Issue Draft: CE2 低リスクAI支援（patch候補限定）

- Type: Feature request
- Status: Draft
- Source Issue: N/A
- Priority: P1
- Owner: AI Integration Team
- Scope: `03_Implement/frontend/`, `03_Implement/backend/`, `04_Documentation/`
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）
- RequirementID: `CE2-LOW-RISK-AI-ASSIST`
- RequirementStatement: AI提案は全件 proposalId+diff を持つ patch として扱う。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE1完了 / 操作=提案生成 / 期待結果=自動適用0件 / 除外=最終結論の自動生成
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: integration
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) 対象ユースケース

- 島タイトル候補
- B型文章ドラフト（reviewed-only）
- contradiction/evidence 由来の論点候補

## 2) 受入条件 / Acceptance criteria

- [x] すべてのAI応答が `proposalId`, `diff`, `sourceBundleHash` を持つ。
- [x] auto-apply経路が0件（API/UIともに禁止）。
- [ ] `human_reviewed` への自動昇格が0件。
- [x] 提案の採用/却下/保留が監査ログで追跡可能。
- [ ] safeMode ONで未レビュー本文を含む提案が生成されない。

## 3) 実装タスク分解 / Task breakdown

- [x] T1: proposal schema（type/status/diff/rationale）定義。
- [x] T2: AIレスポンスをproposalへ変換するadapter実装。
- [x] T3: UIに `AI提案/未レビュー/レビュー済` バッジを追加。
- [x] T4: proposal lifecycle test（create/reject/hold/adopt）追加。

## 4) 検証計画 / Validation plan

- 実行コマンド:
  - `pytest -q 03_Implement/backend/tests -k "proposal and not auto_apply and safe_mode"`
  - `npm --prefix 03_Implement/frontend test -- --runInBand --testNamePattern "proposal|unreviewed|review badge"`
- 期待結果:
  - 追跡可能性100%、自動適用0件。

## 5) リスクとロールバック / Risks & rollback

- 失敗モード: 差分を持たない提案が混入し監査不能。
- ロールバック: 提案型変換を必須チェックでfail-fast化し、無効提案をreject。
