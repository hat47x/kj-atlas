// Captures a comprehensive catalog of current UI elements for user-facing docs and
// design-review handoff. Complements capture_release_screenshots.mjs (entry flow)
// and capture_product_value_screenshots.mjs (value states). Deterministic data, ja
// locale, KJ_ATLAS_LLM_PROVIDER=none. No secrets/customer data.
import { chromium } from "@playwright/test";
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(__dirname, "..");
const repoRoot = path.resolve(frontendDir, "..", "..");

const host = process.env.KJ_ATLAS_SCREENSHOT_HOST ?? "127.0.0.1";
const port = Number(process.env.KJ_ATLAS_SCREENSHOT_PORT ?? "4173");
const baseUrl = process.env.KJ_ATLAS_SCREENSHOT_BASE_URL ?? `http://${host}:${port}/?locale=ja`;
const outputDir =
  process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ??
  path.resolve(repoRoot, "04_Documentation", "assets", "screenshots");

const ts = "2026-06-05T00:00:00.000Z";

function out(name) {
  return path.join(outputDir, name);
}

function buildCatalogDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "UI catalog fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-fact", text: "観察した事実メモ", x: 150, y: 150, claimType: "fact", textReviewed: true },
      { id: "c-claim", text: "そこから言える主張", x: 430, y: 150, claimType: "claim", textReviewed: false },
      { id: "c-hyp", text: "仮説として残す問い", x: 150, y: 330, claimType: "hypothesis", textReviewed: false, holdState: "pending" },
      {
        id: "c-unknown",
        text: "まだ曖昧な主張",
        x: 430,
        y: 330,
        claimType: "unknown",
        textReviewed: false,
        holdState: "held",
        critique: "採用前に確認が必要",
        critiqueTags: ["unclear_boundary"],
      },
    ],
    edges: [
      { id: "edge-1", from: "c-fact", to: "c-claim", kind: "relates" },
      { id: "edge-2", from: "c-claim", to: "c-unknown", kind: "relates" },
    ],
    islands: [
      {
        id: "island-1",
        title: "確認が残るまとまり",
        cardIds: ["c-fact", "c-claim"],
        shape: { kind: "rect", x: 100, y: 100, width: 600, height: 140 },
      },
    ],
    readingOrder: ["c-fact", "c-claim", "c-hyp", "c-unknown"],
    evidenceLinks: [
      { id: "ev-1", type: "supports", fromCardId: "c-fact", toCardId: "c-claim", createdAt: ts },
      { id: "ev-2", type: "contradicts", fromCardId: "c-unknown", toCardId: "c-claim", createdAt: ts },
    ],
    narratives: [],
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

async function hideTransientStatus(page) {
  await page
    .locator('[data-testid="status-message"]')
    .evaluate((element) => {
      element.style.display = "none";
    })
    .catch(() => {});
}

async function routeSample(page, document) {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  let enabled = false;
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: enabled ? '"catalog-loaded"' : '"catalog-empty"' },
      body: JSON.stringify(enabled ? document : { ...document, cards: [], islands: [], edges: [], evidenceLinks: [], readingOrder: [] }),
    });
  });
  return { enable: () => { enabled = true; } };
}

async function openSample(browser, { width = 1440, height = 900, readOnly = false } = {}) {
  const page = await browser.newPage({ viewport: { width, height } });
  const fixture = await routeSample(page, buildCatalogDocument());
  const url = new URL(baseUrl);
  if (readOnly) url.searchParams.set("readOnly", "1");
  await page.goto(url.toString());
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" }).catch(() => {});
  fixture.enable();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" }).catch(() => {});
  await hideTransientStatus(page);
  return page;
}

const results = [];
async function step(name, fn) {
  try {
    await fn();
    results.push({ name, ok: true });
    console.log(`OK   ${name}`);
  } catch (error) {
    results.push({ name, ok: false, error: String(error && error.message ? error.message : error).split("\n")[0] });
    console.log(`FAIL ${name}: ${String(error && error.message ? error.message : error).split("\n")[0]}`);
  }
}

async function capture() {
  await mkdir(outputDir, { recursive: true });
  const server = await ensureViteServer();
  const browser = await chromium.launch();
  try {
    // 1. Header / primary toolbar (clip to the top band)
    await step("ui-header-toolbar", async () => {
      const page = await openSample(browser);
      await page.screenshot({ path: out("ui-header-toolbar.png"), clip: { x: 0, y: 0, width: 1440, height: 132 } });
      await page.close();
    });

    // 2. Canvas with domain badges (claimType / holdState / critique / unreviewed)
    await step("ui-card-domain-badges", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /まだ曖昧な主張/ }).click();
      await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-card-domain-badges.png"), clip: { x: 0, y: 120, width: 980, height: 560 } });
      await page.close();
    });

    // 3. Selection-context for a card (basic) with hold-state control
    await step("ui-selection-context-holdstate", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /まだ曖昧な主張/ }).click();
      const aside = page.locator('[data-ui-region="selection-context"]');
      await aside.waitFor({ state: "visible" });
      await page.getByText(/判断保留/).first().scrollIntoViewIfNeeded().catch(() => {});
      await hideTransientStatus(page);
      await aside.screenshot({ path: out("ui-selection-context-holdstate.png") });
      await page.close();
    });

    // 4. Island selection-context
    await step("ui-selection-context-island", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /確認が残るまとまり/ }).first().click().catch(async () => {
        // fallback: click island title text
        await page.getByText(/確認が残るまとまり/).first().click();
      });
      await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.locator('[data-ui-region="selection-context"]').screenshot({ path: out("ui-selection-context-island.png") });
      await page.close();
    });

    // 5. Advanced ON -> work-mode panels surfaced in the side panel
    await step("ui-advanced-work-mode-panels", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /まだ曖昧な主張/ }).click();
      await page.getByRole("button", { name: /^詳細$|^Advanced$/ }).click();
      await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.locator('[data-ui-region="selection-context"]').screenshot({ path: out("ui-advanced-work-mode-panels.png") });
      await page.close();
    });

    // 6. View controls flyout (display modes + SafeMode)
    await step("ui-view-controls", async () => {
      const page = await openSample(browser);
      await page.locator('[data-focus-return-id="view-controls-trigger"]').click();
      await page.locator('[data-panel="view"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-view-controls.png") });
      await page.close();
    });

    // 7. Card context menu (right-click)
    await step("ui-card-context-menu", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /そこから言える主張/ }).click({ button: "right" });
      await page.waitForTimeout(300);
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-card-context-menu.png"), clip: { x: 0, y: 120, width: 980, height: 560 } });
      await page.close();
    });

    // 8. Card inline edit (double-click)
    await step("ui-card-inline-edit", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /そこから言える主張/ }).dblclick();
      await page.waitForTimeout(300);
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-card-inline-edit.png"), clip: { x: 0, y: 120, width: 980, height: 560 } });
      await page.close();
    });

    // 9. Share & Reproduce pre-share preflight (full panel)
    await step("ui-share-preflight", async () => {
      const page = await openSample(browser);
      await page.getByRole("option", { name: /そこから言える主張/ }).click();
      await page.getByRole("button", { name: /共有と再現|Share & Reproduce/ }).click();
      await page.locator('[data-panel="share-replay"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.locator('[data-panel="share-replay"]').screenshot({ path: out("ui-share-preflight.png") });
      await page.close();
    });

    // 10. Read-only mode
    await step("ui-read-only-mode", async () => {
      const page = await openSample(browser, { readOnly: true });
      await page.getByRole("option", { name: /そこから言える主張/ }).click();
      await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-read-only-mode.png") });
      await page.close();
    });

    // 11-12. Responsive widths
    await step("ui-responsive-768", async () => {
      const page = await openSample(browser, { width: 768, height: 900 });
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-responsive-768.png") });
      await page.close();
    });
    await step("ui-responsive-960", async () => {
      const page = await openSample(browser, { width: 960, height: 900 });
      await hideTransientStatus(page);
      await page.screenshot({ path: out("ui-responsive-960.png") });
      await page.close();
    });

    console.log(JSON.stringify({ baseUrl, outputDir: path.relative(repoRoot, outputDir), reusedServer: server.reused, results }, null, 2));
  } finally {
    await browser.close();
    if (server.process) server.process.kill();
  }
  const failed = results.filter((r) => !r.ok);
  if (failed.length) process.exitCode = 2;
}

capture().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
