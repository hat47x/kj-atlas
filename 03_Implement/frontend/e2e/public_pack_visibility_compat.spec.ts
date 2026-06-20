import { expect, test } from "@playwright/test";
import { SHARE_REPRODUCE_BUTTON, visibilitySelect } from "./helpers/i18n";

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

test("keeps an explicit missing-pack error visible without falling back to the API document", async ({ page }) => {
  let apiDocumentRequested = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        defaultPackId: "available",
        packs: [{ id: "available", documentPath: "available.document.json", visibility: "Public" }],
      }),
    });
  });
  await page.route("**/api/docs/**", async (route) => {
    apiDocumentRequested = true;
    await route.fulfill({ status: 500, contentType: "application/json", body: "{}" });
  });

  await page.goto("/?locale=ja&pack=missing-pack");

  await expect(page.getByRole("status")).toContainText("公開パックが見つかりません: missing-pack");
  await expect.poll(() => apiDocumentRequested).toBe(false);
});

test("localizes a malformed public-pack index response", async ({ page }) => {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 200, contentType: "text/html", body: "<!doctype html>" });
  });

  await page.goto("/?locale=ja&pack=missing-pack");

  await expect(page.getByRole("status")).toContainText(
    "公開パックの一覧情報をJSONとして読み込めませんでした。packs/index.json を確認してください。"
  );
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

  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await expect(page.getByText(/View visibility|view の公開範囲/).first()).toBeVisible();
  await expect(page.getByText(/Fallback: when view visibility is missing, Restricted is applied\.|view の公開範囲が未指定の場合は、制限付きとして扱います。/)).toBeVisible();
  await expect(visibilitySelect(page, "view")).toHaveValue("Restricted");
});
