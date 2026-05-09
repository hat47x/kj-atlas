# Issue Ready Plan: QA-E2E-USE-01 E2Eテストを実利用ケースへ拡充

- Type: Process
- Status: Draft Ready Candidate (dependency-locked)
- Priority: P1
- Owner: Stream G（QA-E2E-USE-01 Draft Ready化専任）
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

## Phase 1: Read同期（現状整理）

### 1.1 既存シナリオ棚卸し

現行ドラフトでは以下の4ジャーニー定義が存在する。

1. Journey-A: Authoring Continuity（作成→再配置→保存復元）
2. Journey-B: Review Governance（編集→差分→review attribution）
3. Journey-C: Safe Sharing Gate（レビュー→共有/エクスポート判定）
4. Journey-D: Import-to-Safe-Export（sanitize境界、推奨）

### 1.2 欠落・曖昧語

- 欠落1: 優先度（critical/important/optional）がシナリオ単位で固定されていない。
- 欠落2: 実行環境前提（compose profile / auth mode / fixture source）がシナリオ別に機械判定可能な形で記述されていない。
- 欠落3: 失敗時診断導線（どのログをどの順序で確認するか）が統一されていない。
- 曖昧語1: 「安定して完走」「安全境界に回帰がない」の判定基準が定量化不足。
- 曖昧語2: dependency lock下での Ready 判定条件と Proceed 判定条件が混在。

### 1.3 既存AC/DoDの有無確認

- ACは定義済みだが、シナリオ優先度・実行環境との紐付けが不足。
- DoDは定義済みだが、失敗時の診断再現性と再実行性（rerun条件）を追加明文化する余地がある。

---

## Phase 2: Plan（AC/DoD草案 + 依存整理）

### 2.1 AC草案（Ready計画判定用）

- AC-01: 主要3ジャーニー（A/B/C）が `Given/When/Then` で再現可能に定義され、Journey-Dは optional として切替可能である。
- AC-02: 各シナリオに「前提データ」「期待結果」「失敗時診断観点」が明示される。
- AC-03: 期待結果は機械判定可能な contract assertion として記述される（pass/fail判定文を含む）。
- AC-04: 実行環境前提（compose profile / auth mode / fixture / safeMode既定ON）がシナリオごとに明示される。
- AC-05: 優先順（critical / important / optional）に沿った実施順が固定される。

### 2.2 DoD草案（Ready化完了判定）

- DoD-01: シナリオ3本以上（A/B/C必須）に対して Given/When/Then + 優先度 + 診断導線が揃っている。
- DoD-02: safeMode既定ON・share/export fail-closed・review human-only昇格の3境界が必須判定軸として記述される。
- DoD-03: 失敗時に必要なログ採取点（UI console / backend log / compose service log / test trace）が明示される。
- DoD-04: rerun前提（同一fixtureで再実行可能、依存外部通信を切離し可能）が明示される。
- DoD-05: Proceedは dependency gate解除まで Not Allowed のまま固定される。

### 2.3 依存関係（Auth / Mock IdP / Fixture）

- Auth依存:
  - 基本は local/mock auth mode（IAP header相当のテストプロファイル）を使用。
  - 本番OIDC/SAML直結は対象外（ADR-0020に従いMock検証プロファイルを優先）。
- Mock IdP依存:
  - 必須ではない（このIssueはDraft Ready化のみ）。
  - ただし将来実装Issueでは「mock profileで再現可能」を前提条件にする。
- Fixture依存:
  - reviewed/unreviewed混在fixture
  - import正常/悪性fixture
  - 保存復元確認fixture

### 2.4 Mock適用余地（外部依存切離し）

- 判定: **適用推奨**
- 理由:
  1) 外部IdP/LLM実通信を除外してE2E回帰判定の再現性を上げるため。
  2) dependency lock解除直後に最短で実行可能な検証レーンを構築するため。

---

## Phase 3: Execute（Ready計画本文確定）

## 3.1 Context / Decision / Consequences

### Context
- 現行E2Eはスモーク中心で、実利用の縦断フロー検証が不足。
- dependency lock未解除のため、実装・テストコード着手は禁止。

### Decision
- シナリオは A/B/C を必須、Dを optional とする。
- 各シナリオを Given/When/Then + 前提データ + 期待結果 + 失敗時診断観点で固定する。
- 優先度を critical/important/optional で固定し、実施順も固定する。

### Consequences
- 実装レーンは依存解除後に仕様解釈なしでテスト設計へ移行可能。
- 安全境界後退（safeMode緩和/誤共有/review昇格逸脱）を回帰検知しやすくなる。

## 3.2 実行環境前提（シナリオ共通）

- Runtime profile: `docker compose` による結合実行（ADR-0019準拠）。
- Auth mode: mock/local profile（本番IdP接続なし）。
- Safe mode: default ON（開始時に確認必須）。
- Data source: 固定fixture（seed idを記録）。
- 外部通信: LLM provider / 本番SSO通信は無効化またはmock化。

## 3.3 シナリオ定義（Given/When/Then）

### S1: Authoring Continuity（Priority: critical）
- Given: safeMode=ON、新規doc fixture、初期card/relation件数が取得可能。
- When: card作成→配置変更→保存→再読込を実行する。
- Then:
  - card件数が保存前後で一致。
  - relation件数が欠損しない。
  - pending shelf件数が意図せず増減しない。
- 前提データ: `doc_fixture_authoring_v1`。
- 失敗時診断観点: frontend console / backend API response / persistence反映ログ。

### S2: Review Governance（Priority: critical）
- Given: reviewed/unreviewed混在fixture、diff比較対象が存在。
- When: 編集→diff確認→human review操作→状態再取得を実行する。
- Then:
  - diffが生成され変更対象が記録される。
  - `human_reviewed` への昇格は人手操作でのみ成立。
  - 自動経路で昇格が成立しない。
- 前提データ: `doc_fixture_review_mix_v1`。
- 失敗時診断観点: diff出力 / review attribution event / audit相当ログ。

### S3: Safe Sharing Gate（Priority: critical）
- Given: unreviewedを含むdoc、safeMode=ON。
- When: share/exportを実行→review条件充足後に再試行する。
- Then:
  - 初回は fail-closed（拒否）となる。
  - 条件充足後のみ許可される。
  - セッション中にsafeMode既定ONが緩和されない。
- 前提データ: `doc_fixture_unreviewed_block_v1`。
- 失敗時診断観点: policy判定ログ / gate理由 / 再試行時の状態差分。

### S4: Import-to-Safe-Export（Priority: important, optional実施）
- Given: 正常markdown/zip fixture と悪性入力fixture。
- When: import sanitize→編集→share/export判定を実行する。
- Then:
  - 悪性入力がsanitize段階でrejectされる。
  - 正常入力のみ後段フローへ進行。
  - 後段でもS3同等の安全境界が維持される。
- 前提データ: `import_fixture_valid_v1` / `import_fixture_malicious_v1`。
- 失敗時診断観点: import validate log / sanitize判定理由 / downstream gate判定。

## 3.4 実施順（優先度別）

1. critical: S1 → S2 → S3
2. important: S4
3. optional: S4をスキップする軽量回帰レーン（依存解決直後の初回運用向け）

## 3.5 失敗時トリアージ導線（固定順）

1. テスト実行ログで失敗シナリオID（S1〜S4）と失敗assertionを特定。
2. frontend console / networkログでUI↔API境界エラーを確認。
3. backend serviceログでpolicy/review/import判定の根拠を確認。
4. compose service状態（対象コンテナの起動/疎通）を確認。
5. fixture id・doc id・期待値/実測値差分を記録し、再実行可否を判定。

---

## Phase 4: Verify（客観判定 + Self-Correction）

### 4.1 AC客観判定チェック

- [x] AC-01: A/B/C必須、D optional が明記されている。
- [x] AC-02: 全シナリオで前提データ・期待結果・失敗時診断観点が定義されている。
- [x] AC-03: Then句が機械判定可能なassertion文で記載されている。
- [x] AC-04: compose/auth/safeMode/fixture前提が明示されている。
- [x] AC-05: critical/important/optional の順序が確定している。

### 4.2 重複/欠落チェック

- 重複: S2/S3のreview境界判定に一部重複あり（意図的重複。S2は昇格経路、S3は共有境界）。
- 欠落: 本番SSO/外部LLMは除外とし、将来別Issueで管理。
- 環境曖昧さ: compose profileとauth modeを共通前提として固定済み。

### 4.3 Self-Correction（最大3回）

1. 修正1: シナリオごとの優先度を明示。
2. 修正2: 失敗時トリアージ導線を固定順で追加。
3. 修正3: 実行環境前提（compose/auth/safeMode/fixture）を統一記述。

- self-correction count: 3 / 3（上限内）

---

## Phase 5: Proceed判定（dependency-locked）

### 5.1 Ready化判定

- Ready for planning: **Yes**（E2E実装可能な計画粒度まで到達）。
- Ready for implementation: **No**（dependency gate未解除）。

### 5.2 現在判定（2026-05-09）

- Dependency状態: 未解除
- ProceedDecision: **Not Allowed**
- Overall: **Hold**

### 5.3 停止条件（フェイルセーフ）

以下に該当した場合は停止し、実装移行を行わない。

1. 前提環境（compose/profile/auth mode）が特定不能。
2. 依存先Issue/ADRが未特定または判定不整合。
3. 本Issue以外の編集が必要になった。
4. self-correction が 3 回を超過。

### 5.4 停止時に提示すべき項目

- 不足情報: 何が未確定か（例: dependency approval record欠落）。
- 必要な判断: 誰が何を承認すべきか（System Owner / Platform Operator / Security Officer）。
- 再開条件: どの証跡が揃えば Hold 解除できるか。
