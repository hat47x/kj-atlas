# kj-atlas — Whole-System Architecture Coherence & Backlog Synthesis

Analysis date: 2026-07-23. Repo root: `C:/GIT/kj-atlas` (in sync with origin/main).
Scope read: 62 ADRs (`01_Plans/adr/ADR-0000..0061`), 252 issue memos (198 Done, **51 open** = 47 Draft + 2 Open + 2 In Progress), backend (`03_Implement/backend/src/kj_atlas_api/`), frontend (`03_Implement/frontend/src/`), doc linters (`01_Plans/docs_check.py`).

Method note: every claim below is grounded in a file read this session. Where I inferred a relationship from an issue's own `Related ADR/Spec` cross-reference rather than re-deriving it from code, I say so. Where I did not trace every code path, I hedge explicitly.

---

## Section 1 — ADR ↔ code conformance map (load-bearing invariants first)

### 1.1 Core Value Invariants (ADR-0041 / `core_value_guard.test.ts`)

ADR-0041 fixes 7 non-regression invariants (CVI-1..7) and mandates a **single cross-cutting guard test** (`03_Implement/frontend/src/domain/core_value_guard.test.ts`) that indexes existing coverage.

| CVI | Decision (ADR-0041:33-39) | Code status | Evidence |
| --- | --- | --- | --- |
| CVI-1 SafeMode default ON, no unreviewed text leaks on share/export | **VIOLATED (P0, live)** | Policy exists and is correct (`domain/policy/safe_mode.ts:17-51`) and is applied to every markdown bundle file, but `document.json` is emitted with only `resolveShareDocument()` applied — which strips `card.meta` but never redacts `card.text`/`island.summaryText`/`relationSummaries[].text` — at `export/bundle_export.ts:254` and `:313`. `safeMode` is computed (`:250`,`:309`) but never passed to `document.json`. Confirmed against issue-SEC-EXPORT-BUNDLE-01. |
| CVI-2 proposal-only, no auto-apply | Honored | Guarded by `domain/ce2_proposal_only.test.ts`, `domain/ce2_suggestion_candidates.test.ts` (indexed at `core_value_guard.test.ts:29-43`). |
| CVI-3 `human_reviewed` promotion human-only | Honored, actively enforced | `domain/hil_rs_apply.ts:10-29,57` — `hasReviewProtectedField()` rejects any rediff op that carries `reviewState`/`reviewed`/`reviewerRef`, so AI/worker cannot inject review state. |
| CVI-4 Consensus direct-write prohibited | Honored | CE0 contract tests indexed (`core_value_guard.test.ts:65-73`). |
| CVI-5 dryRun no side effects | Honored | Immutability asserted in `hil_rs_apply.test.ts` (indexed `:75-83`); `applyHilRsRediffPayload` clones the doc (`hil_rs_apply.ts:84`). |
| CVI-6 `KJ_ATLAS_LLM_PROVIDER=none` default | Honored | `settings.py:218-220` `default="none"`; `NoneProvider` exists (`llm/provider.py:166-168`). |
| CVI-7 Hold/Critique non-destructive | Honored | `hold_state_ops.test.ts`, critique-preserved assertion in `hil_rs_apply.test.ts` (indexed `:94-107`). |

**Structural weakness in the "single fort."** `core_value_guard.test.ts` verifies CVI coverage by reading test-file *source strings* (`readSource(...).toContain("blocks text exposure ...")`, lines 22-26 etc.), not by exercising behavior. That is why CVI-1 shows green while `document.json` leaks in production: the guard confirms the policy *unit test* mentions the right words, but never asserts that a real export bundle contains no secret. ADR-0041's promise — "a single red catches any regression of core value" (ADR-0041:50) — is not actually met for egress surfaces. This is the single most important conformance finding.

### 1.2 SaaS tenant boundary (ADR-0059) & session concurrency (ADR-0061)

Both ADRs are **Accepted with an explicit Implementation gate** (ADR-0059:105-114, ADR-0061:52-60) and both state Accepted ≠ SaaS-complete. Implementation is substantial and correctly gated, not yet finished (issue-SAAS-TENANT-01 is In Progress).

Honored / implemented:
- D5/D8 tenant guard: `access_control.py:449-469` `apply_tenant_boundary_guard` denies `tenant_context_missing`/`resource_tenant_missing`/`tenant_mismatch` before any PDP call; wired at `access_control.py:490-495`.
- Resource-path enforcement: `routes/docs.py:272-278` calls `resolve_access_decision(..., require_tenant_scope=True)`.
- Session-precondition (ADR-0061 D2 `tenantSessionVersion`): `tenant_session_precondition.py:33-72` validates the `KJ-Atlas-Tenant-Session-Version` header and rejects stale/missing versions; applied on 7 AI routes (`routes/ai.py:506..671`), `routes/ai_relations.py:121`, `routes/context.py:25`.
- Fail-closed SaaS startup (D8/D10): `trusted_saas_runtime.py:64-81,92-120` requires PostgreSQL + disabled JIT + `external_http` access control + `deny` fail-safe + external policy binding + external capability; single-tenant profile cannot enable SaaS adapters (`:180-183`). Preflight is wired into lifespan (`main.py:72-77`).

Gaps against the gate (drift = "gate not finished", not "violated"):
- ADR-0059 gate item 5 / ADR-0061 gate item 4 (cross-tenant + 2-tab stale **negative E2E matrix**) is **not done** → issue-QA-E2E-SAAS-01 ("TenantSession UI E2E coverage is zero").
- Status-code asymmetry for the same membership check (issue-SEC-HTTP-02) contradicts a uniform not-found/deny contract (ADR-0059:79).

### 1.3 Fail-closed vs the "opt-in safety" default

- **`require_tenant_scope` defaults to `False`** (`access_control.py:488`). Safe only because the document path remembers to pass `True` (`docs.py:276`). Routes that don't resolve a document resource rely on the session precondition instead. I did not trace every route to a resource-tenant match, so I flag the opt-in default as a **latent risk**, not a confirmed live cross-tenant hole.
- **`external_http` silently degrades to noop** (issue-SEC-CONFIG-01, P0, verified): `access_control.py:554-579,116-120` returns `NoopAccessControlAdapter` (always `allow=True`) when `adapter_name="external_http"` but the endpoint is unset — with **no log**. In the SaaS profile this is caught by `validate_for_saas()` (`trusted_saas_runtime.py:92-104`), but in `enterprise-production` (non-SaaS) an operator who intends external PDP enforcement gets unconditional allow. This directly contradicts `AGENTS.md`'s "access control fail-closed is the top safety boundary." Note the sibling resolvers (`document_policy_binding`, `tenant_capability`) already fail closed; only access_control and audit do not (confirmed by the issue against `settings.py:85-102`).

### 1.4 i18n parity — strongly honored

en/ja are at exact parity: 1721 keys each (`src/i18n/locales/{en,ja}.json`). Eleven guard tests enforce it, incl. `catalog_integrity.test.ts`, `key_consistency.test.ts`, `ui_hardcode_guard.test.ts`, `dynamic_key_coverage.test.ts`, `document_locale_invariance.test.ts`, `ui/i18n_equivalence.integration.test.ts`. This is the healthiest invariant in the repo. Residual drift is only at the *edges* (domain error codes, timestamps — see §2 FB-RM cluster), not the static catalog.

### 1.5 Fail-closed doc linters (ADR-0024) — honored

`01_Plans/docs_check.py:150` `raise SystemExit(main())`; `main()` returns 1 on failure (`:134,:140`). Single deterministic entrypoint over `docs_contract_checks.py` (ADR ID uniqueness, active-issue-memo validation, etc.). Fail-closed as intended.

### 1.6 Privileged-data lifecycle boundary (ADR-0035) — honored by absence

ADR-0035:24-35 forbids delete/archive/ownership-transfer/admin-content-viewing/retention as standard features. This is a *negative* invariant (features must be absent); no open issue flags a violation, and issue-MVP-EXIT-01 treats it as a release gate. Cannot be positively proven from a read, but no contradicting surface was found.

### 1.7 LLM provider observability & staged connection (ADR-0050 / ADR-0054) — not deeply audited

`llm/provider.py` carries call metadata (`fallback_to_none`, `disabled_reason`, `_new_metadata` at `:154-162`) consistent with ADR-0050's contract-fidelity intent, but I did not verify the full observability contract. EXT-CONN-02/03/04 and GENAI-GOV-01 are future-phase (ADR-0054 staging) and correctly still Draft — no drift, just unbuilt.

---

## Section 2 — Issue supersession / dedup graph (51 open, by theme)

IDs below were each opened and confirmed to exist this session.

**A. Missing-bounds / DoS-surface cluster (8) — one root cause.**
- issue-SEC-DOC-BOUND-01 (unbounded document/identity fields, P3) — **anchor**.
- issue-SEC-DOC-BOUND-02 (unbounded list fields in LLM prompts, P3) — extends 01 to prompt lists.
- issue-SEC-DOC-BOUND-03 (unbounded recursive `ContextQuery.constraints`, **P1**) — distinct failure mode (uncaught exception on deep nesting); highest severity of the cluster.
- issue-SEC-DOC-BOUND-04 (admin document-access list no pagination, P2).
- issue-SEC-DOC-BOUND-05 (merge-decision-logs no pagination, P2).
- issue-DOMAIN-CARD-TEXT-01 (no `max_length` on Card.text/Island.title/etc., P2) — **near-duplicate of SEC-DOC-BOUND-01**; both target the same absent bounds in `models.py`. Fold into 01.
- issue-DX-BACKEND-CE4-01 (CE4 audit tracker dict grows unbounded for process life, P3) — same "no bound" shape, memory axis.
- issue-FB-RM-UX-02 (agent-imported review list grows unbounded, P3) — frontend facet.
Verified root: `models.py` contains only **2** `max_length` references total (one being `RelationSummary.text` at `:495`); the audit/session plane is rigorously bounded (`audit.py` MAX_* constants, `access_control.py:32-37`) but the content plane is not.

**B. Audit-integrity cluster (3).** issue-SEC-AUDIT-DUP-01 (duplicate audit event on retry/double-click, P3), issue-SEC-AUDIT-LOG-01 (proposal rejection reason logged unmasked, P3), issue-DX-BACKEND-CE4-01 (also here) — all centered on `routes/docs.py` CE4 tracker (`docs.py:518`) + `audit.py`. SEC-AUDIT-DUP-01 explicitly cross-refs DX-BACKEND-CE4-01.

**C. Redaction / content-egress leak cluster (3) — spans front+back.** issue-SEC-EXPORT-BUNDLE-01 (document.json, **P0**), issue-SEC-VALIDATION-LEAK-01 (422 echoes raw rejected PII via `main.py:121-123`, P2), issue-SEC-AUDIT-LOG-01 (server log leak, P3). Unified theme: *unredacted content escapes a boundary that the product claims is protected.* Not duplicates (different surfaces) but should be fixed as one workstream.

**D. SaaS implementation-gate cluster (6).** issue-SAAS-TENANT-01 (umbrella, In Progress, P1) — the parent; the rest are sub-gaps: issue-QA-E2E-SAAS-01 (E2E gap), issue-SEC-HTTP-02 (status asymmetry), issue-SAAS-TENANT-FK-03 (case-insensitive index unused in `identity_binding.py`), issue-SAAS-TENANT-MIGRATION-01 (downgrade lacks data-safety guard), issue-DX-CI-PG-02 (PostgreSQL downgrade path never run in CI). All trace to ADR-0059/0061 gates.

**E. Production-hardening / fail-open cluster (3).** issue-SEC-CONFIG-01 (external_http→noop, **P0**), issue-SEC-HEADERS-01 (`/docs`,`/redoc`,`/openapi.json` always exposed — verified `main.py:96` has no profile gating, P2), issue-SEC-RATE-LIMIT-01 (no rate-limit middleware — verified `main.py` has only `require_api_key` + `add_security_headers`, P2).

**F. HTTP status hygiene (2).** issue-SEC-HTTP-01 (blank-field 400 vs 422), issue-SEC-HTTP-02 (403 vs 404 asymmetry). Same "inconsistent status contract" theme; SEC-HTTP-02 also belongs to cluster D.

**G. Edge i18n/locale cluster (4).** issue-FB-RM-I18N-05 (domain error codes not i18n-mapped), issue-FB-RM-I18N-06 (dead legacy key coupled to a test), issue-FB-RM-UX-01 (locale stale-closure in `App.tsx`), issue-FB-RM-UX-03 (raw ISO timestamps in SharePanel/NarrativesPanel). Residual gaps around the otherwise-strong i18n core (§1.4).

**H. UI resilience / a11y cluster (5).** issue-UI-RESILIENCE-01 (no React error boundary anywhere, P2), issue-UI-QUALITY-A11Y-06/07/08 (live-region, focus-return, focus-trap, P3), issue-UI-CANVAS-01 (window-listener peek can leak/stick, P2). Under ADR-0044 (UI quality baseline) / ADR-0052 (canvas+menu ARIA).

**I. Value / social-realization planning cluster (7) — heavy overlap, consolidation candidate.** issue-VALUE-MEASURE-01 (harness, P1), issue-VALUE-MEASURE-02 (two-axis scorecard, P1), issue-VR-ROADMAP-01 (phase baseline, P1), issue-SOCIAL-DIFFUSION-01 (multi-reviewer reproducibility), -02 (consensus revisability), -03 (evidence-anchored safe diffusion), -04 (non-surveillance signals) (all P2). These seven are largely docs-scope and all elaborate the same ADR-0032/0036/0037/0038 roadmap; they read as one program split into seven memos.

**J. External-connection / GenAI future phase (4).** issue-EXT-CONN-02/03/04 (ADR-0054 stages 2/3 + role B), issue-GENAI-GOV-01 (AI-lane gate, P1). Correctly gated/unbuilt; not stale.

**K. Domain features / correctness (4).** issue-DOMAIN-W-ITERATION-01 (W-type cumulative KJ, In Progress, Must/P1), issue-DOMAIN-VISUAL-CUE-01 (representative visual cues, Open, P2 — prototype exists at `domain/representative_visual_cue_prototype.ts`), issue-DOMAIN-GEOM-01 (polygon vertex index-key, latent, P3), issue-HIL-RS-03 (add-op loses id/text, **P1 bug**).

**L. Umbrella.** issue-MVP-EXIT-01 (productization readiness, P0) — spans everything; effectively the release-gate tracker referencing ADR-0035 and the QA/release issues.

Stale check: I found **no** open issue already fully fixed in code. SEC-AUDIT-DUP-01 was just filed (commit `915fe4ad`/#2690), so it is current, not stale. The strongest *dedup* action is folding DOMAIN-CARD-TEXT-01 into SEC-DOC-BOUND-01, and consolidating cluster I (7→1 sequenced plan).

---

## Section 3 — Systemic root-cause patterns (highest-value output)

**P1. Safety is opt-in per surface, not centrally enforced — the dominant pattern.**
The same shape recurs: a protection exists as a *policy object* or *unit test*, but each new surface must remember to call it, and nothing structurally fails when one forgets.
- SafeMode redaction is applied file-by-file in `bundle_export.ts`; `document.json` was forgotten → SEC-EXPORT-BUNDLE-01 (P0).
- The CVI-1 guard checks *source strings*, not egress behavior (`core_value_guard.test.ts:22-26`), so it cannot catch a forgotten surface.
- 422 handler and server logs redact nothing → SEC-VALIDATION-LEAK-01, SEC-AUDIT-LOG-01.
- `require_tenant_scope` defaults `False` (`access_control.py:488`); safe only by caller discipline.
- `external_http`→noop degrades silently (`access_control.py:579`) → SEC-CONFIG-01 (P0).
Members: SEC-EXPORT-BUNDLE-01, SEC-VALIDATION-LEAK-01, SEC-AUDIT-LOG-01, SEC-CONFIG-01 (+ the guard weakness). *Fix the pattern, not the instances:* make the boundary the only path (single redacting serializer; behavioral CVI test; fail-closed defaults).

**P2. No bounds discipline on the content plane (while the audit/session plane is disciplined).**
`models.py` has 2 `max_length` refs; content fields, list endpoints, and one recursive shape are unbounded. This is a single missing convention, not eight bugs.
Members: SEC-DOC-BOUND-01/02/03/04/05, DOMAIN-CARD-TEXT-01, DX-BACKEND-CE4-01, FB-RM-UX-02.

**P3. SaaS gate is far along but unverified end-to-end.**
The hard parts (tenant guard, session-version precondition, fail-closed startup, RLS migrations) are built and correctly gated; the *proof* (negative cross-tenant/stale-tab E2E matrix) and the last hardening (status contract, CI downgrade coverage, index use) are missing.
Members: SAAS-TENANT-01, QA-E2E-SAAS-01, SEC-HTTP-02, SAAS-TENANT-FK-03, SAAS-TENANT-MIGRATION-01, DX-CI-PG-02.

**P4. Decision corpus outpaces execution (ADR-0047's own concern, now observable).**
62 ADRs; 198 Done vs 51 open memos; and a 7-issue value/social-diffusion planning cluster that is mutually redundant and docs-only. ADR-0047 ("ADR saturation and execution-first") explicitly names this; cluster I is the live symptom.
Members: VALUE-MEASURE-01/02, VR-ROADMAP-01, SOCIAL-DIFFUSION-01..04.

**P5. Strong core, weak edges (i18n + a11y).**
Core invariants (i18n parity, CVI proposal-only, tenant startup) are well-guarded, but their *edges* are not: dynamic/domain-error i18n, timestamp formatting, error boundaries, focus management.
Members: FB-RM-I18N-05/06, FB-RM-UX-01/03, UI-RESILIENCE-01, UI-QUALITY-A11Y-06/07/08, UI-CANVAS-01.

---

## Section 4 — Prioritized, dependency-ordered remediation roadmap

Ordered so prerequisites precede dependents. "Mechanical" = safe for a Sonnet/Opus-class executor; "Judgment" = needs human/product decision first.

1. **Close the SafeMode/redaction egress leaks and harden the guard (P0).**
   - 1a. Decide document.json handling — mask fields / exclude in SafeMode / reword the UI promise (`SharePanel` locked-contexts text). **Judgment**: `document.json` doubles as the round-trip import format, so masking can break owner re-import (verify `import/zip_import.ts`). Resolves SEC-EXPORT-BUNDLE-01.
   - 1b. Redact 422 responses (`main.py:121-123`) and audit-log reasons. **Mechanical.** Resolves SEC-VALIDATION-LEAK-01, SEC-AUDIT-LOG-01.
   - 1c. Upgrade `core_value_guard.test.ts` CVI-1 from source-string to behavioral: build a bundle containing a sentinel secret and assert **no** emitted file contains it. **Mechanical**, but do it after 1a fixes the leak. Strengthens ADR-0041. *This is the highest-leverage single item — it converts P1 from a class of latent leaks into a guarded invariant.*

2. **Resolve the fail-open config policy + enterprise-production hardening (P0/P2).**
   - 2a. SEC-CONFIG-01: decide fail-closed-`ValueError` vs warn-on-noop; existing tests pin the current noop fallback, so this is **Judgment** (and may need an ADR). Then implement + update `test_access_control_external_http_adapter.py`.
   - 2b. SEC-HEADERS-01 (gate `/docs` etc. by runtime profile in `main.py:96`) and SEC-RATE-LIMIT-01 (add rate-limit middleware) — **Mechanical** once 2a's policy stance is set.

3. **Establish one content-plane bounds convention, then apply it (P1 first).**
   - 3a. SEC-DOC-BOUND-03 (recursive constraints) first — it can crash the server; **Mechanical** (depth/size cap in `models_context.py`).
   - 3b. Define a `MAX_*` convention + a guard test asserting every content field and list endpoint is bounded, then apply across `models.py`/`models_ai.py` and add pagination to admin/merge-log GETs. **Mostly mechanical** after the convention (which is one small **Judgment** call on limits). Resolves SEC-DOC-BOUND-01/02/04/05, DOMAIN-CARD-TEXT-01 (fold in), DX-BACKEND-CE4-01, FB-RM-UX-02.

4. **Finish the SaaS gate verification matrix (P1).**
   - Cross-tenant + 2-tab stale negative E2E (ADR-0059 gate 5, ADR-0061 gate 4). **Judgment/coordination** (test design), then execute. Unblocks SAAS-TENANT-01, resolves QA-E2E-SAAS-01. Sub-items SEC-HTTP-02, SAAS-TENANT-FK-03, SAAS-TENANT-MIGRATION-01, DX-CI-PG-02 are **Mechanical** and can run in parallel.

5. **Fix HIL-RS-03 (P1 correctness).** Reconcile the add-op with `target.id`/text in `hil_rs_apply.ts:60-63` (and the rediff stub contract). **Mechanical**, self-contained.

6. **UI resilience + a11y batch (P2→P3).** UI-RESILIENCE-01 (add an error boundary in `main.tsx`/`App.tsx`) first — it protects unsaved work; then A11Y-06/07/08 and UI-CANVAS-01. **Mechanical** against ADR-0044/0052.

7. **Consolidate the value/social planning cluster (P1, low effort).** Merge SOCIAL-DIFFUSION-01..04 + VALUE-MEASURE-01/02 + VR-ROADMAP-01 into one sequenced plan; retire the redundant memos. **Judgment** (product/roadmap owner). Directly answers ADR-0047.

8. **Edge i18n cleanup (P3).** FB-RM-I18N-05/06, FB-RM-UX-01/03. **Mechanical.**

Cross-cutting note for the executor: items 1c, 2a's stance, and 3b's convention are *pattern fixes* — landing them makes future regressions in P1/P2 fail loudly instead of silently, which is worth more than any individual instance fix.
