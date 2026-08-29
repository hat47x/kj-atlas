# ADR-0040: 中核ドメイン概念の第一級化戦略（保留・違和感・根拠・矛盾）

- Status: Accepted
- Date: 2026-05-31
- Deciders: Maintainer（委譲された意思決定権限）
- Scope: `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `03_Implement/frontend/`, `01_Plans/`
- Norms: `DOM-AI-02, DOM-AI-03`（AIはHold/Critiqueを解消せず保持対象として扱うという緩和禁止条項が、DOMAIN-EXPR全4フェーズの設計を制約する）

## Context

社会的目標は「散らばった暗黙知・主観・多様な意見を early collapse させず、レビュー可能・可逆・説明可能な形へ構造化する場」を広げること（`README.md` / `domain.md` / `ai_cognitive_externalization_requirements.md`）。その中核は domain.md の概念群（保留 HoldState / 違和感 Critique / 未統合 PendingItems・Shelf / 根拠 EvidenceLink / 矛盾 Contradiction / claimType）である。

しかし現状、これらは**「概念の憲法」と「往復保存される型」の間で宙づり**になっている。

- `schemas.md` は `critiqueInputs` / `evidenceLinks` / `claimType` / `reviewAttribution` を持つが、line 432 が明記:「MVPでは画面上の個別編集や個別CRUDを提供せず、import/export/API保存時の型・検証・監査境界を固定する」＝**利用者が触れる日常UI・視覚言語が無い**。
- frontend 実装に `shelf` / `pending` / `holdState` は**皆無**（コード走査で0件）。`PendingItems/Shelf`（未統合の退避場所）は型すら無い。
- `value_traceability.md` §2.1.1 が「保留・違和感の日常操作」「根拠・主張・反対意見の追跡」を**不足設計観点として明記**。
- `PRODUCT-VALUE-02` の Representation boundary table は5語彙すべてで「現行構造で不足する範囲」を列挙し、各行を「**schema issue を切るか判断する**」と保留。さらに同issueの Open化条件は「`ADR-0032` がAccepted」であり、`ADR-0032` 自身は同issueの Open-ready 待ち＝**循環デッドロック**。

この保留状態のままでは、kj-atlas は「単なるカード配置ツール」に見え、認知外在化フレームワークとしての価値が利用者体験に届かない。保留された設計判断を確定する必要がある。

## Decision

中核ドメイン概念を、**段階的・加算的・後方互換**に第一級化する。新概念は追加せず、domain.md 既存概念を「往復保存される型」から「利用者が触れる作業状態」へ昇格する橋渡しに限定する。`PRODUCT-VALUE-02` が保留した schema 判断を本ADRで確定する。

### 循環デッドロックの解消（代理裁可）

- `ADR-0032`（プロダクト価値実現モデル）を **Accepted** とする（コア V0–V4 ループは active。二軸スコアカード等の VR4 観測機構は `ADR-0039` に従い activation 延期）。これにより `PRODUCT-VALUE-02` の Open化条件「ADR-0032 Accepted」が充足する。
- `PRODUCT-VALUE-02` の `DecisionStatus: Pending` を **Fixed** へ。保留されていた schema 判断は本ADRの方針（下記）を正本とする。Representation boundary table を価値ゲートV2の暫定正本として承認する。

### schema 第一級化の確定方針（PV-02 保留の解消）

| ドメイン語彙 | 現行 | 確定方針 |
| --- | --- | --- |
| 違和感 Critique / 根拠 EvidenceLink / 矛盾 Contradiction / claimType | 型は往復保存。UI無し | **schema変更なし**。既存往復フィールドを読取UI（バッジ/絞り込み/確認）として露出（Phase 1） |
| 保留 HoldState | `claimType="unknown"` の代理のみ | **加算的・任意フィールドを新設**（`holdState?`）。欠落時は従来挙動（Phase 2） |
| 未統合 PendingItems / Shelf | 型すら無し | **加算的・任意の Shelf membership を新設**。退避/復帰は可逆、内容削除と分離（Phase 2） |

加算原則: 新フィールドはすべて optional。未対応クライアント・旧データは欠落を従来挙動として解釈し、破壊しない。schema変更は `schemas.md` 先行更新→import/export/validate/tests 追随（`AGENTS.md` §4.2）。

### フェーズ分割（→ DOMAIN-EXPR-01..04）

- **Phase 1 / `DOMAIN-EXPR-01`**: 既存往復状態の読取UI第一級化（claimType/critique/evidence/reviewStateのバッジ・絞り込み）。schema変更なし、低リスク、価値先行検証。
- **Phase 2 / `DOMAIN-EXPR-02`**: 保留 Hold + 未統合 Shelf の第一級化（加算スキーマ拡張、可逆な退避/復帰）。
- **Phase 3 / `DOMAIN-EXPR-03`**: 違和感→再提案の日常ループUI（理由任意Critique→制約反映→再提案差分確認、P-04）。既存 `critiqueInputs`/`reproposalDiffs` を日常導線へ。
- **Phase 4 / `DOMAIN-EXPR-04`**: 根拠/主張/矛盾を人間レビューの第一級対象＋成果物要素へ接続（`PRODUCT-VALUE-03` reviewable packageと連携）。

### 非目標 / 緩和禁止の不変条件

- 非目標: 正解判定・採点・ランキング、AIによる保留の自動解除、矛盾の自動解決、証拠能力を持つ監査証跡。
- 緩和禁止（`ADR-0039` / CE0契約）: proposal-only、`human_reviewed` 人手昇格、SafeMode既定ON、`KJ_ATLAS_LLM_PROVIDER=none` 既定でも各Phaseの主要価値が成立。AIは Hold/Critique を解消せず保持対象として扱う。

## Three-Element Verification（ADR-0067 遡及適用）

| 次元 | このADRでの主張 | 他次元への制約 |
|------|----------------|---------------|
| **業務設計** | 中核概念（保留HoldState・違和感Critique・未統合Shelf・根拠EvidenceLink・矛盾Contradiction）が「概念の憲法」と「往復保存される型」の間で宙づりで、kj-atlasが単なるカード配置ツールに見える。中核概念を段階的・加算的・後方互換に第一級化し利用者が触れる作業状態へ昇格する | 機能: Phase 1は既存往復状態の読取UI（バッジ/絞り込み）でschema変更なし低リスク。データ: 非目標は正解判定・採点・ランキング・AIによる保留自動解除・矛盾自動解決 |
| **データ設計** | schema変更は違和感/根拠/矛盾/claimTypeは変更なし（既存往復フィールドを読取UIへ）、保留HoldStateは加算的・任意`holdState?`を新設、未統合Shelfは加算的・任意Shelf membershipを新設。新フィールドは全てoptionalで欠落時は従来挙動 | 業務: 退避/復帰は可逆、内容削除と分離。機能: schema変更はschemas.md先行更新→import/export/validate/tests追随 |
| **機能設計** | 4フェーズ（読取UI→保留+未統合→違和感→再提案ループ→根拠/矛盾をレビュー対象に接続）をDOMAIN-EXPR-01..04に分割。循環デッドロックはADR-0032をAcceptedにして解消 | 業務: 緩和禁止はproposal-only・human_reviewed人手昇格・SafeMode既定ON・provider=noneでも主要価値成立。データ: AIはHold/Critiqueを解消せず保持対象として扱う |

## Consequences

- 期待される効果: domain.md 中核概念が利用者体験に到達し、社会的目標（曖昧さを保留する道具）の核が成立する。PV-02 の循環デッドロックが解消し、設計判断の保留が確定する。
- 想定される副作用/制約: Phase 2 で schema を加算拡張するため、import/export/validate/tests の同期作業が伴う。状態語彙の過多はカード操作を重くしうる（Phase 1 を読取専用に限定して緩和）。
- 個人OSS段階の扱い（`ADR-0039`）: DOMAIN-EXPR-01..04 は Draft の deferred backlog とし、Phase 1（schema変更なし）から着手可能。重量級のRACI/KPIは課さない。

## Traceability

- Related: `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`
- Related: `01_Plans/adr/ADR-0001-value-to-requirements.md`（P-01/P-04/P-05）, `ADR-0032-product-value-realization-model.md`（V1–V3）, `ADR-0036`（VR2）, `ADR-0039`（段階適正化）
- Related: `02_Architecture/schemas.md`（DocumentV1 / CritiqueInput / EvidenceLink）, `02_Architecture/value_traceability.md` §2.1.1
- Derived-from: `01_Plans/issues/done/issue-PRODUCT-VALUE-02-ambiguity-evidence-workflow.md`（Representation boundary table の保留判断を確定）
