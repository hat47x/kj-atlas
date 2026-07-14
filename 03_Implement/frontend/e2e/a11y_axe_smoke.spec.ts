import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";
import { buildDomainExpressionDocument } from "./helpers/product_value_fixtures";

// UI-QUALITY-A11Y-02 residual (recorded 2026-07-09): a cross-surface axe
// smoke suite, deferred from the main slice. Runs axe-core's automated
// ruleset against the surfaces already covered by that slice's manual
// aria/focus work (selection context, share panel) plus the two surfaces
// this session's EXT-AGENT-01/02 rounds added (agent task export, agent
// response import) and the always-present canvas/menu chrome. This is a
// smoke check, not exhaustive coverage -- it catches automatable issues
// (missing labels, color-contrast, ARIA misuse) that the existing
// source-string regression anchors and targeted e2e tests don't.

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"a11y-axe-smoke"' },
      body: JSON.stringify(buildDomainExpressionDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

// Both categories tracked in issue-UI-QUALITY-A11Y-03-structural-aria-findings.md
// are now fixed and no rules are deferred:
//   - aria-required-parent: canvas cards were role="option" without a
//     role="listbox" ancestor; ADR-0052 moved cards to role="button" +
//     aria-pressed, an independently-reachable operation target with no
//     required-parent constraint (CardView.tsx, 2026-07-13).
//   - aria-required-children: the File menu's recent-documents <select> was
//     a disallowed direct child of role="menu"; it now lives in its own
//     dialog (RecentDocumentsDialog.tsx), reached via a menuitem instead of
//     rendering inline inside the open menu (2026-07-14).
async function expectNoViolations(page: Page, label: string): Promise<void> {
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations, `axe violations on ${label}: ${JSON.stringify(results.violations, null, 2)}`).toEqual([]);
}

test.beforeEach(async ({ page }) => {
  await routeFixture(page);
  await page.setViewportSize({ width: 1440, height: 900 });
});

test("start panel has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeVisible();
  await expectNoViolations(page, "start panel");
});

test("canvas with a card selected has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.locator('[data-ui-region="primary-flow"] [role="button"]').first().click();
  await expect(page.locator('[data-panel="selection-context"]')).toBeVisible();
  await expectNoViolations(page, "canvas with selection context");
});

test("canvas legend has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.locator('[data-focus-return-id="legend-trigger"]').click();
  await expect(page.locator('[data-ui-region="canvas-legend"]')).toBeVisible();
  await expectNoViolations(page, "canvas legend");
});

test("share panel has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();
  await expectNoViolations(page, "share panel");
});

test("work mode panel (advanced) has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("button", { name: "Advanced", exact: true }).click();
  await page.getByRole("button", { name: "Work mode" }).click();
  await expect(page.locator('[data-ui-region="work-mode"]')).toBeVisible();
  await expectNoViolations(page, "work mode panel");
});

test("agent task export panel has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("button", { name: "Advanced", exact: true }).click();
  await page.getByRole("button", { name: "Export to agent" }).click();
  await expect(page.locator('[data-ui-region="agent-task-export"]')).toBeVisible();
  await expectNoViolations(page, "agent task export panel");
});

test("agent response import panel has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("button", { name: "Advanced", exact: true }).click();
  await page.getByRole("button", { name: "Import agent response" }).click();
  await expect(page.locator('[data-ui-region="agent-response-import"]')).toBeVisible();
  await expectNoViolations(page, "agent response import panel");
});

test("menu bar open has no automatable a11y violations", async ({ page }) => {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();
  await page.getByRole("menuitem", { name: "File", exact: true }).click();
  await expectNoViolations(page, "menu bar with File menu open");
});
