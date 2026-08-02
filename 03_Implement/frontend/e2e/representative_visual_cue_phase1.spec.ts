import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";
import { enableAdvancedUiIfNeeded } from "./helpers/i18n";

async function routeFixture(page: Page): Promise<void> {
  let persistedDocument: DocumentV1 | null = null;
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    if (route.request().method() === "PUT") {
      persistedDocument = JSON.parse(route.request().postData() ?? "{}") as DocumentV1;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"visual-cue-phase1-saved"' },
        body: JSON.stringify(persistedDocument),
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"visual-cue-phase1-e2e"' },
      body: JSON.stringify(persistedDocument ?? buildDomainExpressionDocument()),
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
  await expect(cueDetails.getByText("視覚手掛かりは設定されていません。", { exact: true })).toBeVisible();

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

test("hand-drawn cue persists in scoped IndexedDB, supports keyboard drawing and undo, then deletes after history is closed", async ({ page }) => {
  test.setTimeout(60_000);
  await page.setViewportSize({ width: 390, height: 720 });
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: "島 domain-island を選択" }).press("Enter");

  const panel = page.locator('[data-ui-region="selection-context"]');
  const cueDetails = panel.locator('[data-domain-feature="representative-visual-cue"]');
  await cueDetails.locator("summary").press("Enter");
  const editor = cueDetails.locator('[data-visual-cue-editor="hand-drawn"]');
  const drawingSurface = editor.getByRole("application", { name: "手描き視覚手掛かりの入力面" });
  const drawingBounds = await drawingSurface.boundingBox();
  expect(drawingBounds).not.toBeNull();
  await page.mouse.move(drawingBounds!.x + 20, drawingBounds!.y + 20);
  await page.mouse.down();
  await page.mouse.move(drawingBounds!.x + 45, drawingBounds!.y + 45, { steps: 4 });
  await page.mouse.up();
  await drawingSurface.focus();
  await page.keyboard.press("Space");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Space");
  await expect(editor.getByRole("status")).toContainText("開始できます");

  await editor.getByRole("button", { name: "手描きを採用" }).click();
  const adoptedMark = page.locator('[data-representative-visual-cue^="visual-cue:"]');
  await expect(adoptedMark).toHaveCount(1);
  const imageRef = await adoptedMark.getAttribute("data-representative-visual-cue");
  expect(imageRef).toMatch(/^visual-cue:[0-9a-f-]+$/);
  const storedAsset = await page.evaluate(async (ref) => {
    const database = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("kj-atlas-representative-visual-cues", 1);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    try {
      return await new Promise<{ scopeKey: string; assetJson: string }>((resolve, reject) => {
        const request = database.transaction("assets", "readonly").objectStore("assets").get(ref);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
    } finally {
      database.close();
    }
  }, imageRef);
  expect(storedAsset.scopeKey).toBe("kj-atlas/local-scope/v1/");
  expect(new TextEncoder().encode(storedAsset.assetJson).byteLength).toBeLessThanOrEqual(4096);
  await expect(cueDetails.getByLabel("代替テキスト")).toHaveValue("手描きの印");

  const controlsFit = await cueDetails.evaluate((node) => node.scrollWidth <= node.clientWidth + 1);
  expect(controlsFit).toBe(true);
  const accessibility = await new AxeBuilder({ page }).include('[data-domain-feature="representative-visual-cue"]').analyze();
  expect(accessibility.violations).toEqual([]);

  const firstSave = page.waitForRequest(
    (request) => request.method() === "PUT" && /\/docs\//.test(request.url()),
  );
  await page.getByRole("button", { name: "保存", exact: true }).click();
  const firstSavedDocument = JSON.parse((await firstSave).postData() ?? "{}") as DocumentV1;
  expect(firstSavedDocument.islands[0]?.representativeCue).toEqual({
    kind: "hand_drawn",
    cueId: imageRef,
    imageRef,
    altText: "手描きの印",
  });

  await page.reload();
  await page.getByRole("button", { name: "サンプルを開く" }).click();
  await enableAdvancedUiIfNeeded(page);
  await expect(page.locator(`[data-representative-visual-cue="${imageRef}"]`)).toHaveCount(1);
  await page.getByRole("button", { name: "島 domain-island を選択" }).press("Enter");
  const reloadedDetails = page
    .locator('[data-ui-region="selection-context"]')
    .locator('[data-domain-feature="representative-visual-cue"]');
  await expect(reloadedDetails).toBeVisible();
  await reloadedDetails.locator("summary").click();
  await reloadedDetails.getByRole("button", { name: "視覚手掛かりを外す" }).click();
  await expect(page.locator(`[data-representative-visual-cue="${imageRef}"]`)).toHaveCount(0);
  await page.keyboard.press("Control+z");
  await expect(page.locator(`[data-representative-visual-cue="${imageRef}"]`)).toHaveCount(1);

  await reloadedDetails.getByRole("button", { name: "視覚手掛かりを外す" }).click();
  const removalSave = page.waitForRequest(
    (request) => request.method() === "PUT" && /\/docs\//.test(request.url()),
  );
  await page.getByRole("button", { name: "保存", exact: true }).click();
  await removalSave;
  await page.reload();
  await page.getByRole("button", { name: "サンプルを開く" }).click();
  await enableAdvancedUiIfNeeded(page);

  await expect.poll(async () =>
    page.evaluate(async (ref) => {
      const database = await new Promise<IDBDatabase>((resolve, reject) => {
        const request = indexedDB.open("kj-atlas-representative-visual-cues", 1);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
      });
      try {
        return await new Promise<boolean>((resolve, reject) => {
          const request = database.transaction("assets", "readonly").objectStore("assets").get(ref);
          request.onsuccess = () => resolve(request.result === undefined);
          request.onerror = () => reject(request.error);
        });
      } finally {
        database.close();
      }
    }, imageRef),
  ).toBe(true);
});
