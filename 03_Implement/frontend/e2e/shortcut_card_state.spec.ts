import { expect, test, type Page } from "@playwright/test";
import type { DocumentV2 } from "../src/domain/types";

const START_PANEL = '[data-panel="start-document-entry"]';

function buildShortcutDocument(): DocumentV2 {
  const now = "2026-07-07T00:00:00.000Z";
  return {
    version: 2,
    id: "doc_shortcut_card_state",
    title: "shortcut card state fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "shortcut-target",
        text: "shortcut target card",
        x: 160,
        y: 140,
        claimType: "unknown",
        textReviewed: false,
      },
      {
        id: "shortcut-neighbor",
        text: "shortcut neighbor card",
        x: 460,
        y: 180,
        claimType: "fact",
        textReviewed: true,
      },
    ],
    edges: [],
    islands: [],
    readingOrder: ["shortcut-target", "shortcut-neighbor"],
    evidenceLinks: [],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeShortcutFixture(page: Page): Promise<void> {
  const document = buildShortcutDocument();

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"shortcut-card-state"' },
      body: JSON.stringify(document),
    });
  });
}

async function openShortcutFixture(page: Page): Promise<void> {
  await routeShortcutFixture(page);
  await page.goto("/?locale=en");
  await expect(page.locator(START_PANEL)).toBeVisible();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();
}

async function selectTargetCard(page: Page) {
  const targetCard = page.getByRole("option", { name: "shortcut target card" });
  await expect(targetCard).toBeVisible();
  await targetCard.focus();
  await expect(targetCard).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(targetCard).toHaveAttribute("aria-selected", "true");
  return targetCard;
}

test("selected-card H/U/R shortcuts toggle state and remain undoable", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await openShortcutFixture(page);
  await selectTargetCard(page);

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  const holdState = page.locator("#selected-card-hold-state");
  const reviewedCheckbox = page.getByLabel("Card text reviewed");
  const critiqueNote = page.getByPlaceholder("Optional feedback about this card");

  await expect(selectionPanel).toContainText("Review state: Unreviewed");
  await expect(holdState).toHaveValue("active");
  await expect(reviewedCheckbox).not.toBeChecked();
  await expect(critiqueNote).toHaveValue("");

  await page.keyboard.press("h");
  await expect(holdState).toHaveValue("held");
  await expect(selectionPanel).toContainText("Hold: Held");
  await page.keyboard.press("Control+Z");
  await expect(holdState).toHaveValue("active");

  await page.keyboard.press("u");
  await expect(critiqueNote).toHaveValue("Critique mark (edit the reason in the selection panel)");
  await expect(selectionPanel).toContainText("Critique note: Critique mark (edit the reason in the selection panel)");
  await page.keyboard.press("Control+Z");
  await expect(critiqueNote).toHaveValue("");

  await page.keyboard.press("r");
  await expect(reviewedCheckbox).toBeChecked();
  await expect(selectionPanel).toContainText("Review state: Reviewed");
  await page.keyboard.press("Control+Z");
  await expect(reviewedCheckbox).not.toBeChecked();
  await expect(selectionPanel).toContainText("Review state: Unreviewed");
});

test("selected-card single-key shortcuts are disabled while editing text", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await openShortcutFixture(page);
  await selectTargetCard(page);

  const holdState = page.locator("#selected-card-hold-state");
  const reviewedCheckbox = page.getByLabel("Card text reviewed");
  const critiqueNote = page.getByPlaceholder("Optional feedback about this card");

  await critiqueNote.focus();
  await expect(critiqueNote).toBeFocused();
  await page.keyboard.press("h");
  await page.keyboard.press("u");
  await page.keyboard.press("r");

  await expect(critiqueNote).toHaveValue("hur");
  await expect(holdState).toHaveValue("active");
  await expect(reviewedCheckbox).not.toBeChecked();
});
