# Issue Ready Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft Ready Candidate (implementation-decoupled)
- Priority: P1
- Owner: Stream J（QA-E2E-USE-01 Draft整備専任）
- Scope: `01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md` のみ（実装コード変更禁止）
- Dependencies:
  - `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（FB-P0収束をGo条件として固定）
  - `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（HIL-RS-02計画同期完了まで実装着手禁止）
- Related Backlog: `QA-E2E-USE-01`
- Related ADR/Spec:
  - `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
  - `01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile.md`
  - `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## 0. Requirement meta I/F（共通キー）

- RequirementID: QA-E2E-USE-01
- RequirementStatement: 現在のE2E検証を、実運用に近いユーザージャーニー（作成→編集→レビュー→安全共有）で再現できるシナリオ群へ拡張し、回帰検知力を向上させる。
- PriorityClass: Must
- VerificationLevel: e2e
- SecurityGateImpact: SafeMode / share-export / import-sanitize
- ContractPolicy: E2Eケース定義は contract レベルで固定し、DOM構造・内部関数名・一時UI文言への依存を禁止する。
- DecisionStatus: Hold-for-Dependency-Gate
- GoNoGoGate: Required

---

## Phase 1: Read（Draft理由・依存・評価指標不足の抽出）

### 1.1 Draft理由（なぜDraftのままか）

- 理由A: realistic journey は列挙されているが、**Open判定のゲート条件**（何を満たせばHold解除か）が未固定。
- 理由B: AC/DoDに「判定文」はあるが、**blocked時の記録様式**と再開条件が機械的に追跡できない。
- 理由C: 依存Issueの状態が未解決でも進められるように見える記述が混在し、Proceed条件が曖昧。

### 1.2 依存関係の確定（未確定を確定扱いしない）

- 依存1: `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` が Go 条件。
- 依存2: `issue-HIL-RS-02-next-phase-delivery-plan.md` の同期完了が Go 条件。
- 本Issue単体では依存解除可否を決定しない。**解除証跡が提示されるまで Hold 固定**。

### 1.3 評価指標不足（Open判定の不足点）

- 不足1: Scenario完成度を測る最小メタ（ID/優先度/境界条件/assertion種別）の必須化不足。
- 不足2: blocked発生時に残す証跡（理由・影響・次アクション・再開条件）がテンプレ化されていない。
- 不足3: 実装非依存を担保する「非目標（DOM依存禁止、実装関数依存禁止）」が散発的で監査しにくい。

---

## Phase 2: ADR CDC（価値・非目標の明文化）

### 2.1 Value（この拡張の価値）

1. 実利用縦断フローで回帰を検出できる（スモーク偏重を解消）。
2. 安全境界（safeMode既定ON / fail-closed / human-only review昇格）をE2Eで継続監視できる。
3. dependency解除後に即実装可能な、解釈不要のテスト設計入力を用意できる。

### 2.2 Non-Goals（このIssueでやらないこと）

- E2Eテストコードの追加・変更。
- DOMセレクタやUIテキストの確定。
- 本番OIDC/SAML接続を伴う統合検証。
- 依存Issueの完了判定代行。

### 2.3 CDC（Context / Decision / Consequence）

- Context: 実装着手禁止の依存ロック下で、計画品質のみ引き上げる必要がある。
- Decision: A/B/C必須 + D重要（任意スキップ可）を固定し、すべて contract assertion で記述する。
- Consequence: Hold中でもOpen判定可能な計画品質を確保し、依存解除後に実装へ直結できる。

---

## Phase 3: Plan（AC/DoD確定）

### 3.1 AC（Open判定可能な受入条件）

- AC-01: 対象ユーザーフローは S1/S2/S3 必須、S4 重要（optional実行可）としてID固定される。
- AC-02: 各シナリオに `Given/When/Then + 前提データ + 境界条件 + assertion種別` がある。
- AC-03: assertionは実装非依存（契約語彙）で表現され、DOM/内部関数への依存がない。
- AC-04: blocked時記録テンプレート（後述4.5）で、発生事象を再開可能な粒度で残せる。
- AC-05: Proceed判定は dependency gate解除証跡が揃うまで `Not Allowed` 固定。

### 3.1.1 Draft→Open 判定ゲート（明文化）

- Gate-O1（Contract Completeness）: S1〜S4すべてに `Given/When/Then + 前提データ + 境界条件 + assertion種別` が記入済み。
- Gate-O2（Implementation Decoupling）: シナリオ本文・判定文に DOMセレクタ / 内部関数名 / 一時UI文言 への依存記述がない。
- Gate-O3（Dependency Lock）: 依存Issueは read-only snapshot として参照され、状態推測・完了判定代行をしていない。
- Gate-O4（Blocked Operability）: 4.5テンプレートで blocked 記録を再開可能粒度（Evidence / ReopenCondition 必須）で残せる。
- Gate-O5（Go/No-Go Clarity）: ProceedDecision が依存解除証跡ベースで一意に判定でき、未提示時は `Not Allowed` になる。

判定規則:
- `Open` = Gate-O1〜O5 がすべて `Pass`。
- `Draft` = Gate-O1〜O5 のいずれか1つでも `Fail`。
- `Hold` は依存未解除時の実装可否状態であり、`Open/Draft`（計画品質判定）と独立して併記する。

### 3.2 DoD（Draft品質完了条件）

- DoD-01: S1〜S4に優先度・境界条件・判定文・診断導線が揃う。
- DoD-02: 安全境界3点（safeMode既定ON / share-export fail-closed / human-only昇格）が必須判定軸として明示される。
- DoD-03: 失敗時トリアージ順序（test log → frontend/network → backend → compose → fixture差分）が固定される。
- DoD-04: 同一fixture rerun前提と外部依存切離し方針（mock/local）が明示される。
- DoD-05: 依存未解除時は `Overall: Hold` を維持し、推測で解除しない。

### 3.3 対象ユーザーフロー（固定）

- S1: Authoring Continuity（critical）
- S2: Review Governance（critical）
- S3: Safe Sharing Gate（critical）
- S4: Import-to-Safe-Export（important / optional実行）

### 3.4 実行環境前提（実装非依存）

- Runtime profile: compose統合実行（ADR-0019準拠）
- Auth mode: mock/local（ADR-0020準拠）
- SafeMode: default ON（開始時確認）
- Fixture: fixed seed idを記録
- External: 本番SSO/外部LLM通信なし

### 3.5 blocked時記録テンプレート（必須）

```md
- BlockID:
- Date(UTC):
- ScenarioID: S1|S2|S3|S4
- DependencyRef: issue/ADRリンク
- BlockingFact: （観測事実のみ）
- ImpactedAC_DoD: AC-xx / DoD-xx
- Evidence: log path / trace id / screenshot id
- NextActionOwner:
- ReopenCondition: （何が揃えば再開可能か）
- Decision: Hold | Escalate
```

---

## Phase 4: Execute（本Issue更新内容）

### 4.1 Scenario定義（Given/When/Then）

#### S1: Authoring Continuity（Priority: critical）
- Given: safeMode=ON、新規doc fixture、初期card/relation件数が取得可能。
- When: card作成→配置変更→保存→再読込。
- Then:
  - card件数一致（保存前後）。
  - relation欠損なし。
  - pending shelf件数の意図しない変動なし。
- 前提データ: `doc_fixture_authoring_v1`
- 境界条件: persistence成功/失敗双方で判定可能。
- Assertion種別: count-equality / no-loss

#### S2: Review Governance（Priority: critical）
- Given: reviewed/unreviewed混在fixture、diff比較対象あり。
- When: 編集→diff確認→human review操作→状態再取得。
- Then:
  - diff記録が残る。
  - `human_reviewed` 昇格は人手操作のみ成立。
  - 自動経路では昇格しない。
- 前提データ: `doc_fixture_review_mix_v1`
- 境界条件: review操作有無の分岐を区別。
- Assertion種別: state-transition / audit-presence

#### S3: Safe Sharing Gate（Priority: critical）
- Given: unreviewed含有doc、safeMode=ON。
- When: share/export実行→review条件充足後に再試行。
- Then:
  - 初回 fail-closed（拒否）。
  - 条件充足後のみ許可。
  - セッション中にsafeMode既定が緩和されない。
- 前提データ: `doc_fixture_unreviewed_block_v1`
- 境界条件: reject→allow の順序固定。
- Assertion種別: gate-decision / policy-invariant

#### S4: Import-to-Safe-Export（Priority: important / optional実行）
- Given: 正常fixture + 悪性fixture。
- When: import sanitize→編集→share/export判定。
- Then:
  - 悪性入力はsanitizeでreject。
  - 正常入力のみ後段へ進行。
  - 後段でもS3同等境界を維持。
- 前提データ: `import_fixture_valid_v1` / `import_fixture_malicious_v1`
- 境界条件: import段階とshare/export段階を分離判定。
- Assertion種別: sanitize-reject / flow-allowlist

### 4.2 実施順

1. critical: S1 → S2 → S3
2. important: S4
3. optional lane: S4スキップの軽量回帰

### 4.3 失敗時トリアージ導線（固定順）

1. test logで ScenarioID と失敗assertionを特定
2. frontend console / network境界確認
3. backend policy/review/import判定根拠確認
4. compose service稼働・疎通確認
5. fixture id と期待値/実測値差分を記録

---

## Phase 5: Verify（docs-check + 依存矛盾なし判定）

### 5.1 docs-check（本Issue観点）

- [x] スコープ外編集なし（本Issueファイルのみ更新）。
- [x] 実装依存記述（DOM/関数名依存）なし。
- [x] AC/DoD/blocked記録テンプレが明示。

### 5.1.1 Gate-O 判定表（2026-05-09 UTC）

- [x] Gate-O1: Pass
- [x] Gate-O2: Pass
- [x] Gate-O3: Pass
- [x] Gate-O4: Pass
- [x] Gate-O5: Pass
- PlanningQualityStatus: **Open**

### 5.2 依存矛盾チェック

- [x] 依存IssueはGo条件として参照のみ（状態を確定扱いしない）。
- [x] ADR-0019/0020との方針整合（compose + mock/local auth）。
- [x] Proceedは dependency解除まで `Not Allowed` 固定。

### 5.3 Self-Correction（最大3回）

1. 修正1: Open判定不足（blocked記録欠如）をテンプレ化。
2. 修正2: AC/DoDへ実装非依存判定（assertion種別）を追加。
3. 修正3: Proceed条件を依存証跡ベースに再固定。

- self-correction count: 3 / 3（上限内）

---

## Phase 6: Proceed（証跡不足時はHold）

### 6.1 判定（2026-05-09 UTC）

- Ready for planning quality: **Yes**
- Ready for implementation: **No**
- Dependency evidence: **Insufficient**
- ProceedDecision: **Not Allowed**
- DraftOpenStatus: **Open**（Gate-O1〜O5 Pass）
- Overall: **Hold**

### 6.2 Hold継続条件（推測解決禁止）

1. 依存IssueのGo証跡未提示。
2. compose/auth前提の運用証跡未提示。
3. blocked記録に ReopenCondition が欠落。

### 6.3 Stop条件（本Issue運用）

- 実装変更要求が混入した場合。
- 未確定依存を確定扱いする要求が入った場合。
- self-correction が3回を超える場合。
