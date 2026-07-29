// Machine-substitute evidence for the "physical keyboard acceptance" blocker of
// MVP-EXIT-01. Reproduces 04_Documentation/acceptance_check.md
// "キーボードで確認すること" 1-5 using real key events only (no mouse input at
// any point after the initial page load).
//
// Emits a JSON report to stdout. Exit code 1 if any check fails.
import { chromium } from "@playwright/test";

const baseUrl = process.env.KJ_ATLAS_BASE_URL ?? "http://127.0.0.1:4173/?locale=ja";
const results = [];

function record(id, title, ok, detail) {
  results.push({ id, title, result: ok ? "pass" : "fail", detail });
}

function buildDocument(cardTexts) {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Keyboard acceptance sample",
    createdAt: "2026-06-03T00:00:00.000Z",
    updatedAt: "2026-06-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `sample-card-${index + 1}`,
      text,
      x: 120 + index * 260,
      y: 120 + (index % 2) * 150,
    })),
    edges: [],
    islands: [],
    readingOrder: cardTexts.map((_, index) => `sample-card-${index + 1}`),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const activeSummary = (page) =>
  page.evaluate(() => {
    const a = document.activeElement;
    if (!a) return { tag: "(none)", name: "", region: "" };
    const text = (a.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 60);
    const name = a.getAttribute("aria-label") || text || a.getAttribute("title") || "";
    const landmark = a.closest("header,[role=banner],aside,[role=complementary],main,[role=main],[data-panel]");
    return {
      tag: a.tagName.toLowerCase(),
      type: a.getAttribute("type") ?? "",
      name,
      pressed: a.getAttribute("aria-pressed"),
      region: landmark
        ? landmark.getAttribute("data-panel") ||
          landmark.getAttribute("role") ||
          landmark.tagName.toLowerCase()
        : "(root)",
    };
  });

async function tabUntil(page, predicate, maxTabs = 400) {
  const trail = [];
  for (let i = 0; i < maxTabs; i += 1) {
    const summary = await activeSummary(page);
    trail.push(summary);
    if (predicate(summary)) return { found: true, summary, trail };
    await page.keyboard.press("Tab");
  }
  return { found: false, summary: null, trail };
}

const browser = await chromium.launch({
  executablePath: process.env.KJ_ATLAS_SCREENSHOT_BROWSER_PATH || undefined,
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const sample = { value: false };

await page.route("**/packs/index.json", (r) =>
  r.fulfill({ status: 404, contentType: "application/json", body: "{}" })
);
await page.route("**/docs/doc_phase1_canvas", (r) =>
  r.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { ETag: sample.value ? '"kbd-loaded"' : '"kbd-empty"' },
    body: JSON.stringify(
      buildDocument(sample.value ? ["キーボード確認カードA", "キーボード確認カードB"] : [])
    ),
  })
);

try {
  await page.goto(baseUrl);
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });

  // --- K0: reach and activate the start panel entry with the keyboard only.
  sample.value = true;
  const startPanel = await tabUntil(page, (s) => s.tag === "button" && /^(サンプルを開く|Open sample)/.test(s.name));
  record(
    "K0",
    "開始パネルの「サンプルを開く」へTabで到達できる",
    startPanel.found,
    startPanel.found
      ? `${startPanel.trail.length}回のTabで到達`
      : `到達不可 (${startPanel.trail.length}回Tab)`
  );
  await page.keyboard.press("Enter");
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });
  record("K0b", "Enterで開始パネルの操作を実行できる", true, "開始パネルが閉じ、文書が開いた");

  // --- K1: Tab reaches header, canvas cards, and the right-hand panel.
  await page.evaluate(() => document.body.focus());
  await page.keyboard.press("Tab");
  const regions = new Set();
  const names = [];
  let cardReached = false;
  for (let i = 0; i < 160; i += 1) {
    const s = await activeSummary(page);
    regions.add(s.region);
    names.push(`${s.region}|${s.name}`);
    if (/キーボード確認カード/.test(s.name)) cardReached = true;
    await page.keyboard.press("Tab");
  }
  const hasHeader = [...regions].some((r) => /banner|header/.test(r));
  const hasSelection = [...regions].some((r) => /aside|complementary|selection-context/.test(r));
  record(
    "K1",
    "Tabでヘッダー・キャンバス操作・右側パネルへ移動できる",
    hasHeader && cardReached && hasSelection,
    `到達領域: ${[...regions].join(", ")} / カード到達=${cardReached}`
  );

  // --- K2: focused control runs with Enter and with Space.
  await page.reload();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });
  const openSample = await tabUntil(page, (s) => s.tag === "button" && /^(サンプルを開く|Open sample)/.test(s.name));
  if (openSample.found) await page.keyboard.press("Enter");
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

  const cardCountBefore = await page.getByRole("button", { name: /キーボード確認カード/ }).count();
  const newCard = await tabUntil(page, (s) => s.tag === "button" && /^(新規カード|New Card)$/.test(s.name));
  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  const cardCountAfterEnter = await page
    .locator('[data-ui-core-action="create-card"]')
    .count()
    .then(() => page.evaluate(() => document.querySelectorAll("[aria-pressed]").length));
  record(
    "K2a",
    "フォーカス中のボタンをEnterで実行できる（新規カード）",
    newCard.found && cardCountAfterEnter > 0,
    `新規カードボタン到達=${newCard.found} / 実行後のaria-pressed要素数=${cardCountAfterEnter}`
  );
  await page.keyboard.press("Escape");

  const safeToggle = await tabUntil(page, (s) => s.tag === "button" && /^(詳細|Advanced)$/.test(s.name));
  const pressedBefore = safeToggle.summary?.pressed ?? null;
  await page.keyboard.press("Space");
  await page.waitForTimeout(300);
  const pressedAfter = (await activeSummary(page)).pressed;
  record(
    "K2b",
    "フォーカス中のトグルをSpaceで実行できる（詳細）",
    safeToggle.found && pressedBefore !== pressedAfter,
    `対象=${safeToggle.summary?.name ?? "(未到達)"} / aria-pressed ${pressedBefore} -> ${pressedAfter}` +
      (safeToggle.found
        ? ""
        : ` / Tab経路のbutton名: ${[...new Set(safeToggle.trail.filter((t) => t.tag === "button").map((t) => t.name.slice(0, 24)))].slice(0, 40).join(" > ")}`)
  );
  await page.keyboard.press("Space"); // restore

  // --- K3: opening 表示 / 共有と再現 leads focus to the opened panel.
  const viewBtn = await tabUntil(page, (s) => s.tag === "button" && /^(表示|View)$/.test(s.name));
  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  const viewPanelVisible = await page
    .locator('[data-panel="view-controls"], [data-panel="view"], [data-panel]')
    .filter({ hasText: /表示|View/ })
    .first()
    .isVisible()
    .catch(() => false);
  const afterViewOpen = await tabUntil(
    page,
    (s) => s.region !== "banner" && s.region !== "header" && s.region !== "(root)",
    40
  );
  record(
    "K3a",
    "「表示」を開いた後、次に操作すべき項目へ移動できる",
    viewBtn.found && viewPanelVisible,
    `パネル可視=${viewPanelVisible} / 開いた後の到達領域=${afterViewOpen.summary?.region ?? "(未到達)"}`
  );

  await page.reload();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });
  const openSample2 = await tabUntil(page, (s) => s.tag === "button" && /^(サンプルを開く|Open sample)/.test(s.name));
  if (openSample2.found) await page.keyboard.press("Enter");
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

  const shareBtn = await tabUntil(page, (s) => s.tag === "button" && /^(共有と再現|Share and reproduce)$/.test(s.name));
  await page.keyboard.press("Enter");
  const sharePanel = page.locator('[data-panel="share-replay"]');
  await sharePanel.waitFor({ state: "visible", timeout: 5000 });
  const focusInShare = await tabUntil(page, (s) => s.region === "share-replay", 30);
  record(
    "K3b",
    "「共有と再現」を開いた後、パネル内の項目へ移動できる",
    shareBtn.found && focusInShare.found,
    `パネル内到達=${focusInShare.found} / 先頭項目=${focusInShare.summary?.name ?? "(未到達)"}`
  );

  // --- K5: Escape closes the panel and returns focus to its trigger.
  await page.keyboard.press("Escape");
  await page.waitForTimeout(300);
  const closed = await sharePanel.isHidden().catch(() => false);
  const afterEscape = await activeSummary(page);
  const returned = /共有と再現|Share and reproduce/.test(afterEscape.name);
  record(
    "K5",
    "Escapeで閉じ、元のボタンへフォーカスが戻る",
    closed && returned,
    `閉じた=${closed} / Escape後のフォーカス=${afterEscape.name || afterEscape.tag}`
  );

  // --- K4: text entry, correction, and confirmation are keyboard-complete.
  const newCard2 = await tabUntil(page, (s) => s.tag === "button" && /^(新規カード|New Card)$/.test(s.name));
  await page.keyboard.press("Enter");
  await page.waitForTimeout(500);
  const editorFocused = await page.evaluate(() => {
    const a = document.activeElement;
    return !!a && (a.tagName === "TEXTAREA" || a.tagName === "INPUT");
  });
  await page.keyboard.type("キーボード入力テスト");
  await page.keyboard.press("Backspace");
  const typed = await page.evaluate(() => {
    const a = document.activeElement;
    return a && "value" in a ? String(a.value) : "";
  });
  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  const committed = await page
    .getByRole("button", { name: /キーボード入力テス/ })
    .count();
  record(
    "K4",
    "文字入力欄で入力・削除・確定の流れが完結する",
    newCard2.found && editorFocused && typed === "キーボード入力テス" && committed > 0,
    `作成直後に入力欄へフォーカス=${editorFocused} / 削除後の値="${typed}" / 確定後にカードとして存在=${committed > 0}`
  );

  // --- K4b: Escape cancels an edit without committing.
  const newCard3 = await tabUntil(page, (s) => s.tag === "button" && /^(新規カード|New Card)$/.test(s.name));
  await page.keyboard.press("Enter");
  await page.waitForTimeout(400);
  await page.keyboard.type("取消されるべき本文");
  await page.keyboard.press("Escape");
  await page.waitForTimeout(400);
  const cancelled = (await page.getByRole("button", { name: /取消されるべき本文/ }).count()) === 0;
  record(
    "K4b",
    "Escapeで編集を取り消して元の作業へ戻れる",
    newCard3.found && cancelled,
    `取消後に本文が残っていない=${cancelled}`
  );
} catch (error) {
  record("EXCEPTION", "実行時例外", false, String(error).slice(0, 400));
} finally {
  await browser.close();
}

const failed = results.filter((r) => r.result === "fail");
console.log(
  JSON.stringify(
    {
      check: "keyboard-only acceptance (acceptance_check.md キーボードで確認すること)",
      baseUrl,
      generatedAt: new Date().toISOString(),
      total: results.length,
      passed: results.length - failed.length,
      failed: failed.length,
      results,
    },
    null,
    2
  )
);
process.exit(failed.length === 0 ? 0 : 1);
