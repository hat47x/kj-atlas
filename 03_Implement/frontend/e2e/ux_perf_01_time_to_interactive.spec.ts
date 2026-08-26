import { expect, test, type Browser } from "@playwright/test";
import { START_PANEL_NEW_DOCUMENT } from "./helpers/i18n";

/**
 * UX-PERF-01: Time-to-Interactive (操作可能化時間) measurement probe.
 *
 * Background: `issue-UX-PERF-01-large-initial-javascript-chunk.md` AC-1 asks
 * for a baseline "main chunk上位module and 操作可能化時間", and AC-5 asks for a
 * repeatable "低速条件の性能probe". The 2026-08-21/08-25 checkpoints recorded
 * the bundle breakdown and shipped a code-split reducing the main chunk from
 * ~1,378KB to ~1,272KB, but left the actual Time-to-Interactive measurement
 * unmeasured. This spec is that measurement.
 *
 * "操作可能化" (operationally ready) definition used here: the moment the
 * start panel's "Create new document" button (`start_panel.action.new`)
 * becomes enabled. This is a deliberate, concrete choice over
 * `DOMContentLoaded`/`load`:
 *   - `App.tsx` renders `<StartPanel>` unconditionally from the very first
 *     paint (`isStartPanelVisible` starts as `useState(true)`), so its
 *     presence alone would fire immediately and say nothing about whether
 *     the app has actually hydrated.
 *   - `StartPanel.tsx` disables the "Create new document" button while
 *     `canCreateNew = !isBusy && !isReadOnly` is false, and `isBusy` tracks
 *     the app's own `isLoading` state (true for the initial mount-time
 *     document load, see `App.tsx`'s mount effect calling `loadDocument`).
 *     The button transitioning from disabled to enabled is therefore an
 *     existing, production-code-defined signal for "the app has finished
 *     booting and the user can start working" -- not a heuristic invented
 *     for this probe.
 *   - Creating the new document itself (`handleStartCreateNewDocument` ->
 *     `handleNewDocument`) is synchronous/local (no network), which matches
 *     `empty_canvas_onboarding.spec.ts`'s precedent that clicking this
 *     button leads straight to "Start with one card" / "Write first card".
 *     A separate one-shot check below actually clicks through this flow to
 *     confirm the enabled button is genuinely operable, not just visually
 *     enabled.
 *
 * Throttling profile: this repo's Maintainer decided (2026-08-26) to use an
 * established, named convention rather than a bespoke one. This probe uses
 * Chrome DevTools' "Fast 3G" network-throttling preset together with
 * Lighthouse's default mobile CPU-throttling multiplier -- the same
 * "slow representative device/network" baseline DevTools/Lighthouse-style
 * tooling conventionally uses:
 *   - Network (`Network.emulateNetworkConditions`): latency 562.5ms,
 *     download ~180,000 B/s, upload ~84,375 B/s. These are exactly the
 *     numbers Chrome DevTools' own frontend ships for its "Fast 3G" preset
 *     (`ChromeDevTools/devtools-frontend`,
 *     `front_end/core/sdk/NetworkManager.ts`, `Slow4GConditions` --
 *     internal name, but its `i18nTitleKey` is `UIStrings.fastG`, i.e. the
 *     label shown in the DevTools Network-conditions dropdown is
 *     "Fast 3G"): `download = 1.6 * 1000 * 1000 / 8 * 0.9`,
 *     `upload = 750 * 1000 / 8 * 0.9`, `latency = 150 * 3.75`. The same
 *     150ms RTT / 1.6Mbps-down / 750Kbps-up figures, before the same 0.9
 *     throughput / 3.75 RTT DevTools adjustment factors, are also
 *     Lighthouse's `throttling.mobile3G` constant
 *     (`GoogleChrome/lighthouse`, `lighthouse-core/config/constants.js`,
 *     `DEVTOOLS_RTT_ADJUSTMENT_FACTOR = 3.75`,
 *     `DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR = 0.9`) -- so this one profile
 *     is simultaneously "Chrome DevTools' Fast 3G preset" and "Lighthouse's
 *     default mobile network throttling".
 *   - CPU (`Emulation.setCPUThrottlingRate`): rate 4, matching the same
 *     Lighthouse constant's `cpuSlowdownMultiplier: 4` (Lighthouse's
 *     default mobile CPU throttling, calibrated against a high-end desktop
 *     baseline).
 *   - "Disable cache" is paired with the throttled condition (via
 *     `Network.setCacheDisabled`), matching the standard DevTools workflow
 *     of throttling + disabling cache together to model a first-time/cold
 *     visit rather than a warm-cache repeat visit. Each trial also gets a
 *     brand-new browser context (no cookies/localStorage/HTTP-cache carried
 *     over from a previous trial), for the same reason.
 *
 * This is a measurement probe, not a performance gate: see the "regression
 * probe" comment below the metrics block for why no historical-baseline
 * pass/fail threshold is asserted on the measured medians.
 */

// Chrome DevTools "Fast 3G" preset / Lighthouse `throttling.mobile3G`
// (see file header for exact source citations).
const DEVTOOLS_RTT_ADJUSTMENT_FACTOR = 3.75;
const DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR = 0.9;
const FAST_3G_RTT_MS = 150;
const FAST_3G_DOWNLOAD_KBPS = 1.6 * 1000; // 1.6 Mbps
const FAST_3G_UPLOAD_KBPS = 750; // 750 Kbps

const FAST_3G_LATENCY_MS = FAST_3G_RTT_MS * DEVTOOLS_RTT_ADJUSTMENT_FACTOR; // 562.5
const FAST_3G_DOWNLOAD_BYTES_PER_SEC =
  (FAST_3G_DOWNLOAD_KBPS * 1000 * DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR) / 8; // 180,000 B/s
const FAST_3G_UPLOAD_BYTES_PER_SEC =
  (FAST_3G_UPLOAD_KBPS * 1000 * DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR) / 8; // 84,375 B/s
const CPU_SLOWDOWN_MULTIPLIER = 4;

// Sanity ceiling only (see "regression probe" note below) -- generous enough
// that only a catastrophic regression (e.g. a hang) would ever trip it.
const SANITY_CEILING_MS = 45_000;

const TRIALS = Number(process.env.KJ_ATLAS_UX_PERF_01_TRIALS ?? "5");

type Trial = {
  readyMs: number;
  domContentLoadedMs: number | null;
  loadEventMs: number | null;
};

async function measureOnce(browser: Browser, throttled: boolean): Promise<Trial> {
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    const client = await context.newCDPSession(page);
    await client.send("Network.enable");
    // Cold/first-time-visit modelling: no cached responses from an earlier
    // trial or an earlier CDP-throttled/un-throttled run in this same probe.
    await client.send("Network.setCacheDisabled", { cacheDisabled: true });
    if (throttled) {
      await client.send("Network.emulateNetworkConditions", {
        offline: false,
        latency: FAST_3G_LATENCY_MS,
        downloadThroughput: FAST_3G_DOWNLOAD_BYTES_PER_SEC,
        uploadThroughput: FAST_3G_UPLOAD_BYTES_PER_SEC,
      });
      await client.send("Emulation.setCPUThrottlingRate", { rate: CPU_SLOWDOWN_MULTIPLIER });
    }

    await page.goto("/?locale=en");

    const startPanel = page.locator('[data-panel="start-document-entry"]');
    const newDocumentButton = startPanel.getByRole("button", { name: START_PANEL_NEW_DOCUMENT });
    await expect(newDocumentButton).toBeEnabled({ timeout: SANITY_CEILING_MS });

    // Read the ready timestamp from the page's own high-resolution clock
    // (relative to navigation start / `performance.timeOrigin`) rather than
    // a Node-side `Date.now()` around the Playwright call, so the value is
    // not inflated by IPC/polling overhead between the test process and the
    // browser.
    const readingsAtMs = await page.evaluate(() => {
      const [entry] = performance.getEntriesByType("navigation") as PerformanceNavigationTiming[];
      return {
        readyMs: performance.now(),
        domContentLoadedMs: entry ? entry.domContentLoadedEventEnd : null,
        loadEventMs: entry ? entry.loadEventEnd : null,
      };
    });

    return readingsAtMs;
  } finally {
    await context.close();
  }
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
}

test("UX-PERF-01 measures production-build Time-to-Interactive under normal and Fast-3G+4x-CPU throttled conditions", async ({ browser }, testInfo) => {
  test.slow();

  const normalTrials: Trial[] = [];
  for (let index = 0; index < TRIALS; index += 1) {
    normalTrials.push(await measureOnce(browser, false));
  }

  const throttledTrials: Trial[] = [];
  for (let index = 0; index < TRIALS; index += 1) {
    throttledTrials.push(await measureOnce(browser, true));
  }

  const normalReadyMs = normalTrials.map((trial) => trial.readyMs);
  const throttledReadyMs = throttledTrials.map((trial) => trial.readyMs);
  const normalMedianMs = median(normalReadyMs);
  const throttledMedianMs = median(throttledReadyMs);

  const metrics = {
    trials: TRIALS,
    throttlingProfile: {
      source: "Chrome DevTools 'Fast 3G' preset (devtools-frontend NetworkManager.ts Slow4GConditions) == Lighthouse throttling.mobile3G",
      latencyMs: FAST_3G_LATENCY_MS,
      downloadBytesPerSec: FAST_3G_DOWNLOAD_BYTES_PER_SEC,
      uploadBytesPerSec: FAST_3G_UPLOAD_BYTES_PER_SEC,
      cpuSlowdownMultiplier: CPU_SLOWDOWN_MULTIPLIER,
    },
    operationallyReadySignal: "start_panel.action.new (Create new document) button becomes enabled",
    normal: {
      readyMsTrials: normalReadyMs.map((value) => Number(value.toFixed(1))),
      readyMsMedian: Number(normalMedianMs.toFixed(1)),
    },
    throttled: {
      readyMsTrials: throttledReadyMs.map((value) => Number(value.toFixed(1))),
      readyMsMedian: Number(throttledMedianMs.toFixed(1)),
    },
  };

  console.info(`UX-PERF-01 time-to-interactive: ${JSON.stringify(metrics)}`);
  await testInfo.attach("ux-perf-01-time-to-interactive.json", {
    contentType: "application/json",
    body: Buffer.from(JSON.stringify(metrics, null, 2)),
  });

  // Regression-probe design note (AC-5): this intentionally does NOT assert
  // a tight pass/fail performance budget on the measured medians. No prior
  // Time-to-Interactive baseline exists for this app (AC-1 was open until
  // this same checkpoint), so any specific millisecond threshold right now
  // would be a guess dressed up as a number -- either loose enough to catch
  // nothing, or tight enough to make CI flaky on ordinary variance, with no
  // historical data to justify either choice. Matching this issue's own
  // established "honest partial progress" style (AC-1 was left half-checked
  // in the 2026-08-21 checkpoint rather than checked on a technicality),
  // this probe records the medians as evidence/attachments for a human to
  // set a real budget from once 2-3 dated data points exist, and only
  // asserts a generous sanity ceiling that would fail solely on a
  // catastrophic regression (e.g. the app hanging and never becoming
  // interactive), not on ordinary run-to-run variance.
  expect(normalMedianMs).toBeGreaterThan(0);
  expect(throttledMedianMs).toBeGreaterThan(0);
  expect(throttledMedianMs).toBeLessThan(SANITY_CEILING_MS);

  // Functional proof that "button enabled" really means "operationally
  // ready", not just a visually-enabled attribute: click all the way through
  // to a first card, the same flow `empty_canvas_onboarding.spec.ts` fixes
  // for the mocked-backend case. Run once, unthrottled, outside the timed
  // trials above -- this validates the *signal*, not the *timing*.
  const context = await browser.newContext();
  try {
    const page = await context.newPage();
    await page.goto("/?locale=en");
    const startPanel = page.locator('[data-panel="start-document-entry"]');
    const newDocumentButton = startPanel.getByRole("button", { name: START_PANEL_NEW_DOCUMENT });
    await expect(newDocumentButton).toBeEnabled();
    await newDocumentButton.click();
    await expect(startPanel).toBeHidden();
    const hint = page.locator('[data-ui-region="empty-canvas-hint"]');
    await expect(hint).toBeVisible();
    await hint.getByRole("button", { name: "Write first card" }).click();
    await expect(hint).toHaveCount(0);
    await expect(page.locator('[data-ui-region="primary-flow"] textarea')).toBeFocused();
  } finally {
    await context.close();
  }
});
