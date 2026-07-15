import JSZip from "jszip";
import { expect, test, type Download } from "@playwright/test";
import { continueThroughPreShareGateIfPresent, DOCUMENT_REPLACED_STATUS, EXPORT_BUNDLE_BUTTON, LOAD_DOCUMENT_BUTTON, REPLACE_DOCUMENT_BUTTON, SHARE_REPRODUCE_BUTTON } from "./helpers/i18n";

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

test("importing a self-intersecting polygon document degrades invalid polygon to a non-polygon fallback shape", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;

  const now = new Date().toISOString();
  const invalidPolygonDoc = {
    version: 1,
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

  const replaceButton = page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON });
  await expect(replaceButton).toBeEnabled();
  await replaceButton.click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();
  await continueThroughPreShareGateIfPresent(page);
  const download = await downloadPromise;
  const zipBuffer = await readDownloadToBuffer(download);

  const zip = await JSZip.loadAsync(zipBuffer);
  const documentEntryName = Object.keys(zip.files).find((name) => name.endsWith("document.json"));
  expect(documentEntryName).toBeTruthy();
  const documentEntry = documentEntryName ? zip.file(documentEntryName) : null;
  expect(documentEntry).toBeTruthy();

  const exportedDocument = JSON.parse(await documentEntry!.async("string")) as {
    islands: Array<{ id: string; shape?: unknown }>;
  };

  const island = exportedDocument.islands.find((item) => item.id === "i1");
  expect(island).toBeDefined();
  expect(island?.shape).not.toEqual(expect.objectContaining({ kind: "polygon" }));
  expect(island?.shape === undefined || JSON.stringify(island.shape) === JSON.stringify({ kind: "rect" })).toBe(true);
});
