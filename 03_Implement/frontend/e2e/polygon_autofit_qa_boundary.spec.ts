import { expect, test, type Download } from "@playwright/test";
import JSZip from "jszip";

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
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

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
  await page.getByRole("button", { name: /^Load document\.json$|^document\.json を読み込む$/ }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "polygon-deterministic.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(polygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  const firstDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export document JSON|ドキュメントJSONを書き出す（legacy）/ }).click();
  const firstBuffer = await readDownloadToBuffer(await firstDownloadPromise);

  const secondDownloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export document JSON|ドキュメントJSONを書き出す（legacy）/ }).click();
  const secondBuffer = await readDownloadToBuffer(await secondDownloadPromise);

  expect(secondBuffer.toString("utf-8")).toBe(firstBuffer.toString("utf-8"));
});

test("QA-2: importing self-intersecting polygon degrades invalid polygon to a non-polygon fallback shape", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: /^Load document\.json$|^document\.json を読み込む$/ }).click();
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

  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export bundle \(\.zip\)|bundle をエクスポート \(.zip\)/ }).click();
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
  await page.goto("/");
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

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
  await page.getByRole("button", { name: /^Load document\.json$|^document\.json を読み込む$/ }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "polygon-guard.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(polygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  await page.getByRole("button", { name: /Polygon island #1/ }).dispatchEvent("click");
  await page.getByRole("checkbox", { name: /Edit island boundary/ }).check();

  const firstVertexHandle = page.getByRole("button", { name: "Move polygon vertex 1" });
  const handleBox = await firstVertexHandle.boundingBox();
  const startX = (handleBox?.x ?? 0) + (handleBox?.width ?? 0) / 2;
  const startY = (handleBox?.y ?? 0) + (handleBox?.height ?? 0) / 2;

  await page.mouse.move(startX, startY);
  await page.mouse.down();
  await page.mouse.move(startX + 250, startY + 170);
  await page.mouse.up();

  await expect(page.getByText("Polygon must not self-intersect")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export document JSON|ドキュメントJSONを書き出す（legacy）/ }).click();
  const jsonBuffer = await readDownloadToBuffer(await downloadPromise);

  const exportedDocument = JSON.parse(jsonBuffer.toString("utf-8")) as {
    islands: Array<{ id: string; shape?: { points?: Array<{ x: number; y: number }> } }>;
  };

  expect(exportedDocument.islands.find((island) => island.id === "i1")?.shape?.points?.[0]).toEqual({ x: 120, y: 120 });
});
