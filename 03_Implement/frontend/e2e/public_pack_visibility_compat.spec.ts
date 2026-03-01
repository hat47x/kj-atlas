import { expect, test } from "@playwright/test";

test("loads legacy public pack without visibility and legacy view metadata without visibility", async ({ page }) => {
  const now = new Date().toISOString();
  const documentPayload = {
    version: 2,
    id: "doc_public_pack_legacy",
    title: "Legacy Pack",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "card-1", text: "legacy card", x: 120, y: 140 }],
    edges: [],
    islands: [],
  };

  const viewPayload = {
    version: "1",
    generatedAt: now,
    docSignature: "doc_public_pack_legacy",
    camera: { panX: 0, panY: 0, zoom: 1 },
    viewState: {
      summaryView: false,
      abstractMapView: false,
      hideSourceCards: false,
      maxDepth: "all",
      focusIslandId: null,
      showReadingOrder: false,
    },
    export: { mode: "viewport" },
  };

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        defaultPackId: "legacy",
        packs: [{ id: "legacy", documentPath: "legacy.document.json", viewPath: "legacy.view.json" }],
      }),
    });
  });

  await page.route("**/packs/legacy.document.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(documentPayload),
    });
  });

  await page.route("**/packs/legacy.view.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(viewPayload),
    });
  });

  await page.goto("/?pack=legacy");

  await expect(page.getByText("legacy card")).toBeVisible();
  await expect(page.getByText("Invalid pack view metadata")).toHaveCount(0);
});
