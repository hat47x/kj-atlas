# Issue Draft: PRODUCT-VALUE-02 保留・違和感・根拠不足を扱う作業フロー

- Type: Feature request
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (Product Value contract steward; accountable owner remains Productization Program Owner)
- Scope: `03_Implement/frontend/src/`, `03_Implement/frontend/e2e/`, `02_Architecture/schemas.md`, `02_Architecture/value_traceability.md`
- Related Backlog: `PRODUCT-VALUE-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `01_Plans/adr/ADR-0032-product-value-realization-model.md`, `00_Prompt/domain.md`, `00_Prompt/ai_cognitive_externalization_requirements.md`, `02_Architecture/llm_input_ir_spec.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Expected verification level: `e2e`

## Draft→Open 2026-06-20
PRODUCT-VALUE-02 Open化。循環デッドロック解消済み（ADR-0040: ADR-0032 Accepted + PV-02 schema判断確定）。
DOMAIN-EXPR-01..04のPhase 1から着手可能。DecisionStatus=Fixed。

## Implementation Progress 2026-06-21

### Done
- **CardView claimType badges**: fact/claim/hypothesis color-coded pills (DOMAIN-EXPR-01)
- **CardView critique indicators**: tag count pills + unreviewed dots (DOMAIN-EXPR-01)
- **SidePanel card detail**: claimType, critique text, critiqueTags chips, evidence link counts, contradiction counts
- **DomainStateSummary**: document-level card state distribution with map progress hints
- **Domain-expression keyboard E2E**: claim classification, review state, critique note/tag, evidence/contradiction visibility, hold/shelf restoration, and SafeMode share preflight
- **Localized domain-state labels**: selection context and critique controls render localized claim, hold, and critique-tag labels while preserving stored enum values
- No schema changes (reads existing card.claimType, card.critique, card.critiqueTags, card.textReviewed, document.evidenceLinks)

### Remaining
- H-PV2 proxy acceptance for the current Phase 1 ambiguity/evidence packet is recorded in `issue-PRODUCT-VALUE-02-current-open-readiness-summary.md` and carried forward on 2026-07-02.
- Current evidence packet links are recorded in `PRODUCT-QA-01` and `MVP-EXIT-01`.
- Remaining non-H-PV gates: Hold/Shelf first-class follow-up (`DOMAIN-EXPR-02`), CE1 real data-source parity, physical keyboard acceptance, screen-reader acceptance, and final program approval.

### Human Work Delegation Sync 2026-07-02

- 2026-06-29 H-PV2 delegated approval accepts the split-first Phase 1 strategy, fixture meaning, findability sufficiency, SafeMode/share boundary, and fixed-profile AI/review boundary for the current packet.
- The previous umbrella human-acceptance blocker is fixed for this issue's current Phase 1 evidence packet.
- This does not approve persistent Hold/Shelf semantics, automatic resolution, `human_reviewed` authority changes, SafeMode/share policy changes, or final shipment.

### Commits
- 7f655b15 CardView domain state badges
- a8309640 SidePanel card detail domain state
- 89d9fdc1 evidence/contradiction counts in SidePanel
- PR #2486 DOMAIN-EXPR-03: critique types migrated to domain.md 5 types, SidePanel reproposal diff preview, Open Reproposal button
- PR #2486 DOMAIN-EXPR-04: evidence/contradiction links in narrative export

### Domain-state localization evidence 2026-06-22

- The Japanese UI no longer exposes stored enum values such as `fact`, `claim`, `hypothesis`, `held`, or `too_close` in the state filters, card badges, selection context, or critique controls.
- Card claim type, review state, hold state, critique presence, and representative-count accessibility labels now use the active locale catalog.
- Unknown legacy critique tags remain visible as their stored value instead of being discarded, preserving backward-compatible diagnosis.
- Chrome verification on `http://127.0.0.1:4173/` confirmed `事実 / 主張 / 仮説` filters and the selected-card summary `主張種別: 主張（解釈） / 保留状態: 保留 / 近すぎる`, with no matching internal enum text in that UI region.
- Verification:
  - TypeScript `--noEmit`: pass.
  - Focused i18n, accessibility, filter, and operability tests: pass.
  - `domain_expression_keyboard_access.spec.ts`: 3 passed.
- No ADR is required because stored values, schema, SafeMode, proposal authority, and share/export behavior are unchanged.

### Evidence overlay localization evidence 2026-07-05

- The View controls evidence overlay no longer shows raw enum-like labels (`supports`, `contradicts`, `both`, `selection`, `all`, `hop(s)`) in Japanese. It now uses user-facing labels such as `支持`, `反証`, `支持と反証`, `選択中のカード`, `すべて`, and `{count}段階`.
- The SidePanel evidence overlay status now reuses the same localized scope labels instead of rendering the internal scope value.
- The SidePanel trace analytics progress and relation-count rows now render localized mode/relation labels instead of raw `both`, `supports`, or `contradicts` values.
- Added translation regression coverage in `src/i18n/translate.test.ts` so these labels do not silently revert to stored values.
- No ADR is required because this is a display-language and accessibility improvement only; stored view metadata, schema, SafeMode/share policy, and AI authority are unchanged.

## Requirement meta I/F（共通キー）

- RequirementID: PRODUCT-VALUE-02
- RequirementStatement: 利用者が、保留、違和感、根拠不足、反対意見を、削除や失敗ではなく作業状態として記録、確認、再提案の制約に使えるようにする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=カード、島、関係がある文書を開く / 操作=対象に保留、違和感、根拠不足、反対意見を付け、表示と絞り込みを確認する / 期待結果=未確定状態が残り、共有やAI提案時にもレビュー状態と安全境界が維持される / 除外=自動採点、正解判定、AIによる保留解除。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed（`ADR-0040` で schema 判断確定 / `ADR-0032` Accepted）
- DecisionQueueRef（未確定時の参照先）: N/A（`ADR-0040` で確定済み。実行は `DOMAIN-EXPR-01..04` と証跡ゲートへ分離）

## 1) 課題 / Problem statement

- `domain.md` は保留と違和感を中核概念として定義しているが、製品化UI上で日常操作としてどう扱うかがまだ薄い。
- `llm_input_ir_spec.md` は evidence / contradiction をAI文脈に含めているが、利用者が画面上で根拠不足や反対意見を記録する作業単位が十分に固定されていない。
- この不足により、kj-atlas が単なるカード配置ツールに見え、認知外在化ツールとしての価値が伝わりにくい。

## 2) 背景 / Context

- `ADR-0032` は V1/V2/V3 として、外在化、構造化、レビューを価値ループへ位置づけた。
- `CE0-REVIEW-IF` と `CE0-SAFEMODE-IF` は、未レビュー情報の保護と人手レビュー昇格を固定している。
- `PRODUCT-UX-02` は画面構造を扱うが、保留や根拠不足の操作語彙までは十分に分解していない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 保留と違和感を記録できないと、P-01/P-04の価値がUIで成立しない。
- 安全（THREAT_MODEL / SafeMode）: 未レビュー・根拠不足の情報が共有物で確定事項に見えると誤共有につながる。
- 企業・行政要件（enterprise_architecture）: 判断根拠、反対意見、未解決点を残せることは説明責任に直結する。
- 後方互換（schemas）: 既存スキーマへ破壊的変更を入れず、必要なら新規issue/ADRで拡張案を分離する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - カード/島/関係の選択コンテキスト、状態バッジ、絞り込み、共有前確認、AI Context Query入力。
- 変更の最小単位:
  - 保留、違和感、根拠不足、反対意見を利用者向け状態語彙として定義する。
  - これらの状態が表示、絞り込み、共有前確認、AI提案制約に現れることを確認する。
- 非目標:
  - 正解判定、採点、ランキング。
  - AIによる保留解除やレビュー済み昇格。
  - 証拠能力を持つ監査証跡の実装。

## 5) 受入条件 / Acceptance criteria

- [ ] カード、島、関係のいずれかに、保留または違和感を理由なしで付けられる。
- [ ] 根拠不足と反対意見を、確定済み情報と区別して表示できる。
- [ ] 状態バッジや絞り込みで、未整理、未レビュー、根拠不足を見つけられる。
- [ ] 共有前確認で、保留点、未レビュー情報、根拠不足が残っていることを確認できる。
- [ ] AI提案に渡す場合は、ContextBundle上で制約または除外理由として追跡できる。
- [ ] `human_reviewed` は人間操作でのみ昇格し、AI/worker/APIで自動昇格しない。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 保留、違和感、根拠不足、反対意見のUI語彙とデータ責務を整理する。
- [ ] T2 現行スキーマで表現できる範囲と、追加スキーマが必要な範囲を分離する。
- [ ] T3 選択コンテキスト、絞り込み、共有前確認に表示するワイヤーフローを作成する。
- [ ] T4 ContextQuery/ContextBundleへの受け渡し境界を確認する。
- [ ] T5 E2Eまたは統合テストで状態付与、表示、共有前確認を検証する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `rg -n "保留|違和感|根拠不足|反対意見|human_reviewed|unreviewed" 00_Prompt 01_Plans 02_Architecture 03_Implement/frontend 04_Documentation`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test --reporter=line`
- 期待結果:
  - 保留・違和感・根拠不足が操作、表示、共有前確認、AI入力境界で一貫して扱われる。
- 未実施時の理由・代替検証:
  - スキーマ拡張判断前は、ワイヤーフローとContextBundle境界レビューで代替する。

## 8) 代替案 / Alternatives considered

- 代替案A: コメント欄だけで保留や違和感を表現する。検索、共有前確認、AI制約に接続しにくいため採用しない。
- 代替案B: AIが保留点を自動解消する。プロジェクト価値とCE0契約に反するため採用しない。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 状態語彙が増えすぎて、カード編集が重くなる。
- 影響範囲: frontend selection context、schemas、ContextBundle、share/export。
- ロールバック手順: 状態語彙を表示専用の補助メタデータへ戻し、スキーマ拡張は別ADRに切り出す。

## 10) Additional context

- ADR化が必要になる条件: document/view/packスキーマへ新しい永続状態を追加する場合、またはEvidenceLink/ClaimTypeの製品UI責務を固定する場合。


## 11) 価値実現シリアル（Hypothesis → Action → Evidence → Decision）

- 価値仮説: 保留・違和感・根拠不足・反対意見を明示管理できると、早すぎる収束を防ぎレビュー品質が上がる。
- 行動:
  1. カード/島/関係に4状態（保留、違和感、根拠不足、反対意見）を付与する。
  2. 状態バッジと絞り込みで未確定項目を抽出する。
  3. 共有前確認で未確定情報の残存を確認する。
  4. AI提案入力境界で状態情報が制約として扱われることを確認する。
- 証拠:
  - E1: 状態付与と表示の検証結果（UIまたは仕様手順）。
  - E2: 絞り込み結果の再現記録。
  - E3: 共有前確認で未確定情報が表示された証拠。
  - E4: ContextBundle入力境界で状態が追跡可能な証拠。
- 判定（Go/No-Go）:
  - Go: E1〜E4が揃い、未確定状態抽出の再現率100%（同一条件3回で同一結果）。
  - No-Go: いずれかの状態が欠落、または再現率100%未満。

## 12) KPI定義（定義可能・再測定可能・比較可能）

- KPI-01 `ambiguity_state_coverage`
  - 定義: 4状態のうちUI語彙と証拠手順が定義済みの割合。
  - 再測定: issue本文と受入条件を照合する。
  - 比較: 版間で定義済み割合を比較する。
- KPI-02 `unresolved_extraction_reproducibility`
  - 定義: 同一条件で未確定項目抽出結果が一致する試行割合。
  - 再測定: 同一データで3回実行する。
  - 比較: 実装/仕様変更前後で割合比較する。
- KPI-03 `review_boundary_integrity`
  - 定義: `human_reviewed` が自動昇格しない検証項目の合格率。
  - 再測定: 固定チェックリストで確認する。
  - 比較: 回帰有無を版間で比較する。


---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。


## Stream I 要件契約固定パック（2026-05-18）

### Phase 1: Read同期サマリ
- 重複論点: 画面導線の分かりやすさ、SafeMode境界、検証証跡要件。
- 曖昧論点: Open化の判定条件と、依存関係が契約依存か実装依存かの境界。
- 欠落補完: 価値→要件→受入→測定の追跡行と、Draft→Open判定を明文化。

### Phase 2-3: ADR要素 + 要件契約
| Context | Decision | Consequences |
| --- | --- | --- |
| 上流価値定義（ADR-0001/0031/0032）を実装入口へ接続する必要がある。 | AC/DoDを機械検証可能な粒度で固定し、未確定はDecision Queueへ隔離する。 | 下流実装Streamは要件の再発明をせず、検証可能なIssue単位で着手できる。 |

### 価値→要件→受入→測定 対応表（最小）
| 価値仮説 | 要件（Requirement） | 受入条件（AC） | 測定（Evidence/KPI） |
| --- | --- | --- | --- |
| 利用者が安全に判断を共有できる。 | SafeMode境界を保持し、共有前確認を必須化する。 | SafeMode/公開範囲/未レビュー状態を実行前に提示できる。 | docs-check + E2E記録 + 文言一致確認。 |
| 要件から実装へ手戻りなく移行できる。 | AC/DoDをOpen前に固定し、未確定はPending化する。 | Draft→Open条件を満たしたIssueのみ実装に着手する。 | checklist充足率、No-Go件数、Pending解消件数。 |

### Phase 4: Draft→Open 条件（要件側ゲート）
- [ ] `DecisionStatus=Fixed` の要求のみでACが評価可能（PendingはDecision Queueへ退避済み）。
- [ ] 依存が `契約依存`（schema/api/policy/ops）と `実装依存`（UI/Backend/E2E）に分離されている。
- [ ] Validation plan のコマンドがこのIssue本文だけで再実行可能。

### Phase 5-6: Verify / Proceed 引き継ぎ条件
- Verify合格条件: 価値仮説とACの1対1追跡が可能で、非検証要件が残っていない。
- Proceed条件: 実装ストリームが「どのACをどのテストで満たすか」を追加解釈なしで決定できる。
- フェイルセーフ: 上流価値定義との矛盾・非検証要件・競合編集を検出した場合はOpen化を停止する。

## Open化判定メタ（Draft gate解除条件）

### Open化に必要な最小条件（全件必須）
- [ ] O-OPEN-01: `Owner` が `TBD` ではなく、実行責務者（個人またはロール）に確定している。
- [ ] O-OPEN-02: 依存Issue/ADRごとに `依存待ち理由` と `再開条件` が1:1で明示されている。
- [ ] O-OPEN-03: `Acceptance criteria` と `Validation plan` が `Expected verification level` と一致している。
- [ ] O-OPEN-04: docs-only範囲外の要求が本文に混入していない（本memoの範囲と矛盾しない）。

### 依存待ち理由（未解消時は Draft 維持）
| Dependency | 依存待ち理由 | 再開条件 | Owner |
|---|---|---|---|
| 上位ADR/関連Issue | 上位合意または境界仕様の最終確定待ち | 参照先に承認IDまたは確定コミットを追記 | Platform Architecture Owner / 各Issue Owner |
| QA検証経路 | `e2e`/`integration` の実行経路と証跡フォーマット未固定 | 実行経路（Compose/SQLite/例外）を1件固定し、判定ログ形式を定義 | QA Lead |
| 実行責務 | 実装担当とレビュー担当の分離未確定 | RACI（R/A）を本文に追記し通知記録を残す | PM/Triage |

### Proceed / Stop
- Proceed（Open化可）: O-OPEN-01〜04がすべて充足。
- Stop（Draft維持）: 依存先不明 / Status正規化不能 / 競合ファイル検出時は更新停止し、理由を `Additional context` に記録。



## Stream H Contract Finalization (2026-05-20)

### Scope confirmation
- Stream H dedicated; plan/ADR layer only; no implementation code edits.
- Target backlog: `MVP-EXIT-01` / `PRODUCT-VALUE-01..03` only.

### C/D/C lock (Context / Decision / Consequences)
| Context | Decision | Consequences |
| --- | --- | --- |
| PRODUCT-VALUE-02 requires Open-ready contract quality before downstream execution. | AC/DoD/KPI/audit fields are locked for docs-only verification first. | Downstream streams can execute without re-interpreting value intent. |

### KPI + audit scorecard mapping
- KPI field quality gate: definition / formula / evidence / re-measurement must all exist.
- Audit field quality gate: `reviewer`, `date`, `artifact id`, `decision`, `re-decision condition` must be explicit.

### AC / DoD final lock
- [ ] AC-F1 Hypothesis→Action→Evidence→Decision chain is explicit.
- [ ] AC-F2 Go/No-Go rule is explicit and binary-decidable.
- [ ] AC-F3 KPI definitions are re-measurable by docs-only procedure.
- [ ] DoD-F1 No cross-stream implementation dependency is required for contract validation.
- [ ] DoD-F2 Safety boundary wording (SafeMode/share-export/review attribution) is consistent with ADR-0032.

### Verify (non-dependency)
- Result: Contract validation is executable without waiting for other stream code merges.
- Reason: Inputs are issue text completeness and evidence schema only.

### Self-correction (<=3)
1. Normalized gate terms to `Go / Conditional Go / No-Go`.
2. Removed ambiguous wording that implied implementation readiness was required at this phase.
3. Added explicit audit metadata requirements for approval traceability.

### Approval-wait packet
- This section + ADR-0032 Stream H block are the approval bundle for PRODUCT-VALUE-02.

## Draft Gate Assessment 2026-05-23: Open readiness

- Assessment scope: 計画層のreadiness確認のみ。`Status: Draft` は維持し、実装着手やスキーマ変更はこの追記では行わない。
- Gate result: Draft維持。`DecisionStatus=Pending` と `Owner: TBD` に加え、曖昧さ、違和感、証拠、矛盾を現行データ構造でどこまで表現するかの境界が未確定。
- Proposed RACI: R=Product Value Stream Lead（未割当）, A=Productization Program Owner, C=Platform Architecture Owner / QA Lead, I=Documentation Maintainer。CodexはOwner確定までissue本文と証跡パックの整備を支援する。
- O-OPEN status:
  - O-OPEN-01: Blocked. `Owner` が `TBD` のため、実行責務者をロールまたは個人で確定する必要がある。
  - O-OPEN-02: Blocked. `ADR-0032` と `llm_input_ir_spec.md` のどちらが保留・違和感・根拠・矛盾の最小表現を正本化するかが本文上で未分離。
  - O-OPEN-03: Partial. ACはe2eで評価可能だが、入力、状態遷移、出力証跡の最小fixtureが未固定。
  - O-OPEN-04: Pass for assessment. この追記はOpen判定の整理であり、docs-only範囲外の実装要求を追加しない。
- 契約依存:
  - `ADR-0032`: 保留や違和感を価値実現モデルの中でどの単位として扱うか。
  - `00_Prompt/domain.md`: 保留、違和感、可逆性の用語定義。
  - `00_Prompt/ai_cognitive_externalization_requirements.md`: AI支援時の文脈束、根拠、判断保留の扱い。
  - `02_Architecture/llm_input_ir_spec.md`: LLM投入前の正規化IRで保持できる根拠・制約。
- 実装/証跡依存:
  - 利用者が曖昧さを1件登録し、根拠または反証メモを付与し、判断待ちとして画面上で確認できるE2E。
  - AI未使用、ローカルLLM使用、共有前確認の3経路で、未確定情報が断定表現に変換されないことの検証。
- Next action:
  - 現行スキーマで対応する範囲と、ADRまたはschema issueが必要な範囲を1表に分ける。
  - ADR-0032でDecisionStatusをFixedにできる承認IDまたは確定コミットを得るまではOpen化しない。

## Draft Gate Reassessment 2026-05-27: owner fixed, representation boundary split

- Assessment scope: 計画層のDraft維持理由を、担当未確定ではなくADR-0032承認待ちと「現行構造で表現できる範囲」の固定へ絞り込む。
- Gate result: **Draft維持**. OwnerはCodexの契約・証跡整備責務として確定したが、`DecisionStatus=Pending` と `ADR-0032` Proposed が残るためOpen化しない。
- RACI:
  - R: Codex (Product Value contract steward)
  - A: Productization Program Owner
  - C: Platform Architecture Owner / QA Lead
  - I: Documentation Maintainer / Frontend Lead
- O-OPEN status:
  - O-OPEN-01: Pass. OwnerはCodexに確定し、最終説明責任はProductization Program Ownerに分離した。
  - O-OPEN-02: Partial. `ADR-0032` の価値語彙と `02_Architecture/schemas.md` の現行DocumentV2要素を以下の表で分離したが、第一級のHold/Pendingデータ構造を追加するかは未承認。
  - O-OPEN-03: Partial. e2e前提のACは維持するが、曖昧さ、違和感、証拠、矛盾の最小fixtureと保存先は未固定。
  - O-OPEN-04: Pass. 本更新は契約整理であり、実装変更やスキーマ変更を直接要求しない。

### Representation boundary table

| 価値語彙 | 現行構造で扱える範囲 | 現行構造で不足する範囲 | 次の扱い |
| --- | --- | --- | --- |
| 保留 / Pending | `claimType="unknown"`、カード/島の`critique`、未レビュー`reviewState`で「未確定である」ことを補助的に表現できる。 | 利用者が明示的に「保留」として作業状態を付ける第一級フィールドは未固定。 | ADR-0032承認後に、既存フィールド運用で足りるか、schema issueを切るか判断する。 |
| 違和感 / Critique | `critiqueInputs`、`critiqueTags`、HIL-RS critique payloadでAI入力境界には保持できる。 | 日常UIでの登録、一覧、絞り込み、共有前確認までの標準導線は未固定。 | 初回はUI語彙とE2E fixtureで検証し、永続化拡張が必要なら別issue化する。 |
| 根拠 / Evidence | `evidenceLinks`、claim/evidence overlay、trace exportでカード間の支持/反証関係を扱える。 | 根拠の粒度、必須/任意、成果物内での表示順は価値ゲートとして未固定。 | `PRODUCT-VALUE-03` と連携し、reviewable packageの最小要素へ接続する。 |
| 矛盾 / Contradiction | contradiction checks、evidence overlay mode、trace exportで検出/表示の入口がある。 | 矛盾を利用者が確認済み、保留、解決済みとして扱う状態遷移は未固定。 | schema変更なしで代表E2Eを先に固定し、状態遷移が必要ならADR/schema issueへ送る。 |
| 人間レビュー境界 | `reviewState`（`unreviewed` / `human_reviewed`）と `reviewedAt` で人手昇格境界を保持できる。 | 曖昧さや根拠不足の解消と`human_reviewed`昇格の関係は未固定。 | `review_attribution.md` と整合し、AI自動昇格禁止を維持する。 |

### Evidence route refinement 2026-06-02

This refinement keeps `Status: Draft`. It does not authorize schema expansion or UI implementation. The goal is to make ambiguity/evidence work measurable with the current architecture first, and to identify the exact point where a future schema/ADR decision would be required.

Minimum value states to exercise:

| State | User-facing meaning | Current representation candidate | Evidence required before Open |
| --- | --- | --- | --- |
| Hold | The user intentionally pauses a decision | card/island note, critique marker, or unresolved review state | fixture plus screenshot/trace showing the hold can be found again |
| Ambiguity | More than one interpretation remains plausible | critique text, relation context, or unresolved claim type | trace showing the ambiguity is visible before share/export |
| Evidence gap | A claim lacks supporting material | evidence link absence or explicit gap note | fixture showing the gap is preserved and not converted to a resolved claim |
| Contradiction | Two statements cannot both be accepted as-is | contradiction/evidence overlay or review note | trace showing the user can inspect both sides without auto-resolution |

Required evidence packet before Open:

| Evidence item | Required content | Gate handoff |
| --- | --- | --- |
| State fixture | At least one hold, ambiguity, evidence gap, and contradiction | `PRODUCT-QA-01` V2/V3 |
| Review boundary proof | `human_reviewed` is not assigned by AI, worker, or API automation | G1 / G7 |
| Share/export proof | unresolved or unreviewed state remains visible or safely excluded before sharing | G1 / G5 |
| AI-input proof | ContextBundle or equivalent input keeps the state as a constraint, not as a solved fact | CE / value gate handoff |
| Decision record | Go/Conditional Go/No-Go and unresolved schema/ADR need | `MVP-EXIT-01` |

No-Go conditions for this value gate:

- Ambiguity, hold, evidence gap, or contradiction is silently converted into a resolved claim.
- AI output can mark a state as `human_reviewed`.
- Share/export hides unresolved state in a way that makes the reader over-trust the result.
- The scenario requires a new persistent schema field but no issue/ADR records that requirement.

- Reopen/Open condition:
  - `ADR-0032` がAcceptedになる、またはProductization Program Ownerが上記representation boundaryを価値ゲートの暫定正本として明示承認する。
  - 曖昧さ、違和感、根拠、矛盾を含む最小fixtureと、同一条件3回の再現性検証手順が本文で固定される。
  - 上記完了後、StatusをOpenへ変更し、`PRODUCT-QA-01` のValue Gate V2/V3へ戻す。

## 解消ログ 2026-05-31（Maintainer 代理裁可 / `ADR-0040`）

- 循環デッドロック（`ADR-0032` Proposed ⇄ 本issue Draft）を解消した。`ADR-0032` を **Accepted** 化し、本issueの `DecisionStatus` を **Fixed** に確定。
- 上表 Representation boundary table を価値ゲートV2の**暫定正本として承認**。各行「次の扱い」で保留されていた schema 判断は `ADR-0040` で次のとおり確定:
  - 違和感 / 根拠 / 矛盾 / claimType / レビュー境界 → **schema変更なし**。既存往復フィールドを読取UIへ露出（`DOMAIN-EXPR-01`）。
  - 保留 Hold / 未統合 Shelf → **加算的・任意フィールドを新設**（`DOMAIN-EXPR-02`、後方互換・欠落は従来挙動）。
- 本issueは「保留・違和感・根拠不足・反対意見の作業フロー」の価値仮説の正本を維持し、実装は段階分割した `DOMAIN-EXPR-01..04`（`ADR-0040`）が担う。本issue自体の Open化は個人OSS段階（`ADR-0039`）では延期し、Phase 1（`DOMAIN-EXPR-01`、schema変更なし）から着手可能とする。

## Mainline gap assessment 2026-06-04: partial domain-expression evidence only

- Candidate mainline: `origin/main@70b6269a24d01c6f4b386e5b7a724738dd02e2bd`
- Status impact: **Draft remains**. Current `main` contains partial evidence for reading and reaching ambiguity-related fields, but it does not yet provide the complete PRODUCT-VALUE-02 workflow evidence packet.
- Mainline evidence now available:
  - #2315 adds keyboard reachability for claim type, unreviewed state, evidence/contradiction text, critique memo, and critique tags through `DOMAIN-EXPR-01`.
  - #2314 adds review-pack trace export consistency for selected-card evidence, contradiction, and trace analytics files through `PRODUCT-VALUE-03`.
  - #2319 records the post-2318 release-gate sync and keeps full shipment No-Go.
- Evidence packet status:

| Required evidence item | Current status | Remaining Draft blocker |
| --- | --- | --- |
| State fixture | Not satisfied as a combined PRODUCT-VALUE-02 fixture. | Need one scenario that includes hold, ambiguity, evidence gap, and contradiction, or an explicit decision to split them across `DOMAIN-EXPR-01..04`. |
| Review boundary proof | Partially satisfied by visible unreviewed state and the absence of automated `human_reviewed` promotion in the current UI path. | Need a targeted guard or evidence note proving AI/worker/API automation cannot mark the value-gate state as human-reviewed. |
| Share/export proof | Partially satisfied by SafeMode/share preflight and review-pack trace export behavior. | Need proof that unresolved or unreviewed ambiguity/evidence state is visible or safely excluded before sharing for the PRODUCT-VALUE-02 scenario. |
| AI-input proof | Not satisfied by current mainline evidence. | Need ContextBundle or equivalent evidence showing ambiguity/evidence/contradiction is preserved as a constraint, not converted into a solved fact. |
| Decision record | Partially satisfied by PRODUCT-QA / MVP-EXIT post-2318 records. | Final PRODUCT-VALUE-02 decision must cite this issue after the state fixture, review boundary, share/export, and AI-input proof are complete. |

- Next work proposal:
  - Keep this issue Draft and create a follow-up implementation/evidence slice only when the Productization Program Owner accepts whether the four value states should be tested in one fixture or split by `DOMAIN-EXPR-01..04`.
  - If the four-state fixture requires persistent Hold/Pending/Shelf fields, route that through `DOMAIN-EXPR-02` and ADR/schema review before implementation.
  - If the proof can remain schema-neutral, define a Playwright scenario that uses existing `claimType`, `textReviewed`, `critique`, `critiqueTags`, and `evidenceLinks` fields and records the SafeMode/share outcome.
- No ADR is needed for this gap assessment. ADR routing is required only if the next slice changes the value-state model, adds persistent Hold/Shelf fields, changes AI review authority, or changes SafeMode/share policy.

## Open route proposal 2026-06-06: split value-state evidence, then integrate

- Candidate baseline: current `main` after post-2338/2339/2340 planning sync.
- Status impact: **Draft remains**. `DecisionStatus=Fixed` stays valid because `ADR-0040` fixed the schema strategy, but Open still requires value evidence and human acceptance.
- Recommendation: do **not** force hold, ambiguity, evidence gap, and contradiction into one first implementation fixture. Split evidence across `DOMAIN-EXPR-01..04`, then add one umbrella PRODUCT-VALUE-02 review packet that confirms the four states remain understandable together.

### Why split first

| Value state | Best first slice | Reason | Escalation trigger |
| --- | --- | --- | --- |
| Ambiguity / critique visible | `DOMAIN-EXPR-01` | Existing `claimType`, critique text/tags, evidence, contradiction, and review state can be inspected without schema expansion. | If users cannot re-find the state without dedicated filters, keep Draft or add a frontend-only filter slice. |
| Hold / pending | `DOMAIN-EXPR-02` | `ADR-0040` already says first-class Hold/Shelf requires additive optional schema. | Any persistent Hold/Shelf field needs schema-first review and migration/compatibility tests. |
| Critique -> reproposal | `DOMAIN-EXPR-03` | This is an action loop, not only a read UI; it needs proposal-only and reversible review boundaries. | If AI output can resolve or overwrite critique, route through ADR/CE review before implementation. |
| Evidence / contradiction review | `DOMAIN-EXPR-04` | The user must inspect both support and contradiction without auto-resolution before it becomes a reviewable package element. | If evidence state changes review attribution, route through review schema/policy review. |

### Umbrella PRODUCT-VALUE-02 evidence packet

The final value gate should be evaluated only after the slice evidence exists. The packet should include:

| Evidence item | Minimum content | Human judgement needed |
| --- | --- | --- |
| State inventory | A small scenario that names at least one ambiguity/critique, one hold or pending item, one evidence gap, and one contradiction. | Productization Program Owner confirms these states are meaningful to a general user. |
| Findability proof | Search/filter/review panel evidence showing each state can be found again after navigation. | UX reviewer confirms the operation is natural with mouse and keyboard. |
| Safety proof | Share/export or Review Pack evidence showing unresolved/unreviewed state is visible or safely excluded. | Safety reviewer confirms the result cannot be mistaken for a fully reviewed conclusion. |
| AI-boundary proof | ContextBundle or equivalent evidence showing states are carried as constraints, not solved facts. | Architecture owner confirms AI remains proposal-only and cannot set `human_reviewed`. |
| Integration decision | Go / Hold / Stop decision citing the four slice issues. | Productization Program Owner decides whether PRODUCT-VALUE-02 can move from Draft to Open. |

### Current human decision queue

| Decision | Owner | Recommended default | Consequence |
| --- | --- | --- | --- |
| PV2-D1 Evidence strategy | Productization Program Owner | Split by `DOMAIN-EXPR-01..04`, then integrate. | Avoids a monolithic fixture that pressures premature schema or UI scope. |
| PV2-D2 Phase 1 findability | UX reviewer | Require either dedicated filters or explicit acceptance that search is enough for Phase 1. | Determines whether `DOMAIN-EXPR-01` can Open as-is. |
| PV2-D3 Schema boundary | Architecture owner | Keep `DOMAIN-EXPR-01` schema-neutral; route Hold/Shelf to `DOMAIN-EXPR-02`. | Preserves `ADR-0040` staging and avoids hidden schema drift. |
| PV2-D4 Safety boundary | Safety reviewer / Maintainer | Keep SafeMode/share and human review authority unchanged. | Any relaxation requires ADR before implementation. |

- ADR need: none for the split-first evidence strategy itself because it follows `ADR-0040`. New ADR/schema work is required only if a slice changes persistence, AI review authority, SafeMode/share policy, or the value-state model.

## Evidence rerun sync 2026-06-06: DOMAIN-EXPR-01 keyboard slice

- Candidate mainline: `origin/main@b8a1619d20aad91713800f3f0c209af3de14ff8b`.
- Status impact: **Draft remains**. This sync improves the freshness of the ambiguity/critique read-only evidence slice, but it does not complete the umbrella PRODUCT-VALUE-02 value gate.
- Evidence consumed:
  - `e2e/domain_expression_keyboard_access.spec.ts` rerun with bundled Node.js and Vite direct startup -> **pass, 1 test**.
- Value-gate impact:
  - Ambiguity / critique visible: current-main evidence is fresh for keyboard access to claim type, review state, evidence, contradiction, critique memo, and critique tags.
  - Hold / pending: unchanged; first-class Hold/Shelf remains routed to `DOMAIN-EXPR-02`.
  - Critique -> reproposal: unchanged; action-loop evidence remains routed to `DOMAIN-EXPR-03`.
  - Evidence / contradiction review: partially supported by read-only visibility, but review workflow remains routed to `DOMAIN-EXPR-04`.
- Remaining blockers before PRODUCT-VALUE-02 Open:
  - Human acceptance of whether `DOMAIN-EXPR-01` is a meaningful read-only slice for standard users.
  - Decision on search-only versus dedicated unresolved-state filters.
  - Evidence for Hold/Pending, critique-to-reproposal, AI-boundary proof, share/export proof, and umbrella integration decision.
- No ADR is needed for this sync. ADR/schema routing remains required if a later slice changes persistence, AI review authority, SafeMode/share policy, or the value-state model.

## Stream F Frontend implementation note (2026-06-13)

- Scope: current-schema frontend workflow only; no schema expansion was performed.
- Ambiguity/evidence signals are now bundled into the share/export preflight as a review checkpoint: unresolved holds, critiques, contradictions, evidence gaps, and unreviewed content are visible before outcome sharing.
- The flow remains proposal/readiness-only: it does not auto-resolve ambiguity, auto-apply AI output, or auto-promote `human_reviewed`.

## Fixture manifest 2026-06-17: PV02 ambiguity/evidence packet entry

- Candidate mainline: `origin/main@4fe6740678dd970a18eacab094ec4e99c53496c5`.
- Fixture source: `03_Implement/frontend/e2e/helpers/product_value_fixtures.ts`.
- Fixture builder: `buildDomainExpressionDocument()`.
- Fixture document ID: `doc_domain_expression_keyboard_access`.
- Representative E2E: `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`.
- Status impact: **Draft remains**. This manifest names the reusable fixture entry for the PV02 evidence packet; it does not complete the umbrella Product Value ambiguity/evidence gate or approve Open status.

### Evidence packet mapping

| Evidence item | Manifest status | Remaining Draft blocker |
| --- | --- | --- |
| State fixture | Named and stored in `product_value_fixtures.ts`; includes one ambiguous target claim, one reviewed supporting field note, one unreviewed contradicting stakeholder signal, critique text, critique tag, and support/contradiction links. | Hold/pending remains split to `DOMAIN-EXPR-02`; Productization Program Owner must accept whether PV02 can proceed with split evidence rather than one monolithic four-state fixture. |
| Review boundary proof | Existing E2E verifies the selected target starts as `Review state: Unreviewed` and requires keyboard action to check `Card text reviewed`. | Need a targeted guard or evidence note that AI/worker/API paths cannot promote `human_reviewed` for this value-gate state. |
| Findability proof | Existing E2E verifies keyboard reachability of claim type, evidence/contradiction text, critique note, and critique tag controls after card selection. | UX reviewer must decide whether this read-only reachability is enough or whether dedicated unresolved-state filters are required. |
| Share/export proof | Not added by this manifest. | Need share/export preflight evidence showing unresolved or unreviewed ambiguity/evidence state is visible or safely excluded. |
| AI-boundary proof | Not added by this manifest. | Need ContextBundle or equivalent evidence that ambiguity/evidence/contradiction is carried as a constraint, not solved fact. |

- No ADR is needed for this manifest because it follows the `ADR-0040` split-first strategy. ADR/schema routing remains required if a later slice adds persistent Hold/Shelf fields, changes AI review authority, changes SafeMode/share policy, or changes the value-state model.

## Share preflight evidence 2026-06-18: unresolved signals remain explicit

- Candidate mainline: `origin/main@2e1f0edd38a089005269da91b213914500ec3af5`.
- Representative E2E: `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`.
- Screenshot: `04_Documentation/assets/screenshots/product-value-ambiguity-share-preflight.png`.
- Fixture: `buildDomainExpressionDocument()` / `doc_domain_expression_keyboard_access`.
- Automated evidence:
  - Share & Reproduce reports 5 remaining review signals.
  - The preflight summary reports 2 unreviewed cards, 1 Hold/unknown claim, 1 critique/pending-feedback target, 2 evidence links, 1 contradiction, and 0 evidence gaps.
  - SafeMode ON explicitly excludes unreviewed drafts, and the control to include them is not presented.
  - The summary tells the reviewer to review the material or keep holds explicit before sharing.
- Verification result: targeted Playwright **2 passed**, covering both keyboard reachability and share-preflight safety.

### Evidence packet update

| Required evidence item | Current status after this slice | Remaining Draft blocker |
| --- | --- | --- |
| State fixture | Phase 1 ambiguity/critique/evidence/contradiction fixture remains replayable. | First-class Hold/Pending remains split to `DOMAIN-EXPR-02`; umbrella acceptance remains human-owned. |
| Review boundary proof | The fixture remains unreviewed until a user explicitly changes review state. | Targeted AI/worker/API non-promotion proof remains required. |
| Findability proof | Keyboard reachability and selected-card inspection remain covered. | UX reviewer must decide whether dedicated unresolved-state filters are required. |
| Share/export proof | **Satisfied for the Phase 1 fixture.** Unreviewed and unresolved signals are visible before sharing, and SafeMode excludes unreviewed drafts by default. | Human safety/UX acceptance of the wording and counts remains required. |
| AI-input proof | Not changed by this slice. | ContextBundle or equivalent proof must preserve ambiguity/evidence/contradiction as constraints. |

- Status impact: **Draft remains**. The Phase 1 share/export proof blocker is addressed, but Hold/Pending, AI-boundary proof, umbrella integration, and human acceptance remain incomplete.
- No new ADR is needed. The slice verifies the existing SafeMode/share policy and does not change persistence, review authority, or the value-state model.

## AI review-boundary guard 2026-06-19

- Candidate mainline: `origin/main@219eec7ed1e9e36c87905bae04cd917b1b98efa5`.
- Guarded paths:
  - Backend AI proposal envelopes now accept only `reviewState="unreviewed"`.
  - HIL rediff contract validation rejects review-protected fields such as `textReviewed`, `reviewState`, `reviewedAt`, `reviewerRef`, and `reviewAttribution`, including nested occurrences.
  - HIL rediff application repeats the same protection so typed or otherwise prevalidated callers cannot inject review state through an `add` operation.
  - Normal document import remains able to preserve valid human review attribution; it is not an AI-promotion path.
- Verification:
  - Backend CE2 proposal API: 6 passed.
  - Frontend HIL contract/apply, CE2 candidate, and document-import tests: 23 passed.
  - Frontend typecheck: pass.

### Evidence packet update

| Required evidence item | Current status after this guard | Remaining Draft blocker |
| --- | --- | --- |
| Review boundary proof | **Satisfied for AI proposal and HIL worker/apply paths.** AI proposals remain unreviewed and rediff payloads cannot inject review-protected fields. | Human review transition authorization and audit remain governed by the existing review-attribution contract. |
| Import boundary | Valid human-reviewed documents remain preservable through document import. | Productization Program Owner / QA Lead must accept this separation as sufficient value-gate evidence. |
| Share/export proof | Phase 1 preflight evidence is already replayable. | Human wording and findability acceptance remain open. |
| AI-input proof | Promotion is blocked, but ContextBundle semantic preservation is not changed by this slice. | Need explicit proof that ambiguity/evidence/contradiction are carried as constraints rather than solved facts. |

- Status impact: **Draft remains**. The automated review-promotion blocker is addressed, but ContextBundle constraint proof, Hold/Pending, umbrella integration, and human acceptance remain incomplete.
- No new ADR is needed. This change enforces the accepted `CE0-REVIEW-IF` and does not change review authority or state vocabulary.

## ContextBundle constraint-preservation proof 2026-06-19

- Candidate mainline: `origin/main@8f81e5d70112d9570bf5c940a206a216cd468293`.
- Fixed profile: `A2-minimal-v1`.
- Implementation and contract evidence:
  - The reviewed selected item remains a `hypothesis`; review does not convert it into a fact.
  - Selected items, relations, evidence, counter-opinions, and contradictions carry `resolutionState="unresolved"`, `aiDisposition="constraint"`, and `autoResolve=false`.
  - Strict SafeMode excludes the unreviewed counter-opinion text from `selected` while retaining text-free evidence and contradiction signals as constraints.
  - A backend route test asserts these semantics through the public `/context/bundle` boundary.
- Verification target: `03_Implement/backend/tests/test_context_bundle_routes.py`.

### Evidence packet update

| Required evidence item | Current status after this proof | Remaining Draft blocker |
| --- | --- | --- |
| AI-input proof | **Satisfied for the fixed CE1 mock profile.** Ambiguity, evidence, counter-opinion, and contradiction signals remain unresolved constraints and cannot be marked for automatic resolution. | Real repository projection remains on the existing CE1 data-source hold; production parity must be reverified when that hold is lifted. |
| SafeMode boundary | Unreviewed text is excluded while non-textual unresolved signals remain traceable. | Human safety/UX acceptance remains required. |
| Hold/Pending | Not changed by this slice. | First-class Hold/Pending remains routed to `DOMAIN-EXPR-02`. |
| Umbrella decision | Automated evidence is now available for state, share/export, review-promotion, and fixed-profile AI-input boundaries. | Productization Program Owner / QA Lead acceptance and findability/accessibility review remain open. |

- Status impact: **Draft remains**. Fixed-profile AI-input proof is addressed, but real data-source parity, Hold/Pending, human findability/accessibility acceptance, and umbrella approval remain incomplete.
- No new ADR is needed. This change clarifies the accepted CE1 mock profile without changing top-level contract keys, persistent schema, review authority, or SafeMode policy.
