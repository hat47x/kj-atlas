import { expect, test, type Locator, type Page } from "@playwright/test";
import {
  DOCUMENT_REPLACED_STATUS,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  closeSharePanelIfOpen,
} from "./helpers/i18n";

function buildKeyboardDocument() {
  const now = "2026-05-22T00:00:00.000Z";
  return {
    version: 2,
    id: "doc_e2e_canvas_focus_order",
    title: "canvas focus order fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-primary", text: "keyboard focus primary card", x: 180, y: 160, textReviewed: true },
      { id: "card-secondary", text: "keyboard focus secondary card", x: 460, y: 170, textReviewed: false },
    ],
    edges: [{ id: "edge-1", fromId: "card-primary", toId: "card-secondary", type: "related" }],
    islands: [
      {
        id: "island-a",
        title: "Keyboard 操作確認の島",
        cardIds: ["card-primary", "card-secondary"],
        shape: { kind: "rect" as const },
      },
    ],
  };
}

async function replaceCurrentDocument(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "canvas-focus-order.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildKeyboardDocument()), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await closeSharePanelIfOpen(page);
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

test("cards, islands, and selection panel controls are reachable from keyboard focus", async ({ page }) => {
  await page.setViewportSize({ width: 960, height: 720 });
  await replaceCurrentDocument(page);

  const primaryCard = page.getByRole("option", { name: /keyboard focus primary card/ });
  await expect(primaryCard).toBeVisible();
  await primaryCard.focus();
  await expect(primaryCard).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(primaryCard).toHaveAttribute("aria-selected", "true");

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();
  await expect(selectionPanel.getByText(/現在の選択|Current selection/)).toBeVisible();
  await expect(selectionPanel.getByText(/^カードを選択中$|^Card selected$/)).toBeVisible();
  await expect(selectionPanel.getByText(/レビュー状態: レビュー済み|Review state: Reviewed/)).toBeVisible();
  await expect(selectionPanel.getByText(/カードの確認|Card Inspector/)).toBeVisible();

  const selectedCardFocusButton = selectionPanel.getByRole("button", { name: /選択中のカードを表示|Focus selected card/ });
  await pressTabUntilFocused(page, selectedCardFocusButton, 30);
  await expect(selectedCardFocusButton).toBeFocused();

  const cardFocusButton = selectionPanel.getByRole("button", { name: /このカードを表示|Focus this card/ });
  await pressTabUntilFocused(page, cardFocusButton);
  await expect(cardFocusButton).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(primaryCard).toBeVisible();

  const islandSelect = page.getByRole("button", { name: /島 island-a を選択|Select island island-a/ });
  await islandSelect.focus();
  await expect(islandSelect).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(selectionPanel.getByText(/^島を選択中$|^Island selected$/)).toBeVisible();
  await expect(selectionPanel.getByRole("button", { name: /選択中の島を表示|Focus selected island/ })).toBeVisible();
  await expect(selectionPanel.getByText(/島の編集|Island editor/)).toBeVisible();
  await expect(selectionPanel.getByText("親の島")).toBeVisible();
  await expect(selectionPanel.getByText("代表カード", { exact: true })).toBeVisible();
  await expect(selectionPanel.getByPlaceholder("代表カードの本文")).toHaveCount(0);
  await expect(selectionPanel.getByText("Parent island")).toHaveCount(0);
  await expect(selectionPanel.getByText("Placard card")).toHaveCount(0);

  const islandFocusButton = selectionPanel.getByRole("button", { name: /この島を表示|Focus this island/ });
  await pressTabUntilFocused(page, islandFocusButton);
  await expect(islandFocusButton).toBeFocused();
});
