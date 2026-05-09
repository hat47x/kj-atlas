# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P1
- Owner: Stream D（QA計画整備専任）
- Scope: `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` のみ（実装コード変更禁止）
- Dependencies（前提条件として明示のみ）:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Related Backlog: `QA-E2E-USE-01`
- Related ADR/Spec:
  - `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
  - `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`
  - `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## 1) Read同期（Draft理由と不足の固定）

### 1.1 Draft維持理由
- Open判定の閾値（Ready条件）が定義されていても、依存解除証跡の扱いが曖昧だと誤Proceedが起こる。
- AC/DoDはあるが、blocked時の記録様式が固定されていないと再開性が低い。
- 実装非依存（contract assertion）を守る監査観点が散在している。

### 1.2 前提条件（依存扱い）
- 本Issueは依存解除の判定を行わない。
- 依存が未解除の場合、結論は常に `Execution: Hold`。
- 依存解除の証跡提示があって初めて実装フェーズへ進める。

## 2) Plan（AC/DoD不足補完提案）

## Requirement meta I/F
- RequirementID: `QA-E2E-USE-01`
- RequirementStatement: 実運用に近いユーザージャーニー（作成→編集→レビュー→安全共有）をE2Eで再現し、回帰検知力を向上する。
- PriorityClass: Must
- VerificationLevel: e2e
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- ContractPolicy: DOM構造・内部関数名・一時UI文言に依存しない。
- DecisionStatus: Hold-for-Dependency-Gate

### 2.1 Acceptance Criteria（補完後）
- AC-01: S1/S2/S3を必須、S4を重要（任意実行）としてScenario ID固定する。
- AC-02: 各Scenarioに `Given/When/Then + 前提データ + 境界条件 + assertion種別` を記載する。
- AC-03: assertionを契約語彙で記述し、実装詳細依存（DOM/内部関数）を禁止する。
- AC-04: blocked時記録テンプレートを使用し、再開条件まで必須記録する。
- AC-05: 依存未解除時のProceedを `Not Allowed` と明文化する。

### 2.2 Definition of Done（補完後）
- DoD-01: S1〜S4の優先度・境界条件・判定文・診断導線が揃っている。
- DoD-02: safeMode既定ON / share-export fail-closed / human-only昇格が必須判定軸になっている。
- DoD-03: 失敗時トリアージ順序（test log → frontend/network → backend → compose → fixture差分）が固定されている。
- DoD-04: 同一fixtureで再実行可能（再現性）であり、外部依存を切離す方針が明示される。
- DoD-05: 依存未解除時は `Overall: Hold` を維持する。

## 3) Execute（Draft/Ready条件の明文化 + テスト観点表）

### 3.1 Draft/Ready条件
- Draft維持条件: AC/DoDの空欄、または blocked記録様式未整備。
- Ready（Planning）条件: AC/DoD/観点表/blockedテンプレートが埋まり、依存前提が明文化済み。
- Ready（Implementation）条件: 上記に加え、依存解除証跡が提示済み。

### 3.2 テスト観点表（contract-based）

| Scenario | Priority | 主目的 | 必須観点 | Assertion種別 |
|---|---|---|---|---|
| S1 Authoring Continuity | critical | 作成・編集・再読込で欠損を出さない | count整合 / relation欠損なし / 意図しない棚変動なし | count-equality / no-loss |
| S2 Review Governance | critical | review昇格統治の保証 | diff記録存在 / human操作でのみ昇格 / 自動昇格なし | state-transition / audit-presence |
| S3 Safe Sharing Gate | critical | 安全共有ゲート保証 | 初回reject / 条件充足後のみallow / safeMode既定維持 | gate-decision / policy-invariant |
| S4 Import-to-Safe-Export | important | import sanitizeと共有境界の連結確認 | 悪性reject / 正常のみ進行 / 後段でもS3境界維持 | sanitize-reject / flow-allowlist |

### 3.3 blocked時記録テンプレート
```md
- BlockID:
- Date(UTC):
- ScenarioID: S1|S2|S3|S4
- DependencyRef:
- BlockingFact:
- ImpactedAC_DoD:
- Evidence:
- NextActionOwner:
- ReopenCondition:
- Decision: Hold | Escalate
```

## 4) Verify（検証手順の実行可能性自己点検）

- チェック1: 文書だけでYes/No判定可能か（AC/DoDが機械的に照合できるか）。
- チェック2: テスト観点表が実装詳細を参照せずに維持できるか。
- チェック3: blockedテンプレートで停止→再開を追跡できるか。
- チェック4: 依存未解除時にProceedしない統制文が残っているか。

自己点検結果（2026-05-09 UTC）
- Planning Ready: Yes
- Implementation Ready: No（前提条件未確認のため）

## 5) Proceed / Stop

- Proceed条件: 依存解除証跡が揃った場合のみ実装計画へ移行。
- Stop条件:
  1. 依存解除証跡が不足。
  2. 実装詳細依存の記述が混入。
  3. スコープ外編集が必要。
  4. self-correction が3回を超える。

self-correction count: 0 / 3
