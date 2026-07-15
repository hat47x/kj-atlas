// design-qa-checklist.md conformance review for UX-MENU-01 (menu bar / slim
// toolbar) -- this feature never had a recorded screenshot-based review.
// Modeled on capture_release_screenshots.mjs.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(frontendDir, ".tmp-menu-conformance");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  desktopClosed: path.join(outputDir, "01-desktop-1440-closed.png"),
  desktopFileOpen: path.join(outputDir, "02-desktop-1440-file-open.png"),
  desktopWorkOpen: path.join(outputDir, "03-desktop-1440-work-open.png"),
  desktopShareOpen: path.join(outputDir, "04-desktop-1440-share-open.png"),
  tablet768: path.join(outputDir, "05-tablet-768.png"),
  mobile390Closed: path.join(outputDir, "06-mobile-390-closed.png"),
  mobile390Open: path.join(outputDir, "07-mobile-390-open.png"),
};

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Menu conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "サンプルカード", x: 150, y: 150, claimType: "fact", textReviewed: true }],
    edges: [],
    islands: [],
    readingOrder: ["c1"],
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
      headers: { ETag: '"menu-conformance"' },
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

    await page.screenshot({ path: files.desktopClosed, fullPage: false });

    await page.locator('[data-ui-menu-category="file"]').click();
    await page.locator('[role="menu"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.desktopFileOpen, fullPage: false });
    await page.keyboard.press("Escape");

    await page.locator('[data-ui-menu-category="work"]').click();
    await page.locator('[role="menu"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.desktopWorkOpen, fullPage: false });
    await page.keyboard.press("Escape");

    await page.locator('[data-ui-menu-category="share"]').click();
    await page.locator('[role="menu"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.desktopShareOpen, fullPage: false });
    await page.keyboard.press("Escape");

    await page.setViewportSize({ width: 768, height: 1024 });
    await page.screenshot({ path: files.tablet768, fullPage: false });

    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: files.mobile390Closed, fullPage: false });

    const menuTrigger = page.locator('[data-ui-region="menu-bar"] [role="menuitem"]').first();
    await menuTrigger.click();
    await page.locator('[role="menu"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.mobile390Open, fullPage: false });

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
