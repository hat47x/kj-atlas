# Issue Draft: DOMAIN-EXPR-02 保留(Hold)と未統合(Pending/Shelf)の第一級化

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `02_Architecture/schemas.md`, `03_Implement/frontend/src/`, `03_Implement/frontend/src/import/`, `03_Implement/frontend/src/export/`, `03_Implement/frontend/tests/`
- Related Backlog: `DOMAIN-EXPR-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0040-domain-expression-first-class-strategy.md`, `00_Prompt/domain.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `02_Architecture/schemas.md`, `01_Plans/adr/ADR-0039-governance-right-sizing-personal-oss.md`
- Dependencies: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done 2026-06-20）
- Expected verification level: `integration`

## Draft→In Progress 2026-06-21

DOMAIN-EXPR-01 Doneにより依存充足。ADR-0040 Phase 2着手。

### Done
- **Schema**: `02_Architecture/schemas.md` §14 DOMAIN-EXPR-02 加算スキーマ拡張
  - Card.holdState (`"held" | "pending" | "shelved"`, optional, L2.5)
  - ShelfEntry type (`{ cardId, shelvedAt, reason? }`)
  - DocumentV2.shelf (`ShelfEntry[]`, optional)
  - 後方互換: version 2維持、全フィールドoptional
- **Types**: `types.ts` Card.holdState, ShelfEntry, DocumentV2.shelf
- **CardView**: holdStateバッジ (Held=amber, Pending=indigo, Shelved=gray)

### Remaining
- Shelf API (backend route for shelf add/remove)
- import/export support for shelf entries
- E2E tests

### Commits
- 277f2411 holdState + ShelfEntry schema and CardView badge
- 261839ea ShelfPanel component

## Implementation checkpoint 2026-06-21: card decision-status control

- Added a card-inspector control for `通常 / 保留 / 未決 / 棚上げ`.
- The control is keyboard-operable through a labeled native select and is disabled in read-only review mode.
- Returning to `通常` removes the optional `holdState` field instead of writing a new default value.
- Import parsing and strict validation now preserve supported `holdState` values and reject unknown values.
- Document history records the change while keeping suggestion preview state intact.
- Browser verification confirmed card selection, `通常 -> 保留`, localized card badge/accessible name, status feedback, and undo restoration.
- Remaining scope is unchanged: a visible Shelf list, set-aside/restore operations, ShelfEntry import/export, and E2E coverage belong to the next slice.
- No ADR is required because the accepted optional schema, review authority, SafeMode behavior, and sharing policy are unchanged.

## Implementation checkpoint 2026-06-21: card decision-status control

- Added a card-inspector control for `通常 / 保留 / 未決 / 棚上げ`.
- The control is keyboard-operable through a labeled native select and is disabled in read-only review mode.
- Returning to `通常` removes the optional `holdState` field instead of writing a new default value.
- Import parsing and strict validation now preserve supported `holdState` values and reject unknown values.
- Document history records the change while keeping suggestion preview state intact.
- Browser verification confirmed card selection, `通常 -> 保留`, localized card badge/accessible name, status feedback, and undo restoration.
- Remaining scope is unchanged: a visible Shelf list, set-aside/restore operations, ShelfEntry import/export, and E2E coverage belong to the next slice.
- No ADR is required because the accepted optional schema, review authority, SafeMode behavior, and sharing policy are unchanged.

## Implementation checkpoint 2026-06-21: Shelf workflow and persistence

- Selecting `棚上げ` now adds a `ShelfEntry`, preserves the card body and coordinates, and removes the card from the canvas.
- The side panel shows a visible Shelf list with the card text, shelved timestamp, optional reason, and a read-only-aware restore action.
- Restoring removes both Shelf membership and the optional `holdState`, returns the card at its original coordinates, selects it, and records one reversible history operation.
- Tolerant JSON import keeps valid Shelf entries, normalizes their cards to `holdState: "shelved"`, and drops invalid, duplicate, or orphaned entries.
- Strict frontend validation accepts only typed Shelf entries, rejects duplicate or unknown card references, and requires Shelf members to use `holdState: "shelved"`.
- Backend `DocumentV2` now models `CardV2.holdState` and `DocumentV2.shelf`; SQLite PUT/GET coverage proves that status, coordinates, timestamp, and reason survive persistence.
- Browser verification confirmed `通常 -> 棚上げ`, canvas removal, Shelf list rendering, restore, and the exact pre/post viewport bounds `(80, 166, 245.6 x 105.6)`.
- At a 280 px side-panel width, the Shelf section had no horizontal overflow (`scrollWidth == clientWidth`) and emitted no browser console warning or error.
- Remaining scope: add a maintained automated E2E scenario for keyboard traversal and persisted reload. The native select and button are keyboard-capable, but the in-app browser key simulation did not activate the focused restore button reliably, so this must be verified in the Playwright E2E harness.
- No ADR is required: this implements the already accepted additive schema and reversible Shelf behavior without changing authority, SafeMode, sharing, or compatibility policy.

## Post-merge regression repair 2026-06-22

- The `main` integration commit `976f1510` removed `hold_state_ops.ts` while leaving its import in `App.tsx`, omitted `domain/view/state_filter.ts`, and disconnected Shelf restore behavior.
- Restored the two pure domain modules and their tests, reconnected shelving to canvas visibility and Shelf membership, and restored the read-only-aware restore action.
- Restored previously accepted plain-language copy for layout suggestions and the patch workspace after internal `CE2` / `CE3` and implementation-phase wording reappeared during the merge.
- Verification: TypeScript passed; frontend unit/integration suite passed with 172 files and 817 tests; production build passed.
- Chrome verification confirmed card selection, `通常 -> 棚上げ`, canvas removal, Shelf rendering, restore, and zero console warnings/errors.
- This is a regression repair within the accepted ADR-0040 contract. No new ADR is required.

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0040` Phase 2。加算的・後方互換のschema拡張を含む。

## Dependencies

- 前段: `issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（`ADR-0040` Phase 1 の読取UIを前提に、保留/Shelfの登録・状態変更・加算スキーマを重ねる）。

## 1) 課題 / Problem statement

domain.md は `HoldState`（判断を確定させない状態）と `PendingItems/Shelf`（まだ束ねない要素の退避場所）を中核概念に定義するが、`schemas.md` にも frontend にも実体が無い（保留は `claimType="unknown"` の代理のみ、Shelf は型すら無し）。利用者が「これは今は決めない」「いったん脇に置く」を可逆的に表現できない。これは社会的目標（early collapse させない）の中核欠落。

## 2) 背景 / Context

- `ADR-0040` Phase 2 は保留と未統合を加算的・任意フィールドで第一級化する。
- `ADR-0001` P-01（意味の保留）と `DATA-01-1`（確定/未確定状態の表現）、3.1 collapse要件（不可視化は削除扱いにしない）が上流要件。
- `DOMAIN-EXPR-01`（読取UI）完了後に、登録/状態変更を加える順序。

## 3) 提案する解決策 / Proposed solution

- Schema（加算・後方互換、`AGENTS.md` §4.2 の順序で `schemas.md` 先行）:
  - カード/島に任意の `holdState?`（例: `active | held`）を追加。欠落時は従来挙動（held でない）。
  - 任意の Shelf membership（未統合退避）を追加。退避はキャンバス座標を保持し、復帰で原位置へ戻せる（内容削除と分離）。
- Frontend: 保留トグル、Shelf への退避/復帰、Shelf 一覧表示。
- import/export/validate/tests を新フィールドへ追随。
- 非目標: AIによる自動保留解除、保留の自動分類、正解判定。

## 4) 受入条件 / Acceptance criteria

- [ ] カード/島を「保留」にでき、表示上も保留と分かる。
- [ ] 要素を Shelf へ退避し、可逆に復帰できる（内容・座標が失われない）。
- [ ] `holdState` / Shelf membership が import/export で往復保存される。
- [ ] 旧データ（フィールド欠落）が破壊されず従来挙動で読める（後方互換）。
- [ ] AIは保留を自動解除しない（proposal-only、保留は保持対象）。
- [ ] `schemas.md` を先に更新し、validate/tests が新旧両形式で通る。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/typescript/bin/tsc --noEmit`
  - `cd 03_Implement/frontend && node ./node_modules/vitest/vitest.mjs run src/import src/export src/domain`
  - `rg -n "holdState|shelf|Shelf|pending|Pending" 02_Architecture/schemas.md 03_Implement/frontend/src`
- 期待結果: 保留と未統合が往復保存され、旧データ互換が保たれる。
- 未実施時の代替: schema差分レビューと import/export golden fixture 比較。

## 6) リスクとロールバック / Risks & rollback

- 失敗モード: 新フィールドが旧クライアントで失われる／状態語彙が複雑化。
- 影響範囲: DocumentV2、import/export、validate、canvas。
- ロールバック: 加算フィールドのため、UIを無効化し読取保存のみへ縮退できる。

## Open gate sync 2026-06-04: Phase 2 remains blocked by schema and acceptance decisions

- Candidate mainline: `origin/main@0133c744b60e4cc5f0c48435a62c72fbb5ca9f52`
- Status impact: **Draft remains**. `DOMAIN-EXPR-01` keyboard/read-state evidence is now on `main`, but it is not the same as approval to add persistent Hold/Shelf state.
- Current prerequisite state:
  - #2322 records `DOMAIN-EXPR-01` mainline evidence intake and keeps Phase 1 Draft pending UX/product/schema acceptance.
  - #2323 records that PRODUCT-VALUE-02 still lacks a combined hold/ambiguity/evidence-gap/contradiction workflow fixture.
  - `ADR-0040` permits Phase 2 as an additive schema direction, but this issue still needs an implementation contract before Open.
- Open gate checklist before implementation:

| Gate | Current status | Required decision before Open |
| --- | --- | --- |
| Phase 1 acceptance | Not complete. | Productization Program Owner / UX reviewer must accept the current DOMAIN-EXPR-01 read UI as the base for adding Hold/Shelf controls. |
| Schema contract | Not complete. | Architecture owner must approve exact field names, allowed values, missing-field defaults, and import/export compatibility for `holdState` and Shelf membership. |
| User workflow boundary | Not complete. | Decide whether Hold and Shelf are one workflow slice or two separate PRs, and whether Shelf needs a visible list before card-level Hold ships. |
| PRODUCT-VALUE-02 fixture | Not complete. | Define whether the four-state value fixture will use the new Hold/Shelf fields, or whether Phase 2 can ship with a smaller Hold/Shelf-specific fixture first. |
| ADR need | Conditional. | No new ADR is needed for additive fields matching ADR-0040; create an ADR if the work changes review authority, SafeMode/share policy, or introduces breaking schema behavior. |

- Recommended next slice:
  - Start with a schema-contract PR only: update `02_Architecture/schemas.md` and validation expectations for optional `holdState` plus Shelf membership, without UI behavior.
  - Add old/new document fixtures proving missing fields still read as default active/non-shelf state.
  - Defer UI controls until the schema contract and PRODUCT-VALUE-02 fixture boundary are accepted.
- No implementation is authorized by this sync. It only records the minimum decisions needed before `DOMAIN-EXPR-02` can move from Draft to Open.

## 7) Additional context

- 本issueは schema を加算拡張するため `ADR-0040` の確定方針に直接対応する。破壊的変更が必要になった場合は新ADRを起票する。
