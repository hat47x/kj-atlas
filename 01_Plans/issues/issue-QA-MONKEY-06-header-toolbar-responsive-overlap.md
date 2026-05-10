# Issue Draft: QA-MONKEY-06 Header toolbar responsive overlap

- Type: Bug
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui`
- Related Backlog: `QA-MONKEY-06`
- Related ADR/Spec: `04_Documentation/e2e_testing.md`, `02_Architecture/architecture.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-06
- RequirementStatement: Header toolbar controls must remain readable and non-overlapping at the default desktop browser viewport.
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=1280x720 browser viewport / 操作=open app and open view/share controls / 期待結果=toolbar buttons do not wrap into vertical unreadable labels or occlude canvas/right panels / 除外=very narrow mobile layout, which should be handled by its own breakpoint spec.
- GoNoGoGate（Required / Optional / N/A）: N/A
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export labels must remain visible.
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- Monkey testing at the default browser size showed the header toolbar crowding.
- Some buttons wrapped into stacked vertical text and dropdown panels overlapped canvas/right-panel content.
- SafeMode/share labels became harder to read during ordinary exploration.

## 2) 背景 / Context

- The app has accumulated many header controls for view modes, search, share/export, and CE workflows.
- Current layout appears to rely on available horizontal space without a stable overflow strategy.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Repeated analysis work needs a scannable, low-friction control surface.
- 安全（THREAT_MODEL / SafeMode）: SafeMode and share/export status should not be visually obscured.
- 企業・行政要件（enterprise_architecture）: Operator workflows require predictable navigation.
- 後方互換（schemas）: UI layout only; no data contract change.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend header/layout components.
- 変更の最小単位: Introduce stable toolbar wrapping/overflow groups or responsive breakpoints that preserve readable labels and panel placement.
- 非目標: Redesigning the full product navigation IA.

## 5) 受入条件 / Acceptance criteria

- [ ] At 1280x720, toolbar labels are horizontal/readable and do not overlap adjacent controls.
- [ ] Open panels are positioned without covering essential status controls incoherently.
- [ ] SafeMode/share/export status remains visible and readable.
- [ ] Browser screenshot/e2e regression covers at least 1280x720 and one narrower breakpoint.
- [ ] No behavior changes to document data, SafeMode rules, or export output.

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 Identify the header/control containers causing wrap and overlap.
- [ ] T2 Add responsive grouping or overflow behavior.
- [ ] T3 Verify screenshots at 1280x720 and a narrower breakpoint.
- [ ] T4 Re-run frontend tests and browser smoke.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test`
  - Browser screenshot checks at 1280x720 and narrow breakpoint.
- 期待結果:
  - No vertical button text, no incoherent overlap, SafeMode/share labels readable.
- 未実施時の理由・代替検証:
  - Open issue; not fixed in the current monkey-test repair set because it requires layout design work.

## 8) 代替案 / Alternatives considered

- 代替案A: Shorten labels only. Rejected as insufficient for accumulated controls.
- 代替案B: Hide lower-priority controls entirely. Rejected unless paired with an explicit overflow/menu design.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Moving controls can disrupt existing keyboard/muscle-memory workflows.
- 影響範囲: Header toolbar and dropdown positioning.
- ロールバック手順: Revert layout grouping/overflow changes.

## 10) Additional context

- ADR化が必要になる条件: Product-level navigation or responsive strategy is redefined.

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
