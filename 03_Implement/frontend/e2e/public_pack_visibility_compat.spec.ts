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


test("shows visibility controls with fallback view visibility and pack visibility", async ({ page }) => {
  const now = new Date().toISOString();
  const documentPayload = {
    version: 2,
    id: "doc_public_pack_visibility_ui",
    title: "Visibility UI",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "card-1", text: "visible card", x: 100, y: 100 }],
    edges: [],
    islands: [],
  };

  const viewPayload = {
    version: "1",
    generatedAt: now,
    docSignature: "doc_public_pack_visibility_ui",
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
        defaultPackId: "org-pack",
        packs: [{ id: "org-pack", documentPath: "org.document.json", viewPath: "org.view.json", visibility: "Org" }],
      }),
    });
  });

  await page.route("**/packs/org.document.json", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(documentPayload) });
  });

  await page.route("**/packs/org.view.json", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(viewPayload) });
  });

  await page.goto("/?pack=org-pack");
  await expect(page.getByText("visible card")).toBeVisible();

  await page.getByRole("button", { name: /共有と再現|Share & Reproduce/ }).click();

  await expect(page.getByText("View visibility", { exact: true })).toBeVisible();
  await expect(page.getByText("Fallback: when view visibility is missing, Restricted is applied.")).toBeVisible();
  await expect(page.locator('select').first()).toHaveValue("Restricted");
});
