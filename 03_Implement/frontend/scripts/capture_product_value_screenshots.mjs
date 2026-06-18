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

const files = {
  firstValue: path.join(outputDir, "product-value-first-island.png"),
  ambiguity: path.join(outputDir, "product-value-ambiguity-state.png"),
  ambiguityPreflight: path.join(outputDir, "product-value-ambiguity-share-preflight.png"),
  reviewPack: path.join(outputDir, "product-value-review-pack-trace.png"),
  readOnlyReview: path.join(outputDir, "product-value-review-pack-readonly.png"),
};

const fixedTimestamp = "2026-06-04T00:00:00.000Z";

function buildFirstMeaningfulMapDocument(cardTexts = [
  "利用者が最初に困ること",
  "観察メモから見えた根拠",
  "判断の軸として残す論点",
]) {
  return {
    version: 2,
    id: "doc_first_meaningful_map_mouse",
    title: "First meaningful map mouse fixture",
    createdAt: fixedTimestamp,
    updatedAt: fixedTimestamp,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `mouse-value-card-${index + 1}`,
      text,
      x: 140 + index * 270,
      y: 150 + (index % 2) * 150,
      textReviewed: index === 0,
    })),
    edges: [],
    islands: [],
    readingOrder: cardTexts.map((_, index) => `mouse-value-card-${index + 1}`),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

function buildDomainExpressionDocument() {
  return {
    version: 2,
    id: "doc_domain_expression_keyboard_access",
    title: "domain expression keyboard access fixture",
    createdAt: fixedTimestamp,
    updatedAt: fixedTimestamp,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "domain-target",
        text: "まだ曖昧な主張",
        x: 140,
        y: 130,
        claimType: "unknown",
        textReviewed: false,
        critique: "採用前に確認が必要",
        critiqueTags: ["unclear_boundary"],
      },
      {
        id: "domain-support",
        text: "根拠になる観察メモ",
        x: 430,
        y: 130,
        claimType: "fact",
        textReviewed: true,
      },
      {
        id: "domain-counter",
        text: "反対意見を示す発言",
        x: 430,
        y: 290,
        claimType: "claim",
        textReviewed: false,
      },
    ],
    edges: [],
    islands: [
      {
        id: "domain-island",
        title: "確認が残るまとまり",
        cardIds: ["domain-target", "domain-support", "domain-counter"],
      },
    ],
    readingOrder: ["domain-target", "domain-support", "domain-counter"],
    evidenceLinks: [
      {
        id: "domain-support-link",
        type: "supports",
        fromCardId: "domain-support",
        toCardId: "domain-target",
        createdAt: fixedTimestamp,
      },
      {
        id: "domain-counter-link",
        type: "contradicts",
        fromCardId: "domain-counter",
        toCardId: "domain-target",
        createdAt: fixedTimestamp,
      },
    ],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

function buildReviewPackTraceDocument() {
  return {
    version: 2,
    id: "doc_review_pack_trace_export",
    title: "review pack trace export fixture",
    createdAt: fixedTimestamp,
    updatedAt: fixedTimestamp,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-target", text: "共有前に確認する主張", x: 140, y: 130, claimType: "claim", textReviewed: true },
      { id: "c-support", text: "根拠になる観察メモ", x: 430, y: 130, claimType: "fact", textReviewed: true },
      { id: "c-counter", text: "反対意見を示す発言", x: 430, y: 290, claimType: "claim", textReviewed: false },
    ],
    edges: [],
    islands: [
      {
        id: "i-review",
        title: "共有前に確認するまとまり",
        cardIds: ["c-target", "c-support", "c-counter"],
      },
    ],
    readingOrder: ["c-target", "c-support", "c-counter"],
    evidenceLinks: [
      { id: "e-support", type: "supports", fromCardId: "c-support", toCardId: "c-target", createdAt: fixedTimestamp },
      { id: "e-counter", type: "contradicts", fromCardId: "c-counter", toCardId: "c-target", createdAt: fixedTimestamp },
    ],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

function withoutProductValueContent(document) {
  return {
    ...document,
    cards: [],
    islands: [],
    evidenceLinks: [],
    readingOrder: [],
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

async function captureScreenshot(page, file) {
  await hideTransientStatus(page);
  await page.screenshot({ path: file, fullPage: false });
}

async function routeDocument(page, document, emptyDocument) {
  let shouldReturnSample = false;
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"product-value-loaded"' : '"product-value-empty"' },
      body: JSON.stringify(shouldReturnSample ? document : emptyDocument),
    });
  });
  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

async function captureFirstValue(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const fixture = await routeDocument(page, buildFirstMeaningfulMapDocument(), buildFirstMeaningfulMapDocument([]));
  await page.goto(baseUrl);
  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.getByRole("option", { name: "利用者が最初に困ること" }).click();
  await page.getByRole("option", { name: "観察メモから見えた根拠" }).click({ modifiers: ["Shift"] });
  await page.getByRole("button", { name: /島を作成|Create Island/ }).click();
  await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
  await captureScreenshot(page, files.firstValue);
  await page.close();
}

async function captureAmbiguity(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const fixture = await routeDocument(
    page,
    buildDomainExpressionDocument(),
    withoutProductValueContent(buildDomainExpressionDocument()),
  );
  await page.goto(baseUrl);
  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.getByRole("option", { name: "まだ曖昧な主張" }).click();
  await page.locator('[data-ui-region="selection-context"]').waitFor({ state: "visible" });
  await captureScreenshot(page, files.ambiguity);
  await page.close();
}

async function captureAmbiguityPreflight(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const fixture = await routeDocument(
    page,
    buildDomainExpressionDocument(),
    withoutProductValueContent(buildDomainExpressionDocument()),
  );
  await page.goto(baseUrl);
  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.getByRole("option", { name: "まだ曖昧な主張" }).click();
  await page.getByRole("button", { name: /共有と再現|Share & Reproduce/ }).click();
  const summary = page.getByTestId("share-domain-expression-summary");
  await summary.waitFor({ state: "visible" });
  await summary.scrollIntoViewIfNeeded();
  await captureScreenshot(page, files.ambiguityPreflight);
  await page.close();
}

async function captureReviewPack(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const fixture = await routeDocument(
    page,
    buildReviewPackTraceDocument(),
    withoutProductValueContent(buildReviewPackTraceDocument()),
  );
  await page.goto(baseUrl);
  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.getByRole("option", { name: "共有前に確認する主張" }).click();
  await page.getByRole("button", { name: /共有と再現|Share & Reproduce/ }).click();
  await page.getByLabel(/読解アウトラインを含める|Include reading outline/).uncheck();
  await page.getByLabel(/診断結果を含める|Include diagnostics/).uncheck();
  await page.getByLabel(/詳細（トレースをすべて含める）|Detail \(full trace exports\)/).check();
  await page.locator('[data-panel="share-replay"]').waitFor({ state: "visible" });
  await captureScreenshot(page, files.reviewPack);
  await page.close();
}

async function captureReadOnlyReview(browser) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const fixture = await routeDocument(
    page,
    buildReviewPackTraceDocument(),
    withoutProductValueContent(buildReviewPackTraceDocument()),
  );
  const readOnlyUrl = new URL(baseUrl);
  readOnlyUrl.searchParams.set("readOnly", "1");

  await page.goto(readOnlyUrl.toString());
  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.getByRole("option", { name: "共有前に確認する主張" }).click();
  await page.getByText(/読み取り専用モードが有効|Read-only mode is active/).waitFor({ state: "visible" });
  await captureScreenshot(page, files.readOnlyReview);
  await page.close();
}

async function capture() {
  await mkdir(outputDir, { recursive: true });
  const server = await ensureViteServer();
  const browser = await chromium.launch();

  try {
    await captureFirstValue(browser);
    await captureAmbiguity(browser);
    await captureAmbiguityPreflight(browser);
    await captureReviewPack(browser);
    await captureReadOnlyReview(browser);
    console.log(
      JSON.stringify(
        {
          baseUrl,
          outputDir,
          screenshots: Object.fromEntries(Object.entries(files).map(([name, file]) => [name, path.relative(repoRoot, file)])),
          reusedServer: server.reused,
        },
        null,
        2,
      ),
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
