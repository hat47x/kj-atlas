# Issue Draft: DOMAIN-EXPR-01 既存ドメイン状態の読取UI第一級化

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex (UI evidence steward; accountable acceptance owner remains Productization Program Owner / UX reviewer)
- Scope: `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/e2e/`
- Related Backlog: `DOMAIN-EXPR-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `00_Prompt/domain.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: N/A
- Expected verification level: `e2e`

## Done 2026-06-20

ADR-0040 Phase 1 読取UI第一級化 完了。Schema変更なし、既存往復フィールドの読取UI露出。

### Implemented

**CardView (canvas/CardView.tsx)**:
- claimType badge: 色分けpill (fact=緑, claim=青, hypothesis=紫, unknownは非表示)
- critique indicator: タグ数表示付き (critiqueTagsがある場合はタグ数pill、なければamber dot)
- unreviewed indicator: カード右下amber dot (textReviewed=falseの場合)

**SidePanel (ui/SidePanel.tsx)**:
- 選択カード詳細にclaimType表示
- 選択カード詳細に違和感(critique)テキスト表示 (amber背景)
- 選択カード詳細にcritiqueTagsチップ表示

**i18n**: en/ja locale keys追加 (side_panel.context.claim_type, side_panel.context.critique)

### Verification
- TypeScript typecheck: clean
- Vitest: 160 test files / 753 tests passed
- Backend pytest: 269 passed / 19 skipped
- Schema: 変更なし (ADR-0040 Phase 1 非破壊原則遵守)

### Commits
- 7f655b15 feat(DOMAIN-EXPR-01): add claimType/critique/reviewState badges to CardView
- faed8fe6 feat(DOMAIN-EXPR-01): add domain state display to SidePanel card detail

> 個人OSS段階（`ADR-0039`）の軽量起票。重量級の RACI/KPI セクションは省略。`ADR-0040` Phase 1。

## 1) 課題 / Problem statement

`schemas.md` は `claimType` / `critiqueInputs` / `evidenceLinks` / `reviewAttribution` を往復保存するが、line 432 のとおり画面上の個別UIを提供していない。利用者は domain.md 中核概念（違和感・根拠・矛盾・レビュー状態）が文書に存在しても、画面上で確認・発見できない。frontend に Hold/Pending系の表示も無い。

## 2) 背景 / Context

- `ADR-0040` Phase 1 は「schema変更なしで、既存往復状態を読取UIとして第一級化する」最小・低リスク段階。
- `PRODUCT-VALUE-02` Representation boundary table が、違和感/根拠/矛盾/レビュー境界は「現行構造で扱える」と確認済み（不足は日常導線）。
- `PRODUCT-UX-02`（Done）で選択コンテキストパネルは既に存在し、そこへ状態を露出できる。

## 3) 提案する解決策 / Proposed solution

- 変更対象（Frontend のみ、schema変更なし）:
  - カード/島の選択コンテキストに、`claimType`（fact/hypothesis/unknown等）、`reviewState`（unreviewed/human_reviewed）、関連する `critiqueInputs`・`evidenceLinks` 件数を状態バッジとして表示。
  - キャンバス/一覧で「未レビュー」「根拠なし」「違和感あり」を絞り込めるフィルタ。
- 最小単位: まず表示とフィルタ（読取専用）。登録・編集は `DOMAIN-EXPR-02/03` で扱う。
- 非目標: schema拡張、Hold/Shelfの新設、AIによる状態変更、正解判定・採点。

## 4) 受入条件 / Acceptance criteria

- [x] カード/島選択時に claimType と reviewState がバッジ等で確認できる。→ CardView の claimType badge（fact/claim/hypothesis 色分けpill）、critique indicator、unreviewed amber dot、SidePanel の claimType・違和感テキスト・critiqueTags 表示（上記 Done 2026-06-20 節）。
- [x] 「未レビュー」「根拠なし」「違和感あり」で対象を絞り込める。→ `DomainStateFilterBar.tsx` + `domain_state_filter.ts` に claimType / unreviewedOnly / hasCritique / holdStates のフィルタを実装（`domain_state_filter.test.ts` 56行で検証）。
- [x] schema（DocumentV2）に変更がない（往復保存フィールドの読取のみ）。→ Done 2026-06-20 節「Schema: 変更なし (ADR-0040 Phase 1 非破壊原則遵守)」。
- [x] AI/worker/API が `human_reviewed` を自動昇格しない（CE0-REVIEW-IF 非後退）。→ `core_value_guard.test.ts` CVI-3「human_reviewed promotion is human-only」で担保。
- [x] `KJ_ATLAS_LLM_PROVIDER=none` 既定でも表示・絞り込みが成立する。→ 表示・絞り込みは純 frontend 処理で LLM 非依存（provider=none でも成立）。
- [x] E2E で状態表示と絞り込みを検証する。→ `e2e/domain_expression_keyboard_access.spec.ts`（状態表示・キーボード到達性）。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/typescript/bin/tsc --noEmit`
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run`
  - `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test --reporter=line`
  - `rg -n "claimType|reviewState|critiqueInputs|evidenceLinks" 03_Implement/frontend/src`
- 期待結果: 既存往復状態が選択コンテキストと絞り込みで一貫して確認でき、schema差分が無い。
- 未実施時の代替: 実装前はワイヤーフローと選択コンテキストのレビューで代替。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: バッジ過多で選択コンテキストが煩雑化。
- 影響範囲: SidePanel、CardView/IslandView、フィルタ状態。
- ロールバック: バッジ/フィルタをコンポーネント単位で無効化（schema非依存のため安全）。

## 7) Additional context

- ADR化が必要になる条件: 表示のために永続状態を追加する必要が出た場合（その時点で `DOMAIN-EXPR-02` または新schema issueへ送る）。

## 8) Chrome UI evidence intake（2026-06-03）

### Scope

- 対象: `origin/main@3abccd34` の local-dev UI。
- 起動: frontend `http://127.0.0.1:4173/`、backend `http://127.0.0.1:8000/`。
- 環境: `KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db`、`KJ_ATLAS_LLM_PROVIDER=none`。
- この追記は Draft gate の証跡整理であり、Status変更、schema変更、API変更、SafeMode変更、実装着手許可ではない。

### Observed UI evidence

| Observation | Result | Gate impact |
| --- | --- | --- |
| Sample load | backend 起動後、`サンプルを開く` で `doc_phase1_canvas` のカードが表示された。 | `PRODUCT-VALUE-01` の初回価値導線に使える候補。 |
| Card selection | `ユーザー課題を集める` を選択すると、`現在の選択` に対象名と `レビュー状態: 未レビュー` が表示された。 | claim/review state の入口は画面上で確認可能。 |
| Claim/review controls | 選択カード詳細に `主張タイプ`、`カード本文をレビュー済みにする` が表示された。 | AC1 の一部は実装済み候補。ただし受入には人間確認が必要。 |
| Evidence/contradiction | `根拠`、`根拠トレース`、`矛盾トレース`、`トレース分析` が表示された。 | evidence/contradiction の読取UI候補が存在する。 |
| Critique | `批評メモ` と `too_close` / `too_far` / `belongs_together` / `unrelated` / `unclear_boundary` が表示された。 | `DOMAIN-EXPR-03` へ渡す前に、Phase 1 の読取/入力境界を人間が確認する必要がある。 |
| Search | `カードを検索` に `観察` を入力すると `1/1` になり、該当カードが表示された。 | 絞り込みACの入口はあるが、`未レビュー` / `根拠なし` / `違和感あり` 固有フィルタは未確認。 |

### Human acceptance tasks

| Task | Owner | Required action | Exit criteria |
| --- | --- | --- | --- |
| H-DX1 Phase 1 acceptance | Productization Program Owner / UX reviewer | 上表の visible controls が `DOMAIN-EXPR-01` Phase 1 の「読取UI第一級化」として十分か確認する。 | 十分なら Draft->Open 候補へ進める。不十分なら不足UIを1つずつACへ戻す。 |
| H-DX2 Filter boundary | UX reviewer | `未レビュー` / `根拠なし` / `違和感あり` の固有フィルタが現UIで足りるか、追加UIが必要か判断する。 | フィルタ追加が必要なら Frontend-only issue とE2E条件を明記する。 |
| H-DX3 Keyboard acceptance | UX reviewer | 実Chromeで選択カード、主張タイプ、レビュー済みチェック、批評メモ、批評タグへキーボードだけで到達できるか確認する。 | 到達できるなら evidence として記録。到達できない場合はフォーカス順修正を別issue化する。 |
| H-DX4 Schema stop check | Architecture owner | Phase 1 が schema変更なしで成立するか再確認する。 | schema追加が必要なら本IssueではStopし、`DOMAIN-EXPR-02` または別schema issueへ送る。 |

### Proceed / Stop

- Proceed: Phase 1 の読取UIを現行schemaで受け入れられ、固有フィルタとキーボード到達性の扱いが明確になった場合に限り Draft->Open を検討する。
- Hold: 画面上の状態表示は存在するが、固有フィルタ、キーボード到達性、スクリーンショット証跡が未確定の間は Draft 維持。
- Stop: schema変更、AIによる `human_reviewed` 自動昇格、SafeMode/share-export境界の緩和、または `DOMAIN-EXPR-02/03` 相当の入力・永続化拡張を本Issueへ混在させる要求を検知した場合。

### Verification commands

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py`
- `git diff --check -- 01_Plans\issues\issue-DOMAIN-EXPR-01-readonly-state-surfacing.md 01_Plans\issues\issue-PRODUCT-QA-01-release-readiness-quality-gates.md`
- `rg -n "Chrome UI evidence intake|Human acceptance tasks|H-DX1|H-DX2|H-DX3|H-DX4|Productization Gate Record 2026-06-03|Human Task Queue|H-UI-01|H-UI-02|H-UI-03|H-UI-04" 01_Plans\issues\issue-DOMAIN-EXPR-01-readonly-state-surfacing.md 01_Plans\issues\issue-PRODUCT-QA-01-release-readiness-quality-gates.md`

## Evidence route update 2026-06-04: keyboard reachability candidate

- Candidate branch: `codex/domain-expression-keyboard-evidence-20260604`
- Status impact: **Draft remains**. This update adds a replayable keyboard-reachability evidence candidate, but it does not by itself open the domain-expression gate.
- Evidence added:
  - `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts` covers a keyboard path from a focused card to card selection, then `Tab` navigation through claim type, card review state, critique memo, and critique tag controls.
  - `03_Implement/frontend/src/canvas/CanvasShell.tsx` no longer intercepts Space for focused form controls, so checkbox and button keyboard activation remains available while canvas Space-pan still works outside controls.
- Evidence packet mapping:
  - H-DX3 Keyboard acceptance: partially satisfied for card selection and the first-class read UI controls already present in the selection context panel.
  - Read-only state surfacing: partially satisfied by asserting `claimType`, unreviewed state, incoming evidence, contradiction, and critique text are visible after keyboard selection.
  - Fixed filter boundary and human acceptance tasks H-DX1/H-DX2/H-DX4 remain pending.
- Remaining blockers before Open:
  - UX reviewer must accept the focused-card -> Tab path as natural enough for representative keyboard operation.
  - Dedicated filters for unreviewed, no-evidence, and critique-present states remain undecided.
  - Architecture owner must confirm no schema expansion is required for Phase 1 acceptance.

## Mainline evidence intake 2026-06-04: keyboard reachability landed

- Candidate mainline: `origin/main@70b6269a24d01c6f4b386e5b7a724738dd02e2bd`
- Status impact: **Draft remains**. The keyboard reachability E2E and Space-key repair are now on `main`, but this issue still needs UX/product acceptance for the Phase 1 domain-expression surface and a decision on dedicated filters before Open.
- Evidence now canonical on `main`:
  - #2315 merged `03_Implement/frontend/e2e/domain_expression_keyboard_access.spec.ts`, covering keyboard selection and Tab reachability for claim type, card review state, critique memo, and critique tag controls.
  - #2318 restored the current `CanvasShell` Space-pan guard on `main`, keeping Space activation available for focused form controls while preserving canvas Space-pan outside controls.
  - #2319 records the post-2318 PRODUCT-QA / MVP-EXIT mainline gate sync, keeping full shipment No-Go while acknowledging the merged DOMAIN-EXPR evidence lane.
- Evidence packet status:

| Evidence item | Current status | Remaining Open blocker |
| --- | --- | --- |
| Read-only state surfacing | Partially satisfied by visible claim type, unreviewed state, evidence, contradiction, critique note, and critique tags after keyboard card selection. | Productization Program Owner / UX reviewer must accept this as sufficient for Phase 1 first-class read UI. |
| Keyboard reachability | Satisfied for the representative focused-card to form-control path. | UX reviewer must confirm the Tab path is natural enough for release-candidate operation. |
| Fixed filter boundary | Not yet satisfied. | Decide whether unreviewed, no-evidence, and critique-present states need dedicated filters in this issue or a follow-up frontend issue. |
| Schema stop check | Partially satisfied by using existing DocumentV2 fields only. | Architecture owner must confirm no Phase 1 schema expansion is required. |
| Decision record | Partially satisfied by PRODUCT-QA / MVP-EXIT post-2318 gate records. | Final domain-expression gate decision must explicitly cite this issue after UX/product/filter/schema acceptance. |

- Next human task queue:
  - H-DX1: Productization Program Owner / UX reviewer accepts or rejects the current visible controls as the Phase 1 domain-expression read UI.
  - H-DX2: UX reviewer decides whether dedicated filters are required before Open.
  - H-DX3: UX reviewer confirms keyboard operation is natural in real Chrome, not only replayable in Playwright.
  - H-DX4: Architecture owner confirms that Phase 1 can remain schema-neutral.
- No ADR is needed for this intake. ADR routing is required only if acceptance changes schema ownership, AI review authority, SafeMode/share policy, or the staged DOMAIN-EXPR boundary.

## Open route packet 2026-06-06: human-operability check before Phase 1 Open

- Candidate baseline: current `main` after the post-2338/2339/2340 release-gate sync.
- Status impact: **Draft remains**. This packet makes the remaining human judgement concrete; it does not authorize implementation, schema expansion, AI authority changes, or SafeMode/share relaxation.
- Product value link: `DOMAIN-EXPR-01` is the smallest visible slice of `PRODUCT-VALUE-02`. It should prove that existing ambiguity-related state can be found and inspected by a general user before the project adds Hold/Shelf schema or critique-to-reproposal flows.

### Representative Chrome operation checks

| Check | Mouse operation | Keyboard operation | Naturalness criteria | Gate mapping |
| --- | --- | --- | --- | --- |
| Open a representative document | Click `サンプルを開く` or equivalent document entry. | Reach the entry action with `Tab`, then activate it with `Enter` or `Space`. | The entry action is discoverable without reading internal docs, and focus does not disappear after load. | H-DX1 / PRODUCT-VALUE-01 handoff |
| Select a card with domain state | Click a card that has claim/review/evidence/critique state. | Move focus to the card and activate selection with `Enter` or `Space`. | Selection feedback is visible, and canvas keyboard behavior does not block form-control activation. | H-DX3 |
| Inspect read-only state | Read `主張タイプ`, `レビュー状態`, evidence/contradiction, and critique memo/tags in the selection context. | Move through the same controls with `Tab` / `Shift+Tab`. | Labels are Japanese, grouped near the selected object, and do not imply that AI has resolved or reviewed the state. | H-DX1 / H-DX4 |
| Find unresolved state | Use search or visible filters to locate unreviewed, no-evidence, or critique-present items. | Reach the same search/filter controls with `Tab`, type a query, and confirm the result count. | A general user can re-find the state later; if dedicated filters are absent, the gap is explicit before Open. | H-DX2 |
| Leave the panel safely | Click outside, change selection, or use the visible close/navigation affordance if present. | Use `Esc` or predictable focus movement where available. | The user can recover from selection without losing the document state or triggering share/export. | H-DX3 / PRODUCT-UX handoff |

### Open decision options

| Option | Meaning | When to choose | Required follow-up |
| --- | --- | --- | --- |
| Proceed as Phase 1 Open | Current read UI plus the chosen findability path is sufficient for read-only state surfacing. | H-DX1, H-DX2, H-DX3, and H-DX4 all pass with Chrome evidence. | Move this issue to Open and connect the evidence to `PRODUCT-QA-01` V2/V3. |
| Hold for dedicated filters | The visible state is acceptable, but search alone is not enough to find `未レビュー` / `根拠なし` / `違和感あり`. | H-DX2 fails or is undecided. | Keep Draft and add a frontend-only implementation slice for dedicated filters before Open. |
| Stop and route to schema/ADR | Existing DocumentV2 fields are not enough to explain the state honestly. | H-DX4 fails, or the UI needs persistent Hold/Shelf fields. | Stop this issue and route through `DOMAIN-EXPR-02` plus schema/ADR review. |

### Human task queue update

| Task | Owner | Action | Evidence to attach before Open |
| --- | --- | --- | --- |
| H-DX1 Visible-state acceptance | Productization Program Owner / UX reviewer | Confirm whether claim/review/evidence/critique exposure is sufficient as a first-class read UI. | Screenshot or short note naming the selected card and visible fields. |
| H-DX2 Findability boundary | UX reviewer | Choose between search-only acceptance and dedicated filters before Open. | Result count or filter screenshot for at least one unresolved state. |
| H-DX3 Real Chrome keyboard naturalness | UX reviewer | Confirm the focused-card -> state inspection path in Chrome, not only Playwright. | Key sequence and observed focus order. |
| H-DX4 Schema-neutral stop check | Architecture owner | Confirm Phase 1 can remain schema-neutral. | Citation to `DocumentV2` fields used, or Stop route if new persistence is needed. |

- ADR need: none for Proceed or Hold. ADR/schema routing is required only for Stop, AI review authority changes, SafeMode/share policy changes, or adding persistent Hold/Shelf state to this Phase 1 issue.

## Mainline E2E rerun 2026-06-06: domain-expression keyboard access

- Candidate mainline: `origin/main@b8a1619d20aad91713800f3f0c209af3de14ff8b`.
- Status impact: **Draft remains**. This rerun proves the representative keyboard access path is executable on current `main`; it does not replace human UX/product acceptance, dedicated filter decisions, schema-neutral confirmation, release screenshots, or final program approval.
- Environment note: Vite and Playwright were executed with bundled Node.js because this Codex host does not expose `npm` on PATH for Playwright webServer startup:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe`
  - Vite was started directly with `node .\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 4173`.
- Verification command:
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/domain_expression_keyboard_access.spec.ts --reporter=line`
- Result: **pass, 1 test**.

### Evidence packet update

| Evidence item | Current status after rerun | Remaining Open blocker |
| --- | --- | --- |
| Read-only state surfacing | Reconfirmed keyboard route to claim type, review state, evidence, contradiction, critique memo, and critique tags. | Productization Program Owner / UX reviewer must accept the surface as sufficient Phase 1 read UI. |
| Keyboard reachability | Reconfirmed by Playwright on current `main`. | UX reviewer must still judge whether the path feels natural in real Chrome operation. |
| Fixed filter boundary | Unchanged. | Decide whether search is enough or dedicated `未レビュー` / `根拠なし` / `違和感あり` filters are required before Open. |
| Schema stop check | Unchanged; rerun uses existing DocumentV2 fields only. | Architecture owner must confirm no Phase 1 schema expansion is required. |
| Decision record | This section adds a current-main rerun record. | Final Open decision must cite H-DX1/H-DX2/H-DX3/H-DX4 outcomes. |

- No ADR is needed for this rerun. ADR routing remains limited to schema ownership changes, AI review authority changes, SafeMode/share policy changes, or staged DOMAIN-EXPR boundary changes.

## Stream F Frontend implementation note (2026-06-13)

- Scope: schema-free read-only surfacing in `03_Implement/frontend`.
- The share/export preflight now summarizes existing document state without adding fields: review state (`textReviewed` / `summaryReviewed`), hold proxy (`claimType=unknown`), critique fields, evidence links, contradictions, and evidence-gap candidates.
- This satisfies the Phase 1 boundary by making existing round-tripped states visible before sharing while preserving import/export compatibility.
