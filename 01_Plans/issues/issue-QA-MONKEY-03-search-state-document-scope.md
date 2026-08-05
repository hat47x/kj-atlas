# Issue Draft: QA-MONKEY-03 Search state document scope

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend`
- Related Backlog: `QA-MONKEY-03`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `03_Implement/frontend/src/App.tsx`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-03
- RequirementStatement: Search query and hide-non-matches state must not leak across document boundaries.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=sample document open / 操作=enter a no-match query, enable hide non-matches, create or open another document / 期待結果=search field is cleared and new document content is visible / 除外=within-document search continuity.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A

## 1) 課題 / Problem statement

- Monkey test entered a no-match search term and enabled `非一致を非表示`.
- Creating a new document retained the old search term, hiding the new document content.
- This made a fresh document appear empty or broken.

## 2) 背景 / Context

- Search state was app-level UI state.
- Document changes reset selection and draft state, but search and hide-non-matches were not reset.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Fresh document work should be immediately readable.
- 安全（THREAT_MODEL / SafeMode）: No direct safety impact.
- 企業・行政要件（enterprise_architecture）: Reduces operator confusion in repeated review sessions.
- 後方互換（schemas）: UI-only; no persistence or schema change.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend.
- 変更の最小単位: Reset search query, hide-non-matches, and match index when `activeDocumentId` changes.
- 非目標: Introducing per-document persisted search history.

## 5) 受入条件 / Acceptance criteria

- [x] New/Open document clears the search field.
- [x] Hide-non-matches no longer hides another document unexpectedly.
- [x] Within-document search behavior remains unchanged.
- [x] Browser smoke verifies the reset.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Add document-boundary reset effect.
- [x] T2 Verify browser search reset.
- [x] T3 Re-run frontend tests.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test`
  - Browser smoke: search no-match, hide non-matches, click `New`.
- 期待結果:
  - Search value becomes empty and `新しいカード` is visible.
- 未実施時の理由・代替検証:
  - N/A.

## 8) 代替案 / Alternatives considered

- 代替案A: Persist search per document. Rejected as larger UX design work.
- 代替案B: Keep current global search. Rejected because it creates false-empty documents.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Users lose a cross-document search term when switching documents.
- 影響範囲: Search UI state only.
- ロールバック手順: Remove the `activeDocumentId` reset effect.

## 10) Additional context

- ADR化が必要になる条件: Search state persistence becomes a product-level workflow decision.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
