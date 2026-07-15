import { expect, test, type Page } from "@playwright/test";

// QA-MONKEY-10 regression: sequentially created cards cascade at (+40,+40),
// overlap each other's label rects, and overlap culling used to render the
// losing cards completely blank -- freshly typed text looked lost (it was
// intact in the document model the whole time). This spec reproduces the
// VALUE-DOGFOOD-01 scenario: four cards created back-to-back, each must keep
// its text visible while active (AC-1), and any card whose text is culled
// must show an explicit omission mark carrying the full text (AC-2).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildEmptyDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Label culling fixture",
    createdAt: "2026-07-10T00:00:00.000Z",
    updatedAt: "2026-07-10T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeEmptyStartupDocument(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"label-culling-active-text"' },
      body: JSON.stringify(buildEmptyDocument()),
    });
  });
}

const CARD_TEXTS = [
  "first note about the import destinations",
  "second note about the candidate payload",
  "third note about the audit contract",
  "fourth note holding the open uncertainty",
];

test("sequentially created cascade cards never show freshly typed text as blank", async ({ page }) => {
  await routeEmptyStartupDocument(page);
  await page.goto("/?locale=en");

  await page.locator(START_PANEL).getByRole("button", { name: "Create new document" }).click();

  const cards = page.locator(`${PRIMARY_FLOW} [role="button"]`);

  for (const [index, text] of CARD_TEXTS.entries()) {
    await page.getByRole("button", { name: "New card" }).click();

    // A new card auto-enters edit mode; role="button" moves entirely to the
    // textarea while editing (ADR-0052), so the card does not match `cards`
    // (role="button") until the edit commits. Locate it via the textarea
    // itself first, type, and commit with Enter -- only one card is ever
    // mid-edit at a time, so this locator is unambiguous.
    const editTextarea = page.locator(`${PRIMARY_FLOW} textarea`);
    await expect(editTextarea).toBeVisible();
    await editTextarea.fill(text);
    await editTextarea.press("Enter");
    await expect(editTextarea).toHaveCount(0);

    await expect(cards).toHaveCount(index + 1);
    const newCard = cards.nth(index);

    // AC-1: the just-committed card is still selected (active), so its text
    // must be fully visible -- not culled -- despite overlapping neighbours.
    await expect(newCard).toContainText(text);
  }

  // After the burst, every card must show either its full text or the
  // explicit omission mark -- never an empty body (AC-2).
  for (const [index, text] of CARD_TEXTS.entries()) {
    const card = cards.nth(index);
    const culledMark = card.locator('[data-card-text-culled="true"]');
    const isCulled = (await culledMark.count()) > 0;
    if (isCulled) {
      await expect(culledMark).toHaveAttribute("aria-label", text);
      await expect(culledMark).toHaveAttribute("title", text);
    } else {
      await expect(card).toContainText(text);
    }
  }

  // Selecting a previously culled card must always bring its text back.
  await cards.nth(0).click({ position: { x: 12, y: 12 } });
  await expect(cards.nth(0)).toContainText(CARD_TEXTS[0]);
});
