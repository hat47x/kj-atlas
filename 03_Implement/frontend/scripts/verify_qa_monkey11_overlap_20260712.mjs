// Re-verification requested by Claude Design's conformance review (P31,
// 2026-07-11 △ finding): the b1-05b screenshot from
// capture_design_review_20260711.mjs did not show a visible overlap for the
// "Suggest layout" button, even though a real Playwright click on that
// button was intercepted during the DOMAIN-EXPR-03 verification script
// (domain_expr03_provider_local_e2e.mjs) and again during the design-review
// capture run. This script isolates that exact moment: it reads
// document.elementFromPoint() at the button's own center coordinates
// immediately before attempting a real mouse click, so the finding is
// settled by hard evidence instead of a static screenshot that may miss a
// transient re-render.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(repoRoot, ".tmp-overlap-verify");

function file(name) {
  return path.join(outputDir, name);
}

const ts = "2026-07-12T00:00:00.000Z";

function buildDoc() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Overlap re-verification fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "利用者が最初に迷う導線", x: 100, y: 100, claimType: "claim", textReviewed: true },
      { id: "c2", text: "同じ迷いを示す別の観察", x: 380, y: 100, claimType: "claim", textReviewed: true },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const mockMergeSuggestions = {
  suggestions: [
    {
      groupId: "group-nav-confusion",
      targetCardId: "c1",
      candidateCardIds: ["c2"],
      scoreSummary: { min: 0.88, max: 0.95, avg: 0.91 },
      reasonCodes: ["heuristic:normalized-text"],
      snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
      cardIds: ["c1", "c2"],
      mergedTextDraft: "利用者が最初に迷う導線（統合案）",
      rationale: "同じ迷いを指す2枚の重複",
    },
  ],
};

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

async function run() {
  await mkdir(outputDir, { recursive: true });
  const server = await ensureViteServer();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 1200 } });

  await page.route("**/packs/index.json", (route) => route.fulfill({ status: 404, contentType: "application/json", body: "{}" }));
  await page.route("**/docs/doc_phase1_canvas", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", headers: { ETag: '"overlap-verify"' }, body: JSON.stringify(buildDoc()) }));
  await page.route("**/ai/provider-status", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "local" }) }));
  await page.route("**/ai/suggest-merges", (route) =>
    route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mockMergeSuggestions) }));

  await page.goto(baseUrl);
  await page.locator('button', { hasText: /サンプルを開く|Open sample/ }).first().click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });
  await page.locator('button', { hasText: /^詳細$|^Advanced$/ }).first().click();
  await page.locator('button', { hasText: /^作業モード$|^Work mode$/ }).first().click();
  await page.locator('[data-ui-region="work-mode"]').waitFor({ state: "visible" });

  console.log("[step] collecting candidates");
  await page.getByRole("button", { name: /Collect candidates|候補を収集/i }).click();
  await page.getByText(/利用者が最初に迷う導線（統合案）/).first().waitFor({ state: "visible" });

  const suggestButton = page.getByRole("button", { name: /Suggest layout|配置を提案/ }).first();

  // Hypothesis test: is this a settle-timing race (layout still reflowing
  // right after the candidate list renders) rather than a persistent CSS
  // overlap? Check the geometry BOTH immediately and after a short settle.
  const immediateBox = await suggestButton.boundingBox();
  console.log("[step] suggestButton boundingBox IMMEDIATELY after candidates appear:", immediateBox);
  await page.waitForTimeout(400);
  const settledBox = await suggestButton.boundingBox();
  console.log("[step] suggestButton boundingBox AFTER 400ms settle:", settledBox);

  // Read the button's own bounding box, then ask the DOM what element is
  // actually hit-tested at that exact center point -- this is the
  // ground-truth check for whether something else covers it.
  const box = await suggestButton.boundingBox();
  if (!box) {
    console.log("[result] suggestButton has no bounding box (not rendered) -- cannot verify");
  } else {
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    const hit = await page.evaluate(([x, y]) => {
      const el = document.elementFromPoint(x, y);
      if (!el) return null;
      return {
        tag: el.tagName,
        text: (el.textContent ?? "").trim().slice(0, 80),
        isSuggestButton: el.closest("button")?.textContent?.includes("配置を提案") ?? false,
        rect: el.getBoundingClientRect(),
      };
    }, [cx, cy]);
    console.log("[step] suggestButton boundingBox:", box);
    console.log("[step] elementFromPoint at button center:", JSON.stringify(hit, null, 2));

    await page.screenshot({ path: file("overlap-verify-before-click.png"), fullPage: false });

    // Zoomed crop tightly around the button's own box (with margin) to see
    // pixel-level overlap if any exists.
    const clip = {
      x: Math.max(0, box.x - 40),
      y: Math.max(0, box.y - 60),
      width: box.width + 80,
      height: box.height + 140,
    };
    await page.screenshot({ path: file("overlap-verify-zoomed-crop.png"), clip });
  }

  // Now attempt the REAL mouse click (not keyboard) and record whether it
  // throws, to reproduce the exact original finding.
  let clickError = null;
  try {
    await suggestButton.click({ timeout: 5000 });
    console.log("[result] real mouse click SUCCEEDED (no interception)");
  } catch (error) {
    clickError = error.message;
    console.log("[result] real mouse click FAILED:", error.message.split("\n")[0]);
  }

  await page.screenshot({ path: file("overlap-verify-after-click-attempt.png"), fullPage: false });

  console.log(JSON.stringify({ clickError }, null, 2));
  await browser.close();
  if (server.process) server.process.kill();
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
