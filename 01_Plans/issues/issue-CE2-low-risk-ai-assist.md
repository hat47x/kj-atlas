# Issue Draft: CE2 低リスクAI支援（patch候補限定）

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: AI Integration Team
- Scope: `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE2-LOW-RISK-AI-ASSIST`
- RequirementStatement: AI提案は全件 proposalId+diff を持つ patch として扱う。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE1完了 / 操作=提案生成 / 期待結果=自動適用0件 / 除外=最終結論の自動生成
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: N/A

## 1) Context

- CE-2は「低リスク導入」が目的であり、AIを確定器として扱わない契約固定が必要。
- CE-1で確定した `bundleHash` を入力として受け、比較可能・可逆な proposal 運用へ接続する。

## 2) Decision

### 2.1 対象ユースケース（提案のみ）

- 島タイトル候補
- B型文章ドラフト（reviewed-only既定）
- contradiction/evidence 由来の論点候補

### 2.2 Proposal 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `proposalId` | string | Yes | 一意識別子 |
| `diff` | object | Yes | 比較・部分採用可能な差分 |
| `sourceBundleHash` | string | Yes | CE-1 bundleHashとの対応 |
| `rationale` | string | Yes | 提案根拠 |
| `status` | enum | Yes | `proposed/accepted/rejected/held` |
| `reviewState` | enum | Yes | `unreviewed/reviewed` 表示専用 |

### 2.3 責務境界（Responsibility）

- CE-2は proposal 作成までを責務とし、apply は人手承認ゲートの外で実行しない。
- `human_reviewed` 昇格は人手操作のみで、AIによる状態変更は禁止。
- safeMode ON では未レビュー本文を含む提案生成を禁止する。

## 3) Consequences

- UI/APIともに auto-apply 経路を契約違反として扱い、検知時は即No-Go。
- すべてのAI応答は patch/diff と監査ログで追跡可能でなければならない。
- CE-3 の Patch Workspace は CE-2 proposal I/F を変更せず利用する。

## 4) 受入条件 / Acceptance criteria

- [ ] すべてのAI応答が `proposalId`, `diff`, `sourceBundleHash`, `status` を持つ。
- [ ] auto-apply経路が0件（API/UIともに禁止）。
- [ ] `human_reviewed` への自動昇格が0件。
- [ ] 提案の採用/却下/保留が監査ログで追跡可能。
- [ ] safeMode ONで未レビュー本文を含む提案が生成されない。

## 5) タスク分解（文書限定）

- [ ] T1: proposal schema 契約を architecture/docs へ同期。
- [ ] T2: auto-apply禁止と review昇格禁止を運用文書へ明示。
- [ ] T3: proposal lifecycle（create/reject/hold/adopt）の語彙を統一。
- [ ] T4: CE-3引き渡し項目（部分採用可逆性）を記録。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "proposalId|sourceBundleHash|auto-apply|human_reviewed|safeMode|unreviewed" 01_Plans/adr 01_Plans/issues 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 提案I/Fと禁止事項が文書間で一致し、validatorが成功する。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: 差分を持たない提案や自動適用導線が混入し監査不能。
- ロールバック: proposal契約違反箇所をrevertし、CE-1連携キー準拠へ戻す。
