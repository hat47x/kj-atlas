import JSZip from "jszip";
import { expect, test, type Download } from "@playwright/test";

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

test("importing a self-intersecting polygon document falls back to rect island shape", async ({ page }) => {
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

  const replaceButton = page.getByRole("button", { name: /Replace current document|現在の document を置換/ });
  await expect(replaceButton).toBeEnabled();
  await replaceButton.click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export bundle \(\.zip\)|bundle をエクスポート \(.zip\)/ }).click();
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
  expect(island?.shape).toEqual({ kind: "rect" });
});
