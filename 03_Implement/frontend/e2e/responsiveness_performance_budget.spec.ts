import { expect, test, type Page } from "@playwright/test";
import { buildRepresentativePerformanceDocument } from "./helpers/representative_inquiry_fixture";

type DurationRecord = {
  label: string;
  durationMs: number;
};

async function measure(records: DurationRecord[], label: string, action: () => Promise<void>) {
  const startedAt = Date.now();
  await action();
  records.push({ label, durationMs: Date.now() - startedAt });
}

async function installLongTaskProbe(page: Page) {
  await page.addInitScript(() => {
    const longTasks: Array<{ duration: number; name: string }> = [];
    (window as unknown as { __kjAtlasLongTasks: typeof longTasks }).__kjAtlasLongTasks = longTasks;
    if (!("PerformanceObserver" in window)) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          longTasks.push({ duration: entry.duration, name: entry.name });
        }
      });
      observer.observe({ entryTypes: ["longtask"] });
    } catch {
      // Some browser contexts do not expose longtask entries. Duration assertions still cover the budget.
    }
  });
}

test("PERF-BUDGET-01 representative document keeps core operations responsive", async ({ page }) => {
  test.slow();
  const durations: DurationRecord[] = [];
  await installLongTaskProbe(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");

  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "perf-budget-01-representative.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildRepresentativePerformanceDocument()), "utf-8"),
  });

  await measure(durations, "replace-document", async () => {
    await page.getByRole("button", { name: "Replace current document" }).click();
    await expect(page.getByText("Replaced the current document")).toBeVisible({ timeout: 10_000 });
  });
  await page.getByRole("button", { name: "Close panel" }).click();
  const closeStartPanel = page.getByRole("button", { name: "Close start panel" });
  if (await closeStartPanel.isVisible()) {
    await closeStartPanel.click();
  }

  await measure(durations, "search-filter", async () => {
    await page.getByPlaceholder("Search cards").fill("rare performance signal");
    await expect(page.getByText("1/1")).toBeVisible();
    await page.getByRole("checkbox", { name: "Hide non-matches" }).check();
    await expect(page.getByText("rare performance signal 287", { exact: true })).toBeVisible();
  });

  await measure(durations, "card-selection", async () => {
    const rareSignalCard = page.getByRole("button", { name: "rare performance signal 287" });
    await rareSignalCard.focus();
    await page.keyboard.press("Enter");
    await expect(page.locator('[data-panel="selection-context"]')).toContainText("Card selected");
  });

  await measure(durations, "view-panel-open", async () => {
    await page.getByRole("button", { name: "View", exact: true }).click();
    await expect(page.getByRole("dialog", { name: "View", exact: true })).toBeVisible();
  });
  await page.keyboard.press("Escape");

  await measure(durations, "share-panel-open", async () => {
    await page.getByRole("button", { name: "Share & Reproduce" }).click();
    await expect(page.locator('[data-panel="share-replay"]')).toBeVisible();
  });

  const byLabel = Object.fromEntries(durations.map((record) => [record.label, record.durationMs]));
  expect(byLabel["replace-document"]).toBeLessThan(8_000);
  expect(byLabel["search-filter"]).toBeLessThan(2_500);
  expect(byLabel["card-selection"]).toBeLessThan(2_000);
  expect(byLabel["view-panel-open"]).toBeLessThan(2_000);
  expect(byLabel["share-panel-open"]).toBeLessThan(2_500);

  const maxLongTaskMs = await page.evaluate(() => {
    const tasks = (window as unknown as { __kjAtlasLongTasks?: Array<{ duration: number }> }).__kjAtlasLongTasks ?? [];
    return tasks.reduce((max, task) => Math.max(max, task.duration), 0);
  });
  expect(maxLongTaskMs).toBeLessThan(2_500);
});
