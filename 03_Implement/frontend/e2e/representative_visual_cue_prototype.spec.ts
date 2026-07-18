import { expect, test, type Page } from "@playwright/test";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";
import { WORK_MODE_BUTTON, enableAdvancedUiIfNeeded } from "./helpers/i18n";

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"visual-cue-prototype-e2e"' },
      body: JSON.stringify(buildDomainExpressionDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openPrototype(page: Page): Promise<void> {
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: WORK_MODE_BUTTON }).click();
  await page.getByRole("tab", { name: "視覚手掛かり評価" }).click();
}

test.beforeEach(async ({ page }) => {
  await routeFixture(page);
  await page.addInitScript(() => window.localStorage.removeItem("kj-atlas.advanced-ui-enabled"));
  await page.goto("/?locale=ja");
  await page.getByRole("button", { name: "サンプルを開く" }).click();
});

test("mouse flow records errors and ratings while the photo fixture stays local", async ({ page }) => {
  const externalRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if ((url.protocol === "http:" || url.protocol === "https:") && !["127.0.0.1", "localhost"].includes(url.hostname)) {
      externalRequests.push(request.url());
    }
  });

  await expect(page.locator('[data-panel="representative-visual-cue-prototype"]')).toHaveCount(0);
  await openPrototype(page);
  const panel = page.locator('[data-panel="representative-visual-cue-prototype"]');
  await expect(panel).toContainText("文書には保存されません");

  await panel.getByRole("button", { name: "探索を始める" }).click();
  await panel.getByRole("button", { name: "受付前の準備" }).click();
  await expect(panel.getByRole("status").filter({ hasText: "誤選択" })).toContainText("1 回");
  await panel.getByRole("button", { name: "入口の案内表示" }).click();
  await panel.getByRole("group", { name: /探しやすさ/ }).getByRole("button", { name: "4" }).click();
  await panel.getByRole("button", { name: "記録して次へ" }).click();
  await expect(panel.getByText("1 件のセッション内記録")).toBeVisible();

  await panel.getByLabel("評価場面").selectOption("VC-S3");
  await panel.getByRole("button", { name: "C3: 利用者写真の切り抜き" }).click();
  await panel.getByRole("button", { name: "探索を始める" }).click();
  await panel.getByRole("button", { name: "入口の案内板が反射して読めない" }).click();
  await panel.getByRole("group", { name: /探しやすさ/ }).getByRole("button", { name: "3" }).click();
  await panel.getByRole("button", { name: "元資料と撮影状況を確認" }).click();
  await expect(panel.getByRole("img", { name: /テスト用合成画像/ })).toHaveAttribute(
    "src",
    "/evaluation/representative-visual-cue/source-photo-sign-glare-01.png",
  );
  await expect(panel).toContainText("実際の観察証拠ではありません");
  expect(externalRequests).toEqual([]);
});

test("keyboard flow works at 390px without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await openPrototype(page);
  const panel = page.locator('[data-panel="representative-visual-cue-prototype"]');

  const start = panel.getByRole("button", { name: "探索を始める" });
  await start.focus();
  await page.keyboard.press("Enter");
  const target = panel.getByRole("button", { name: "入口の案内表示" });
  await target.focus();
  await page.keyboard.press("Enter");
  const rating = panel.getByRole("group", { name: /探しやすさ/ }).getByRole("button", { name: "5" });
  await rating.focus();
  await page.keyboard.press("Space");
  await expect(rating).toHaveAttribute("aria-pressed", "true");

  const fits = await panel.evaluate((node) => node.scrollWidth <= node.clientWidth + 1);
  expect(fits).toBe(true);
});
