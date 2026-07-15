import { expect, test, type Locator, type Page } from "@playwright/test";

// DOMAIN-CARD-QUALITY-01 T7: mouse/keyboard/390px e2e for the "Tidy this
// card" self-check flow (src/domain/card_quality.ts + src/ui/SidePanel.tsx).
// Covers AC-4 (non-modal, one-question-at-a-time), AC-5 (no text change
// before adoption), AC-8 (keyboard reachability + focus return), AC-9
// (bilingual copy, 390px containment).

const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const START_PANEL = '[data-panel="start-document-entry"]';
const OPEN_ASSIST = '[data-domain-action="open-card-quality-assist"]';
const CLOSE_ASSIST = '[data-domain-action="close-card-quality-assist"]';
const DECISION_APPLY = '[data-domain-action="card-quality-decision-apply"]';
const DECISION_KEEP_AS_IS = '[data-domain-action="card-quality-decision-keep-as-is"]';
const DECISION_HOLD_FOR_NOW = '[data-domain-action="card-quality-decision-hold-for-now"]';
const CARD_TEXT = "quality assist target card";

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "card quality assist fixture",
    createdAt: "2026-07-15T00:00:00.000Z",
    updatedAt: "2026-07-15T00:00:00.000Z",
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [{ id: "c1", text: CARD_TEXT, x: 0, y: 0 }],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"card-quality-assist-2"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"card-quality-assist"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  // KJ_ATLAS_LLM_PROVIDER=none equivalence: the assist must work identically
  // with no AI provider configured (it has no provider dependency at all).
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

async function selectTargetCard(page: Page): Promise<void> {
  const card = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: CARD_TEXT });
  await card.click();
  await expect(card).toHaveAttribute("aria-pressed", "true");
}

async function activeElementSummary(page: Page): Promise<string> {
  return page.evaluate(() => {
    const active = document.activeElement;
    if (!active) {
      return "(none)";
    }
    const text = (active.textContent ?? "").replace(/\s+/g, " ").trim();
    const label = active.getAttribute("aria-label") ?? "";
    return `${active.tagName.toLowerCase()} ${label} ${text}`.trim();
  });
}

async function pressTabUntilFocused(page: Page, target: Locator, maxTabs = 80): Promise<void> {
  for (let index = 0; index < maxTabs; index += 1) {
    if (await target.evaluate((node) => document.activeElement === node).catch(() => false)) {
      return;
    }
    await page.keyboard.press("Tab");
  }

  throw new Error(`Target was not reachable with Tab. Active element: ${await activeElementSummary(page)}`);
}

test("mouse: steps through all 4 questions non-modally without changing the card, then closes (AC-4, AC-5)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTargetCard(page);

  const trigger = page.locator(OPEN_ASSIST);
  await expect(trigger).toBeVisible();
  await trigger.click();

  const assistGroup = page.getByRole("group", { name: /Tidy this card|カードを整える/ });
  await expect(assistGroup).toBeVisible();

  const decisions = [DECISION_APPLY, DECISION_KEEP_AS_IS, DECISION_HOLD_FOR_NOW, DECISION_APPLY];
  for (const decisionSelector of decisions) {
    const decisionButton = assistGroup.locator(decisionSelector);
    await expect(decisionButton).toBeVisible();
    await decisionButton.click();

    // AC-5: the canvas card's text is never touched by a decision itself —
    // only the explicit, separate "edit the text" action can do that.
    const cardOnCanvas = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: CARD_TEXT });
    await expect(cardOnCanvas).toBeVisible();
  }

  await expect(assistGroup.getByText(/Self-check complete|確認が完了しました/)).toBeVisible();

  await assistGroup.locator(CLOSE_ASSIST).click();
  await expect(assistGroup).toBeHidden();
  // Focus returns to the trigger, not lost to <body> (AC-8).
  await expect(trigger).toBeFocused();
});

test("keyboard: open, answer every question, and close entirely via Tab/Enter, with focus returned to the trigger (AC-8)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTargetCard(page);

  const trigger = page.locator(OPEN_ASSIST);
  await pressTabUntilFocused(page, trigger);
  await expect(trigger).toBeFocused();
  await page.keyboard.press("Enter");

  const assistGroup = page.getByRole("group", { name: /Tidy this card|カードを整える/ });
  await expect(assistGroup).toBeVisible();

  for (let index = 0; index < 4; index += 1) {
    const keepAsIs = assistGroup.locator(DECISION_KEEP_AS_IS);
    await pressTabUntilFocused(page, keepAsIs);
    await expect(keepAsIs).toBeFocused();
    await page.keyboard.press("Enter");
  }

  await expect(assistGroup.getByText(/Self-check complete|確認が完了しました/)).toBeVisible();

  const closeButton = assistGroup.locator(CLOSE_ASSIST);
  await pressTabUntilFocused(page, closeButton);
  await expect(closeButton).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(assistGroup).toBeHidden();
  await expect(trigger).toBeFocused();
});

test("390px: the open assist and its decision controls stay within the viewport width (AC-9)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 390, height: 720 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTargetCard(page);

  const trigger = page.locator(OPEN_ASSIST);
  await expect(trigger).toBeVisible();
  await trigger.click();

  const assistGroup = page.getByRole("group", { name: /Tidy this card|カードを整える/ });
  await expect(assistGroup).toBeVisible();

  const controls = [
    assistGroup.locator(DECISION_APPLY),
    assistGroup.locator(DECISION_KEEP_AS_IS),
    assistGroup.locator(DECISION_HOLD_FOR_NOW),
  ];
  for (const control of controls) {
    const box = await control.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(391);
  }
});

test("locale: opening in Japanese shows the Japanese self-check copy (AC-9)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=ja");
  await openSample(page);
  await selectTargetCard(page);

  await page.locator(OPEN_ASSIST).click();
  const assistGroup = page.getByRole("group", { name: "カードを整える" });
  await expect(assistGroup).toBeVisible();
  await expect(assistGroup.getByText("このカードは一つの中心的な内容だけを扱っていますか？")).toBeVisible();
  await expect(assistGroup.locator(DECISION_APPLY)).toHaveText("整える");
  await expect(assistGroup.locator(DECISION_KEEP_AS_IS)).toHaveText("このまま保存");
  await expect(assistGroup.locator(DECISION_HOLD_FOR_NOW)).toHaveText("今は保留");
});
