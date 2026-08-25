import { expect, test, type Page } from "@playwright/test";

// DATA-INQUIRY-CONCURRENCY-01 (AC-9, issue-DATA-INQUIRY-CONCURRENCY-01-
// unconditional-bundle-replace-and-delete.md): prove, in a real browser
// against a real backend, that a genuine 409 conflict response from
// POST /inquiry-bundles/{journey_id} (backend: 03_Implement/backend/src/
// kj_atlas_api/routes/inquiry_bundles.py put_inquiry_bundle()) surfaces as
// the panel's conflict_backend message -- never a false "saved" state, and
// never a silent auto-retry/auto-merge into the newer server revision
// (InquiryJourneyPrototypePanel.tsx handleSaveToBackend(), AC-6 comment
// right above its 409 branch).
//
// Every other inquiry_*.spec.ts / *.spec.ts in this project pins the backend
// with page.route() mocks -- right for UI-only regression coverage, but this
// scenario needs a genuine second writer racing the browser's own save, i.e.
// two independent HTTP clients hitting one real backend process and a real
// row-level CAS. Follows the precedent set by
// ai_model_ux_available_models_reason.spec.ts: gated behind
// KJ_ATLAS_E2E_REAL_BACKEND (the SAME env var and startup convention -- there
// is no reason for this scenario to need its own gate) so a plain `npm run
// e2e` is unaffected.
//
// Setup (per CONTRIBUTING.md's "SQLite代替E2E" path -- Playwright itself
// starts the frontend dev server on 127.0.0.1:4173 per playwright.config.ts,
// which proxies /api to 127.0.0.1:8000 per vite.config.ts):
//
//   cd 03_Implement/backend
//   PYTHONPATH=src KJ_ATLAS_DATABASE_URL="sqlite:////tmp/kj_atlas_inquiry_conflict_e2e.sqlite3" \
//     python -m alembic upgrade head
//   PYTHONPATH=src KJ_ATLAS_DATABASE_URL="sqlite:////tmp/kj_atlas_inquiry_conflict_e2e.sqlite3" \
//     KJ_ATLAS_LLM_PROVIDER=none \
//     python -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000
//
// Then, from 03_Implement/frontend (WSL-native checkout on Windows):
//
//   KJ_ATLAS_E2E_REAL_BACKEND=1 npx playwright test \
//     e2e/inquiry_bundle_backend_conflict.spec.ts --reporter=line --workers=1
//
// No fresh-database requirement, unlike ai_model_ux_available_models_reason
// .spec.ts: this scenario creates its own journey with a fresh
// crypto.randomUUID()-derived journeyId every run (InquiryJourneyPanel's
// handleStart -> startInquiryJourney(document)), so it does not depend on
// (and does not disturb) any other fixture state already sitting in the
// backend's database.
//
// Mechanism note: local-dev/single-tenant resolves every unauthenticated
// request to the same "local-default" tenant + a stable single-tenant
// principal (tenant_context.py SingleTenantContextResolver,
// LOCAL_DEFAULT_TENANT_ID) regardless of which HTTP client sent it. That is
// exactly what lets this spec's raw `request` fixture calls (simulating a
// second browser tab / a second concurrent editor) land in the very same
// tenant row the first browser's own fetches did, with no session headers
// needed on either side -- the same property ai_model_ux_available_models_
// reason.spec.ts's admin calls already rely on.

const BACKEND_URL = process.env.KJ_ATLAS_E2E_BACKEND_URL ?? "http://127.0.0.1:8000";
const START_PANEL = '[data-panel="start-document-entry"]';
const INQUIRY_PANEL = '[data-panel="inquiry-journey-prototype"]';

const CONFLICT_MESSAGE =
  "The inquiry changed on the server. Reload it from the backend before saving to avoid overwriting newer work.";
const SAVED_MESSAGE = "Inquiry saved to the backend.";
const RECORDED_ROUND_TEXT = "R1 Problem setting, iteration 1";
const INQUIRY_RECORDS_LIST = "Inquiry records";

// The stage/iteration label also appears (with extra surrounding text) in
// the round-parent <select>'s current-head option, the export-scope
// <select>'s options, and a "Current stage: ..." status line -- scope
// strictly to the history <ol> (aria-label="Inquiry records") and require
// an exact match so this only ever resolves to that one <li>.
function recordedRoundHistoryEntry(panel: import("@playwright/test").Locator) {
  return panel.getByRole("list", { name: INQUIRY_RECORDS_LIST }).getByText(RECORDED_ROUND_TEXT, { exact: true });
}

async function enableAdvancedUiIfNeeded(page: Page): Promise<void> {
  const advancedToggle = page.getByRole("button", { name: /^Advanced$|^詳細$/ });
  if ((await advancedToggle.getAttribute("aria-pressed")) !== "true") {
    await advancedToggle.click();
  }
}

async function openInquiryPanel(page: Page): Promise<void> {
  await expect(page.locator(START_PANEL)).toBeVisible();
  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: /^Work mode$|^作業モード$/ }).click();
  await page.getByRole("tab", { name: /^Inquiry$|^探究$/ }).click();
}

function extractJourneyId(requestUrl: string): string {
  const path = new URL(requestUrl).pathname;
  const segment = path.split("/").pop();
  if (!segment) throw new Error(`Could not extract journeyId from ${requestUrl}`);
  return decodeURIComponent(segment);
}

test.beforeEach(() => {
  test.skip(
    process.env.KJ_ATLAS_E2E_REAL_BACKEND !== "1",
    "Requires a live backend -- see the file-header comment for setup, then "
      + "set KJ_ATLAS_E2E_REAL_BACKEND=1 to run this spec.",
  );
});

test.beforeAll(async ({ request }) => {
  if (process.env.KJ_ATLAS_E2E_REAL_BACKEND !== "1") {
    return;
  }
  const health = await request.get(`${BACKEND_URL}/healthz`).catch(() => null);
  if (!health || !health.ok()) {
    throw new Error(
      `Backend not reachable at ${BACKEND_URL}/healthz. Start it per the `
        + "file-header comment before running with KJ_ATLAS_E2E_REAL_BACKEND=1.",
    );
  }
});

test(
  "a real 409 from a concurrent writer shows the conflict message, never a "
    + "false save-success, and never a silent auto-retry/auto-merge",
  async ({ page, request }) => {
    await page.goto("/?locale=en");
    await openInquiryPanel(page);
    const panel = page.locator(INQUIRY_PANEL);

    await panel.locator('[data-domain-action="start-inquiry-journey-prototype"]').click();

    // Step 1: create the bundle through the real backend by driving the
    // panel's own "Save to backend" button (If-None-Match: * -> 201). This
    // is the same code path (handleSaveToBackend) the later, conflicting
    // save will use, so the whole scenario proves real end-to-end behavior
    // rather than a synthetic setup shortcut.
    const [createResponse] = await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes("/inquiry-bundles/") && response.request().method() === "POST",
      ),
      panel.getByRole("button", { name: "Save to backend" }).click(),
    ]);
    expect(createResponse.status()).toBe(201);
    expect(createResponse.headers()["etag"]).toBe('"1"');
    await expect(panel.getByText(SAVED_MESSAGE)).toBeVisible();

    const journeyId = extractJourneyId(createResponse.url());

    // Step 2: from OUTSIDE this browser -- a second concurrent editor/tab,
    // modeled as a direct backend call -- fetch the current bundle and PUT
    // an update with the correct current If-Match, bumping the server-side
    // revision to 2. The browser above still only knows about revision 1.
    const getResponse = await request.get(`${BACKEND_URL}/inquiry-bundles/${encodeURIComponent(journeyId)}`);
    expect(getResponse.ok()).toBe(true);
    expect(getResponse.headers()["etag"]).toBe('"1"');
    const currentPayload = (await getResponse.json()) as Record<string, unknown>;

    const concurrentPayload = { ...currentPayload, _e2eConcurrentEditorMarker: "second-tab-wrote-this" };
    const concurrentPut = await request.post(`${BACKEND_URL}/inquiry-bundles/${encodeURIComponent(journeyId)}`, {
      data: concurrentPayload,
      headers: { "If-Match": '"1"' },
    });
    expect(concurrentPut.status()).toBe(204);
    expect(concurrentPut.headers()["etag"]).toBe('"2"');

    // Step 3: back in the browser (still holding the now-stale revision 1),
    // make a local edit -- proof material for the "no silent replace" check
    // below -- then try to save.
    await panel.locator('[data-domain-action="record-inquiry-round-prototype"]').click();
    await expect(recordedRoundHistoryEntry(panel)).toBeVisible();

    const [conflictResponse] = await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes(`/inquiry-bundles/${journeyId}`) && response.request().method() === "POST",
      ),
      panel.getByRole("button", { name: "Save to backend" }).click(),
    ]);
    expect(conflictResponse.status()).toBe(409);

    // The exact conflict_backend message must appear (as role="alert",
    // per the panel's message.kind === "error" -> role="alert" branch) --
    // never a false success, and never any of the other generic error text.
    await expect(panel.getByRole("alert")).toHaveText(CONFLICT_MESSAGE);
    await expect(panel.getByText(SAVED_MESSAGE)).toBeHidden();

    // No silent auto-merge: the local round recorded just above (the user's
    // own unsaved edit) is still present -- the panel never discarded or
    // replaced it with the second editor's server-side content on the 409.
    await expect(recordedRoundHistoryEntry(panel)).toBeVisible();

    // No silent auto-retry: if the failed save had silently advanced the
    // panel's remembered revision to 2 (i.e. treated the conflict as
    // resolved / merged in the background), a second attempt with no
    // intervening reload would now succeed. It must still conflict.
    const [secondConflictResponse] = await Promise.all([
      page.waitForResponse(
        (response) => response.url().includes(`/inquiry-bundles/${journeyId}`) && response.request().method() === "POST",
      ),
      panel.getByRole("button", { name: "Save to backend" }).click(),
    ]);
    expect(secondConflictResponse.status()).toBe(409);
    await expect(panel.getByRole("alert")).toHaveText(CONFLICT_MESSAGE);

    // The row on the server still holds the second (concurrent) editor's
    // content, completely untouched by any of the browser's failed saves.
    const finalGet = await request.get(`${BACKEND_URL}/inquiry-bundles/${encodeURIComponent(journeyId)}`);
    expect(finalGet.headers()["etag"]).toBe('"2"');
    const finalPayload = (await finalGet.json()) as Record<string, unknown>;
    expect(finalPayload._e2eConcurrentEditorMarker).toBe("second-tab-wrote-this");
  },
);
