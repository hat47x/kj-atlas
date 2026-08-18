# Issue: UX-OPERABILITY-01 マウス/キーボード操作動線レビュー（仕様固定）

- Type: Planning
- Status: Done
- Priority: P1
- Owner: Stream C
- Execution: Ready
- Scope: `01_Plans/issues/issue-UX-OPERABILITY-01..05*.md`（docs + frontend ui）
- Related Backlog: `UX-OPERABILITY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`
- Expected verification level: `docs-check`

## Goal

UI 操作モデルを 4 分類（到達性 / フォーカススコープ / 段階的開示 / 閉じる・復帰）で仕様固定し、後続 Issue（02→03→04→05）の契約前提を統一する。

## Operation Flow Contract（Unified / Mock-first）

- Pointer contract:
  - `PointerSelect(targetId)` は `SelectionChanged(targetId)` を発火する。
- Keyboard contract:
  - `KeyboardSelect(targetId)` は `SelectionChanged(targetId)` を発火する。
- Focus contract:
  - `SelectionChanged(targetId)` 後、フォーカススコープは `selection-context` に遷移可能である。
- Panel contract:
  - `SelectionChanged(targetId)` は `ContextPanelRequested(targetId)` を後続へ通知する。

## AC (Acceptance Criteria)

- [x] 4分類の用語が ADR-0030 と一致している。
- [x] 固定順序 `01 → 02 → 03 → 04 → 05` が明記されている。
- [x] 後続 Issue が参照する統一契約（pointer / keyboard / focus / panel）を先行定義している。
- [x] 本 Issue は仕様のみで、実装コード変更を含まない。

## DoD

- [x] 後続 Issue 参照が有効で重複・矛盾がない。
- [x] 受入境界は E2E 観測可能な事実で記述されている。
- [x] 曖昧なアクセシビリティ要件が残る場合は `Execution: Hold` 条件を明示する。

## Phase Plan（Read → Contract → Execute/Verify）

- Phase 1 Read:
  - issue-UX-OPERABILITY-01..05 のメタ情報、AC、Validation plan を照合済み。
- Phase 2 Contract unify:
  - keyboard / pointer / focus / panel の4契約を基底契約として固定。
- Phase 3 Plan→Execute→Verify（max 3 self-heal）:
  - `docs-check-1`: 契約語彙の整合を検証。
  - `docs-check-2`: 依存順序の整合を検証。
  - `docs-check-3`: 回帰（用語・イベント・属性）を検証。
- Phase 4 Stopper:
  - 競合、前提崩れ、未定義依存（仕様参照先欠落）が発生した場合は `Execution: Hold` へ遷移。

## Validation plan

- `rg -n "Operation Flow Contract|PointerSelect|KeyboardSelect|SelectionChanged|ContextPanelRequested|01 → 02 → 03 → 04 → 05" 01_Plans/issues/issue-UX-OPERABILITY-0{1,2,3,4,5}*.md`
- `git diff -- 01_Plans/issues/issue-UX-OPERABILITY-01-pointer-keyboard-flow-review.md`

## Dependencies

- Blocks: `UX-OPERABILITY-02`
- Blocked by: `ADR-0030` Accepted

## Hold trigger

- `Execution: Hold` は、フォーカス可視性・読み上げ可能名・キーボード到達性のいずれかが未確定で E2E 観測条件へ落とせない場合に適用する。
- 解除条件は、未確定項目が ADR-0030 と整合した観測可能文（DOM属性またはイベント契約）として AC/DoD に反映されること。


## Implementation Notes

- `03_Implement/frontend/src/canvas/CardView.tsx` における keyboard 選択契約（`Enter/Space`, `aria-selected`, `data-focus="card"`）を回帰対象として固定。
- `03_Implement/frontend/src/ui/SidePanel.tsx` で `selection-context` / `advanced` の段階開示契約（`data-panel`, `data-panel-group`, `aria-expanded`）を実装・検証。
- `03_Implement/frontend/src/ui/SharePanel.tsx` と `03_Implement/frontend/src/App.tsx` の `Escape` 閉鎖 + フォーカス復帰契約を回帰対象として維持。

## Evidence Refresh 2026-06-06: current-main canvas and polygon operability rerun

- Candidate: `origin/main@7472004655500e3f737e1ef1abd22577a1f9a56b`.
- Reviewer: Codex.
- Scope: current-main browser automation rerun for pointer/keyboard canvas selection, selection-panel reachability, and polygon boundary editing. This is an evidence refresh only; it does not change runtime behavior, UI copy, SafeMode/share-export policy, issue status, or release authority.
- Local execution:
  - Bundled Node.js started Vite directly on `127.0.0.1:4173` because this Codex host did not expose `npm` on PATH.
  - `C:\Users\yhata\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe .\node_modules\playwright\cli.js test e2e/polygon_vertex_edit.spec.ts e2e/polygon_autofit_qa_boundary.spec.ts e2e/canvas_focus_order.spec.ts --reporter=line` -> pass, 6 tests.
- Covered user operations:
  - Card selection by keyboard `Enter`, `aria-selected` confirmation, and selection-context panel visibility at 960px width.
  - Tab traversal from canvas selection into selected-card and selected-island panel actions.
  - Island selection by keyboard activation and localized island editor label checks.
  - Polygon vertex drag with persisted point changes.
  - Polygon vertex keyboard nudge, Shift+Arrow larger nudge, and Delete removal.
  - Deterministic polygon export, self-intersecting import fallback, and self-intersection edit rejection.
- Human follow-ups:
  - Keep physical keyboard acceptance, screen-reader acceptance, and real Chrome visual review human-owned before release.
  - Keep broader advanced-panel traversal as sampled evidence rather than exhaustive proof unless UX scope expands.
