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

test("hierarchy level switch changes only visibility and preserves sub-island/placard data", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();

  const now = new Date().toISOString();
  const hierarchyDocument = {
    version: 2,
    id: "doc_e2e_hierarchy_level",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-root-placard", text: "Root Placard", x: 80, y: 80 },
      { id: "c-root-member", text: "Root Member", x: 220, y: 80 },
      { id: "c-child-placard", text: "Child Placard", x: 80, y: 220 },
      { id: "c-child-member", text: "Child Member", x: 220, y: 220 },
    ],
    edges: [],
    islands: [
      {
        id: "i-root",
        cardIds: ["c-root-placard", "c-root-member"],
        placardCardId: "c-root-placard",
      },
      {
        id: "i-child",
        cardIds: ["c-child-placard", "c-child-member"],
        parentIslandId: "i-root",
        placardCardId: "c-child-placard",
      },
    ],
  };

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: /^Load document\.json$|^document\.json を読み込む$/ }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "hierarchy-level.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(hierarchyDocument), "utf-8"),
  });

  await page.getByRole("button", { name: /Replace current document|現在の document を置換/ }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.getByLabel(/Structure level|構造レベル/).selectOption("overview");

  await expect(page.getByText("Root Placard").first()).toBeVisible();
  await expect(page.getByText("Child Placard").first()).toBeHidden();
  await expect(page.getByText("Root Member").first()).toBeHidden();
  await expect(page.getByText("Child Member").first()).toBeHidden();

  await page.getByLabel(/Structure level|構造レベル/).selectOption("detail");
  await expect(page.getByText("Child Placard").first()).toBeVisible();
  await expect(page.getByText("Root Member").first()).toBeVisible();
  await expect(page.getByText("Child Member").first()).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: /Export bundle \(\.zip\)|bundle をエクスポート \(.zip\)/ }).click();
  const download = await downloadPromise;
  const zipBuffer = await readDownloadToBuffer(download);

  const zip = await JSZip.loadAsync(zipBuffer);
  const documentEntryName = Object.keys(zip.files).find((name) => name.endsWith("document.json"));
  expect(documentEntryName).toBeTruthy();

  const exportedDocument = JSON.parse(await zip.file(documentEntryName!)!.async("string")) as {
    cards: Array<{ id: string }>;
    islands: Array<{ id: string; parentIslandId?: string; placardCardId?: string }>;
  };

  expect(exportedDocument.cards.map((card) => card.id).sort()).toEqual([
    "c-child-member",
    "c-child-placard",
    "c-root-member",
    "c-root-placard",
  ]);

  const exportedIslandsById = Object.fromEntries(exportedDocument.islands.map((island) => [island.id, island]));
  expect(exportedIslandsById["i-child"]?.parentIslandId).toBe("i-root");
  expect(exportedIslandsById["i-root"]?.placardCardId).toBe("c-root-placard");
  expect(exportedIslandsById["i-child"]?.placardCardId).toBe("c-child-placard");
});
