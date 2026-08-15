import { expect, test, type Page } from "@playwright/test";
import {
  DOCUMENT_REPLACED_STATUS,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  closeSharePanelIfOpen,
} from "./helpers/i18n";

// AI-TITLE-01: an island title that would fit ANY island (universal phrase)
// surfaces a proposal-only warning in the title editor. Rule-based, so it works
// without a backend or an LLM.

function buildUniversalTitleDocument() {
  const now = "2026-08-15T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_e2e_universal_title",
    title: "universal title fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-wait", text: "待ち時間が長いと感じた", x: 0, y: 0, textReviewed: true },
      { id: "c-serv", text: "接客は丁寧だった", x: 200, y: 0, textReviewed: true },
    ],
    edges: [],
    islands: [
      {
        id: "island-univ",
        title: "重要な論点",
        cardIds: ["c-wait", "c-serv"],
        shape: { kind: "rect" as const },
      },
    ],
  };
}

async function loadDocument(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "universal-title.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildUniversalTitleDocument()), "utf-8"),
  });
  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await closeSharePanelIfOpen(page);
}

test("a universal-phrase island title shows the proposal-only warning", async ({ page }) => {
  await loadDocument(page);

  const islandSelect = page.getByRole("button", { name: /島 island-univ を選択|Select island island-univ/ });
  await expect(islandSelect).toBeVisible();
  await islandSelect.focus();
  await page.keyboard.press("Enter");

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();
  await expect(selectionPanel.getByText(/^島を選択中$|^Island selected$/)).toBeVisible();

  // "重要な論点" fits any island -> universal warning is surfaced.
  const warning = selectionPanel.locator('[data-ui-region="universal-title-warning"]');
  await expect(warning).toBeVisible();

  // Editing the title to an island-specific advocacy clears the warning.
  const titleInput = selectionPanel.locator("#selected-island-title");
  await titleInput.fill("待ち時間の長さは体験を損ねる");
  await expect(warning).toHaveCount(0);
});
