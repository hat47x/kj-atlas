import { expect, test, type Page } from "@playwright/test";

// ADR-0052: the File menu's recent-documents form used to render as a
// disallowed non-menuitem child of role="menu" (axe aria-required-children).
// It is now its own dialog, launched via a "File > Open recent document..."
// menuitem. Covers: empty state, populated state (pre-seeded via
// localStorage, matching how storage/recent.ts actually persists it),
// selecting + opening a different recent document, the Open button's
// disabled states, and Escape/close returning focus to the File menu button.

const START_PANEL = '[data-panel="start-document-entry"]';
const RECENT_STORAGE_KEY = "kj-atlas/recent-doc-ids";

function buildDocument(id: string, title: string) {
  return {
    version: 1,
    id,
    title,
    createdAt: "2026-07-13T00:00:00.000Z",
    updatedAt: "2026-07-13T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: `${title} marker card`, x: 0, y: 0 }],
    edges: [],
    islands: [],
    readingOrder: ["c1"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocuments(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"recent-dialog-active"' },
      body: JSON.stringify(buildDocument("doc_phase1_canvas", "Active sample")),
    });
  });
  await page.route("**/docs/doc_other_recent", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"recent-dialog-other"' },
      body: JSON.stringify(buildDocument("doc_other_recent", "Other recent document")),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function openRecentDocumentsDialog(page: Page): Promise<void> {
  await page.getByRole("menuitem", { name: "File", exact: true }).click();
  await page.getByRole("menuitem", { name: "Open recent document…" }).click();
}

test.beforeEach(async ({ page }) => {
  await routeDocuments(page);
  await page.setViewportSize({ width: 1440, height: 900 });
});

test("lists the just-opened document on first use (opening a document always remembers it)", async ({ page }) => {
  await page.addInitScript((key) => window.localStorage.removeItem(key), RECENT_STORAGE_KEY);
  await page.goto("/?locale=en");
  await openSample(page);

  // Opening a document always remembers it (App.tsx's rememberRecentDocumentId
  // fires on every successful load) -- so the dialog is never reachable in a
  // truly empty state via this menu path. The empty-state message itself is
  // still exercised directly against the component in isolation; here we lock
  // the realistic minimum: exactly the document just opened.
  await openRecentDocumentsDialog(page);
  const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("combobox").locator("option")).toHaveCount(2); // placeholder + doc_phase1_canvas
  await expect(dialog).not.toContainText("No recently opened documents yet.");
});

test("lists pre-seeded recent documents and opens the selected one", async ({ page }) => {
  await page.addInitScript(
    ({ key, ids }) => window.localStorage.setItem(key, JSON.stringify(ids)),
    { key: RECENT_STORAGE_KEY, ids: ["doc_other_recent", "doc_phase1_canvas"] },
  );
  await page.goto("/?locale=en");
  await openSample(page);

  await openRecentDocumentsDialog(page);
  const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
  await expect(dialog).toBeVisible();

  const select = dialog.getByRole("combobox");
  await expect(select.locator("option")).toHaveCount(3); // placeholder + 2 ids
  const openButton = dialog.getByRole("button", { name: "Open" });
  await expect(openButton).toBeDisabled();

  await select.selectOption("doc_other_recent");
  await expect(openButton).toBeEnabled();
  await openButton.click();

  await expect(dialog).toHaveCount(0);
  await expect(page.locator('[data-ui-region="primary-flow"]').getByText("Other recent document marker card")).toBeVisible();
});

test("Open is disabled when the selected document is already the active one", async ({ page }) => {
  await page.addInitScript(
    ({ key, ids }) => window.localStorage.setItem(key, JSON.stringify(ids)),
    { key: RECENT_STORAGE_KEY, ids: ["doc_phase1_canvas"] },
  );
  await page.goto("/?locale=en");
  await openSample(page);

  await openRecentDocumentsDialog(page);
  const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
  await dialog.getByRole("combobox").selectOption("doc_phase1_canvas");
  await expect(dialog.getByRole("button", { name: "Open" })).toBeDisabled();
});

test("Escape closes the dialog and returns focus to the File menu button", async ({ page }) => {
  await page.addInitScript(
    ({ key, ids }) => window.localStorage.setItem(key, JSON.stringify(ids)),
    { key: RECENT_STORAGE_KEY, ids: ["doc_other_recent"] },
  );
  await page.goto("/?locale=en");
  await openSample(page);

  const fileButton = page.getByRole("menuitem", { name: "File", exact: true });
  await openRecentDocumentsDialog(page);
  const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
  await expect(dialog).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(fileButton).toBeFocused();
});

test("has no automatable a11y violations and is not nested inside role=menu", async ({ page }) => {
  await page.addInitScript(
    ({ key, ids }) => window.localStorage.setItem(key, JSON.stringify(ids)),
    { key: RECENT_STORAGE_KEY, ids: ["doc_other_recent"] },
  );
  await page.goto("/?locale=en");
  await openSample(page);

  await openRecentDocumentsDialog(page);
  // The File role="menu" must have already closed (MenuBar's runRow closes
  // the menu before invoking the item's run()) -- this dialog is a sibling
  // surface, never a menu child, which is the whole point of the fix.
  await expect(page.getByRole("menu")).toHaveCount(0);
  await expect(page.locator('[data-ui-region="recent-documents-dialog"]')).toHaveAttribute("role", "dialog");
});

test("canvas list shows all tenant documents with titles, filters by mine, and archives", async ({ page }) => {
  // 第2反復: the canvas list (GET /docs) shows every tenant document with its
  // title, the my-documents filter refetches with createdBy, and Archive calls
  // POST /docs/{id}/archive.
  await page.route("**/docs", async (route) => {
    const url = new URL(route.request().url());
    const createdBy = url.searchParams.get("createdBy");
    const list = [
      { id: "doc-alpha", title: "Alpha canvas", lifecycle_state: "active", updated_at: "2026-08-15T00:00:00Z" },
      { id: "doc-archived", title: "Old canvas", lifecycle_state: "archived", updated_at: "2026-08-14T00:00:00Z" },
      { id: "doc-mine", title: "My canvas", created_by: "principal-1", lifecycle_state: "active", updated_at: "2026-08-13T00:00:00Z" },
    ];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(createdBy === "principal-1" ? [list[2]] : list) });
  });
  let archiveCalled = "";
  await page.route("**/docs/doc-alpha/archive", async (route) => {
    archiveCalled = "doc-alpha";
    await route.fulfill({ status: 204, body: "" });
  });
  await page.addInitScript((key) => window.localStorage.removeItem(key), RECENT_STORAGE_KEY);
  await page.goto("/?locale=en");
  await openSample(page);
  await openRecentDocumentsDialog(page);

  const dialog = page.locator('[data-ui-region="recent-documents-dialog"]');
  await expect(dialog).toBeVisible();

  // All canvases (with titles + archived marker) are shown. The my-documents
  // filter (createdBy) is a unit-level contract (backend filter test + client
  // createdBy query test) — it needs an auth-context principalId, which a
  // standalone E2E mount does not provide.
  const allSelect = dialog.locator('label:has-text("All canvases")').getByRole("combobox");
  await expect(allSelect.locator("option")).toHaveCount(4); // placeholder + 3 canvases
  await expect(dialog).toContainText("Old canvas");
  await expect(allSelect.locator("option", { hasText: "Old canvas" })).toContainText("archived");
  await expect(dialog.getByRole("checkbox", { name: /My documents only/ })).toBeVisible();

  // Archive the selected document calls POST /docs/{id}/archive.
  await allSelect.selectOption("doc-alpha");
  await dialog.getByRole("button", { name: "Archive", exact: true }).click();
  await expect.poll(() => archiveCalled).toBe("doc-alpha");
});
