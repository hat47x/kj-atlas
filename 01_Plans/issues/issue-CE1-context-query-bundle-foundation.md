# Issue Draft: CE1 ContextQuery/ContextBundle foundation

- Type: Feature request
- Status: Open
- Source Issue: N/A
- Priority: P1
- Owner: Backend/Frontend Team
- Scope: `01_Plans/issues/`, `02_Architecture/`, `04_Documentation/`
- Related Backlog: `CE-1`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）
- RequirementID: `CE1-CONTEXT-FOUNDATION`
- RequirementStatement: ContextQuery/Bundleを決定論で生成し、Query Preview必須導線を契約として固定する。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE0完了 / 操作=同一Queryを再実行 / 期待結果=bundleHash一致 / 除外=自動適用
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode / share-export
- VerificationLevel: docs-check
- DecisionStatus: Fixed
- DecisionQueueRef: `UNC-VSC-CE-01-02`

## 1) Context

- CE-1は CE-2/3/4 の前提であり、ここで Query/Bundle の最小I/Fが曖昧だと後続で互換性崩壊が起きる。
- Stream Dでは実装詳細ではなく、モックで依存切離し可能な契約（API/型/責務境界）を先に固定する。

## 2) Decision

### 2.1 API/型 契約（実装非依存）

- Query endpoint（論理名）:
  - `POST /context/query`: Query payload の構文・必須項目検証のみ。
- Bundle endpoint（論理名）:
  - `POST /context/bundle`: deterministic projection + `bundleHash` の返却。

### 2.2 ContextQuery 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `goal` | string | Yes | 問合せ目的 |
| `scope` | enum | Yes | document/view/island 等 |
| `depth` | integer | Yes | 探索深さ上限 |
| `constraints` | object | Yes | token/time/source 制約 |
| `reviewFilter` | enum | Yes | `reviewedOnly` を既定許可 |
| `safeModePolicy` | enum | Yes | `strict` 既定 |
| `outputMode` | enum | Yes | summary/proposal/candidate |

### 2.3 ContextBundle 最小I/F

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `bundleHash` | string | Yes | canonical serializationに基づく決定論ハッシュ |
| `selected` | array | Yes | 採択要素 |
| `relations` | array | Yes | 関連構造 |
| `evidence` | array | Yes | 根拠 |
| `contradictions` | array | Yes | 矛盾候補 |
| `reviewFlags` | object | Yes | reviewed/unreviewed 内訳 |
| `truncationMeta` | object | Yes | 省略理由/上限情報 |

### 2.4 責務境界（Responsibility）

- Query Preview は「送信前確認」の必須ゲートであり、バイパス経路を契約上禁止する。
- safeMode ON では未レビュー本文を既定除外とし、例外時は監査理由を必須記録する。
- CE-1時点では proposal 適用責務を持たず、生成までを担当する。

## 3) Consequences

- CE-2以降は `sourceBundleHash` をCE-1の `bundleHash` と一致照合する。
- 実装レーンは上記I/Fに対しモック実装を先行可能（UI/Backend分離）。
- Query Preview 未実装またはバイパス可能設計は No-Go。

## 4) 受入条件 / Acceptance criteria

- [ ] ContextQuery/ContextBundleの最小I/FがADR/Issue/Architectureで同一語彙で定義される。
- [ ] `bundleHash` の決定論要件（canonical化対象と順序規則）が記載される。
- [ ] safeMode ON + reviewedOnly の既定除外ルールが明記される。
- [ ] Query Preview必須導線（バイパス禁止）が明記される。
- [ ] 監査ログ必須キー `queryId`, `bundleHash`, `excludedReason` が固定される。

## 5) タスク分解（文書限定）

- [ ] T1: CE-1 I/F固定表を issue + architecture に同期。
- [ ] T2: deterministic bundle 要件を `02_Architecture` 側へ追記。
- [ ] T3: Query Preview 必須導線を `04_Documentation/operations.md` へ追記。
- [ ] T4: CE-2連携キー（`sourceBundleHash`）を明示。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "ContextQuery|ContextBundle|bundleHash|Query Preview|reviewFilter|safeModePolicy" 01_Plans/adr 01_Plans/issues 02_Architecture 04_Documentation`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
- 期待結果:
  - 契約語彙の欠落・重複がなく、validatorが成功する。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: bundleHash定義の差異でCE-2以降の比較不能。
- ロールバック: CE0 Contract ID準拠でI/Fを再固定し、未同期文書をrevert。
