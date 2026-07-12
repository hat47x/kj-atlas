// Claude Design P32 follow-up (single live check): with the evidence
// overlay (sky #0369a1 solid lines) active, is the teal search-match
// outline (#0d9488 3px active / #5eead4 2px) distinguishable when both
// touch the same card? Produces a zoomed screenshot for the next
// conformance round. One-off; not wired into CI.
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
const baseUrl = `http://${host}:${port}/?locale=ja`;
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(repoRoot, ".tmp-teal-sky");

const ts = "2026-07-12T00:00:00.000Z";

function buildDoc() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Teal vs sky live check fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "検索でこの一致を確認する", x: 200, y: 200, claimType: "claim", textReviewed: true },
      { id: "c2", text: "裏付けとなる観察メモ", x: 560, y: 220, claimType: "fact", textReviewed: true },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2"],
    narratives: [],
    evidenceLinks: [{ id: "ev-1", type: "supports", fromCardId: "c2", toCardId: "c1", createdAt: ts }],
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
  if (!(await waitForServer(url, 30_000))) {
    child.kill();
    throw new Error(`Vite did not become ready at ${url}`);
  }
  return { process: child, reused: false };
}

async function run() {
  await mkdir(outputDir, { recursive: true });
  const server = await ensureViteServer();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  await page.route("**/packs/index.json", (route) => route.fulfill({ status: 404, contentType: "application/json", body: "{}" }));
  await page.route("**/docs/doc_phase1_canvas", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", headers: { ETag: '"teal-sky"' }, body: JSON.stringify(buildDoc()) }));
  await page.route("**/ai/provider-status", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) }));

  await page.goto(baseUrl);
  await page.locator("button", { hasText: /サンプルを開く/ }).first().click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

  // Enable the evidence overlay (sky lines) from the View panel.
  await page.locator("button", { hasText: /^表示$/ }).first().click();
  await page.getByLabel(/根拠オーバーレイを有効化/).check();
  await page.keyboard.press("Escape");

  // Activate a search that matches the evidence-target card -> teal outline.
  const searchInput = page.getByPlaceholder(/カードを検索/);
  await searchInput.click();
  await searchInput.fill("検索でこの一致");
  await page.waitForTimeout(400);

  // The evidence overlay draws lines only for the selected card. Select the
  // matched card: isActiveSearchMatch takes outline precedence over
  // isSelected, so the teal outline stays while the sky evidence line
  // appears -- the exact co-occurrence P32 asked to check.
  await page.getByRole("option", { name: /検索でこの一致を確認する/ }).click({ position: { x: 12, y: 12 } });
  await page.waitForTimeout(400);

  await page.screenshot({ path: path.join(outputDir, "teal-vs-sky-full.png"), fullPage: false });
  await page.screenshot({
    path: path.join(outputDir, "teal-vs-sky-zoom.png"),
    clip: { x: 120, y: 120, width: 700, height: 320 },
  });

  console.log(JSON.stringify({ outputDir, done: true }, null, 2));
  await browser.close();
  if (server.process) server.process.kill();
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
