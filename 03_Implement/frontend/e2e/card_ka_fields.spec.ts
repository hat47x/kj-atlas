import { expect, test, type Page } from "@playwright/test";

// DOMAIN-KA-01 (ADR-0048 D3改訂, schemas.md §17): KA-method card fields
// (心の声/inner-voice, 価値/value). Covers: side-panel editor (AC-1),
// undoable single-step edit, Card.text stays the event-of-record (AC-3),
// no canvas display (AC-4), and save round-trip via PUT (AC-2).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "KA fields fixture",
    createdAt: "2026-07-09T00:00:00.000Z",
    updatedAt: "2026-07-09T00:00:00.000Z",
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [
      { id: "c1", text: "ka target card", x: 0, y: 0 },
      { id: "c2", text: "preset ka card", x: 400, y: 0, ka: { voice: "already tired", value: "wanted to be heard" } },
    ],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

type SavedCard = { id: string; text: string; ka?: { voice?: string; value?: string } };

async function routeDocument(page: Page): Promise<{ readSavedCards: () => SavedCard[] | null }> {
  let savedCards: SavedCard[] | null = null;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      const body = route.request().postDataJSON() as { cards?: SavedCard[] };
      savedCards = body.cards ?? [];
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"ka-fields-2"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"ka-fields"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return { readSavedCards: () => savedCards };
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function selectKaCard(page: Page): Promise<void> {
  const card = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "ka target card" });
  await card.click();
  await expect(card).toHaveAttribute("aria-selected", "true");
}

test("side-panel KA editor sets voice/value, and undo reverts one field at a time", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectKaCard(page);

  const editor = page.locator('[data-panel="card-ka-editor"]');
  await expect(editor).toBeVisible();
  const voiceField = editor.getByPlaceholder(/honestly, it felt exhausting/);
  const valueField = editor.getByPlaceholder(/relief of not having to wait/);
  await voiceField.fill("this is exhausting");
  await valueField.fill("wanting to be understood");

  await expect(voiceField).toHaveValue("this is exhausting");
  await expect(valueField).toHaveValue("wanting to be understood");

  // Each field edit is one history step: undo drops value first, then voice.
  await page.keyboard.press("Control+z");
  await expect(valueField).toHaveValue("");
  await expect(voiceField).toHaveValue("this is exhausting");
  await page.keyboard.press("Control+z");
  await expect(voiceField).toHaveValue("");
});

test("Card.text stays the event-of-record and is never overwritten by KA fields; no canvas display", async ({ page }) => {
  const { readSavedCards } = await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectKaCard(page);

  const editor = page.locator('[data-panel="card-ka-editor"]');
  await editor.getByPlaceholder(/honestly, it felt exhausting/).fill("inner voice text");
  await editor.getByPlaceholder(/relief of not having to wait/).fill("extracted value text");

  // The KA fields never render on the canvas card itself (AC-4).
  const cardOption = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "ka target card" });
  await expect(cardOption).not.toContainText("inner voice text");
  await expect(cardOption).not.toContainText("extracted value text");

  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByTestId("status-message")).toContainText(/Saved|保存/);

  const cards = readSavedCards();
  expect(cards).not.toBeNull();
  const savedTarget = cards?.find((card) => card.id === "c1");
  expect(savedTarget?.text).toBe("ka target card");
  expect(savedTarget?.ka).toEqual({ voice: "inner voice text", value: "extracted value text" });
  const savedPreset = cards?.find((card) => card.id === "c2");
  expect(savedPreset?.ka).toEqual({ voice: "already tired", value: "wanted to be heard" });
});
