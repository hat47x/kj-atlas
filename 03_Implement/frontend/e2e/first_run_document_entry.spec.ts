import { expect, test } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';

function seedDocumentJson(): string {
  return JSON.stringify(
    {
      version: 2,
      id: "first-run-import",
      title: "First run import",
      createdAt: "2026-05-31T00:00:00.000Z",
      updatedAt: "2026-05-31T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "card-1", text: "first run imported card", x: 120, y: 120 }],
      edges: [],
      islands: [],
      readingOrder: [],
      narratives: [],
      evidenceLinks: [],
      mergeSuggestionDecisions: [],
    },
    null,
    2
  );
}

test("first-run panel presents safe document entry choices", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await page.goto("/");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await expect(startPanel).toContainText(/作業を開始|Start work/);
  await expect(startPanel).toContainText(/セーフモード: ON|SafeMode: ON/);

  await expect(page.getByRole("button", { name: /新しい文書を作成|Create new document/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /サンプルを開く|Open sample/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /文書ファイルを読み込む|Load document file/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /レビューパックを取り込む|Import review pack/ })).toBeVisible();

  const box = await startPanel.boundingBox();
  expect(box).not.toBeNull();
  expect(box!.x).toBeGreaterThanOrEqual(0);
  expect(box!.y).toBeGreaterThanOrEqual(0);
  expect(box!.x + box!.width).toBeLessThanOrEqual(390);
  expect(box!.y + box!.height).toBeLessThanOrEqual(720);
});

test("first-run document file entry opens the validation-before-replace flow", async ({ page }) => {
  await page.goto("/");

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: /文書ファイルを読み込む|Load document file/ }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "first-run-import.document.json",
    mimeType: "application/json",
    buffer: Buffer.from(seedDocumentJson(), "utf-8"),
  });

  const shareDialog = page.locator('[data-panel="share-replay"]');
  await expect(shareDialog).toBeVisible();
  await expect(shareDialog).toContainText("first-run-import.document.json");
  await expect(shareDialog).toContainText(/カード: 1|cards: 1/);
  await expect(page.getByRole("button", { name: /現在のドキュメントを置換|Replace current document/ })).toBeVisible();
});

test("first-run panel can create a new document from keyboard activation", async ({ page }) => {
  await page.goto("/");

  const createButton = page.getByRole("button", { name: /新しい文書を作成|Create new document/ });
  await expect(createButton).toBeEnabled();
  await createButton.focus();
  await expect(createButton).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(page.locator(START_PANEL)).toBeHidden();
  await expect(page.locator("header")).toContainText(/未保存|Unsaved changes/);
});
