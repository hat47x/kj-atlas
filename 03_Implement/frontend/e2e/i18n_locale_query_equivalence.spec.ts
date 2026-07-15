import { expect, test } from "@playwright/test";
import { DOCUMENT_REPLACED_STATUS } from "./helpers/i18n";

test("smoke: locale query switches shell labels to English", async ({ page }) => {
  await page.goto("/?locale=en");

  await expect(page.getByRole("button", { name: "Share & Reproduce" })).toBeVisible();
  await expect(page.getByRole("button", { name: "View", exact: true })).toBeVisible();
});

test("invalid locale query falls back to Japanese shell labels", async ({ page }) => {
  await page.goto("/?locale=zz");

  await expect(page.getByRole("button", { name: "共有と再現" })).toBeVisible();
  await expect(page.getByRole("button", { name: "表示", exact: true })).toBeVisible();
  await expect(page.getByRole("button", { name: "Share & Reproduce" })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "View", exact: true })).toHaveCount(0);
});

test("locale=en keeps document replace flow behavior equivalent", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  const now = new Date().toISOString();
  const doc = {
    version: 1,
    id: "doc_e2e_i18n_locale_equivalence",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "locale flow card", x: 120, y: 120 }],
    edges: [],
    islands: [],
  };

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "locale-en-document.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(doc), "utf-8"),
  });

  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await expect(page.getByText("locale flow card")).toBeVisible();
});
