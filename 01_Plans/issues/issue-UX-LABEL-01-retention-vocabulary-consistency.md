# Issue: UX-LABEL-01 Retention Vocabulary Consistency

- Type: UX / Content design
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
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

## Acceptance Criteria

- [ ] A vocabulary table maps bulk bar, side panel, command palette, shortcut help, legend, status messages, and history messages.
- [ ] The same canonical terms are used in English and Japanese across the mapped surfaces.
- [ ] The keyboard help explains the result of `H`/`U` in user terms without exposing implementation vocabulary.
- [ ] Unit catalog checks and one English/Japanese E2E assertion cover the changed labels.

## Validation Plan

- Review the rendered bulk bar, card inspector, shortcut help, and command palette in both locales.
- Run catalog integrity and untranslated-key inventory tests.
- Extend the hold/reason E2E to assert the canonical labels in both locales.

## ADR Impact

No new ADR is required while this remains a terminology and content-design correction. Create an ADR only if the project decides to rename the domain concept `Critique` itself or merge it with `Reason` in the data model.
