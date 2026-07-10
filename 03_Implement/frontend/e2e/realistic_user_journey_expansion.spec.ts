import { expect, test, type Page } from "@playwright/test";
import {
  closeSharePanelIfOpen,
  DOCUMENT_REPLACED_STATUS,
  enableAdvancedUiIfNeeded,
  LOAD_DOCUMENT_BUTTON,
  READ_ONLY_INDICATOR,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  SUGGEST_LAYOUT_BUTTON,
  visibilitySelect,
} from "./helpers/i18n";

type SeedDocument = {
  version: number;
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  transform: { panX: number; panY: number; zoom: number };
  cards: Array<{ id: string; text: string; x: number; y: number }>;
  edges: Array<{ id: string; from: string; to: string }>;
  islands: Array<{ id: string; title: string; cardIds: string[] }>;
};

function buildSeedDocument(): SeedDocument {
  const fixedTimestamp = "2026-05-10T00:00:00.000Z";
  return {
    version: 2,
    id: "doc_e2e_realistic_journey",
    title: "realistic journey fixture",
    createdAt: fixedTimestamp,
    updatedAt: fixedTimestamp,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-1", text: "user insight 1", x: 120, y: 120 },
      { id: "card-2", text: "user insight 2", x: 300, y: 120 },
      { id: "card-3", text: "review anchor", x: 220, y: 260 },
    ],
    edges: [{ id: "edge-1", from: "card-1", to: "card-3" }],
    islands: [{ id: "island-1", title: "draft cluster", cardIds: ["card-1", "card-2"] }],
  };
}

async function replaceDocumentFromSharePanel(page: Page, doc: SeedDocument): Promise<void> {
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

test("S1-S3 realistic journey: authoring continuity + safe sharing gate with deterministic fixture", async ({ page }) => {
  const seed = buildSeedDocument();

  await page.goto("/?locale=en");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await replaceDocumentFromSharePanel(page, seed);
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();

  for (const card of seed.cards) {
    await expect(page.getByText(card.text)).toBeVisible();
  }

  // Visibility scopes moved behind the Advanced UI gate inside the share
  // panel (QA-MONKEY-11): enable Advanced first, then reopen the panel.
  await closeSharePanelIfOpen(page);
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const viewVisibility = visibilitySelect(page, "view");
  const packVisibility = visibilitySelect(page, "pack");
  await viewVisibility.selectOption("Restricted");
  await packVisibility.selectOption("Org");

  await expect(viewVisibility).toHaveValue("Restricted");
  await expect(packVisibility).toHaveValue("Org");

  await page.goto("/?locale=en&readOnly=1");
  await expect(page.getByText(READ_ONLY_INDICATOR).first()).toBeVisible();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  await expect(page.getByText("Locked redaction contexts: Share / Review Pack (cannot be disabled)."))
    .toBeVisible();
  await closeSharePanelIfOpen(page);
  // Idempotent: Advanced UI persists in localStorage across the readOnly
  // reload, so a plain toggle click here would turn it back OFF.
  await enableAdvancedUiIfNeeded(page);
  await expect(page.getByRole("button", { name: SUGGEST_LAYOUT_BUTTON }).first()).toBeDisabled();
});
