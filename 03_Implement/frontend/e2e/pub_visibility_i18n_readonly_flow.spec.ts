import { expect, test, type Page } from "@playwright/test";

function buildDocument(id: string, cardText: string) {
  const now = new Date().toISOString();
  return {
    version: 2,
    id,
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: `${id}-c1`, text: cardText, x: 120, y: 120 }],
    edges: [],
    islands: [],
  };
}

async function replaceDocumentFromSharePanel(page: Page, doc: ReturnType<typeof buildDocument>) {
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

test("visibility edits persist after reload in default locale", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  const viewVisibility = page.locator('label:has-text("View visibility") select');
  const packVisibility = page.locator('label:has-text("Pack visibility") select');

  await viewVisibility.selectOption("Public");
  await packVisibility.selectOption("Org");

  await page.reload();
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  await expect(viewVisibility).toHaveValue("Public");
  await expect(packVisibility).toHaveValue("Org");
});

test("locale=en keeps visibility/edit-replace flow equivalent", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  const viewVisibility = page.locator('label:has-text("View visibility") select');
  await viewVisibility.selectOption("Unlisted");
  await expect(viewVisibility).toHaveValue("Unlisted");

  const replacement = buildDocument("doc_e2e_en_visibility_replace", "english flow card");
  await replaceDocumentFromSharePanel(page, replacement);

  await expect(page.getByText("Replaced current document")).toBeVisible();
  await expect(page.getByText("english flow card")).toBeVisible();

  await page.reload();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  await expect(viewVisibility).toHaveValue("Unlisted");
});

test("readOnly + safe-mode context blocks edit actions", async ({ page }) => {
  await page.goto("/?locale=en&readOnly=1");

  await expect(page.getByText(/• Read-only/)).toBeVisible();
  await expect(page.getByRole("button", { name: "Suggest layout" }).first()).toBeDisabled();

  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  await expect(page.getByText("Locked redaction contexts: Share / Review Pack (cannot be disabled).")).toBeVisible();
});
