import { expect, test, type Download } from "@playwright/test";
import JSZip from "jszip";
import {
  EDIT_ISLAND_BOUNDARY_CHECKBOX,
  EXPORT_BUNDLE_BUTTON,
  EXPORT_DOCUMENT_JSON_BUTTON,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  closeSharePanelIfOpen,
  openLegacyJsonMenu,
} from "./helpers/i18n";

async function readDownloadToBuffer(download: Download): Promise<Buffer> {
  const stream = await download.createReadStream();
  if (!stream) {
    throw new Error("Failed to open download stream");
  }

  const chunks: Buffer[] = [];
  await new Promise<void>((resolve, reject) => {
    stream.on("data", (chunk: Buffer | string) => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    });
    stream.on("end", () => resolve());
    stream.on("error", reject);
  });

  return Buffer.concat(chunks);
}

test("QA-1: polygon export stays deterministic for identical input", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const now = new Date().toISOString();
  const polygonDoc = {
    version: 2,
    id: "doc_e2e_polygon_deterministic",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "alpha", x: 160, y: 160 }],
    edges: [],
    islands: [
      {
        id: "i1",
        title: "Polygon island",
        cardIds: ["c1"],
        shape: {
          kind: "polygon",
          points: [
            { x: 120, y: 120 },
            { x: 320, y: 120 },
            { x: 320, y: 300 },
            { x: 120, y: 300 },
          ],
        },
      },
    ],
  };

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "polygon-deterministic.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(polygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByTestId("status-message")).toContainText(/現在のドキュメントを置換しました|Replaced the current document/);
  await closeSharePanelIfOpen(page);
  await openLegacyJsonMenu(page);

  const firstDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_DOCUMENT_JSON_BUTTON }).click();
  const firstBuffer = await readDownloadToBuffer(await firstDownloadPromise);

  await openLegacyJsonMenu(page);
  const secondDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_DOCUMENT_JSON_BUTTON }).click();
  const secondBuffer = await readDownloadToBuffer(await secondDownloadPromise);

  expect(secondBuffer.toString("utf-8")).toBe(firstBuffer.toString("utf-8"));
});

test("QA-2: importing self-intersecting polygon degrades invalid polygon to a non-polygon fallback shape", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;

  const now = new Date().toISOString();
  const invalidPolygonDoc = {
    version: 2,
    id: "doc_e2e_polygon_self_intersection",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "alpha", x: 100, y: 100 },
      { id: "c2", text: "beta", x: 260, y: 140 },
    ],
    edges: [],
    islands: [
      {
        id: "i1",
        cardIds: ["c1", "c2"],
        shape: {
          kind: "polygon",
          points: [
            { x: 0, y: 0 },
            { x: 120, y: 120 },
            { x: 120, y: 0 },
            { x: 0, y: 120 },
          ],
        },
      },
    ],
  };

  await fileChooser.setFiles({
    name: "self-intersecting-polygon.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(invalidPolygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByTestId("status-message")).toContainText(/現在のドキュメントを置換しました|Replaced the current document/);

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();
  const zipBuffer = await readDownloadToBuffer(await downloadPromise);

  const zip = await JSZip.loadAsync(zipBuffer);
  const documentEntryName = Object.keys(zip.files).find((name) => name.endsWith("document.json"));
  const exportedDocument = JSON.parse(await zip.file(documentEntryName!)!.async("string")) as {
    islands: Array<{ id: string; shape?: unknown }>;
  };

  const fallbackShape = exportedDocument.islands.find((item) => item.id === "i1")?.shape as { kind?: string } | undefined;
  expect(fallbackShape?.kind === undefined || fallbackShape.kind === "rect").toBe(true);
});

test("QA-3: self-intersection edit is rejected and last valid polygon is kept", async ({ page }) => {
  await page.goto("/?locale=ja");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const now = new Date().toISOString();
  const polygonDoc = {
    version: 2,
    id: "doc_e2e_polygon_guard",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "alpha", x: 160, y: 160 }],
    edges: [],
    islands: [
      {
        id: "i1",
        title: "Polygon island",
        cardIds: ["c1"],
        shape: {
          kind: "polygon",
          points: [
            { x: 120, y: 120 },
            { x: 320, y: 120 },
            { x: 320, y: 300 },
            { x: 120, y: 300 },
          ],
        },
      },
    ],
  };

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "polygon-guard.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(polygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByTestId("status-message")).toContainText(/現在のドキュメントを置換しました|Replaced the current document/);
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await page.getByRole("button", { name: /Select island i1|島 i1 を選択/ }).dispatchEvent("click");
  await page.getByRole("checkbox", { name: EDIT_ISLAND_BOUNDARY_CHECKBOX }).check();

  const secondVertexHandle = page.getByRole("button", { name: "多角形の頂点 2 を移動" });
  const handleBox = await secondVertexHandle.boundingBox();
  expect(handleBox).toBeTruthy();
  const startX = (handleBox?.x ?? 0) + (handleBox?.width ?? 0) / 2;
  const startY = (handleBox?.y ?? 0) + (handleBox?.height ?? 0) / 2;

  await secondVertexHandle.dragTo(page.locator("body"), {
    sourcePosition: { x: (handleBox?.width ?? 10) / 2, y: (handleBox?.height ?? 10) / 2 },
    targetPosition: { x: startX - 250, y: startY + 170 },
  });

  await expect(page.getByText("多角形の辺が交差する配置にはできません")).toBeVisible();

  await closeSharePanelIfOpen(page);
  await openLegacyJsonMenu(page);
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_DOCUMENT_JSON_BUTTON }).click();
  const jsonBuffer = await readDownloadToBuffer(await downloadPromise);

  const exportedDocument = JSON.parse(jsonBuffer.toString("utf-8")) as {
    islands: Array<{ id: string; shape?: { points?: Array<{ x: number; y: number }> } }>;
  };

  expect(exportedDocument.islands.find((island) => island.id === "i1")?.shape?.points?.[1]).toEqual({ x: 320, y: 120 });
});
