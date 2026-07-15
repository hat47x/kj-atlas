// design-qa-checklist.md conformance review for UX-EMPTY-01 (empty-canvas
// core-loop onboarding hint). Never had a screenshot-based review. Modeled
// on capture_release_screenshots.mjs.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(frontendDir, ".tmp-empty-conformance");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  emptyHintVisible: path.join(outputDir, "01-empty-hint-visible.png"),
  hintGoneAfterFirstCard: path.join(outputDir, "02-hint-gone-after-first-card.png"),
  viewControlsResetOption: path.join(outputDir, "03-view-controls-reset-option.png"),
};

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Empty canvas conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    readingOrder: [],
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
      headers: { ETag: '"empty-conformance"' },
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
    // The routed fixture above returns 0 cards regardless of which
    // StartPanel entry point is used, so the usual "sample" trigger opens an
    // empty canvas here.
    await page.getByRole("button", { name: "サンプルを開く" }).click();
    await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

    await page.locator('[data-ui-region="empty-canvas-hint"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.emptyHintVisible, fullPage: false });

    // First card creation must make the hint disappear and must not steal focus
    // away from the canvas in a way that breaks the existing keyboard contract.
    await page.getByRole("button", { name: "最初のカードを書く" }).click();
    await page.locator('[data-ui-region="empty-canvas-hint"]').waitFor({ state: "hidden" });
    await page.screenshot({ path: files.hintGoneAfterFirstCard, fullPage: false });

    // View controls panel should offer a re-show option now that the hint is completed.
    await page.locator('[data-focus-return-id="view-controls-trigger"]').click();
    await page.locator('[data-panel="view"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.viewControlsResetOption, fullPage: false });

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
