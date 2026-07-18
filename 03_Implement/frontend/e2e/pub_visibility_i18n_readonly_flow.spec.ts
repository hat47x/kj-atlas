import { expect, test, type Page } from "@playwright/test";
import {
  ADVANCED_UI_BUTTON,
  LOAD_DOCUMENT_BUTTON,
  READ_ONLY_INDICATOR,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  SUGGEST_LAYOUT_BUTTON,
  visibilitySelect,
} from "./helpers/i18n";

const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const START_PANEL = '[data-panel="start-document-entry"]';
const READ_ONLY_EDIT_BLOCKED_MESSAGE = /Read-only mode:.*is disabled\.|読み取り専用モード:.*は無効です。/;

function buildDocument(id: string, cardText: string) {
  const now = new Date().toISOString();
  return {
    version: 1,
    id,
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: `${id}-c1`, text: cardText, x: 120, y: 120 }],
    edges: [],
    islands: [],
  };
}

async function replaceDocumentFromSharePanel(page: Page, doc: ReturnType<typeof buildDocument>) {
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: `${doc.id}.json`,
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(doc), "utf-8"),
  });
  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
}

async function routeFrontendDependencies(page: Page, document = buildDocument("doc_phase1_canvas", "visibility flow card")) {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"visibility-flow-e2e"' },
      body: JSON.stringify(document),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

test("fixture-backed visibility edits persist after reload in default locale", async ({ page }) => {
  await routeFrontendDependencies(page);
  await page.goto("/");
  await page.getByRole("button", { name: ADVANCED_UI_BUTTON }).click();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const viewVisibility = visibilitySelect(page, "view");
  const packVisibility = visibilitySelect(page, "pack");

  await viewVisibility.selectOption("Public");
  await packVisibility.selectOption("Org");

  await page.reload();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await expect(viewVisibility).toHaveValue("Public");
  await expect(packVisibility).toHaveValue("Org");
});

test("share preflight explains differing view and pack visibility scopes", async ({ page }) => {
  await routeFrontendDependencies(page, buildDocument("doc_phase1_canvas", "visibility scope card"));
  await page.goto("/?locale=en");
  await expect(page.getByRole("button", { name: ADVANCED_UI_BUTTON })).toBeVisible();
  await page.getByRole("button", { name: ADVANCED_UI_BUTTON }).click();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const viewVisibility = visibilitySelect(page, "view");
  const packVisibility = visibilitySelect(page, "pack");
  await viewVisibility.selectOption("Restricted");
  await packVisibility.selectOption("Public");

  await expect(viewVisibility).toHaveValue("Restricted");
  await expect(packVisibility).toHaveValue("Public");
  await expect(page.getByText("View visibility controls the displayed view. Pack visibility controls the files you share. If they differ, confirm both scopes before exporting.")).toBeVisible();
});

test("fixture-backed locale=en keeps visibility/edit-replace flow equivalent", async ({ page }) => {
  await routeFrontendDependencies(page);
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: ADVANCED_UI_BUTTON }).click();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const viewVisibility = visibilitySelect(page, "view");
  await viewVisibility.selectOption("Unlisted");
  await expect(viewVisibility).toHaveValue("Unlisted");

  const replacement = buildDocument("doc_e2e_en_visibility_replace", "english flow card");
  await replaceDocumentFromSharePanel(page, replacement);

  await expect(page.getByText(/Replaced the current document/)).toBeVisible();
  await expect(page.getByText("english flow card")).toBeVisible();

  await page.reload();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  await expect(viewVisibility).toHaveValue("Unlisted");
});

test("fixture-backed readOnly + safe-mode context blocks edit actions", async ({ page }) => {
  await routeFrontendDependencies(page);
  await page.goto("/?locale=en&readOnly=1");

  await expect(page.getByText(READ_ONLY_INDICATOR).first()).toBeVisible();
  await page.getByRole("button", { name: ADVANCED_UI_BUTTON }).click();
  await expect(page.getByRole("button", { name: SUGGEST_LAYOUT_BUTTON }).first()).toBeDisabled();

  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  await expect(page.getByText("Locked redaction contexts: Share / Review Pack (cannot be disabled).")).toBeVisible();
});

test("fixture-backed readOnly + safe-mode blocks a committed card text edit in the default locale", async ({ page }) => {
  await routeFrontendDependencies(page, buildDocument("doc_phase1_canvas", "readonly guarded card"));
  await page.goto("/?readOnly=1");

  await expect(page.getByText(READ_ONLY_INDICATOR).first()).toBeVisible();

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  const card = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "readonly guarded card" });
  await card.click();
  await card.dblclick();

  const editor = page.locator(`${PRIMARY_FLOW} textarea`);
  await editor.press("Control+a");
  await page.keyboard.type("attempted edit while read-only");
  await editor.press("Enter");

  // The commit path (handleCommitCardText -> applyDocumentChange) is the same
  // central gate used for every document mutation, so blocking it here proves
  // the readOnly boundary holds for real edit attempts, not only for a single
  // disabled toolbar button as the sibling test above checks.
  await expect(page.getByText(READ_ONLY_EDIT_BLOCKED_MESSAGE)).toBeVisible();
  await expect(card).toBeVisible();
  await expect(page.getByText("attempted edit while read-only")).toHaveCount(0);
});
