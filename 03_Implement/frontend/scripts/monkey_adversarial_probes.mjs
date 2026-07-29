// Targeted adversarial probes over the surfaces exercised by the MVP-EXIT-01
// acceptance work. Each probe states the documented expectation it checks.
import { chromium } from "@playwright/test";

const only = process.env.ONLY ? process.env.ONLY.split(",") : null;
const out = [];
const rec = (id, title, ok, detail) =>
  out.push({ id, title, result: ok ? "ok" : "SUSPECT", detail });

function doc(cards, islands = []) {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "adversarial fixture",
    createdAt: "2026-06-03T00:00:00.000Z",
    updatedAt: "2026-06-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands,
    readingOrder: cards.map((c) => c.id),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const browser = await chromium.launch({
  executablePath: process.env.KJ_ATLAS_SCREENSHOT_BROWSER_PATH || undefined,
});

async function open(cards, islands) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.route("**/packs/index.json", (r) =>
    r.fulfill({ status: 404, contentType: "application/json", body: "{}" })
  );
  await page.route("**/docs/doc_phase1_canvas", (r) =>
    r.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"adv"' },
      body: JSON.stringify(doc(cards, islands)),
    })
  );
  await page.goto("http://127.0.0.1:4173/?locale=ja");
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });
  await page.waitForTimeout(300);
  return page;
}

const run = (id) => !only || only.includes(id);

try {
  // A1: acceptance_check.md L59 -- Esc cancels an edit of an EXISTING card.
  if (run("A1")) {
    const page = await open([{ id: "c1", text: "元の本文", x: 220, y: 220 }]);
    await page.getByRole("button", { name: "元の本文" }).dblclick();
    await page.waitForTimeout(300);
    await page.keyboard.press("Control+a");
    await page.keyboard.type("書き換えた本文");
    await page.keyboard.press("Escape");
    await page.waitForTimeout(500);
    const kept = await page.getByRole("button", { name: "元の本文" }).count();
    const overwritten = await page.getByRole("button", { name: "書き換えた本文" }).count();
    rec("A1", "既存カードの編集をEscで取り消すと元の本文へ戻る", kept === 1 && overwritten === 0,
      `元の本文が残る=${kept === 1} / 書き換えが残る=${overwritten > 0}`);
    await page.close();
  }

  // A2: acceptance_check.md L59 -- clicking outside commits the edit.
  if (run("A2")) {
    const page = await open([{ id: "c1", text: "元の本文", x: 220, y: 220 }]);
    await page.getByRole("button", { name: "元の本文" }).dblclick();
    await page.waitForTimeout(300);
    await page.keyboard.press("Control+a");
    await page.keyboard.type("外クリックで確定");
    await page.mouse.click(1000, 700);
    await page.waitForTimeout(500);
    const committed = await page.getByRole("button", { name: "外クリックで確定" }).count();
    rec("A2", "入力欄の外をクリックすると編集が確定する", committed === 1, `確定した=${committed === 1}`);
    await page.close();
  }

  // A3: context menu must close with Escape (acceptance_check.md 操作感: Escapeで閉じる).
  if (run("A3")) {
    const page = await open([{ id: "c1", text: "右クリック対象", x: 220, y: 220 }]);
    await page.getByRole("button", { name: "右クリック対象" }).click({ button: "right" });
    await page.waitForTimeout(300);
    const opened = await page.getByRole("menuitem").count();
    await page.keyboard.press("Escape");
    await page.waitForTimeout(400);
    const stillOpen = await page.getByRole("menuitem").count();
    const focus = await page.evaluate(() => {
      const a = document.activeElement;
      return a ? `${a.tagName.toLowerCase()}:${(a.getAttribute("aria-label") || (a.textContent ?? "").trim()).slice(0, 30)}` : "(none)";
    });
    rec("A3", "カードのコンテキストメニューがEscapeで閉じる", opened > 0 && stillOpen === 0,
      `開いた項目数=${opened} / Escape後=${stillOpen} / Escape後のフォーカス=${focus}`);
    await page.close();
  }

  // A4: Delete while focus is inside a text field must not delete the selection.
  if (run("A4")) {
    const page = await open([
      { id: "c1", text: "検索されるカード", x: 220, y: 220 },
      { id: "c2", text: "残るカード", x: 500, y: 220 },
    ]);
    await page.getByRole("button", { name: "検索されるカード" }).click();
    const search = page.locator('header input[type="text"]').first();
    await search.click();
    await search.type("検索");
    await page.keyboard.press("Delete");
    await page.keyboard.press("Backspace");
    await page.waitForTimeout(400);
    const survived = await page.getByRole("button", { name: "検索されるカード" }).count();
    rec("A4", "検索欄でのDelete/Backspaceが選択カードを削除しない", survived === 1,
      `選択カードが残る=${survived === 1}`);
    await page.close();
  }

  // A5: 元に戻す must revert an island creation (acceptance_check.md 元に戻すは1回).
  if (run("A5")) {
    const page = await open([
      { id: "c1", text: "カードA", x: 220, y: 220 },
      { id: "c2", text: "カードB", x: 500, y: 220 },
    ]);
    await page.getByRole("button", { name: "カードA" }).click();
    await page.getByRole("button", { name: "カードB" }).click({ modifiers: ["Shift"] });
    await page.getByRole("banner").getByRole("button", { name: /^(島を作成|Create Island)$/ }).click();
    await page.waitForTimeout(500);
    const afterCreate = await page.locator("aside").innerText();
    await page.getByRole("banner").getByRole("button", { name: /^(元に戻す|Undo)$/ }).click();
    await page.waitForTimeout(500);
    const afterUndo = await page.locator("aside").innerText();
    const islandsAfterUndo = /島:\s*0/.test(afterUndo);
    rec("A5", "島の作成を「元に戻す」で取り消せる", /島:\s*1/.test(afterCreate) && islandsAfterUndo,
      `作成後="${(afterCreate.match(/島:\s*\d+/) ?? [""])[0]}" / 取消後="${(afterUndo.match(/島:\s*\d+/) ?? [""])[0]}"`);
    await page.close();
  }

  // A6: work mode tablist must keep a single tab stop (roving tabindex).
  if (run("A6")) {
    const page = await open([{ id: "c1", text: "タブ確認", x: 220, y: 220 }]);
    await page.getByRole("button", { name: /^(詳細|Advanced)$/ }).click();
    await page.waitForTimeout(200);
    await page.getByRole("button", { name: /^(作業モード|Work Mode)$/ }).click();
    await page.waitForTimeout(500);
    const tabs = page.getByRole("tab");
    const n = await tabs.count();
    const tabIndexes = await page.evaluate(() =>
      [...document.querySelectorAll('[role="tab"]')].map((t) => t.getAttribute("tabindex"))
    );
    const stops = tabIndexes.filter((v) => v === "0").length;
    rec("A6", "作業モードtabのtab stopが1つだけ（roving tabindex）", n > 1 && stops === 1,
      `tab数=${n} / tabindex=0 の数=${stops} / 値=${tabIndexes.join(",")}`);
    await page.close();
  }

  // A7: rapid double activation of 島を作成 must not create two islands from one selection.
  if (run("A7")) {
    const page = await open([
      { id: "c1", text: "二重確認A", x: 220, y: 220 },
      { id: "c2", text: "二重確認B", x: 500, y: 220 },
    ]);
    await page.getByRole("button", { name: "二重確認A" }).click();
    await page.getByRole("button", { name: "二重確認B" }).click({ modifiers: ["Shift"] });
    const btn = page.getByRole("banner").getByRole("button", { name: /^(島を作成|Create Island)$/ });
    await btn.click();
    await btn.click({ timeout: 2000 }).catch(() => {});
    await page.waitForTimeout(600);
    const aside = await page.locator("aside").innerText();
    const count = Number((aside.match(/島:\s*(\d+)/) ?? [0, "0"])[1]);
    rec("A7", "「島を作成」の連打で島が二重生成されない", count <= 1, `生成された島=${count}`);
    await page.close();
  }

  // A8: the island editor fields in the side panel must have accessible names.
  if (run("A8")) {
    const page = await open(
      [{ id: "c1", text: "名前確認", x: 220, y: 220 }],
      [{ id: "i1", title: "名前確認の島", cardIds: ["c1"], shape: { kind: "rect", x: 150, y: 160, width: 400, height: 220 } }]
    );
    await page.getByRole("button", { name: /名前確認の島|島/ }).first().click({ timeout: 3000 }).catch(() => {});
    await page.waitForTimeout(400);
    const nameless = await page.evaluate(() =>
      [...document.querySelectorAll("aside input:not([type=hidden]),aside textarea,aside select")]
        .filter((f) => {
          const r = f.getBoundingClientRect();
          if (r.width === 0 || r.height === 0) return false;
          return !(
            f.getAttribute("aria-label") ||
            f.getAttribute("aria-labelledby") ||
            (f.labels && f.labels.length) ||
            f.getAttribute("placeholder") ||
            f.getAttribute("title")
          );
        })
        .map((f) => `${f.tagName.toLowerCase()}[${f.type ?? ""}]="${String(f.value ?? "").slice(0, 24)}"`)
    );
    rec("A8", "右側パネルの入力欄すべてにaccessible nameがある", nameless.length === 0,
      nameless.length ? `無名の入力欄: ${nameless.join(" , ")}` : "無名の入力欄なし");
    await page.close();
  }

  // A9: a Japanese session must not receive an English default island title.
  if (run("A9")) {
    const page = await open([
      { id: "c1", text: "日本語UI確認A", x: 220, y: 220 },
      { id: "c2", text: "日本語UI確認B", x: 500, y: 220 },
    ]);
    await page.getByRole("button", { name: "日本語UI確認A" }).click();
    await page.getByRole("button", { name: "日本語UI確認B" }).click({ modifiers: ["Shift"] });
    await page.getByRole("banner").getByRole("button", { name: /^(島を作成|Create Island)$/ }).click();
    await page.waitForTimeout(600);
    const mainText = await page.locator("main").innerText();
    const asideText = await page.locator("aside").innerText();
    const hit = /Island\s*\d+/.exec(mainText + "\n" + asideText);
    rec("A9", "ja localeで島の既定名に英語が出ない", !hit, hit ? `画面に "${hit[0]}" が表示された` : "英語の既定名なし");
    await page.close();
  }
} catch (error) {
  rec("EXCEPTION", "実行時例外", false, String(error).slice(0, 300));
} finally {
  await browser.close();
}

console.log(JSON.stringify({ probes: out.length, suspects: out.filter((o) => o.result === "SUSPECT").length, out }, null, 2));
