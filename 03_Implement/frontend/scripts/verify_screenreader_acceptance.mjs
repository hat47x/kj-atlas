// Machine-substitute evidence for the "screen reader acceptance" blocker of
// MVP-EXIT-01. Reproduces 04_Documentation/acceptance_check.md
// "スクリーンリーダーで確認すること" 1-6 by inspecting the Chromium
// accessibility tree (the same computed roles/names/states that NVDA, JAWS and
// VoiceOver consume) plus the live-region wiring that drives announcements.
//
// Limitation, stated deliberately: this verifies what an AT *would be given*.
// It does not verify what a specific AT actually speaks, nor speech ordering
// inside a single utterance. Residual human acceptance is therefore narrowed,
// not eliminated.
import { chromium } from "@playwright/test";

const baseUrl = process.env.KJ_ATLAS_BASE_URL ?? "http://127.0.0.1:4173/?locale=ja";
const results = [];
const record = (id, title, ok, detail) =>
  results.push({ id, title, result: ok ? "pass" : "fail", detail });

function buildDocument(cardTexts) {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Screen reader acceptance sample",
    createdAt: "2026-06-03T00:00:00.000Z",
    updatedAt: "2026-06-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `sample-card-${index + 1}`,
      text,
      x: 160 + index * 280,
      y: 160 + (index % 2) * 150,
    })),
    edges: [],
    islands: [],
    readingOrder: cardTexts.map((_, index) => `sample-card-${index + 1}`),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const browser = await chromium.launch({
  executablePath: process.env.KJ_ATLAS_SCREENSHOT_BROWSER_PATH || undefined,
});
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const cdp = await page.context().newCDPSession(page);
await cdp.send("Accessibility.enable");

async function axNodes() {
  const { nodes } = await cdp.send("Accessibility.getFullAXTree");
  return nodes.map((n) => ({
    role: n.role?.value ?? "",
    name: (n.name?.value ?? "").replace(/\s+/g, " ").trim(),
    level: n.properties?.find((p) => p.name === "level")?.value?.value,
    selected: n.properties?.find((p) => p.name === "selected")?.value?.value,
    focused: n.properties?.find((p) => p.name === "focused")?.value?.value,
    described: n.properties?.find((p) => p.name === "describedby") !== undefined,
    live: n.properties?.find((p) => p.name === "live")?.value?.value,
    ignored: n.ignored,
  }));
}

const sample = { value: false };
await page.route("**/packs/index.json", (r) =>
  r.fulfill({ status: 404, contentType: "application/json", body: "{}" })
);
await page.route("**/docs/doc_phase1_canvas", (r) =>
  r.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { ETag: sample.value ? '"sr-loaded"' : '"sr-empty"' },
    body: JSON.stringify(
      buildDocument(sample.value ? ["読み上げ確認カードA", "読み上げ確認カードB"] : [])
    ),
  })
);

try {
  await page.goto(baseUrl);
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });
  sample.value = true;
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });

  // --- S1: heading jump reaches the product name h1.
  const nodes = await axNodes();
  const headings = nodes.filter((n) => n.role === "heading" && !n.ignored);
  const h1 = headings.find((n) => String(n.level) === "1");
  record(
    "S1",
    "見出しジャンプでプロダクト名のh1へ到達できる",
    Boolean(h1) && /kj-atlas/i.test(h1?.name ?? ""),
    `h1="${h1?.name ?? "(なし)"}" / 検出見出し数=${headings.length}`
  );

  // --- S2: card creation moves focus to a named text field; commit is announced.
  await page.getByRole("button", { name: /^(新規カード|New Card)$/ }).click();
  await page.waitForTimeout(400);
  const editor = await page.evaluate(() => {
    const a = document.activeElement;
    if (!a) return null;
    return {
      tag: a.tagName.toLowerCase(),
      name:
        a.getAttribute("aria-label") ||
        (a.labels && a.labels[0] ? a.labels[0].textContent : "") ||
        a.getAttribute("placeholder") ||
        "",
    };
  });
  const focusedAx = await (async () => {
    const { root } = await cdp.send("DOM.getDocument", { depth: -1, pierce: true });
    const { nodeId } = await cdp.send("DOM.querySelector", {
      nodeId: root.nodeId,
      selector: "textarea",
    });
    if (!nodeId) return null;
    const { nodes } = await cdp.send("Accessibility.getPartialAXTree", {
      nodeId,
      fetchRelatives: false,
    });
    const n = (nodes ?? []).find((x) => x.role?.value && x.role.value !== "generic");
    return n
      ? { role: n.role?.value ?? "", name: (n.name?.value ?? "").trim(), ignored: n.ignored }
      : null;
  })();
  await page.keyboard.type("読み上げ確認の入力");
  await page.keyboard.press("Enter");
  await page.waitForTimeout(500);
  const afterCommit = await axNodes();
  const liveRegions = afterCommit.filter((n) => n.live === "polite" || n.live === "assertive");
  const committed = await page.getByRole("button", { name: /読み上げ確認の入力/ }).count();
  record(
    "S2",
    "カード追加直後の入力欄がrole/nameを持ち、確定内容が反映される",
    editor?.tag === "textarea" || editor?.tag === "input"
      ? focusedAx?.role === "textbox" &&
        (focusedAx?.name ?? "").length > 0 &&
        committed > 0
      : false,
    `focus=${editor?.tag} AXrole=${focusedAx?.role ?? "(なし)"} AXname="${focusedAx?.name ?? ""}" / 確定後にカード化=${committed > 0} / live領域数=${liveRegions.length}`
  );

  // --- S3: selecting a card announces the selection context automatically.
  await page.getByRole("button", { name: /読み上げ確認カードA/ }).click();
  await page.waitForTimeout(400);
  const selection = await page.evaluate(() => {
    const section = document.querySelector('[data-panel="selection-context"]');
    if (!section) return null;
    return {
      live: section.getAttribute("aria-live"),
      label: section.getAttribute("aria-label"),
      text: (section.textContent ?? "").replace(/\s+/g, " ").trim(),
    };
  });
  const t = selection?.text ?? "";
  const iTarget = t.indexOf("対象");
  const iReview = t.indexOf("レビュー状態");
  const orderOk = iTarget >= 0 && iReview > iTarget;
  record(
    "S3",
    "選択時に「現在の選択」が自動的に読み上げられ、対象→レビュー状態の順で並ぶ",
    selection?.live === "polite" && Boolean(selection?.label) && orderOk,
    `aria-live=${selection?.live} / aria-label="${selection?.label}" / 読み上げ順="${t.slice(0, 120)}"`
  );

  // --- S4: work mode tabs are real tabs with arrow / Home / End navigation.
  await page.getByRole("button", { name: /^(詳細|Advanced)$/ }).click();
  await page.waitForTimeout(300);
  await page.getByRole("button", { name: /^(作業モード|Work Mode)$/ }).click();
  await page.waitForTimeout(500);
  const tablist = await page.getByRole("tablist").count();
  const tabs = page.getByRole("tab");
  const tabCount = await tabs.count();
  let arrowOk = false;
  let homeEndOk = false;
  let firstName = "";
  let afterArrowName = "";
  if (tabCount > 1) {
    await tabs.first().focus();
    firstName = (await tabs.first().innerText()).replace(/\s+/g, " ").trim();
    await page.keyboard.press("ArrowRight");
    await page.waitForTimeout(250);
    const focusedTab = await page.evaluate(() => {
      const a = document.activeElement;
      return a
        ? {
            role: a.getAttribute("role"),
            selected: a.getAttribute("aria-selected"),
            name: (a.textContent ?? "").replace(/\s+/g, " ").trim(),
          }
        : null;
    });
    afterArrowName = focusedTab?.name ?? "";
    arrowOk = focusedTab?.role === "tab" && afterArrowName !== firstName;
    await page.keyboard.press("End");
    await page.waitForTimeout(200);
    const endName = await page.evaluate(() =>
      (document.activeElement?.textContent ?? "").replace(/\s+/g, " ").trim()
    );
    await page.keyboard.press("Home");
    await page.waitForTimeout(200);
    const homeName = await page.evaluate(() =>
      (document.activeElement?.textContent ?? "").replace(/\s+/g, " ").trim()
    );
    homeEndOk = homeName === firstName && endName !== firstName;
  }
  const tabAx = (await axNodes()).filter((n) => n.role === "tab" && !n.ignored);
  const selectedAx = tabAx.filter((n) => n.selected === true);
  record(
    "S4",
    "作業モードがtabとして認識され、矢印/Home/Endで移動し選択タブ名が読み上げられる",
    tablist > 0 && tabCount > 1 && arrowOk && homeEndOk && selectedAx.length === 1,
    `tablist=${tablist} tab数=${tabCount} 矢印移動=${arrowOk} (${firstName}->${afterArrowName}) Home/End=${homeEndOk} / AX選択中="${selectedAx[0]?.name ?? "(なし)"}"`
  );

  // --- S5: the source-reference toggle carries its warning as a description.
  await page.keyboard.press("Escape");
  await page.waitForTimeout(300);
  await page.getByRole("button", { name: /^(共有と再現|Share and reproduce)$/ }).click();
  await page.locator('[data-panel="share-replay"]').waitFor({ state: "visible" });
  const toggle = page.locator("[data-share-include-source-references] input[type=checkbox]");
  await toggle.scrollIntoViewIfNeeded();
  const beforeDesc = await toggle.getAttribute("aria-describedby");
  await toggle.check();
  await page.waitForTimeout(300);
  const afterDesc = await toggle.getAttribute("aria-describedby");
  const warningText = await page
    .locator("[data-share-source-references-warning]")
    .innerText()
    .catch(() => "");
  const describedResolves = afterDesc
    ? await page.evaluate((id) => Boolean(document.getElementById(id)), afterDesc)
    : false;
  record(
    "S5",
    "「出典参照を含める」をONにすると警告文が説明として結び付く",
    Boolean(afterDesc) && describedResolves && warningText.length > 0,
    `OFF時 aria-describedby=${beforeDesc ?? "(なし)"} / ON時=${afterDesc ?? "(なし)"} 解決可能=${describedResolves} / 警告文="${warningText.slice(0, 80)}"`
  );
  await toggle.uncheck();
  await page.keyboard.press("Escape");
  await page.waitForTimeout(300);

  // --- S6: the legend is a named dialog; Escape returns focus to its trigger.
  await page.getByRole("button", { name: /^(表示|View)$/ }).click();
  await page.waitForTimeout(400);
  const legendTrigger = page.locator('[data-focus-return-id="legend-trigger"]');
  await legendTrigger.first().click();
  await page.locator('[data-ui-region="canvas-legend"]').waitFor({ state: "visible" });
  const legendLabel = await page
    .locator('[data-ui-region="canvas-legend"]')
    .getAttribute("aria-label");
  const dialogAx = (await axNodes()).filter((n) => n.role === "dialog" && !n.ignored);
  const legendAx = dialogAx.find((n) => n.name === (legendLabel ?? ""));
  await page.keyboard.press("Escape");
  await page.waitForTimeout(400);
  const legendClosed = await page.locator('[data-ui-region="canvas-legend"]').isHidden();
  const focusReturned = await page.evaluate(() =>
    Boolean(document.activeElement?.closest('[data-focus-return-id="legend-trigger"]')) ||
    document.activeElement?.getAttribute("data-focus-return-id") === "legend-trigger"
  );
  record(
    "S6",
    "凡例がdialogとして名前付きで読み上げられ、Escape後にトリガーへ戻る",
    Boolean(legendAx) && legendClosed && focusReturned,
    `凡例aria-label="${legendLabel}" / 一致するAX dialog="${legendAx?.name ?? "(なし)"}" / 同時に開いているdialog=${dialogAx.map((d) => d.name).join(", ")} / Escapeで閉じた=${legendClosed} / トリガー復帰=${focusReturned}`
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
      check:
        "accessibility-tree acceptance proxy (acceptance_check.md スクリーンリーダーで確認すること)",
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
