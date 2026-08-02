import { expect, test, type BrowserContext, type Page } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";
import {
  EXPORT_BUNDLE_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  START_PANEL_SAMPLE,
  continueThroughPreShareGateIfPresent,
} from "./helpers/i18n";

const imageRef = "visual-cue:12345678-1234-4123-8123-123456789abc";
const localScopeKey = "kj-atlas/local-scope/v1/";

const asset = {
  version: 1,
  kind: "hand_drawn",
  width: 20,
  height: 20,
  strokes: [[{ x: 2, y: 3 }, { x: 8, y: 9 }]],
} as const;

function buildDocumentWithHandDrawnCue(): DocumentV1 {
  const document = buildDomainExpressionDocument();
  return {
    ...document,
    islands: document.islands.map((island, index) =>
      index === 0
        ? {
            ...island,
            representativeCue: {
              kind: "hand_drawn",
              cueId: imageRef,
              imageRef,
              altText: "Cross-device drawing",
            },
          }
        : island,
    ),
  };
}

async function routeDocument(page: Page, document: DocumentV1): Promise<void> {
  await page.route("**/packs/index.json", (route) =>
    route.fulfill({ status: 404, contentType: "application/json", body: "{}" }),
  );
  await page.route("**/docs/*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"visual-cue-review-pack"' },
      body: JSON.stringify(document),
    }),
  );
  await page.route("**/ai/provider-status", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ providerKind: "none" }),
    }),
  );
}

async function openSample(page: Page, document: DocumentV1): Promise<void> {
  await routeDocument(page, document);
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: START_PANEL_SAMPLE }).click();
}

async function seedAsset(page: Page, documentId: string): Promise<void> {
  await page.evaluate(async ({ cueRef, scopeKey, targetDocumentId, cueAsset }) => {
    const database = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("kj-atlas-representative-visual-cues", 2);
      request.onupgradeneeded = () => {
        const store = request.result.createObjectStore("assets-v2", { keyPath: "storageKey" });
        store.createIndex("scopeDocumentKey", "scopeDocumentKey", { unique: false });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    const transaction = database.transaction("assets-v2", "readwrite");
    transaction.objectStore("assets-v2").put({
      storageKey: JSON.stringify([scopeKey, cueRef]),
      imageRef: cueRef,
      scopeKey,
      documentId: targetDocumentId,
      scopeDocumentKey: JSON.stringify([scopeKey, targetDocumentId]),
      assetJson: JSON.stringify(cueAsset),
    });
    await new Promise<void>((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    });
    database.close();
  }, {
    cueRef: imageRef,
    scopeKey: localScopeKey,
    targetDocumentId: documentId,
    cueAsset: asset,
  });
}

async function readAssetFromFreshContext(context: BrowserContext): Promise<unknown> {
  const pages = context.pages();
  const page = pages[0];
  return page.evaluate(async ({ cueRef, scopeKey }) => {
    const database = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("kj-atlas-representative-visual-cues", 2);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    const transaction = database.transaction("assets-v2", "readonly");
    const request = transaction.objectStore("assets-v2").get(JSON.stringify([scopeKey, cueRef]));
    const record = await new Promise<{ assetJson: string } | undefined>((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    database.close();
    return record ? JSON.parse(record.assetJson) : null;
  }, { cueRef: imageRef, scopeKey: localScopeKey });
}

test("migrates a legacy scoped hand-drawn asset without losing its document binding", async ({ page }) => {
  const document = buildDocumentWithHandDrawnCue();
  await page.route("**/seed-legacy-visual-cue.html", (route) =>
    route.fulfill({ status: 200, contentType: "text/html", body: "<!doctype html><title>seed</title>" }),
  );
  await page.goto("/seed-legacy-visual-cue.html");
  await page.evaluate(async ({ cueRef, scopeKey, targetDocumentId, cueAsset }) => {
    const database = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("kj-atlas-representative-visual-cues", 1);
      request.onupgradeneeded = () => {
        const store = request.result.createObjectStore("assets", { keyPath: "imageRef" });
        store.createIndex("scopeDocumentKey", "scopeDocumentKey", { unique: false });
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    const transaction = database.transaction("assets", "readwrite");
    transaction.objectStore("assets").put({
      imageRef: cueRef,
      scopeKey,
      documentId: targetDocumentId,
      scopeDocumentKey: JSON.stringify([scopeKey, targetDocumentId]),
      assetJson: JSON.stringify(cueAsset),
    });
    await new Promise<void>((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
    database.close();
  }, {
    cueRef: imageRef,
    scopeKey: localScopeKey,
    targetDocumentId: document.id,
    cueAsset: asset,
  });
  await page.unroute("**/seed-legacy-visual-cue.html");

  await openSample(page, document);
  await expect(page.locator(`[data-representative-visual-cue="${imageRef}"]`)).toHaveCount(1);
  const stores = await page.evaluate(async () => {
    const database = await new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open("kj-atlas-representative-visual-cues", 2);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
    const names = Array.from(database.objectStoreNames);
    database.close();
    return names;
  });
  expect(stores).toEqual(["assets-v2"]);
});

test("explicit review-pack opt-in restores a hand-drawn cue in a fresh browser context", async ({ browser }) => {
  test.setTimeout(60_000);
  const document = buildDocumentWithHandDrawnCue();
  const senderContext = await browser.newContext({ acceptDownloads: true });
  const senderPage = await senderContext.newPage();
  await openSample(senderPage, document);
  await seedAsset(senderPage, document.id);
  await senderPage.reload();
  await senderPage.getByRole("button", { name: START_PANEL_SAMPLE }).click();

  await senderPage.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const includeDrawing = senderPage.getByRole("checkbox", {
    name: "Include hand-drawn visual cues (1)",
  });
  await expect(includeDrawing).not.toBeChecked();
  await expect(senderPage.locator("[data-share-preflight-visual-cue-assets]")).toContainText(
    "Excluded by default",
  );
  await includeDrawing.check();
  await expect(senderPage.getByRole("status").filter({ hasText: "sensitive details" })).toBeVisible();

  const downloadPromise = senderPage.waitForEvent("download");
  await senderPage.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();
  await continueThroughPreShareGateIfPresent(senderPage);
  const download = await downloadPromise;
  const downloadStream = await download.createReadStream();
  const chunks: Buffer[] = [];
  for await (const chunk of downloadStream) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const reviewPackBuffer = Buffer.concat(chunks);
  expect(reviewPackBuffer.byteLength).toBeGreaterThan(0);

  const receiverContext = await browser.newContext();
  const receiverPage = await receiverContext.newPage();
  await openSample(receiverPage, buildDomainExpressionDocument());
  await receiverPage.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  await receiverPage
    .getByRole("dialog", { name: "Share & Reproduce" })
    .locator('input[type="file"][accept*=".zip"]')
    .setInputFiles({
      name: "hand-drawn-review-pack.zip",
      mimeType: "application/zip",
      buffer: reviewPackBuffer,
    });

  await expect(receiverPage.getByTestId("status-message")).toContainText("Review pack imported");
  await expect(receiverPage.locator(`[data-representative-visual-cue="${imageRef}"]`)).toHaveCount(1);
  await expect.poll(() => readAssetFromFreshContext(receiverContext)).toEqual(asset);

  await senderContext.close();
  await receiverContext.close();
});
