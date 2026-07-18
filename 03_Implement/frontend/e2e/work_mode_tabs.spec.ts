import { expect, test, type Page } from "@playwright/test";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";
import { WORK_MODE_BUTTON, enableAdvancedUiIfNeeded } from "./helpers/i18n";

// UX-NAV-02 (resolves ADR-0052 C-5): role=tablist, manual-activation contract
// for the work-mode surface's 7 tabs. Covers: arrow keys move focus only
// (not the active panel), Home/End jump to the ends, native button
// activation (Enter/Space/click) switches the active panel, initial focus on
// open lands on the active tab (never the Close button), non-active panels
// keep their state (mounted+hidden, not reset on switch), the staged Escape
// contract (tabpanel -> tab -> panel close -> trigger focus), the narrow
// (390px) tab strip auto-scrolls the active tab into view, and the
// diagnostics tab surfaces the existing document-wide counts with no
// score/rank/% vocabulary.

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"work-mode-tabs-e2e"' },
      body: JSON.stringify(buildDomainExpressionDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openWorkMode(page: Page): Promise<void> {
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: WORK_MODE_BUTTON }).click();
  await expect(page.locator('[data-ui-region="work-mode"]')).toBeVisible();
}

test.beforeEach(async ({ page }) => {
  await routeFixture(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  const startPanel = page.locator('[data-panel="start-document-entry"]');
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
});

test("opening work mode focuses the active (first) tab, not the Close button", async ({ page }) => {
  await openWorkMode(page);
  await expect(page.getByRole("tab", { name: "Diff" })).toBeFocused();
});

test("7 tabs exist in their product order, and 'review' vocabulary is avoided", async ({ page }) => {
  await openWorkMode(page);
  const tabs = page.getByRole("tab");
  await expect(tabs).toHaveCount(7);
  await expect(tabs.nth(0)).toHaveText("Diff");
  await expect(tabs.nth(1)).toHaveText("Merge selection");
  await expect(tabs.nth(2)).toHaveText("AI suggestion");
  await expect(tabs.nth(3)).toHaveText("Inquiry");
  await expect(tabs.nth(4)).toHaveText("Visual cue evaluation");
  await expect(tabs.nth(5)).toHaveText("Diagnostics");
  await expect(tabs.nth(6)).toHaveText("Narrative");
  for (const tab of await tabs.all()) {
    expect((await tab.textContent())?.toLowerCase()).not.toContain("review");
  }
});

test("arrow keys move focus only (manual activation): the active panel does not change until Enter/Space", async ({ page }) => {
  await openWorkMode(page);
  const diffTab = page.getByRole("tab", { name: "Diff" });
  const mergeTab = page.getByRole("tab", { name: "Merge selection" });
  const diffPanel = page.getByRole("tabpanel", { name: "Diff" });

  await expect(diffTab).toBeFocused();
  await expect(diffPanel).toBeVisible();

  await page.keyboard.press("ArrowRight");
  await expect(mergeTab).toBeFocused();
  // Manual activation: moving focus must NOT switch the active panel yet.
  await expect(diffPanel).toBeVisible();
  await expect(diffTab).toHaveAttribute("aria-selected", "true");
  await expect(mergeTab).toHaveAttribute("aria-selected", "false");

  await page.keyboard.press("Enter");
  await expect(mergeTab).toHaveAttribute("aria-selected", "true");
  await expect(page.getByRole("tabpanel", { name: "Merge selection" })).toBeVisible();
  await expect(diffPanel).toBeHidden();
});

test("ArrowLeft wraps to the last tab, Home/End jump to the first/last tab", async ({ page }) => {
  await openWorkMode(page);
  const diffTab = page.getByRole("tab", { name: "Diff" });
  const narrativeTab = page.getByRole("tab", { name: "Narrative" });

  await page.keyboard.press("ArrowLeft");
  await expect(narrativeTab).toBeFocused();

  await page.keyboard.press("Home");
  await expect(diffTab).toBeFocused();

  await page.keyboard.press("End");
  await expect(narrativeTab).toBeFocused();
});

test("roving tabIndex: exactly one tab is in the Tab order at a time, matching the focused tab", async ({ page }) => {
  await openWorkMode(page);
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");

  const tabs = page.getByRole("tab");
  const tabIndexValues = await tabs.evaluateAll((nodes) => nodes.map((node) => node.getAttribute("tabindex")));
  expect(tabIndexValues.filter((value) => value === "0")).toHaveLength(1);
  await expect(page.getByRole("tab", { name: "AI suggestion" })).toHaveAttribute("tabindex", "0");
});

test("switching tabs preserves in-progress input in the non-active panel (mounted+hidden, not reset)", async ({ page }) => {
  await openWorkMode(page);
  await page.getByRole("tab", { name: "Merge selection" }).click();

  const instructionInput = page.locator('[data-ui-region="work-mode"] textarea, [data-ui-region="work-mode"] input[type="text"]').first();
  await instructionInput.fill("work-mode-tabs-e2e-marker-text");

  await page.getByRole("tab", { name: "Narrative" }).click();
  await expect(page.getByRole("tabpanel", { name: "Merge selection" })).toBeHidden();

  await page.getByRole("tab", { name: "Merge selection" }).click();
  await expect(instructionInput).toHaveValue("work-mode-tabs-e2e-marker-text");
});

test("staged Escape: first backs out to the active tab, second closes the panel and restores trigger focus", async ({ page }) => {
  const trigger = page.getByRole("button", { name: WORK_MODE_BUTTON });
  await openWorkMode(page);

  await page.getByRole("tab", { name: "Merge selection" }).click();
  const instructionInput = page.locator('[data-ui-region="work-mode"] textarea, [data-ui-region="work-mode"] input[type="text"]').first();
  await instructionInput.focus();

  await page.keyboard.press("Escape");
  await expect(page.getByRole("tab", { name: "Merge selection" })).toBeFocused();
  await expect(page.locator('[data-ui-region="work-mode"]')).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.locator('[data-ui-region="work-mode"]')).toBeHidden();
  await expect(trigger).toBeFocused();
});

test("diagnostics tab reuses the existing document-wide counts with no score/rank/percent vocabulary", async ({ page }) => {
  await openWorkMode(page);
  await page.getByRole("tab", { name: "Diagnostics" }).click();

  const panel = page.getByRole("tabpanel", { name: "Diagnostics" });
  await expect(panel).toBeVisible();
  await expect(panel).toContainText("Unreviewed: cards 2, islands 0");
  await expect(panel).toContainText("Hold / unknown claims: 1");
  await expect(panel).toContainText("Critique or pending feedback targets: 1");
  await expect(panel).toContainText("Evidence links 2, contradictions 1, evidence gaps 0");

  // The anti-scoring disclaimer itself explicitly names "priority" in a
  // negating sentence ("not a priority order") -- strip it before checking,
  // same pattern agent_task_export.spec.ts uses for its own guardrail text.
  const panelText = (await panel.textContent()) ?? "";
  const withoutDisclaimer = panelText.replace(/These numbers[^.]*\./, "");
  expect(withoutDisclaimer).not.toMatch(/score|rank|priority|%/i);
});

test("at 390px the tab strip scrolls and keeps the active/focused tab in view", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 720 });
  await openWorkMode(page);

  const tablist = page.getByRole("tablist");
  const isScrollable = await tablist.evaluate((node) => node.scrollWidth > node.clientWidth);
  expect(isScrollable).toBe(true);

  const narrativeTab = page.getByRole("tab", { name: "Narrative" });
  await page.keyboard.press("End");
  await expect(narrativeTab).toBeFocused();

  const inView = await narrativeTab.evaluate((node) => {
    const tabRect = node.getBoundingClientRect();
    const listRect = node.closest('[role="tablist"]')!.getBoundingClientRect();
    return tabRect.left >= listRect.left - 1 && tabRect.right <= listRect.right + 1;
  });
  expect(inView).toBe(true);
});
