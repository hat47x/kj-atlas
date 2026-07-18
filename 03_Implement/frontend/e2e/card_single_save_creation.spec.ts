import { expect, test, type Page } from "@playwright/test";

// DOMAIN-CARD-QUALITY-01 AC-3: a card can be created and persisted in a
// single save operation with no required input beyond its body text. There
// is no creation dialog/form, and no other Card field (claimType,
// meta.source, holdState, critique) is required before the save action
// succeeds. See issue-DOMAIN-CARD-QUALITY-01-qualitative-card-quality-
// assistance.md's "複雑性予算" self-declaration: added required operations
// to save a card = 0.

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const CREATE_CARD = '[data-ui-core-action="create-card"]';
const SAVE = '[data-ui-core-action="save"]';

async function routeDocumentSave(page: Page): Promise<{ savedBody: () => string | null }> {
  let savedBody: string | null = null;
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  // "Create new document" builds the document locally with a fresh random
  // id (see handleNewDocument/createNewDocument in App.tsx) -- it never GETs
  // an existing doc. Match any doc id here so the later PUT on save is
  // captured regardless of which id was generated.
  await page.route("**/docs/*", async (route) => {
    if (route.request().method() !== "PUT") {
      await route.fallback();
      return;
    }
    savedBody = route.request().postData() ?? null;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"card-single-save-1"' },
      body: savedBody ?? "{}",
    });
  });
  return { savedBody: () => savedBody };
}

test("a card can be created and saved with only its body text -- no other required field", async ({ page }) => {
  const route = await routeDocumentSave(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: "Create new document" }).click();
  await expect(startPanel).toBeHidden();
  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(0);

  // Single action: click "create card". No dialog or form is presented, and
  // no field other than the card's body text exists before it is created.
  await page.locator(CREATE_CARD).click();
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator(`${PRIMARY_FLOW} textarea`)).toBeFocused();

  // The new card enters edit mode immediately (ADR-0052); commit the
  // pre-filled body text without typing or touching any other field.
  await page.keyboard.press("Tab");
  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(1);

  // Second action: save. Still no field besides the body text was ever
  // required or supplied.
  const saveButton = page.locator(SAVE);
  await expect(saveButton).toBeEnabled();
  await saveButton.click();
  await expect(page.getByTestId("status-message")).toContainText("Saved");

  await expect.poll(() => route.savedBody()).not.toBeNull();
  const saved = JSON.parse(route.savedBody() ?? "{}");
  expect(saved.cards).toHaveLength(1);
  expect(typeof saved.cards[0].text).toBe("string");
  expect(saved.cards[0].text.length).toBeGreaterThan(0);
  // No other Card field was supplied at any point in this flow.
  expect(saved.cards[0].claimType).toBeUndefined();
  expect(saved.cards[0].meta).toBeUndefined();
  expect(saved.cards[0].holdState).toBeUndefined();
  expect(saved.cards[0].critique).toBeUndefined();
});
