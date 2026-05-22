import { expect, test, type Page, type Route } from "@playwright/test";

const DOCUMENT_ID = "doc_phase1_canvas";

function buildDocument() {
  const now = "2026-05-22T00:00:00.000Z";

  return {
    version: 2,
    id: DOCUMENT_ID,
    title: "ops recovery fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "card-1",
        text: "保存復旧の確認用カード",
        x: 120,
        y: 120,
      },
    ],
    edges: [],
    islands: [],
  };
}

async function routeDocumentApi(
  page: Page,
  options: {
    failGet?: boolean;
    failPut?: boolean;
  },
) {
  await page.route("**/api/docs/**", async (route: Route) => {
    const method = route.request().method();
    if (method === "GET") {
      if (options.failGet) {
        await route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({ detail: "backend unavailable" }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildDocument()),
      });
      return;
    }

    if (method === "PUT") {
      if (options.failPut) {
        await route.fulfill({
          status: 503,
          contentType: "application/json",
          body: JSON.stringify({ detail: "database unavailable" }),
        });
        return;
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: route.request().postData() ?? JSON.stringify(buildDocument()),
      });
      return;
    }

    await route.continue();
  });
}

async function expectStatusFitsViewport(page: Page) {
  const viewport = page.viewportSize();
  const box = await page.getByTestId("status-message").boundingBox();

  expect(viewport).toBeTruthy();
  expect(box).toBeTruthy();
  expect(box!.x).toBeGreaterThanOrEqual(0);
  expect(box!.x + box!.width).toBeLessThanOrEqual(viewport!.width);
}

test("API load failure gives safe recovery guidance", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await routeDocumentApi(page, { failGet: true });

  await page.goto("/");

  const status = page.getByTestId("status-message");
  await expect(status).toContainText("ドキュメントを読み込めませんでした");
  await expect(status).toContainText("/api/healthz");
  await expect(status).toContainText("バックエンドの起動状態");
  await expect(status).toContainText("API key や token を含めない");
  await expectStatusFitsViewport(page);
});

test("save failure keeps content and points to export or retry", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await routeDocumentApi(page, { failPut: true });

  await page.goto("/");
  await expect(page.getByTestId("status-message")).toContainText("ドキュメントを読み込みました");

  await page.getByRole("button", { name: /新規|New/ }).click();
  await page.getByRole("button", { name: /^保存$|^Save$/ }).click();

  const status = page.getByTestId("status-message");
  await expect(status).toContainText("ドキュメントを保存できませんでした");
  await expect(status).toContainText("内容は画面上に残っています");
  await expect(status).toContainText("JSONを書き出して保全");
  await expect(status).toContainText("API key や token を除外");
  await expectStatusFitsViewport(page);
});
