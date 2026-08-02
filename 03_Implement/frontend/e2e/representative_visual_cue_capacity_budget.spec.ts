import { expect, test, type Page } from "@playwright/test";

import type { DocumentV1, RepresentativeVisualCue } from "../src/domain/types";
import { SEARCH_CARDS_PLACEHOLDER, START_PANEL_SAMPLE } from "./helpers/i18n";

const REPRESENTATIVE_CARD_COUNT = 300;
const REPRESENTATIVE_ISLAND_COUNT = 30;
const MAX_READY_TIME_MS = 2_500;
const MAX_SEARCH_TIME_MS = 1_000;
const TARGET_LONG_TASK_MS = 100;
const MAX_LONG_TASK_MS = 150;
const MAX_VISUAL_CUE_STORAGE_BYTES = 200 * 1024;
const MAX_HEAP_GROWTH_BYTES = 64 * 1024 * 1024;
const LOCAL_SCOPE_KEY = "kj-atlas/local-scope/v1/";

function imageRef(index: number): string {
  return `visual-cue:00000000-0000-4000-8000-${String(index).padStart(12, "0")}`;
}

function buildRepresentativeDocument(): DocumentV1 {
  const now = "2026-08-02T00:00:00.000Z";
  const cards = Array.from({ length: REPRESENTATIVE_CARD_COUNT }, (_, index) => {
    const row = Math.floor(index / 15);
    const column = index % 15;
    return {
      id: `card-${index + 1}`,
      text: index === 286 ? "rare visual cue capacity anchor" : `representative observation ${index + 1}`,
      x: 120 + column * 180,
      y: 120 + row * 130,
      textReviewed: true,
    };
  });
  const presetIds = ["shape-circle", "shape-triangle", "shape-diamond", "shape-parallel-lines"] as const;
  const islands = Array.from({ length: REPRESENTATIVE_ISLAND_COUNT }, (_, index) => {
    const firstCardIndex = index * 10;
    let representativeCue: RepresentativeVisualCue;
    if (index < 10) {
      const cueId = presetIds[index % presetIds.length];
      representativeCue = {
        kind: "preset_svg",
        cueId,
        altText: `Preset cue ${index + 1}`,
      };
    } else if (index < 20) {
      const cueRef = imageRef(index + 1);
      representativeCue = {
        kind: "hand_drawn",
        cueId: cueRef,
        imageRef: cueRef,
        altText: `Drawing cue ${index + 1}`,
      };
    } else {
      const cueRef = imageRef(index + 1);
      representativeCue = {
        kind: "user_image",
        cueId: cueRef,
        imageRef: cueRef,
        altText: `Image crop cue ${index + 1}`,
      };
    }
    return {
      id: `island-${index + 1}`,
      title: `representative cluster ${index + 1}`,
      cardIds: cards.slice(firstCardIndex, firstCardIndex + 10).map((card) => card.id),
      shape: { kind: "rect" as const },
      representativeCue,
    };
  });
  return {
    version: 1,
    id: "doc_visual_cue_capacity_budget",
    title: "visual cue representative capacity fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands,
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
      headers: { ETag: '"visual-cue-capacity-budget"' },
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

async function openSampleAndMeasure(page: Page, expectedPortableMarkerMinimum = 0): Promise<number> {
  const startedAt = Date.now();
  await page.getByRole("button", { name: START_PANEL_SAMPLE }).click();
  await expect(page.locator('button[aria-label^="Select island island-"]')).toHaveCount(
    REPRESENTATIVE_ISLAND_COUNT,
  );
  if (expectedPortableMarkerMinimum > 0) {
    await expect.poll(() =>
      page.locator('[data-representative-visual-cue^="visual-cue:"]').count(),
    ).toBeGreaterThanOrEqual(expectedPortableMarkerMinimum);
    await expect(page.locator('svg[data-representative-visual-cue^="visual-cue:"]').first()).toBeVisible();
    await expect(page.locator('img[data-representative-visual-cue^="visual-cue:"]').first()).toBeVisible();
  }
  return Date.now() - startedAt;
}

async function collectIslandBounds(page: Page): Promise<Array<{
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
}>> {
  return page.locator('button[aria-label^="Select island island-"]').evaluateAll((nodes) =>
    nodes.map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        label: node.getAttribute("aria-label") ?? "",
        x: rect.x,
        y: rect.y,
        width: rect.width,
        height: rect.height,
      };
    }).sort((left, right) => left.label.localeCompare(right.label)),
  );
}

async function seedPortableAssets(page: Page, documentId: string): Promise<{
  count: number;
  totalBytes: number;
  maxHandDrawnAssetBytes: number;
  maxUserImageAssetBytes: number;
}> {
  return page.evaluate(async ({ targetDocumentId, scopeKey }) => {
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
    const store = transaction.objectStore("assets-v2");
    const encoder = new TextEncoder();
    const handDrawnSizes: number[] = [];
    const userImageSizes: number[] = [];
    for (let index = 10; index < 30; index += 1) {
      const cueRef = `visual-cue:00000000-0000-4000-8000-${String(index + 1).padStart(12, "0")}`;
      let asset: unknown;
      if (index < 20) {
        asset = {
          version: 1,
          kind: "hand_drawn",
          width: 20,
          height: 20,
          strokes: [[
            { x: 2, y: 2 },
            { x: 10, y: index % 20 },
            { x: 18, y: 18 },
          ]],
        };
      } else {
        const canvas = document.createElement("canvas");
        canvas.width = 48;
        canvas.height = 48;
        const context = canvas.getContext("2d");
        if (!context) {
          throw new Error("canvas unavailable");
        }
        context.fillStyle = `hsl(${index * 19} 18% 72%)`;
        context.fillRect(0, 0, 48, 48);
        context.fillStyle = "#334155";
        context.fillRect(8 + (index % 5), 8, 24, 24);
        asset = {
          version: 1,
          kind: "user_image",
          width: 48,
          height: 48,
          mimeType: "image/png",
          base64: canvas.toDataURL("image/png").split(",")[1],
        };
      }
      const assetJson = JSON.stringify(asset);
      const assetBytes = encoder.encode(assetJson).byteLength;
      (index < 20 ? handDrawnSizes : userImageSizes).push(assetBytes);
      store.put({
        storageKey: JSON.stringify([scopeKey, cueRef]),
        imageRef: cueRef,
        scopeKey,
        documentId: targetDocumentId,
        scopeDocumentKey: JSON.stringify([scopeKey, targetDocumentId]),
        assetJson,
      });
    }
    await new Promise<void>((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
      transaction.onabort = () => reject(transaction.error);
    });
    database.close();
    return {
      count: handDrawnSizes.length + userImageSizes.length,
      totalBytes: [...handDrawnSizes, ...userImageSizes].reduce((sum, value) => sum + value, 0),
      maxHandDrawnAssetBytes: Math.max(...handDrawnSizes),
      maxUserImageAssetBytes: Math.max(...userImageSizes),
    };
  }, { targetDocumentId: documentId, scopeKey: LOCAL_SCOPE_KEY });
}

test("representative visual cues stay within layout, storage, memory, and responsiveness budgets", async ({
  page,
}, testInfo) => {
  test.setTimeout(60_000);
  const document = buildRepresentativeDocument();
  await page.addInitScript(() => {
    const target = window as Window & { __kjAtlasLongTasks?: number[] };
    target.__kjAtlasLongTasks = [];
    if (PerformanceObserver.supportedEntryTypes.includes("longtask")) {
      new PerformanceObserver((list) => {
        target.__kjAtlasLongTasks?.push(...list.getEntries().map((entry) => entry.duration));
      }).observe({ type: "longtask", buffered: true });
    }
  });
  await routeDocument(page, document);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");

  const initialReadyMs = await openSampleAndMeasure(page);
  const boundsWithoutAssets = await collectIslandBounds(page);
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Performance.enable");
  await cdp.send("HeapProfiler.collectGarbage");
  const baselineMetrics = await cdp.send("Performance.getMetrics") as {
    metrics: Array<{ name: string; value: number }>;
  };
  const baselineHeapBytes =
    baselineMetrics.metrics.find((metric) => metric.name === "JSHeapUsedSize")?.value ?? 0;

  const storage = await seedPortableAssets(page, document.id);
  await page.reload();
  const assetReadyMs = await openSampleAndMeasure(page, 10);
  const boundsWithAssets = await collectIslandBounds(page);

  expect(boundsWithAssets).toEqual(boundsWithoutAssets);
  expect(storage.count).toBe(20);
  expect(storage.totalBytes).toBeLessThanOrEqual(MAX_VISUAL_CUE_STORAGE_BYTES);
  expect(storage.maxHandDrawnAssetBytes).toBeLessThanOrEqual(4 * 1024);
  expect(storage.maxUserImageAssetBytes).toBeLessThanOrEqual(16 * 1024);

  const searchStartedAt = Date.now();
  await page.getByPlaceholder(SEARCH_CARDS_PLACEHOLDER).fill("rare visual cue capacity anchor");
  await expect(page.getByText("1/1")).toBeVisible();
  const searchMs = Date.now() - searchStartedAt;

  await cdp.send("HeapProfiler.collectGarbage");
  const loadedMetrics = await cdp.send("Performance.getMetrics") as {
    metrics: Array<{ name: string; value: number }>;
  };
  const loadedHeapBytes =
    loadedMetrics.metrics.find((metric) => metric.name === "JSHeapUsedSize")?.value ?? 0;
  const heapGrowthBytes = Math.max(0, loadedHeapBytes - baselineHeapBytes);
  const longTasks = await page.evaluate(() =>
    (window as Window & { __kjAtlasLongTasks?: number[] }).__kjAtlasLongTasks ?? [],
  );
  const maxLongTaskMs = Math.max(0, ...longTasks);

  const measurements = {
    fixture: {
      cards: REPRESENTATIVE_CARD_COUNT,
      islands: REPRESENTATIVE_ISLAND_COUNT,
      presetCues: 10,
      handDrawnCues: 10,
      userImageCues: 10,
    },
    initialReadyMs,
    assetReadyMs,
    searchMs,
    maxLongTaskMs,
    baselineHeapBytes,
    loadedHeapBytes,
    heapGrowthBytes,
    ...storage,
  };
  await testInfo.attach("representative-visual-cue-capacity.json", {
    body: Buffer.from(JSON.stringify(measurements, null, 2)),
    contentType: "application/json",
  });
  console.info(`Representative visual cue capacity: ${JSON.stringify(measurements)}`);
  if (maxLongTaskMs > TARGET_LONG_TASK_MS) {
    testInfo.annotations.push({
      type: "performance",
      description: `Parallel run exceeded the isolated 100ms target: ${maxLongTaskMs.toFixed(2)}ms`,
    });
  }

  expect(initialReadyMs).toBeLessThan(MAX_READY_TIME_MS);
  expect(assetReadyMs).toBeLessThan(MAX_READY_TIME_MS);
  expect(searchMs).toBeLessThan(MAX_SEARCH_TIME_MS);
  expect(maxLongTaskMs).toBeLessThanOrEqual(MAX_LONG_TASK_MS);
  expect(heapGrowthBytes).toBeLessThanOrEqual(MAX_HEAP_GROWTH_BYTES);
});
