import { expect, test, type Download } from "@playwright/test";
import {
  EDIT_ISLAND_BOUNDARY_CHECKBOX,
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

test("polygon vertex drag keeps constraints and persists edited points", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const now = new Date().toISOString();
  const polygonDoc = {
    version: 2,
    id: "doc_e2e_polygon_vertex_edit",
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
    name: "polygon-edit.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(polygonDoc), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await page.getByRole("button", { name: "Select island i1" }).dispatchEvent("click");
  const editCheckbox = page.getByRole("checkbox", { name: EDIT_ISLAND_BOUNDARY_CHECKBOX });
  await expect(editCheckbox).toBeVisible();
  await editCheckbox.check();

  const firstVertexHandle = page.getByRole("button", { name: "Move polygon vertex 1" });
  await expect(firstVertexHandle).toBeVisible();
  const handleBox = await firstVertexHandle.boundingBox();
  expect(handleBox).toBeTruthy();

  const startX = (handleBox?.x ?? 0) + (handleBox?.width ?? 0) / 2;
  const startY = (handleBox?.y ?? 0) + (handleBox?.height ?? 0) / 2;
  await firstVertexHandle.dragTo(page.locator("body"), {
    sourcePosition: { x: (handleBox?.width ?? 10) / 2, y: (handleBox?.height ?? 10) / 2 },
    targetPosition: { x: startX + 40, y: startY + 28 },
  });

  await closeSharePanelIfOpen(page);
  await openLegacyJsonMenu(page);
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_DOCUMENT_JSON_BUTTON }).click();
  const download = await downloadPromise;
  const jsonBuffer = await readDownloadToBuffer(download);

  const exportedDocument = JSON.parse(jsonBuffer.toString("utf-8")) as {
    islands: Array<{ id: string; shape?: { kind: string; points?: Array<{ x: number; y: number }> } }>;
  };

  const editedIsland = exportedDocument.islands.find((island) => island.id === "i1");
  expect(editedIsland?.shape?.kind).toBe("polygon");
  expect(editedIsland?.shape?.points).toHaveLength(4);
  const movedPoint = editedIsland?.shape?.points?.[0];
  expect(movedPoint).toBeDefined();
  expect(movedPoint?.x).toBeGreaterThan(140);
  expect(movedPoint?.y).toBeGreaterThan(130);
  expect(movedPoint).not.toEqual({ x: 120, y: 120 });
});
