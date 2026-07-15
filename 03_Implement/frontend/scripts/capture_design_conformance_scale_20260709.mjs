// design-qa-checklist.md conformance review for UX-SCALE-01 (minimap, bulk
// operations bar, orthogonal island outline). Never had a recorded
// screenshot-based review. Modeled on capture_release_screenshots.mjs.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(__dirname, "..");

const host = process.env.KJ_ATLAS_SCREENSHOT_HOST ?? "127.0.0.1";
const port = Number(process.env.KJ_ATLAS_SCREENSHOT_PORT ?? "4173");
const baseUrl = process.env.KJ_ATLAS_SCREENSHOT_BASE_URL ?? `http://${host}:${port}/?locale=ja`;
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(frontendDir, ".tmp-scale-conformance");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  minimapCollapsed: path.join(outputDir, "01-minimap-collapsed.png"),
  minimapExpanded: path.join(outputDir, "02-minimap-expanded.png"),
  islandOutlineTidy: path.join(outputDir, "03-island-outline.png"),
  bulkOpsBar: path.join(outputDir, "04-bulk-ops-bar.png"),
};

function buildDocument() {
  // L-shaped 5-card island to produce a non-trivial orthogonal outline
  // (rather than a plain rectangle) and give the complexity badge something
  // to show (vertexCount - 4) / 2 > 0.
  const cards = [
    { id: "c1", text: "L字クラスタ 1", x: 100, y: 100 },
    { id: "c2", text: "L字クラスタ 2", x: 260, y: 100 },
    { id: "c3", text: "L字クラスタ 3", x: 420, y: 100 },
    { id: "c4", text: "L字クラスタ 4", x: 100, y: 260 },
    { id: "c5", text: "L字クラスタ 5", x: 100, y: 420 },
    // A distant card so the minimap viewport rect and pan target are meaningful.
    { id: "c-far", text: "遠方の単独カード", x: 2400, y: 1800 },
  ];
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Scale conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands: [
      {
        id: "island-l",
        title: "L字の島",
        cardIds: ["c1", "c2", "c3", "c4", "c5"],
      },
    ],
    readingOrder: cards.map((c) => c.id),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

function fetchStatus(url) {
  return new Promise((resolve) => {
    const req = http.get(url, (res) => {
      res.resume();
      resolve(res.statusCode ?? 0);
    });
    req.on("error", () => resolve(0));
    req.setTimeout(1000, () => {
      req.destroy();
      resolve(0);
    });
  });
}

async function waitForServer(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if ((await fetchStatus(url)) === 200) return true;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return false;
}

async function ensureViteServer() {
  const url = `http://${host}:${port}/`;
  if ((await fetchStatus(url)) === 200) return { process: null, reused: true };

  const viteBin = path.join(frontendDir, "node_modules", "vite", "bin", "vite.js");
  const child = spawn(process.execPath, [viteBin, "--host", host, "--port", String(port)], {
    cwd: frontendDir,
    env: { ...process.env },
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });

  let stderr = "";
  child.stderr.on("data", (chunk) => {
    stderr += chunk.toString();
  });

  if (!(await waitForServer(url, 30_000))) {
    child.kill();
    throw new Error(`Vite did not become ready at ${url}\n${stderr}`);
  }

  return { process: child, reused: false };
}

async function routeDocument(page) {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"scale-conformance"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function capture() {
  await mkdir(outputDir, { recursive: true });
  const server = await ensureViteServer();
  const browser = await chromium.launch();

  try {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await routeDocument(page);
    await page.goto(baseUrl);
    await page.getByRole("button", { name: "サンプルを開く" }).click();
    await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

    // Minimap: collapsed trigger first, then expand.
    const collapsedTrigger = page.locator('[data-ui-region="minimap-collapsed-trigger"]');
    if ((await collapsedTrigger.count()) > 0) {
      await page.screenshot({ path: files.minimapCollapsed, fullPage: false });
      await collapsedTrigger.click();
    }
    await page.locator('[data-ui-region="minimap"]').waitFor({ state: "visible" }).catch(() => {});
    await page.screenshot({ path: files.minimapExpanded, fullPage: false });

    // Island outline: right-click the island member area to open context menu,
    // just to bring focus/hover near the outline; then screenshot the canvas
    // with the island's orthogonal outline + complexity badge visible.
    await page.getByRole("option", { name: /L字クラスタ 1/ }).click();
    await page.screenshot({ path: files.islandOutlineTidy, fullPage: false });

    // Bulk operations bar: shift-click a second and third card.
    await page.getByRole("option", { name: /L字クラスタ 2/ }).click({ modifiers: ["Shift"] });
    await page.getByRole("option", { name: /L字クラスタ 3/ }).click({ modifiers: ["Shift"] });
    await page.locator('[data-ui-region="bulk-operations-bar"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.bulkOpsBar, fullPage: false });

    console.log(
      JSON.stringify(
        {
          baseUrl,
          outputDir,
          screenshots: Object.fromEntries(Object.entries(files).map(([name, file]) => [name, path.basename(file)])),
          reusedServer: server.reused,
        },
        null,
        2
      )
    );
  } finally {
    await browser.close();
    if (server.process) server.process.kill();
  }
}

capture().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
