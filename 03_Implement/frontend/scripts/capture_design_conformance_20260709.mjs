// One-off capture for the design-qa-checklist.md conformance review of this
// session's shipped features (DOMAIN-KA-01, DOMAIN-TRACE-01, UX-SHARE-01,
// UI-QUALITY-A11Y-02). Modeled on capture_release_screenshots.mjs. Not part
// of the regular release screenshot set -- outputs to a scratch directory.
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
const outputDir = process.env.KJ_ATLAS_SCREENSHOT_OUTPUT_DIR ?? path.resolve(repoRoot, "03_Implement", "backend", ".tmp", "design-conformance-20260709");

const ts = "2026-07-09T00:00:00.000Z";

const files = {
  selectionContextChips: path.join(outputDir, "01-selection-context-chips.png"),
  kaEditor: path.join(outputDir, "02-ka-editor.png"),
  traceEditorAndBadgeOff: path.join(outputDir, "03-trace-editor-badge-off.png"),
  seqBadgeOn: path.join(outputDir, "04-seq-badge-on.png"),
  preShareGate: path.join(outputDir, "05-pre-share-gate.png"),
  preShareGateZeroSkip: path.join(outputDir, "06-pre-share-zero-skip.png"),
};

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Design conformance fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "c-target",
        text: "現地で聞いた率直な言葉",
        x: 150,
        y: 150,
        claimType: "claim",
        textReviewed: false,
        holdState: "held",
        critique: "採用前に確認が必要",
        meta: { seq: 12, source: "インタビューA 12行目" },
        ka: { voice: "本当は誰かに頼りたい", value: "自分で決めたい" },
      },
      { id: "c-support", text: "裏付けとなる観察メモ", x: 430, y: 150, claimType: "fact", textReviewed: true },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c-target", "c-support"],
    evidenceLinks: [
      { id: "ev-1", type: "supports", fromCardId: "c-support", toCardId: "c-target", createdAt: ts },
    ],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

function buildCleanDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Clean fixture",
    createdAt: ts,
    updatedAt: ts,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "レビュー済みの一言", x: 0, y: 0, textReviewed: true }],
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

async function clickButtonByText(page, fragments) {
  const match = page.locator("button").filter({
    hasText: new RegExp(fragments.map((fragment) => escapeRegExp(fragment)).join("|")),
  });
  await match.first().click();
}

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

async function routeDocument(page, getDocument) {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"design-conformance"' },
      body: JSON.stringify(getDocument()),
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
    await routeDocument(page, buildDocument);
    await page.goto(baseUrl);
    await clickButtonByText(page, ["サンプルを開く"]);
    await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

    await page.getByRole("option", { name: /現地で聞いた率直な言葉/ }).click();
    await page.locator('[data-panel="selection-context"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.selectionContextChips, fullPage: false });

    const kaEditor = page.locator('[data-panel="card-ka-editor"]');
    if ((await kaEditor.count()) === 0) {
      await page.getByText("遡及情報").first().scrollIntoViewIfNeeded().catch(() => {});
    }
    await kaEditor.scrollIntoViewIfNeeded().catch(() => {});
    await page.screenshot({ path: files.kaEditor, fullPage: false });

    const traceEditor = page.locator('[data-panel="card-trace-editor"]');
    await traceEditor.scrollIntoViewIfNeeded().catch(() => {});
    await page.screenshot({ path: files.traceEditorAndBadgeOff, fullPage: false });

    await clickButtonByText(page, ["表示"]);
    await page.getByLabel(/通し番号をカードに表示/).check();
    await page.keyboard.press("Escape");
    await page.screenshot({ path: files.seqBadgeOn, fullPage: false });

    await clickButtonByText(page, ["共有と再現"]);
    await page.locator('[data-panel="share-replay"]').waitFor({ state: "visible" });
    await clickButtonByText(page, ["レビューパックを書き出す"]);
    await page.locator('[data-panel="pre-share-summary-gate"]').waitFor({ state: "visible" });
    await page.screenshot({ path: files.preShareGate, fullPage: false });

    await browser.close();

    const browser2 = await chromium.launch();
    const page2 = await browser2.newPage({ viewport: { width: 1440, height: 900 } });
    await routeDocument(page2, buildCleanDocument);
    await page2.goto(baseUrl);
    await clickButtonByText(page2, ["サンプルを開く"]);
    await page2.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });
    await clickButtonByText(page2, ["共有と再現"]);
    await page2.locator('[data-panel="share-replay"]').waitFor({ state: "visible" });
    await page2.screenshot({ path: files.preShareGateZeroSkip, fullPage: false });
    await browser2.close();

    console.log(
      JSON.stringify(
        {
          baseUrl,
          outputDir,
          screenshots: Object.fromEntries(Object.entries(files).map(([name, file]) => [name, path.relative(repoRoot, file)])),
          reusedServer: server.reused,
        },
        null,
        2
      )
    );
  } finally {
    if (server.process) server.process.kill();
  }
}

capture().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
