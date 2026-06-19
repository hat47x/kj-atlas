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

function buildPolygonDocument(id: string) {
  const now = new Date().toISOString();
  return {
    version: 2,
    id,
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
}

async function replaceCurrentDocumentWithPolygon(page: import("@playwright/test").Page, id: string): Promise<void> {
  await page.goto("/?locale=ja");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "polygon-edit.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildPolygonDocument(id)), "utf-8"),
  });

  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByTestId("status-message")).toContainText(/現在のドキュメントを置換しました|Replaced the current document/);
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();

  await page.getByRole("button", { name: /Select island i1|島 i1 を選択/ }).dispatchEvent("click");
  const editCheckbox = page.getByRole("checkbox", { name: EDIT_ISLAND_BOUNDARY_CHECKBOX });
  await expect(editCheckbox).toBeVisible();
  await editCheckbox.check();
}

async function exportCurrentDocument(page: import("@playwright/test").Page) {
  await closeSharePanelIfOpen(page);
  await openLegacyJsonMenu(page);
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_DOCUMENT_JSON_BUTTON }).click();
  const download = await downloadPromise;
  const jsonBuffer = await readDownloadToBuffer(download);
  return JSON.parse(jsonBuffer.toString("utf-8")) as {
    islands: Array<{ id: string; shape?: { kind: string; points?: Array<{ x: number; y: number }> } }>;
  };
}

test("polygon vertex drag keeps constraints and persists edited points", async ({ page }) => {
  await replaceCurrentDocumentWithPolygon(page, "doc_e2e_polygon_vertex_edit");

  const firstVertexHandle = page.getByRole("button", { name: "多角形の頂点 1 を移動" });
  await expect(firstVertexHandle).toBeVisible();
  const handleBox = await firstVertexHandle.boundingBox();
  expect(handleBox).toBeTruthy();

  const startX = (handleBox?.x ?? 0) + (handleBox?.width ?? 0) / 2;
  const startY = (handleBox?.y ?? 0) + (handleBox?.height ?? 0) / 2;
  await firstVertexHandle.dragTo(page.locator("body"), {
    sourcePosition: { x: (handleBox?.width ?? 10) / 2, y: (handleBox?.height ?? 10) / 2 },
    targetPosition: { x: startX + 40, y: startY + 28 },
  });
  await expect(page.getByTestId("status-message")).toContainText("多角形の頂点を移動しました");

  const exportedDocument = await exportCurrentDocument(page);

  const editedIsland = exportedDocument.islands.find((island) => island.id === "i1");
  expect(editedIsland?.shape?.kind).toBe("polygon");
  expect(editedIsland?.shape?.points).toHaveLength(4);
  const movedPoint = editedIsland?.shape?.points?.[0];
  expect(movedPoint).toBeDefined();
  expect(movedPoint?.x).toBeGreaterThan(140);
  expect(movedPoint?.y).toBeGreaterThan(130);
  expect(movedPoint).not.toEqual({ x: 120, y: 120 });
});

test("polygon vertex handles support keyboard nudging and removal", async ({ page }) => {
  await replaceCurrentDocumentWithPolygon(page, "doc_e2e_polygon_vertex_keyboard_edit");

  const firstVertexHandle = page.getByRole("button", { name: "多角形の頂点 1 を移動" });
  await expect(firstVertexHandle).toBeVisible();
  await firstVertexHandle.focus();
  await expect(firstVertexHandle).toBeFocused();
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Shift+ArrowDown");

  const fourthVertexHandle = page.getByRole("button", { name: "多角形の頂点 4 を移動" });
  await fourthVertexHandle.focus();
  await expect(fourthVertexHandle).toBeFocused();
  await page.keyboard.press("Delete");
  await expect(page.getByTestId("status-message")).toContainText("多角形の頂点を削除しました");

  const exportedDocument = await exportCurrentDocument(page);
  const editedIsland = exportedDocument.islands.find((island) => island.id === "i1");
  expect(editedIsland?.shape?.kind).toBe("polygon");
  expect(editedIsland?.shape?.points).toHaveLength(3);
  expect(editedIsland?.shape?.points?.[0]).toEqual({ x: 128, y: 152 });
});
