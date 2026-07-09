// design-qa-checklist.md conformance review for DOMAIN-KJ-01 (relation
// symbol vocabulary: causal arrow, mutual double-arrow, equivalence "=",
// negate dashed line). Never had a screenshot-based review; this exact
// rendering layer previously had a real bug (all edges +100000px offscreen)
// found and fixed earlier this session. Modeled on capture_release_screenshots.mjs.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(frontendDir, ".tmp-kj-conformance");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  allSymbols: path.join(outputDir, "01-edge-symbols-overview.png"),
  inspectorOpen: path.join(outputDir, "02-edge-inspector-open.png"),
  unknownTypePreserved: path.join(outputDir, "03-unknown-type-plain.png"),
};

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "KJ vocabulary conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [
      { id: "c1", text: "原因カード", x: 0, y: 0 },
      { id: "c2", text: "結果カード", x: 400, y: 0 },
      { id: "c3", text: "相互A", x: 0, y: 250 },
      { id: "c4", text: "相互B", x: 400, y: 250 },
      { id: "c5", text: "同値A", x: 0, y: 500 },
      { id: "c6", text: "同値B", x: 400, y: 500 },
      { id: "c7", text: "対立A", x: 0, y: 750 },
      { id: "c8", text: "対立B", x: 400, y: 750 },
      { id: "c9", text: "未知種別A", x: 0, y: 1000 },
      { id: "c10", text: "未知種別B", x: 400, y: 1000 },
    ],
    edges: [
      { id: "e-causal", fromId: "c1", toId: "c2", type: "causal" },
      { id: "e-mutual", fromId: "c3", toId: "c4", type: "mutual" },
      { id: "e-equivalence", fromId: "c5", toId: "c6", type: "equivalence" },
      { id: "e-negate", fromId: "c7", toId: "c8", type: "negate" },
      { id: "e-unknown", fromId: "c9", toId: "c10", type: "future-vocab-2030" },
    ],
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
      headers: { ETag: '"kj-conformance"' },
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
    const page = await browser.newPage({ viewport: { width: 1440, height: 1400 } });
    await routeDocument(page);
    await page.goto(baseUrl);
    await page.getByRole("button", { name: "サンプルを開く" }).click();
    await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

    await page.screenshot({ path: files.allSymbols, fullPage: true });

    // Click the causal edge's hit-line to open the inspector (coordinates are
    // in the world -100000..+100000 space, so use dispatchEvent like the
    // existing e2e_type_vocabulary.spec.ts does).
    const hitLine = page.locator('[data-ui-region="primary-flow"] svg line[stroke="transparent"]').first();
    await hitLine.dispatchEvent("click");
    await page.getByTestId("edge-type-select").waitFor({ state: "visible" }).catch(() => {});
    await page.screenshot({ path: files.inspectorOpen, fullPage: false });

    // Focus on the unknown-type edge specifically to confirm it renders plain
    // (no symbol) and its preservation notice reads correctly.
    const hitLines = page.locator('[data-ui-region="primary-flow"] svg line[stroke="transparent"]');
    const count = await hitLines.count();
    await hitLines.nth(count - 1).dispatchEvent("click");
    await page.screenshot({ path: files.unknownTypePreserved, fullPage: false });

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
