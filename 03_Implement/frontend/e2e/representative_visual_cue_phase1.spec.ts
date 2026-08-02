import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";
import { enableAdvancedUiIfNeeded } from "./helpers/i18n";

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    if (route.request().method() === "PUT") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"visual-cue-phase1-saved"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"visual-cue-phase1-e2e"' },
      body: JSON.stringify(buildDomainExpressionDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

test.beforeEach(async ({ page }) => {
  await routeFixture(page);
  await page.addInitScript(() => window.localStorage.removeItem("kj-atlas.advanced-ui-enabled"));
  await page.goto("/?locale=ja");
  await page.getByRole("button", { name: "サンプルを開く" }).click();
});

test("basic-shape cue is hidden by default and can be selected, edited, removed, and undone without network access", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  const externalRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if ((url.protocol === "http:" || url.protocol === "https:") && !["127.0.0.1", "localhost"].includes(url.hostname)) {
      externalRequests.push(request.url());
    }
  });

  await expect(page.locator('[data-domain-feature="representative-visual-cue"]')).toHaveCount(0);
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: "島 domain-island を選択" }).press("Enter");

  const panel = page.locator('[data-ui-region="selection-context"]');
  const cueDetails = panel.locator('[data-domain-feature="representative-visual-cue"]');
  await cueDetails.locator("summary").press("Enter");
  await expect(cueDetails.getByRole("status")).toContainText("設定されていません");

  const circleButton = cueDetails.getByRole("button", { name: "円の手掛かりを選択" });
  await circleButton.focus();
  await page.keyboard.press("Enter");
  await expect(circleButton).toHaveAttribute("aria-pressed", "true");
  const circleMarks = page.locator('[data-representative-visual-cue="shape-circle"]');
  await expect(circleMarks).toHaveCount(2);

  const altText = cueDetails.getByLabel("代替テキスト");
  await expect(altText).toHaveValue("円");
  await altText.fill("入口の目印");

  const controlsFit = await cueDetails.evaluate((node) => node.scrollWidth <= node.clientWidth + 1);
  expect(controlsFit).toBe(true);
  const accessibility = await new AxeBuilder({ page }).include('[data-domain-feature="representative-visual-cue"]').analyze();
  expect(accessibility.violations).toEqual([]);

  await cueDetails.getByRole("button", { name: "視覚手掛かりを外す" }).click();
  await expect(circleMarks).toHaveCount(1);
  await page.keyboard.press("Control+z");
  await expect(circleMarks).toHaveCount(2);

  const saveRequestPromise = page.waitForRequest(
    (request) => request.method() === "PUT" && /\/docs\//.test(request.url()),
  );
  await page.getByRole("button", { name: "保存", exact: true }).click();
  const saveRequest = await saveRequestPromise;
  const savedDocument = JSON.parse(saveRequest.postData() ?? "{}") as DocumentV1;
  expect(savedDocument.islands[0]?.representativeCue).toEqual({
    kind: "preset_svg",
    cueId: "shape-circle",
    altText: "入口の目印",
  });

  expect(externalRequests).toEqual([]);
});
