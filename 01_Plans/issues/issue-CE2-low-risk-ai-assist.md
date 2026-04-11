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
- AcceptanceScenario: 前提=CE1最小I/F（ContextQuery + ContextBundle + bundleHash）をモック契約として利用 / 操作=提案生成 / 期待結果=自動適用0件 / 除外=最終結論の自動生成
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / public-exposure
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- Stream: `D` (CE2 proposal-only / Docs-Plan only)
- DecisionQueueRef: `CE2-DRIFT-STOP`

## 0) CDC Flow（明文化）

CE2 Stream D は、以下の固定フローでのみ進行する。

1. **Plan**
2. **Execute**
3. **Verify**（最大3回まで修復して再検証）
4. **Proceed**

`Verify` で3回修復しても受入条件を満たせない場合は、`status=held` で停止し、人手判断待ちへ遷移する。

## 1) Phase 1 Read（I/F抽出 + mock許容）

- CE2必須I/F: `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState`。
- CE1依存は `mock bundleHash` で切断し、契約検証を先行（待機禁止）。
- 提案は **proposal-only** 境界に固定し、適用はCE2責務外とする。

## 2) Phase 2 Context

- CE-2は「低リスク導入」が目的であり、AIを確定器として扱わない契約固定が必要。
- CE-1で確定した `bundleHash` を入力として受け、比較可能・可逆な proposal 運用へ接続する。
- Stream B は CE1 完了待ちを行わず、CE1最小I/Fを **モック契約** として参照して先行整備する。
- CE1 実装との差異（フィールド欠落・命名差分・状態遷移差分）を検知した場合は CE2 側の実装/文書更新を停止し、差分解消指示を待つ（drift-stop）。

## 3) Phase 3 Decision

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
| `reviewState` | enum | Yes | `unreviewed/reviewed` 表示専用（自動昇格禁止） |

### 2.3 固定値（CE2 Contract Freeze）

- `proposalId`: 必須、proposal単位で不変
- `diff`: 必須、apply差分でなく **比較差分** として保持
- `sourceBundleHash`: 必須、CE1 ContextBundleと1対1対応
- `status`: `proposed | accepted | rejected | held` 以外を禁止
- `reviewState`: `unreviewed | reviewed` のみ。AIによる `reviewed` 付与禁止
- Auto-apply: UI/API/worker の全経路で禁止

### 2.4 責務境界（Responsibility）

- CE-2は proposal 作成までを責務とし、apply は人手承認ゲートの外で実行しない。
- proposal の `accepted` は「適用許可の意思表示」であり、自動適用トリガーではない。
- `held` は drift-stop 専用状態として扱い、`held` 中は apply 導線へ遷移禁止。
- `human_reviewed` 自動昇格は禁止（`reviewState` の AI 更新を含む）。昇格は人手操作のみ。
- safeMode ON では未レビュー本文を含む提案生成を禁止する。

## 4) Phase 4 Execute Consequences

- UI/APIともに auto-apply 経路を契約違反として扱い、検知時は即No-Go。
- すべてのAI応答は patch/diff と監査ログで追跡可能でなければならない。
- CE-3 の Patch Workspace は CE-2 proposal I/F を変更せず利用する。
- review自動昇格・safeMode後退・直接適用経路を検知した場合はフェイルセーフ停止し、運用判断待ちとする。

## 5) Phase 5 Verify（受入条件 / Acceptance criteria）

- [ ] すべてのAI応答が `proposalId`, `diff`, `sourceBundleHash`, `status`, `reviewState` を持つ。
- [ ] auto-apply経路が0件（API/UIともに禁止）。
- [ ] `human_reviewed` への自動昇格が0件。
- [ ] 提案の採用/却下/保留が監査ログで追跡可能。
- [ ] safeMode ONで未レビュー本文を含む提案が生成されない。
- [ ] CE1モック契約との差異検知時に `status=held` で停止し、適用経路が進行しない。

## 6) Verify 修復上限（最大3回）

- Verify で不整合を検知した場合、修復→再検証を最大3回まで許可する。
- 3回以内に解消しない場合は `status=held` へ遷移し、Proceed を禁止する。
- 修復回数は監査ログで追跡可能にする（attempt=1..3）。

## 7) タスク分解（文書限定）

- [ ] T1: proposal schema 契約を architecture/docs へ同期。
- [ ] T2: auto-apply禁止と review昇格禁止を運用文書へ明示。
- [ ] T3: proposal lifecycle（create/reject/hold/adopt）の語彙を統一。
- [ ] T4: CE-3引き渡し項目（部分採用可逆性）を記録。

## 8) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "proposalId|diff|sourceBundleHash|status|reviewState|auto-apply|human_reviewed|safeMode|unreviewed|held" 01_Plans/issues/issue-CE2-low-risk-ai-assist.md 02_Architecture/llm_escalation_policy.md 04_Documentation/local_llm_ops_guide.md`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 提案I/Fと禁止事項が文書間で一致し、validatorが成功する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 差分を持たない提案や自動適用導線が混入し監査不能。
- ロールバック: proposal契約違反箇所をrevertし、CE-1連携キー準拠へ戻す。


## 10) Phase 6 Proceed（CE3向け参照専用I/F）

- CE3は CE2 Proposal I/F を変更せず受理する（後方互換必須）。
- `status` 遷移は `proposed -> accepted/rejected/held` のみ。`held` からの自動復帰禁止。
- `reviewState` は表示属性であり、AIによる `reviewed` 付与は禁止。
- Phase 1〜6 で `proposalId/diff/sourceBundleHash/status/reviewState` は固定し、改名・省略・型変更を禁止する。
- CE1差分検知時は `held` で停止し、差分解消が確認されるまで Proceed しない。

フェイルセーフ（即停止）: SafeMode後退 / auto-apply許容 / 未レビュー昇格許容。
