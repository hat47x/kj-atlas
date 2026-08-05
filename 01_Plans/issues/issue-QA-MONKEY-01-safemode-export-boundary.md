# Issue Draft: QA-MONKEY-01 SafeMode export boundary regression

- Type: Security / Bug
- Status: Done
- Source Issue: N/A
- Priority: P0
- Owner: TBD
- Scope: `03_Implement/frontend`
- Related Backlog: `QA-MONKEY-01`
- Related ADR/Spec: `AGENTS.md`, `THREAT_MODEL.md`, `02_Architecture/architecture.md`, `04_Documentation/e2e_testing.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: QA-MONKEY-01
- RequirementStatement: Explore preset and share/export controls must not relax SafeMode default ON or expose unreviewed drafts while SafeMode is ON.
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=frontend dev server + SQLite API / 操作=Open app, choose Explore, open share/export panel / 期待結果=SafeMode remains ON and "include unreviewed drafts" is not available while SafeMode is ON / 除外=SafeMode OFF explicit local review workflow.
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- Monkey test found the first screen and Explore preset could show `セーフモード: OFF`.
- Share/export panel exposed `未レビューのドラフトを含める` while SafeMode was ON.
- This conflicted with the project rule that SafeMode default ON and share/export leakage prevention are non-regression boundaries.

## 2) 背景 / Context

- `AGENTS.md` marks SafeMode default ON and leak prevention as the highest-priority safety rule.
- `THREAT_MODEL.md` and `02_Architecture/architecture.md` keep share/export redaction as a safety boundary.
- `04_Documentation/e2e_testing.md` requires no additional share/export exposure while SafeMode is ON.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: Users must be able to externalize cognition without accidental disclosure.
- 安全（THREAT_MODEL / SafeMode）: P0 because this directly weakens SafeMode and share/export guarantees.
- 企業・行政要件（enterprise_architecture）: SafeMode must remain enforceable under enterprise/public usage.
- 後方互換（schemas）: No schema change; behavior is restored to the documented contract.

## 4) 提案する解決策 / Proposed solution

- 変更対象: Frontend.
- 変更の最小単位: Keep default Explore inside SafeMode, hide include-unreviewed export control while SafeMode is ON, and default abstract-map export to excluding unreviewed drafts.
- 非目標: Redesigning all share/export flows or changing persisted document schema.

## 5) 受入条件 / Acceptance criteria

- [x] Explore preset keeps `safeMode: true`.
- [x] SafeMode ON share/export UI does not expose the include-unreviewed-drafts toggle.
- [x] Abstract map export excludes unreviewed drafts by default.
- [x] Frontend unit tests and browser smoke confirm SafeMode ON after opening and choosing Explore.
- [x] `GoNoGoGate` is Required and SafeMode/share-export impact is explicit.

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Update default Explore view preset to keep SafeMode ON.
- [x] T2 Make include-unreviewed export opt-in unavailable while SafeMode is ON.
- [x] T3 Default abstract map export to excluding unreviewed summary drafts.
- [x] T4 Add regression tests.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test`
  - Browser smoke: load `http://127.0.0.1:4173/`, click `Explore`, open share/export.
- 期待結果:
  - Typecheck passes.
  - All frontend tests pass.
  - Browser shows `セーフモード: ON`, no `セーフモード: OFF`, and no `未レビューのドラフトを含める` while SafeMode is ON.
- 未実施時の理由・代替検証:
  - N/A; executed in SQLite fallback environment.

## 8) 代替案 / Alternatives considered

- 代替案A: Add a new ADR to allow explicit unreviewed export under SafeMode ON. Rejected because existing safety specs already prohibit the regression.
- 代替案B: Keep UI visible but disabled. Rejected because it keeps a confusing affordance inside the safe path.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: Users expecting unsafe draft export from SafeMode ON need to switch SafeMode OFF explicitly.
- 影響範囲: Frontend view presets and abstract map export.
- ロールバック手順: Revert the frontend changes in `presets.ts`, `SharePanel.tsx`, and `abstract_map_export.ts`.

## 10) Additional context

- ADR化が必要になる条件: SafeMode ONで未レビュー内容を明示操作により露出可能にする方針へ変更する場合は、新規ADRでトレードオフを固定する。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
