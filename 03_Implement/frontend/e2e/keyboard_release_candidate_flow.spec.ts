import { expect, test, type Locator, type Page } from "@playwright/test";
import { SEARCH_CARDS_PLACEHOLDER, SHARE_REPRODUCE_BUTTON } from "./helpers/i18n";

const START_PANEL = '[data-panel="start-document-entry"]';

function buildDocument(cardTexts: string[]) {
  const now = "2026-06-04T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_keyboard_release_candidate",
    title: "Keyboard release candidate fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `keyboard-card-${index + 1}`,
      text,
      x: 120 + index * 280,
      y: 120 + (index % 2) * 160,
      textReviewed: index === 0,
    })),
    edges: [{ id: "keyboard-edge-1", from: "keyboard-card-1", to: "keyboard-card-2", kind: "relates" }],
    islands: [],
    readingOrder: ["keyboard-card-1", "keyboard-card-2", "keyboard-card-3"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeKeyboardFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const document = shouldReturnSample
      ? buildDocument(["keyboard trace primary decision", "keyboard trace observation memo", "keyboard trace share package"])
      : buildDocument([]);

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"keyboard-sample-loaded"' : '"keyboard-sample-empty"' },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

async function activeElementSummary(page: Page): Promise<string> {
  return page.evaluate(() => {
    const active = document.activeElement;
    if (!active) return "(none)";
    const text = (active.textContent ?? "").replace(/\s+/g, " ").trim();
    const label = active.getAttribute("aria-label") ?? "";
    const placeholder = active.getAttribute("placeholder") ?? "";
    return `${active.tagName.toLowerCase()} ${label} ${placeholder} ${text}`.replace(/\s+/g, " ").trim();
  });
}

async function pressTabUntilFocused(page: Page, target: Locator, maxTabs = 100): Promise<void> {
  for (let index = 0; index < maxTabs; index += 1) {
    if (await target.evaluate((node) => document.activeElement === node).catch(() => false)) return;
    await page.keyboard.press("Tab");
  }

  throw new Error(`Target was not reachable with Tab. Active element: ${await activeElementSummary(page)}`);
}

test("keyboard-only release candidate flow reaches start, search, selection, critique, and share close", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeKeyboardFixture(page);

  await page.goto("/?locale=ja");
  await expect(page.locator(START_PANEL)).toBeVisible();

  const sampleButton = page.getByRole("button", { name: /サンプルを開く|Open sample/ });
  await pressTabUntilFocused(page, sampleButton, 20);
  await expect(sampleButton).toBeFocused();
  fixture.enableSample();
  await sampleButton.press(" ");

  await expect(page.locator(START_PANEL)).toBeHidden();
  const observationCard = page.getByRole("button", { name: "keyboard trace observation memo" });
  await expect(observationCard).toBeVisible();

  const searchInput = page.getByPlaceholder(SEARCH_CARDS_PLACEHOLDER);
  await pressTabUntilFocused(page, searchInput, 80);
  await expect(searchInput).toBeFocused();
  await page.keyboard.insertText("observation");
  await expect(searchInput).toHaveValue("observation");
  await expect(page.locator("header")).toContainText("1/1");

  const previousButton = page.locator("header").getByRole("button", { name: /前へ|Prev/ });
  await page.keyboard.press("Tab");
  await expect(previousButton).toBeFocused();
  await page.keyboard.press("Shift+Tab");
  await expect(searchInput).toBeFocused();

  await pressTabUntilFocused(page, observationCard, 100);
  await expect(observationCard).toBeFocused();
  await observationCard.press(" ");
  await expect(observationCard).toHaveAttribute("aria-pressed", "true");

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();
  await expect(selectionPanel).toContainText(/現在の選択|Current selection/);
  await expect(selectionPanel).toContainText(/カードを選択中|Card selected/);

  const critiqueInput = page.getByPlaceholder(/このカードについての補足や懸念を入力|Optional feedback about this card/);
  await pressTabUntilFocused(page, critiqueInput, 140);
  await expect(critiqueInput).toBeFocused();
  await page.keyboard.insertText("Keyboard-only critique note");
  await expect(critiqueInput).toHaveValue("Keyboard-only critique note");

  const shareButton = page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON });
  await pressTabUntilFocused(page, shareButton, 160);
  await expect(shareButton).toBeFocused();
  await page.keyboard.press("Enter");

  const shareDialog = page.locator('[data-panel="share-replay"]');
  await expect(shareDialog).toBeVisible();
  await expect(shareDialog).toBeFocused();
  await expect(shareDialog).toContainText(/セーフモード: ON|SafeMode: ON/);

  const closeButton = shareDialog.getByRole("button", { name: /パネルを閉じる|Close panel/ });
  await pressTabUntilFocused(page, closeButton, 30);
  await expect(closeButton).toBeFocused();
  await closeButton.press(" ");
  await expect(shareDialog).toBeHidden();
  await expect(shareButton).toBeFocused();
});
