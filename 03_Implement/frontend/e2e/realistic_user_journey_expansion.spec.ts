import { expect, test, type Page } from "@playwright/test";

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
  await page.getByRole("button", { name: /Load document.json|document.json を読み込み/ }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: `${doc.id}.json`,
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(doc), "utf-8"),
  });
  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
}

test("S1-S3 realistic journey: authoring continuity + safe sharing gate with deterministic fixture", async ({ page }) => {
  const seed = buildSeedDocument();

  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  await replaceDocumentFromSharePanel(page, seed);
  await expect(page.getByText("Replaced current document")).toBeVisible();

  for (const card of seed.cards) {
    await expect(page.getByText(card.text)).toBeVisible();
  }

  const viewVisibility = page.locator('label:has-text("View visibility") select');
  const packVisibility = page.locator('label:has-text("Pack visibility") select');
  await viewVisibility.selectOption("Restricted");
  await packVisibility.selectOption("Org");

  await page.reload();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  await expect(page.getByRole("button", { name: "Share & Reproduce" })).toBeVisible();
  await expect(viewVisibility).toHaveValue("Restricted");
  await expect(packVisibility).toHaveValue("Org");

  await page.goto("/?locale=en&readOnly=1");
  await expect(page.getByText(/• Read-only/)).toBeVisible();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  await expect(page.getByText("Locked redaction contexts: Share / Review Pack (cannot be disabled)."))
    .toBeVisible();
  await expect(page.getByRole("button", { name: "Suggest layout" }).first()).toBeDisabled();
});
