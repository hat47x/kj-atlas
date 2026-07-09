// design-qa-checklist.md conformance review for UX-NAV-01 (work-mode surface,
// ADR-0031 Area 4). Never had a screenshot-based review. Modeled on
// capture_release_screenshots.mjs.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(frontendDir, ".tmp-navmode-conformance");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  selectionContextBasic: path.join(outputDir, "01-selection-context-basic.png"),
  workModeContentPending: path.join(outputDir, "02-work-mode-content-pending.png"),
  workModeAdvancedOpen: path.join(outputDir, "03-work-mode-advanced-open.png"),
  afterEscapeFocusReturn: path.join(outputDir, "04-after-escape-focus-return.png"),
};

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Work-mode conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "対象カード", x: 150, y: 150, claimType: "fact", textReviewed: true }],
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
      headers: { ETag: '"navmode-conformance"' },
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
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await routeDocument(page);
    await page.goto(baseUrl);
    await page.getByRole("button", { name: "サンプルを開く" }).click();
    await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

    // Select the card: selection-context aside should show only the target
    // card + basic edit/review, with no advanced blob (UX-OPERABILITY-03).
    await page.getByRole("option", { name: /対象カード/ }).click();
    await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.selectionContextBasic, fullPage: false });

    // Open work mode WITHOUT enabling Advanced UI first: confirm the
    // empty-state ("content_pending") copy.
    const workModeTrigger = page.getByRole("button", { name: "作業モード" }).first();
    await workModeTrigger.click();
    await page.locator('[data-ui-region="work-mode"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.workModeContentPending, fullPage: false });
    await page.keyboard.press("Escape");
    await page.locator('[data-ui-region="work-mode"]').waitFor({ state: "hidden" });

    // Enable Advanced UI, then reopen work mode: confirm NarrativesPanel +
    // HilRsWorkflowPanel (diff/merge/AI-suggest) render inside work-mode, and
    // are absent from selection-context.
    await page.getByRole("button", { name: "詳細" }).click();
    await workModeTrigger.click();
    await page.locator('[data-ui-region="work-mode"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.workModeAdvancedOpen, fullPage: true });

    // Escape closes work-mode and returns focus to the trigger button.
    await page.keyboard.press("Escape");
    await page.locator('[data-ui-region="work-mode"]').waitFor({ state: "hidden" });
    const focusReturned = await workModeTrigger.evaluate((el) => el === document.activeElement);
    await page.screenshot({ path: files.afterEscapeFocusReturn, fullPage: false });

    console.log(
      JSON.stringify(
        {
          baseUrl,
          outputDir,
          focusReturnedToTrigger: focusReturned,
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
