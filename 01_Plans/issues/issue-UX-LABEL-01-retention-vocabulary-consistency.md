# Issue: UX-LABEL-01 Retention Vocabulary Consistency

- Type: UX / Content design
- Status: Done
- Source Issue: UX-WORKFLOW-01
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/App.tsx`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
- Expected verification level: unit + E2E content assertions

## Problem

The hold and critique workflow now has a visible path, but its labels vary by surface:

- The bulk bar uses `Toggle hold` and `Toggle feels-off`.
- The side panel uses `Hold state` and `Critique note`.
- Keyboard help uses `Toggle critique quick-flag`.
- Japanese labels mix `違和感`, `違和感クイックフラグ`, and `保留を切り替え`.

The behavior is valid, but users must translate between action wording, state wording, and internal implementation wording. `quick-flag` / `フラグ` is especially implementation-oriented for a general user-facing surface.

## Expected Behavior

- A small canonical vocabulary is used consistently for hold state, critique/reason notes, and the action that changes them.
- Action labels describe what the user can do; state labels describe what is currently stored.
- General user-facing copy does not expose `quick flag` or equivalent implementation language.
- English and Japanese labels preserve the same distinction between a marker, a saved reason, and a review state.

## Canonical Vocabulary

| Meaning | English | Japanese | Used for |
| --- | --- | --- | --- |
| Stored retention state | Hold state | 保留状態 | Card inspector, status copy, history copy |
| Retention action | Change hold state | 保留状態を変更 | Bulk bar, command palette, shortcut help |
| Stored human context | Critique note | 違和感メモ | Selection panel, legend, status copy |
| Lightweight marker | Critique mark | 違和感マーク | Bulk bar, card marker, shortcut help |
| Human explanation | Reason | 理由 | Bulk reason editor and saved note |

## Acceptance Criteria

- [x] A vocabulary table maps bulk bar, side panel, command palette, shortcut help, legend, status messages, and history messages.
- [x] The same canonical terms are used in English and Japanese across the mapped surfaces.
- [x] The keyboard help explains the result of `H`/`U` in user terms without exposing implementation vocabulary.
- [x] Unit catalog checks and one English/Japanese E2E assertion cover the changed labels.

## Validation Plan

- Review the rendered bulk bar, card inspector, shortcut help, and command palette in both locales.
- Run catalog integrity and untranslated-key inventory tests.
- Extend the hold/reason E2E to assert the canonical labels in both locales.

## Implementation Notes

- 2026-07-10: standardized the user-facing vocabulary to `Hold state / 保留状態`, `Critique note / 違和感メモ`, `critique mark / 違和感マーク`, and `reason / 理由`. Removed `quick-flag` and `feels-off` from general action and shortcut copy.
- Updated the affected English E2E expectations and corrected the existing Canvas legend heading assertion drift tracked in `issue-DX-E2E-02-canvas-legend-heading-drift.md`.
- Verification: 32 UI regression tests, catalog/inventory tests, and 16 Playwright E2E tests passed.

## ADR Impact

No new ADR is required while this remains a terminology and content-design correction. Create an ADR only if the project decides to rename the domain concept `Critique` itself or merge it with `Reason` in the data model.
