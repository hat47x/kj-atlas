import { expect, test, type Page } from "@playwright/test";

// DOMAIN-EXPR-04 (ADR-0040 Phase 4, schemas.md §16): human review decisions on
// analyzeContradictions() signals. Covers: signal appears after running
// diagnostics (deterministic heuristic, no AI call), Accept/Hold/Reject/Undo
// as single undoable history steps, and PUT round-trip of the decision.

const START_PANEL = '[data-panel="start-document-entry"]';
const RUN_DIAGNOSTICS_BUTTON = /診断を実行|Run diagnostics/;

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Contradiction signal decision fixture",
    createdAt: "2026-07-08T00:00:00.000Z",
    updatedAt: "2026-07-08T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "island a card", x: 0, y: 0 },
      { id: "c2", text: "island b card", x: 400, y: 0 },
    ],
    edges: [
      { id: "e-pos", fromId: "island-a", toId: "island-b", fromKind: "island", toKind: "island", type: "related" },
      { id: "e-neg", fromId: "island-b", toId: "island-a", fromKind: "island", toKind: "island", type: "negate" },
    ],
    islands: [
      { id: "island-a", title: "Island A", cardIds: ["c1"] },
      { id: "island-b", title: "Island B", cardIds: ["c2"] },
    ],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

type SavedDocument = { contradictionSignalDecisions?: Array<{ signatureKey: string; status: string; decidedAt: string }> };

async function routeDocument(page: Page): Promise<{ readSavedDocument: () => SavedDocument | null }> {
  let saved: SavedDocument | null = null;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      saved = route.request().postDataJSON() as SavedDocument;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"contradiction-decision-2"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"contradiction-decision"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return { readSavedDocument: () => saved };
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function runDiagnosticsAndExpandContradictionSignals(page: Page): Promise<void> {
  await page.getByRole("button", { name: RUN_DIAGNOSTICS_BUTTON }).first().click();
  const contradictionSummary = page.getByText(/矛盾シグナル \(\d+\)|Contradiction signals \(\d+\)/).first();
  await expect(contradictionSummary).toBeVisible();
  await contradictionSummary.click();
}

test("accepts a contradiction signal, shows the badge, and undo reverts it (⌘Z-equivalent single steps)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await runDiagnosticsAndExpandContradictionSignals(page);

  const c001Item = page.locator("li", { hasText: "C001" }).first();
  await expect(c001Item).toBeVisible();

  await c001Item.getByRole("button", { name: "Accept", exact: true }).click();
  await expect(c001Item.getByText("Accepted", { exact: true })).toBeVisible();

  await c001Item.getByRole("button", { name: "Undo decision" }).click();
  await expect(c001Item.getByText("Accepted", { exact: true })).toHaveCount(0);
});

test("held and rejected decisions are mutually exclusive and both persist on save (PUT payload)", async ({ page }) => {
  const { readSavedDocument } = await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await runDiagnosticsAndExpandContradictionSignals(page);

  const c001Item = page.locator("li", { hasText: "C001" }).first();
  await c001Item.getByRole("button", { name: "Hold", exact: true }).click();
  await expect(c001Item.getByText("Held", { exact: true })).toBeVisible();

  await c001Item.getByRole("button", { name: "Reject", exact: true }).click();
  await expect(c001Item.getByText("Rejected", { exact: true })).toBeVisible();
  await expect(c001Item.getByText("Held", { exact: true })).toHaveCount(0);

  // The signal itself must stay visible even though it was rejected (§16.4:
  // "rejected" records a reviewed-and-set-aside decision, not a hidden signal).
  await expect(c001Item).toBeVisible();

  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByTestId("status-message")).toContainText(/Saved|保存/);

  const saved = readSavedDocument();
  expect(saved).not.toBeNull();
  expect(saved?.contradictionSignalDecisions).toEqual([
    expect.objectContaining({ signatureKey: "C001:island:island-a|island:island-b", status: "rejected" }),
  ]);
});
