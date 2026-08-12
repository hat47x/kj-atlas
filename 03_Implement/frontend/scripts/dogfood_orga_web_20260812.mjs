// DOGFOOD-01 / adopting-org-patterns.md §3.5: Org-A batch pattern via the WEB path.
// Opens the real 50-card batch document (dogfood_orga_batch_20260812) through the
// start panel's "recent documents" flow against a real backend (not a mocked route),
// then exercises island formation + save round-trip. One-off exploratory dogfood
// script, not wired into CI. Narrates observations to stdout for the dogfood log.
//
// REPRO NOTE (DOGFOOD-02): with a stale `doc_phase1_canvas` (version: 2) present in
// the dev DB, the WEB first-run path is blocked BEFORE this script's batch-doc flow
// can run: App.tsx auto-loads DEFAULT_DOCUMENT_ID and the 500 renders an error status
// with an empty canvas (see issue-DOGFOOD-02 "実地確認"). Use a DB without the stale
// doc, or clear it, to exercise the Org-A batch flow on the Web path.
import { chromium } from "@playwright/test";

const BASE_URL = process.env.KJ_ATLAS_DOGFOOD_URL ?? "http://127.0.0.1:4173/?locale=ja";
const DOC_ID = process.env.KJ_ATLAS_DOGFOOD_DOC_ID ?? "dogfood_orga_batch_20260812";

function log(step, message) {
  console.log(`\n[${step}] ${message}`);
}

async function run() {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });
  page.on("console", (msg) => {
    if (msg.type() === "error") console.log(`  [browser console error] ${msg.text()}`);
  });
  page.on("pageerror", (err) => console.log(`  [browser page error] ${err.message}`));
  page.on("response", (response) => {
    if (response.status() >= 400) console.log(`  [network ${response.status()}] ${response.url()}`);
  });

  log("setup", `navigating to ${BASE_URL}`);
  await page.goto(BASE_URL);
  await page.waitForTimeout(600);

  // The start panel ("start-document-entry") should be visible on first load.
  const startPanel = page.locator('[data-panel="start-document-entry"]');
  const startVisible = await startPanel.isVisible().catch(() => false);
  log("setup", `start panel visible on first load: ${startVisible}`);

  // Step A: open the batch document via the recent-documents flow.
  log("stepA", `selecting "${DOC_ID}" in the recent-documents dropdown`);
  const recentSelect = page.locator('[data-panel="start-document-entry"] select').first();
  await recentSelect.waitFor({ state: "visible", timeout: 8000 });
  await recentSelect.selectOption({ label: DOC_ID });
  const openRecent = page.locator('[data-panel="start-document-entry"] button').filter({ hasText: /開く|Open/ }).first();
  await openRecent.click();
  await page.waitForTimeout(1200);

  // Count canvas cards after load.
  const cards = page.locator('[data-ui-region="primary-flow"]').getByRole("option");
  const cardCount = await cards.count().catch(() => -1);
  log("stepA", `canvas card count after opening batch doc: ${cardCount} (expected 50)`);

  // Step B: island formation from 2 related cards.
  log("stepB", "selecting two opinion cards and creating an island");
  const b1 = page.locator('[data-ui-region="primary-flow"]').getByRole("option").nth(0);
  const b2 = page.locator('[data-ui-region="primary-flow"]').getByRole("option").nth(1);
  await b1.click({ position: { x: 12, y: 12 } }).catch(() => {});
  await page.waitForTimeout(200);
  await b2.click({ modifiers: ["Shift"], position: { x: 12, y: 12 } }).catch(() => {});
  await page.waitForTimeout(200);
  const islandBtn = page.getByRole("banner").getByRole("button", { name: /島を作成|Create Island/ });
  const canCreate = await islandBtn.isEnabled().catch(() => false);
  log("stepB", `"create island" enabled with 2 cards selected: ${canCreate}`);
  if (canCreate) {
    await islandBtn.click();
    await page.waitForTimeout(500);
    log("stepB", "island created ✅");
  }

  // Step C: save round-trip to the real backend.
  log("stepC", "saving document to the real backend");
  const saveBtn = page.getByRole("button", { name: /保存|Save/ }).first();
  const canSave = await saveBtn.isEnabled().catch(() => false);
  log("stepC", `save button enabled: ${canSave}`);
  if (canSave) {
    await saveBtn.click();
    await page.waitForTimeout(800);
    const status = await page.getByTestId("status-message").textContent().catch(() => null);
    log("stepC", `status message after save: "${status}"`);
  }

  await browser.close();
  log("done", "Org-A Web-path dogfood run complete");
}

run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
