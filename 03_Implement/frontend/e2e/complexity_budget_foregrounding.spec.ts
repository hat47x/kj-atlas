import { readFile } from "node:fs/promises";
import { expect, test, type Page } from "@playwright/test";
import { parseInquiryBundleJson } from "../src/domain/inquiry_bundle_io";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

async function routeDomainExpressionFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const document = shouldReturnSample
      ? buildDomainExpressionDocument()
      : withoutProductValueContent(buildDomainExpressionDocument());
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"advanced-panel-loaded"' : '"advanced-panel-empty"' },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

test("default workspace foregrounds core actions and keeps advanced content reversible", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  await page.goto("/?locale=en");

  const closeStartPanel = page.getByRole("button", { name: "Close start panel" });
  if (await closeStartPanel.isVisible()) {
    await closeStartPanel.click();
  }

  await expect(page.locator('[data-ui-complexity-tier^="core-"]')).toHaveCount(4);
  await expect(page.locator('[data-ui-core-action="create-card"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="create-island"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="delete-selection"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="save"]')).toBeVisible();
  await expect(page.getByRole("button", { name: "New card" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Create Island" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Delete" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Save" })).toBeVisible();

  const advancedToggle = page.getByRole("button", { name: "Advanced" });
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);
  await expect(page.locator('[data-panel="domain-detail-filters"]')).toHaveCount(0);
  await expect(page.locator('[data-panel="guided-flow"]')).toHaveCount(0);

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]').first()).toBeVisible();
  await expect(page.locator('[data-panel="guided-flow"]')).toBeVisible();

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);
  await expect(page.locator('[data-panel="domain-detail-filters"]')).toHaveCount(0);
  await expect(page.locator('[data-panel="guided-flow"]')).toHaveCount(0);
});

test("selection context keeps advanced panel extracted behind explicit disclosure", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await page.getByRole("button", { name: "ambiguous target claim" }).click();

  const selectionContext = page.locator('[data-panel="selection-context"]');
  await expect(selectionContext).toBeVisible();
  await expect(selectionContext).toContainText("Card selected");
  await expect(selectionContext).toContainText("Review state: Unreviewed");
  await expect(page.locator('[data-panel-group="advanced"]')).toHaveCount(0);

  const advancedToggle = page.getByRole("button", { name: "Advanced" });
  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator('[data-panel="domain-detail-filters"]')).toBeVisible();

  const advancedPanel = page.locator('[data-panel-group="advanced"]');
  await expect(advancedPanel).toBeVisible();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "false");
  await expect(selectionContext).toContainText("Critique note:");

  await advancedPanel.locator("summary").click();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "true");
  await expect(selectionContext).toBeVisible();

  await advancedPanel.locator("summary").click();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "false");
});

test("work mode owns narrative and HIL surfaces outside selection context", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await page.getByRole("button", { name: "ambiguous target claim" }).click();

  const selectionContext = page.locator('[data-panel="selection-context"]');
  await expect(selectionContext).toBeVisible();
  await expect(selectionContext).toContainText("Card selected");

  await page.getByRole("button", { name: "Advanced" }).click();
  await expect(selectionContext).not.toContainText("Narrative (draft)");
  await expect(selectionContext).not.toContainText("Compare candidates");
  await expect(selectionContext).not.toContainText("Review Diff (Selective Merge)");

  const workModeTrigger = page.getByRole("button", { name: "Work mode" });
  await workModeTrigger.click();

  const workMode = page.locator('[data-ui-region="work-mode"]');
  await expect(workMode).toBeVisible();
  await expect(workMode).toContainText("Narrative (draft)");
  await expect(workMode).toContainText("Compare candidates");
  await expect(workMode).toContainText("Review changes");
  await expect(workMode).toContainText("Review Diff (Selective Merge)");

  await page.keyboard.press("Escape");
  await expect(workMode).toHaveCount(0);
  await expect(workModeTrigger).toBeFocused();
});

test("iterative inquiry prototype saves and resumes repeated stages without changing the normal entry path", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=ja");
  fixture.enableSample();
  await page.getByRole("button", { name: "サンプルを開く" }).click();
  await expect(page.locator('[data-panel="inquiry-journey-prototype"]')).toHaveCount(0);

  await page.getByRole("button", { name: "詳細" }).click();
  await page.getByRole("button", { name: "作業モード" }).click();
  await page.getByRole("tab", { name: "探究" }).click();

  const prototype = page.locator('[data-panel="inquiry-journey-prototype"]');
  await expect(prototype).toContainText("起点: domain expression keyboard access fixture（カード 3 件）");
  const startButton = prototype.getByRole("button", { name: "現在の文書から探究を始める" });
  await startButton.focus();
  await page.keyboard.press("Enter");
  await expect(prototype.getByRole("status")).toContainText("保存されません");

  const stageSelect = prototype.getByLabel("次に扱う段階");
  await stageSelect.selectOption("r2_situation_grasp");
  await prototype.getByRole("button", { name: "R2 現状把握・1回目を記録" }).click();
  await stageSelect.selectOption("r3_essence_pursuit");
  await prototype.getByRole("button", { name: "R3 本質追求・1回目を記録" }).click();
  await stageSelect.selectOption("r2_situation_grasp");
  await prototype.getByRole("button", { name: "R2 現状把握・2回目を記録" }).click();

  const history = prototype.getByRole("list", { name: "探究の記録" });
  await expect(history.getByRole("listitem")).toHaveText([
    "R2 現状把握・1回目",
    "R3 本質追求・1回目",
    "R2 現状把握・2回目",
  ]);

  const downloadPromise = page.waitForEvent("download");
  await prototype.getByRole("button", { name: "探究ファイルを保存" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.kj-atlas-inquiry\.json$/);
  const downloadedPath = testInfo.outputPath("saved-inquiry.json");
  await download.saveAs(downloadedPath);
  const downloadedBundle = await parseInquiryBundleJson(await readFile(downloadedPath, "utf8"));
  if (!downloadedBundle.ok) throw new Error(JSON.stringify(downloadedBundle.errors, null, 2));

  await prototype.getByRole("button", { name: "画面上の探究を閉じる" }).click();
  const endInquiryDialog = page.getByRole("alertdialog", { name: "探究を終了しますか？" });
  await expect(endInquiryDialog).toContainText("保存していない変更は失われます。探究ファイルを保存済みか確認してください。");
  await endInquiryDialog.getByRole("button", { name: "保存せず閉じる" }).click();
  await expect(prototype.getByRole("list", { name: "探究の記録" })).toHaveCount(0);
  await prototype.locator('input[type="file"]').setInputFiles(downloadedPath);
  await expect(prototype.getByRole("status").last()).toContainText("記録を再開しました");
  await expect(prototype.getByRole("list", { name: "探究の記録" }).getByRole("listitem")).toHaveText([
    "R2 現状把握・1回目",
    "R3 本質追求・1回目",
    "R2 現状把握・2回目",
  ]);

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(prototype.getByRole("button", { name: "探究ファイルを保存" })).toBeVisible();
  await expect(prototype.getByRole("button", { name: "探究ファイルから再開" })).toBeVisible();
});
