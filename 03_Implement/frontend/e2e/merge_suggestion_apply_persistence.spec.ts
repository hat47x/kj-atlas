import { expect, test, type Page } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';
const SAVE = '[data-ui-core-action="save"]';
const WORK_MODE = '[data-ui-core-action="work-mode"]';

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Merge persistence sample",
    createdAt: "2026-09-03T00:00:00.000Z",
    updatedAt: "2026-09-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "The same observation written first.", x: 0, y: 0, textReviewed: true, claimType: "fact" },
      { id: "c2", text: "The same observation written again.", x: 280, y: 0, textReviewed: true, claimType: "fact" },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routePersistentDocument(page: Page) {
  let storedDocument = buildDocument();
  let putCount = 0;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ providerKind: "local", callCounts: {}, tokenUsage: {} }),
    });
  });
  await page.route("**/ai/suggest-merges", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        suggestions: [
          {
            groupId: "merge-1",
            cardIds: ["c1", "c2"],
            mergedTextDraft: "The same observation was recorded twice.",
            rationale: "The two cards express the same reviewed observation.",
          },
        ],
      }),
    });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      storedDocument = JSON.parse(route.request().postData() ?? "{}") as ReturnType<typeof buildDocument>;
      putCount += 1;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: `"merge-persistence-${putCount}"` },
      body: JSON.stringify(storedDocument),
    });
  });

  return {
    storedDocument: () => storedDocument as any,
    putCount: () => putCount,
  };
}

async function openSample(page: Page) {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function openMergePanel(page: Page) {
  const advanced = page.getByRole("button", { name: "Advanced", exact: true });
  if ((await advanced.getAttribute("aria-pressed")) !== "true") {
    await advanced.click();
  }
  await page.locator(WORK_MODE).click();
  const workMode = page.locator('[data-ui-region="work-mode"]');
  await expect(workMode).toBeVisible();
  await workMode.getByRole("tab", { name: "Merge selection" }).click();
  return workMode;
}

test("recorded accept can be explicitly applied, saved, and recovered through the document API", async ({ page }) => {
  const persistence = await routePersistentDocument(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  const workMode = await openMergePanel(page);
  await workMode.getByRole("button", { name: "Collect candidates" }).click();
  await expect(workMode.getByText("The same observation was recorded twice.")).toBeVisible();

  await workMode
    .getByPlaceholder("Record why you accept/partial/reject/defer this proposal")
    .fill("Both reviewed cards carry the same observation, so I accept this integration.");
  await workMode.getByRole("button", { name: "Accept", exact: true }).click();

  const applyButton = workMode.getByRole("button", { name: "Apply accepted merge" });
  await expect(applyButton).toBeEnabled();
  await applyButton.click();
  await expect(workMode.getByRole("button", { name: "Merge applied" })).toBeDisabled();

  // Applying changes the in-memory Document only. Persistence remains an
  // explicit human action through the existing Save control.
  await workMode.getByRole("button", { name: "Close work mode" }).click();
  const saveButton = page.locator(SAVE);
  await expect(saveButton).toBeEnabled();
  await saveButton.click();
  await expect(page.getByTestId("status-message")).toContainText("Saved");
  await expect.poll(() => persistence.putCount()).toBe(1);

  const saved = persistence.storedDocument();
  const representative = saved.cards.find((card: any) => Array.isArray(card.repOf) && card.repOf.includes("c1") && card.repOf.includes("c2"));
  expect(representative).toBeTruthy();
  expect(representative.text).toBe("The same observation was recorded twice.");
  expect(representative.textReviewed).toBe(false);
  expect(new Set(representative.sources)).toEqual(new Set(["c1", "c2"]));

  const source1 = saved.cards.find((card: any) => card.id === "c1");
  const source2 = saved.cards.find((card: any) => card.id === "c2");
  expect(source1.mergedIntoCardId).toBe(representative.id);
  expect(source2.mergedIntoCardId).toBe(representative.id);
  expect(source1.canonicalId).toBe(representative.id);
  expect(source2.canonicalId).toBe(representative.id);

  const decision = saved.mergeSuggestionDecisions.find((item: any) => item.groupId === "merge-1");
  expect(decision.decision).toBe("accept");
  expect(decision.representativeCardId).toBe(representative.id);
  expect(new Set(decision.sourceCardIds)).toEqual(new Set(["c1", "c2"]));

  // Reload the application, then load the same document again through the
  // real GET /docs/{id} client path. The representative and its lineage must
  // survive that boundary, not only an in-memory JSON round-trip.
  await page.reload();
  await openSample(page);
  await expect(page.locator('[data-ui-region="primary-flow"]')).toContainText("The same observation was recorded twice.");
  await expect(page.locator('[data-ui-region="primary-flow"]')).toContainText("The same observation written first.");
  await expect(page.locator('[data-ui-region="primary-flow"]')).toContainText("The same observation written again.");
});
