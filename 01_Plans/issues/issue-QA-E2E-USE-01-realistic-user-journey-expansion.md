# Issue Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft (Plan-Refined / Execution Hold)
- Priority: P1
- Owner: Stream J（QA計画整備専任）
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

## 1) Read同期（Draft理由・依存・Open閾値）

### 1.1 Draft維持理由
- Open判定の閾値（Ready条件）が定義されていても、依存解除証跡の扱いが曖昧だと誤Proceedが起こる。
- AC/DoDはあるが、blocked時の記録様式が固定されていないと再開性が低い。
- 実装非依存（contract assertion）を守る監査観点が散在している。

### 1.2 前提条件（依存扱い）
- 本Issueは依存解除の判定を行わない。
- 依存が未解除の場合、結論は常に `Execution: Hold`。
- 依存解除の証跡提示があって初めて実装フェーズへ進める。

### 1.3 Open閾値（Execution移行ゲート）
- Planning Open: AC/DoD/観点表/blocked記録様式が埋まっている。
- Execution Open: 上記に加えて依存2件（FB-P0 / HIL-RS-02）の解除証跡が提示済み。
- 依存証跡が1件でも欠ける場合は `Execution: Hold` を維持する。

## 2) ADR（Context / Decision / Consequences）

### 2.1 Context
- QA-E2E-USE-01 は realistic user journey のE2E拡充を目的とするが、現時点では依存未解除の可能性を内包する。
- 依存未解除時に実装へ進むと、テスト仕様より先に運用前提が崩れ、再開時の説明責任が失われる。

### 2.2 Decision
- 本Issueは「計画文書の完成」をDoDとし、実装・実行は行わない。
- `Execution: Hold` の判定は依存解除証跡の有無のみで機械的に行う。
- blocked時の証跡様式を固定し、再開条件を必須フィールド化する。

### 2.3 Consequences
- 利点: 再開判断が属人化せず、誤Proceedを抑止できる。
- 制約: 依存解除まで実装進捗は発生しない。
- 監査性: Hold理由と再開条件が時系列で追跡可能になる。

## 3) Plan（AC/DoD補完：blocked記録様式・再開条件）

## Requirement meta I/F
- RequirementID: `QA-E2E-USE-01`
- RequirementStatement: 実運用に近いユーザージャーニー（作成→編集→レビュー→安全共有）をE2Eで再現し、回帰検知力を向上する。
- PriorityClass: Must
- VerificationLevel: e2e
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- ContractPolicy: DOM構造・内部関数名・一時UI文言に依存しない。
- DecisionStatus: Hold-for-Dependency-Gate

### 3.1 Acceptance Criteria（補完後）
- AC-01: S1/S2/S3を必須、S4を重要（任意実行）としてScenario ID固定する。
- AC-02: 各Scenarioに `Given/When/Then + 前提データ + 境界条件 + assertion種別` を記載する。
- AC-03: assertionを契約語彙で記述し、実装詳細依存（DOM/内部関数）を禁止する。
- AC-04: blocked時記録テンプレートを使用し、再開条件まで必須記録する。
- AC-05: 依存未解除時のProceedを `Not Allowed` と明文化する。

### 3.2 Definition of Done（補完後）
- DoD-01: S1〜S4の優先度・境界条件・判定文・診断導線が揃っている。
- DoD-02: safeMode既定ON / share-export fail-closed / human-only昇格が必須判定軸になっている。
- DoD-03: 失敗時トリアージ順序（test log → frontend/network → backend → compose → fixture差分）が固定されている。
- DoD-04: 同一fixtureで再実行可能（再現性）であり、外部依存を切離す方針が明示される。
- DoD-05: 依存未解除時は `Overall: Hold` を維持する。

## 4) Execute（計画文書更新のみ）

### 4.1 Draft/Ready条件
- Draft維持条件: AC/DoDの空欄、または blocked記録様式未整備。
- Ready（Planning）条件: AC/DoD/観点表/blockedテンプレートが埋まり、依存前提が明文化済み。
- Ready（Implementation）条件: 上記に加え、依存解除証跡が提示済み。

### 4.2 テスト観点表（contract-based）

| Scenario | Priority | 主目的 | 必須観点 | Assertion種別 |
|---|---|---|---|---|
| S1 Authoring Continuity | critical | 作成・編集・再読込で欠損を出さない | count整合 / relation欠損なし / 意図しない棚変動なし | count-equality / no-loss |
| S2 Review Governance | critical | review昇格統治の保証 | diff記録存在 / human操作でのみ昇格 / 自動昇格なし | state-transition / audit-presence |
| S3 Safe Sharing Gate | critical | 安全共有ゲート保証 | 初回reject / 条件充足後のみallow / safeMode既定維持 | gate-decision / policy-invariant |
| S4 Import-to-Safe-Export | important | import sanitizeと共有境界の連結確認 | 悪性reject / 正常のみ進行 / 後段でもS3境界維持 | sanitize-reject / flow-allowlist |

### 4.3 blocked時記録テンプレート（固定）
```md
- BlockID: (例) BLK-QA-E2E-USE-01-YYYYMMDD-01
- Date(UTC):
- ScenarioID: S1|S2|S3|S4|N/A
- DependencyRef: FB-P0 | HIL-RS-02
- BlockingFact: （観測事実のみ）
- ImpactedAC_DoD: AC-xx / DoD-xx
- EvidenceType: link | log | decision-note
- EvidenceRef:
- NextActionOwner:
- ReopenCondition: （満たしたら再開できる条件を1文で）
- Decision: Hold | Escalate
```

## 5) Verify（`Execution: Hold` 条件の明確性検証）

- チェック1: 文書だけでYes/No判定可能か（AC/DoDが機械的に照合できるか）。
- チェック2: テスト観点表が実装詳細を参照せずに維持できるか。
- チェック3: blockedテンプレートで停止→再開を追跡できるか。
- チェック4: 依存未解除時にProceedしない統制文が残っているか。
- チェック5: 依存証跡2件が揃わない限り `Execution: Hold` になる判定式が明記されているか。

自己点検結果（2026-05-10 UTC）
- Planning Ready: Yes
- Execution Ready: No（依存解除証跡の未提示を前提とするため）
- Execution Decision: Hold

## 6) Proceed / Hold / Stop

- Proceed条件: 依存解除証跡（FB-P0, HIL-RS-02）が両方提示された場合のみ実装計画へ移行。
- Hold条件:
  1. 依存解除証跡が1件でも不足。
  2. blocked記録テンプレートの必須項目が欠落。
- Stop条件:
  1. 実装詳細依存の記述が混入。
  2. スコープ外編集が必要。
  3. self-correction が3回を超える。

self-correction count: 0 / 3
