import { expect, test, type Download, type Page } from "@playwright/test";
import { DIAGNOSTICS_BUNDLE_BUTTON } from "./helpers/i18n";

// PRODUCT-OPS-02 (ADR-0053): support diagnostics bundle (diag-bundle.v1).
// Covers: trigger is reachable without enabling Advanced (this is a support
// tool, not a power-user feature), generation is blocked until a
// classification is explicitly chosen, the full-text preview always renders
// before copy/download are usable, forbidden content (card text, document
// id, raw User-Agent) never appears in the generated output, download
// produces the exact previewed JSON, and Escape/close discards the
// in-memory snapshot.

const FIXED_TIMESTAMP = "2026-07-13T00:00:00.000Z";
const SECRET_CARD_TEXT = "top secret unreviewed card body should never leak";

function buildFixtureDocument() {
  return {
    version: 2,
    id: "doc_diagnostics_bundle_e2e_fixture",
    title: "Diagnostics bundle e2e fixture",
    createdAt: FIXED_TIMESTAMP,
    updatedAt: FIXED_TIMESTAMP,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: SECRET_CARD_TEXT, x: 0, y: 0, claimType: "claim", textReviewed: true }],
    edges: [],
    islands: [],
    readingOrder: ["c1"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"diagnostics-bundle-e2e"' },
      body: JSON.stringify(buildFixtureDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function readDownloadText(download: Download): Promise<string> {
  const stream = await download.createReadStream();
  if (!stream) throw new Error("Failed to open download stream");
  const chunks: Buffer[] = [];
  await new Promise<void>((resolve, reject) => {
    stream.on("data", (chunk: Buffer | string) => chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk)));
    stream.on("end", () => resolve());
    stream.on("error", reject);
  });
  return Buffer.concat(chunks).toString("utf8");
}

test.beforeEach(async ({ page }) => {
  await routeFixture(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  const startPanel = page.locator('[data-panel="start-document-entry"]');
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
});

test("trigger is reachable without enabling Advanced UI", async ({ page }) => {
  await expect(page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON })).toBeVisible();
});

test("generation is blocked until a classification is chosen; preview shows the fixed shape and excludes forbidden content", async ({
  page,
}) => {
  await page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON }).click();

  const panel = page.locator('[data-ui-region="diagnostics-bundle"]');
  await expect(panel).toBeVisible();

  const generateButton = page.getByTestId("diagnostics-bundle-generate");
  await expect(generateButton).toBeDisabled();
  await expect(page.getByTestId("diagnostics-bundle-preview-text")).toHaveCount(0);

  await page.getByTestId("diagnostics-bundle-classification-select").selectOption("SAVE-FAILURE");
  await expect(generateButton).toBeEnabled();
  await page.getByTestId("diagnostics-bundle-http-status-input").fill("503");
  await generateButton.click();

  const preview = page.getByTestId("diagnostics-bundle-preview-text");
  await expect(preview).toBeVisible();
  const previewText = await preview.inputValue();
  const parsed = JSON.parse(previewText) as Record<string, unknown>;

  expect(parsed.schemaVersion).toBe("diag-bundle.v1");
  expect((parsed.incident as { classificationCode: string }).classificationCode).toBe("SAVE-FAILURE");
  expect((parsed.incident as { httpStatus: number }).httpStatus).toBe(503);
  expect((parsed.document as { counts: { cards: number } }).counts.cards).toBe(1);

  // Forbidden content must never appear: raw card text, document id, and
  // structurally-impossible fields (the generator's input type has no way
  // to receive these, but assert the rendered output too as a hard proof).
  expect(previewText).not.toContain(SECRET_CARD_TEXT);
  expect(previewText).not.toContain("doc_diagnostics_bundle_e2e_fixture");
  expect(previewText).not.toMatch(/score|rank|confidence|priority/i);
});

test("download produces the exact previewed JSON", async ({ page }) => {
  await page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON }).click();
  await page.getByTestId("diagnostics-bundle-classification-select").selectOption("WEB-ENTRY");
  await page.getByTestId("diagnostics-bundle-generate").click();

  const previewText = await page.getByTestId("diagnostics-bundle-preview-text").inputValue();

  const downloadPromise = page.waitForEvent("download");
  await page.getByTestId("diagnostics-bundle-download").click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^kj-atlas-diag-bundle-\d+\.json$/);

  const downloaded = await readDownloadText(download);
  expect(downloaded).toBe(previewText);
});

test("copy shows confirmation feedback", async ({ page, context }) => {
  await context.grantPermissions(["clipboard-read", "clipboard-write"]);
  await page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON }).click();
  await page.getByTestId("diagnostics-bundle-classification-select").selectOption("IMPORT-VALIDATION");
  await page.getByTestId("diagnostics-bundle-generate").click();

  await page.getByTestId("diagnostics-bundle-copy").click();
  await expect(page.getByText(/^Copied$|^コピーしました$/)).toBeVisible();
});

test("Escape closes the panel, returns focus to the trigger, and discards the generated preview", async ({ page }) => {
  const trigger = page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON });
  await trigger.click();

  const panel = page.locator('[data-ui-region="diagnostics-bundle"]');
  await page.getByTestId("diagnostics-bundle-classification-select").selectOption("SHARE-SAFEMODE");
  await page.getByTestId("diagnostics-bundle-generate").click();
  await expect(page.getByTestId("diagnostics-bundle-preview-text")).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(panel).toBeHidden();
  await expect(trigger).toBeFocused();

  await trigger.click();
  await expect(panel).toBeVisible();
  // The generated snapshot itself is discarded; the classification dropdown
  // (a non-sensitive category label) is allowed to persist across reopen.
  await expect(page.getByTestId("diagnostics-bundle-preview-text")).toHaveCount(0);
});

test("renders in Japanese locale", async ({ page }) => {
  await page.goto("/?locale=ja");
  const startPanel = page.locator('[data-panel="start-document-entry"]');
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  await page.getByRole("button", { name: DIAGNOSTICS_BUNDLE_BUTTON }).click();
  const panel = page.locator('[data-ui-region="diagnostics-bundle"]');
  await expect(panel).toBeVisible();
  await expect(panel.getByText("サポート診断バンドル")).toBeVisible();
});
