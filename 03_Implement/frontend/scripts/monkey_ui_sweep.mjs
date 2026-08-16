// Seeded monkey test over the surfaces touched by the MVP-EXIT-01 human
// acceptance work: keyboard navigation, focus management, card inline edit,
// header toolbar, view / share panels, work mode tabs, legend.
//
// Usage: KJ_ATLAS_MONKEY_SEED=1 KJ_ATLAS_MONKEY_ACTIONS=150 KJ_ATLAS_MONKEY_VIEWPORT=1440 node monkey.mjs
import { chromium } from "@playwright/test";

const SEED = Number(process.env.KJ_ATLAS_MONKEY_SEED ?? "1");
const ACTIONS = Number(process.env.KJ_ATLAS_MONKEY_ACTIONS ?? "150");
const WIDTH = Number(process.env.KJ_ATLAS_MONKEY_VIEWPORT ?? "1440");
const HEIGHT = WIDTH <= 420 ? 720 : 900;
const baseUrl = process.env.KJ_ATLAS_BASE_URL ?? "http://127.0.0.1:4173/?locale=ja";

// mulberry32
let s = SEED >>> 0;
const rnd = () => {
  s = (s + 0x6d2b79f5) >>> 0;
  let t = s;
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const pick = (arr) => arr[Math.floor(rnd() * arr.length)];

const findings = [];
const trace = [];
function finding(kind, detail) {
  const key = `${kind}::${detail}`.slice(0, 400);
  if (findings.some((f) => `${f.kind}::${f.detail}`.slice(0, 400) === key)) return;
  findings.push({ kind, detail, afterAction: trace.length, recentTrace: trace.slice(-200) });
}

function buildDocument(n) {
  const cards = [];
  for (let i = 0; i < n; i += 1) {
    cards.push({
      id: `mk-card-${i + 1}`,
      text: `モンキー対象カード${i + 1}`,
      x: 140 + (i % 4) * 240,
      y: 140 + Math.floor(i / 4) * 170,
    });
  }
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Monkey fixture",
    createdAt: "2026-06-03T00:00:00.000Z",
    updatedAt: "2026-06-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands: [
      {
        id: "mk-island-1",
        title: "モンキー島",
        cardIds: cards.slice(0, 2).map((c) => c.id),
        shape: { kind: "rect", x: 100, y: 100, width: 520, height: 260 },
      },
    ],
    readingOrder: cards.map((c) => c.id),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

const browser = await chromium.launch({
  executablePath: process.env.KJ_ATLAS_SCREENSHOT_BROWSER_PATH || undefined,
});
const page = await browser.newPage({ viewport: { width: WIDTH, height: HEIGHT } });

page.on("pageerror", (e) => finding("pageerror", String(e).slice(0, 300)));
page.on("console", (m) => {
  if (m.type() !== "error") return;
  const text = m.text();
  // 404/500 on routed fixtures are expected noise from the stubbed API.
  if (/Failed to load resource/.test(text)) return;
  finding("console.error", text.slice(0, 1200));
});

const sample = { value: true };
await page.route("**/packs/index.json", (r) =>
  r.fulfill({ status: 404, contentType: "application/json", body: "{}" })
);
await page.route("**/docs/doc_phase1_canvas", (r) =>
  r.fulfill({
    status: 200,
    contentType: "application/json",
    headers: { ETag: '"monkey"' },
    body: JSON.stringify(buildDocument(sample.value ? 6 : 0)),
  })
);

async function snapshot() {
  return page.evaluate(() => {
    const a = document.activeElement;
    const body = document.body;
    const openDialogs = [...document.querySelectorAll('[role="dialog"]')]
      .filter((d) => d.getBoundingClientRect().width > 0)
      .map((d) => d.getAttribute("aria-label") || "(無名)");
    const header = document.querySelector("header");
    return {
      activeTag: a ? a.tagName.toLowerCase() : "(none)",
      activeName:
        a
          ? (a.getAttribute("aria-label") || (a.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 40) || a.getAttribute("title") || "")
          : "",
      bodyFocused: a === body || a === null,
      appMounted: Boolean(document.querySelector("main") || document.querySelector("header")),
      visibleText: (body.innerText || "").slice(0, 20000),
      openDialogs,
      dialogsWithoutName: openDialogs.filter((n) => n === "(無名)").length,
      headerOverflowX: header ? header.scrollWidth - header.clientWidth : 0,
      docScrollX: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      safeModeOn: /セーフモード:\s*ON|SafeMode:\s*ON/.test(body.innerText || ""),
      pressedMismatch: [...document.querySelectorAll("[aria-pressed]")].filter(
        (el) => !["true", "false"].includes(el.getAttribute("aria-pressed") ?? "")
      ).length,
      namelessButtons: [...document.querySelectorAll("button")].filter((b) => {
        if (b.getBoundingClientRect().width === 0) return false;
        const n =
          (b.getAttribute("aria-label") ?? "") ||
          (b.textContent ?? "").trim() ||
          (b.getAttribute("title") ?? "");
        return n.length === 0;
      }).length,
      namelessFields: [...document.querySelectorAll("input:not([type=hidden]),textarea,select")].filter((f) => {
        if (f.getBoundingClientRect().width === 0) return false;
        const n =
          (f.getAttribute("aria-label") ?? "") ||
          (f.labels && f.labels.length ? (f.labels[0].textContent ?? "").trim() : "") ||
          (f.getAttribute("aria-labelledby") ? "labelledby" : "") ||
          (f.getAttribute("placeholder") ?? "") ||
          (f.getAttribute("title") ?? "");
        return n.length === 0;
      }).map((f) => `${f.tagName.toLowerCase()}${f.type ? "[" + f.type + "]" : ""}`),
      nanTransforms: [...document.querySelectorAll("[style]")].filter((el) =>
        /NaN|Infinity/.test(el.getAttribute("style") ?? "")
      ).length,
    };
  });
}

function checkInvariants(snap, action) {
  if (!snap.appMounted) finding("app-unmounted", `after ${action}`);
  if (/undefined|NaN|\[object Object\]|null,null/.test(snap.visibleText)) {
    const m = snap.visibleText.match(/.{0,50}(undefined|NaN|\[object Object\]).{0,50}/);
    finding("placeholder-leak", `画面に ${m?.[1]} が表示された: "${(m?.[0] ?? "").replace(/\s+/g, " ")}"`);
  }
  if (!snap.safeModeOn) finding("safemode-off", `SafeMode表示が消えた (after ${action})`);
  if (snap.pressedMismatch > 0) finding("aria-pressed-invalid", `${snap.pressedMismatch}件の不正な aria-pressed`);
  if (snap.dialogsWithoutName > 0) finding("dialog-without-name", `名前のないdialogが${snap.dialogsWithoutName}件`);
  if (snap.namelessButtons > 0) finding("button-without-name", `accessible nameのない可視buttonが${snap.namelessButtons}件 (after ${action})`);
  if (snap.namelessFields.length > 0)
    finding("field-without-name", `accessible nameのない可視入力欄: ${[...new Set(snap.namelessFields)].join(", ")} (after ${action})`);
  if (snap.docScrollX > 2) finding("horizontal-overflow", `viewport ${WIDTH}px で横スクロールが発生 (${snap.docScrollX}px, after ${action})`);
  if (snap.nanTransforms > 0)
    finding("nan-transform", `座標にNaN/Infinityを含む要素が${snap.nanTransforms}件 (after ${action})`);
}

async function isActionable(locator, options = {}) {
  try {
    await locator.click({ ...options, trial: true, timeout: 350 });
    return true;
  } catch {
    return false;
  }
}

async function clickIfActionable(locator, options = {}) {
  if (!(await isActionable(locator, options))) return false;
  await locator.click({ ...options, timeout: 2000 });
  return true;
}

const keyActions = [
  "Tab", "Tab", "Tab", "Shift+Tab", "Enter", "Space", "Escape", "Escape",
  "ArrowRight", "ArrowLeft", "ArrowUp", "ArrowDown", "Home", "End",
  "Delete", "Backspace",
];

try {
  await page.goto(baseUrl);
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "visible" });
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await page.locator('[data-panel="start-document-entry"]').waitFor({ state: "hidden" });
  trace.push("open-sample");

  for (let i = 0; i < ACTIONS; i += 1) {
    const focusBeforeAction = await page.evaluate(() => {
      const active = document.activeElement;
      return {
        bodyFocused: active === document.body || active === null,
        description: active
          ? `${active.tagName.toLowerCase()}:${active.getAttribute("aria-label") || (active.textContent ?? "").replace(/\s+/g, " ").trim().slice(0, 40)}`
          : "(none)",
      };
    });
    const roll = rnd();
    let action = "";
    try {
      if (roll < 0.5) {
        const key = pick(keyActions);
        action = `key:${key}@${focusBeforeAction.description}`;
        await page.keyboard.press(key);
        // Product focus restoration is intentionally deferred to the next
        // animation frame after an element closes or is replaced. Async start
        // actions can also finish after loading, so allow a short bounded wait
        // for focus to settle before classifying a body transition.
        await page.evaluate(() => new Promise((resolve) => window.requestAnimationFrame(() => resolve(undefined))));
        if (!focusBeforeAction.bodyFocused) {
          await page.waitForFunction(() => document.activeElement !== document.body, undefined, { timeout: 1000 }).catch(() => {});
        }
      } else if (roll < 0.62) {
        const buttons = await page.locator("header button:visible:enabled").all();
        if (buttons.length) {
          const b = buttons[Math.floor(rnd() * buttons.length)];
          const name = ((await b.getAttribute("aria-label")) || (await b.innerText()) || "").replace(/\s+/g, " ").trim().slice(0, 24);
          action = `click-header:${name}`;
          if (!(await clickIfActionable(b))) action = "skip-blocked-header";
        }
      } else if (roll < 0.72) {
        const cards = await page.getByRole("button", { name: /モンキー対象カード/ }).all();
        if (cards.length) {
          const c = cards[Math.floor(rnd() * cards.length)];
          const mods = rnd() < 0.3 ? ["Shift"] : [];
          action = `click-card${mods.length ? "+Shift" : ""}`;
          if (!(await clickIfActionable(c, { modifiers: mods }))) action = "skip-blocked-card";
        }
      } else if (roll < 0.78) {
        const cards = await page.getByRole("button", { name: /モンキー対象カード/ }).all();
        if (cards.length) {
          action = "dblclick-card";
          const card = cards[Math.floor(rnd() * cards.length)];
          if (await isActionable(card)) {
            await card.dblclick({ timeout: 2000 });
          } else {
            action = "skip-blocked-card";
          }
        }
      } else if (roll < 0.83) {
        action = "type";
        await page.keyboard.type(pick(["あ", "テスト", "  ", "<b>x</b>", "1", "改行なし"]));
      } else if (roll < 0.88) {
        const cards = await page.getByRole("button", { name: /モンキー対象カード/ }).all();
        if (cards.length) {
          action = "rightclick-card";
          const card = cards[Math.floor(rnd() * cards.length)];
          if (!(await clickIfActionable(card, { button: "right" }))) action = "skip-blocked-card";
        }
      } else if (roll < 0.93) {
        const items = await page.getByRole("menuitem").all();
        if (items.length) {
          const it = items[Math.floor(rnd() * items.length)];
          const name = ((await it.innerText()) || "").replace(/\s+/g, " ").trim().slice(0, 20);
          action = `menuitem:${name}`;
          if (!(await clickIfActionable(it))) action = "skip-blocked-menuitem";
        } else {
          action = "key:Escape";
          await page.keyboard.press("Escape");
        }
      } else if (roll < 0.96) {
        const boxes = await page.locator('input[type="checkbox"]:visible:enabled').all();
        if (boxes.length) {
          action = "toggle-checkbox";
          const box = boxes[Math.floor(rnd() * boxes.length)];
          if (!(await clickIfActionable(box))) action = "skip-blocked-checkbox";
        }
      } else if (roll < 0.985) {
        // drag a random card by a random offset (may land on empty canvas or on the island).
        const cards = await page.getByRole("button", { name: /モンキー対象カード/ }).all();
        if (cards.length) {
          const c = cards[Math.floor(rnd() * cards.length)];
          const box = await c.boundingBox();
          if (box && await isActionable(c)) {
            const dx = Math.floor((rnd() - 0.5) * 400);
            const dy = Math.floor((rnd() - 0.5) * 300);
            action = `drag-card(${dx},${dy})`;
            await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
            await page.mouse.down();
            await page.mouse.move(box.x + box.width / 2 + dx, box.y + box.height / 2 + dy, { steps: 6 });
            await page.mouse.up();
          }
        }
      } else if (roll < 0.995) {
        // rubber-band select: drag on empty canvas background.
        action = "rubber-band-select";
        const startX = 900 + rnd() * 200;
        const startY = 500 + rnd() * 200;
        await page.mouse.move(startX, startY);
        await page.mouse.down();
        await page.mouse.move(startX - 300, startY - 200, { steps: 8 });
        await page.mouse.up();
      } else {
        // wheel zoom in/out at a random point.
        action = "wheel-zoom";
        const dy = rnd() < 0.5 ? 400 : -400;
        await page.mouse.move(600 + rnd() * 400, 400 + rnd() * 300);
        await page.mouse.wheel(0, dy);
      }
    } catch (error) {
      const msg = String(error).split("\n")[0].slice(0, 200);
      if (!/Timeout .* exceeded|intercepts pointer events|not stable|element is not visible/.test(msg)) {
        finding("action-error", `${action}: ${msg}`);
      } else {
        finding("action-blocked", `${action}: ${msg}`);
      }
    }
    if (action) trace.push(action);

    if (i % 5 === 0 || roll >= 0.5) {
      const snap = await snapshot();
      checkInvariants(snap, action);
      if (snap.bodyFocused && !focusBeforeAction.bodyFocused && /^key:(Tab|Shift\+Tab|Enter|Space|Escape|Delete|Backspace)@/.test(action)) {
        finding("focus-lost-to-body", `${action} の後にフォーカスが<body>へ落ちた（操作前=${focusBeforeAction.description}）`);
      }
    }
  }

  const final = await snapshot();
  checkInvariants(final, "final");
} catch (error) {
  finding("harness-exception", String(error).slice(0, 300));
} finally {
  await browser.close();
}

console.log(
  JSON.stringify(
    { seed: SEED, viewport: WIDTH, actions: trace.length, findingCount: findings.length, findings },
    null,
    2
  )
);
