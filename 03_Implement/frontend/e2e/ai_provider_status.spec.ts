import { expect, test, type Page } from "@playwright/test";

// PROV-VIS-01 (ADR-0050 D1): the View panel shows a read-only echo of the
// configured LLM provider. There is no runtime switch — only a display.

const START_PANEL = '[data-panel="start-document-entry"]';

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Provider status fixture",
    createdAt: "2026-07-06T00:00:00.000Z",
    updatedAt: "2026-07-06T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(
  page: Page,
  providerKind: string,
  callCounts?: Record<string, number>,
  tokenUsage?: Record<string, { input: number; output: number }>,
): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"provider-status"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        providerKind,
        callCounts: callCounts ?? {},
        tokenUsage: tokenUsage ?? {},
      }),
    });
  });
}

test("View panel shows the configured provider read-only, with no switch control", async ({ page }) => {
  await routeDocument(page, "local", { local: 7, total: 7 }, { local: { input: 120, output: 37 }, total: { input: 120, output: 37 } });
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  await page.getByRole("button", { name: "View", exact: true }).click();

  await expect(page.getByText("AI provider", { exact: true })).toBeVisible();
  await expect(page.getByText("Local", { exact: true })).toBeVisible();

  // OPS-LLM-COST-02: in-process LLM call counts are surfaced read-only.
  const callCounts = page.locator('[data-ui-region="llm-call-counts"]');
  await expect(callCounts).toBeVisible();
  await expect(callCounts).toContainText("7");
  await expect(callCounts).toContainText("local");

  // OPS-LLM-COST-01 (段階2): in-process token usage (input/output) is surfaced
  // read-only alongside the call counts.
  const tokenUsage = page.locator('[data-ui-region="llm-token-usage"]');
  await expect(tokenUsage).toBeVisible();
  await expect(tokenUsage).toContainText("120/37");
  await expect(tokenUsage).toContainText("local");

  // No runtime switch: no select/combobox/radiogroup for provider anywhere in the panel.
  await expect(page.getByRole("combobox", { name: /provider/i })).toHaveCount(0);
  await expect(page.getByRole("radiogroup", { name: /provider/i })).toHaveCount(0);
});

test("View panel shows 'disabled' when the provider is none", async ({ page }) => {
  await routeDocument(page, "none");
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  await page.getByRole("button", { name: "View", exact: true }).click();

  await expect(page.getByText("Disabled (none)", { exact: false })).toBeVisible();
  // OPS-LLM-COST-02: empty call counts (provider disabled) -> no counts line.
  await expect(page.locator('[data-ui-region="llm-call-counts"]')).toHaveCount(0);
  // OPS-LLM-COST-01 (段階2): empty token usage -> no token line either.
  await expect(page.locator('[data-ui-region="llm-token-usage"]')).toHaveCount(0);
});

test("View panel shows DeepSeek when the configured provider is deepseek", async ({ page }) => {
  await routeDocument(
    page,
    "deepseek",
    { deepseek: 2, total: 2 },
    { deepseek: { input: 80, output: 20 }, total: { input: 80, output: 20 } },
  );
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
  await page.getByRole("button", { name: "View", exact: true }).click();

  await expect(page.getByText("DeepSeek", { exact: true })).toBeVisible();
  await expect(page.locator('[data-ui-region="llm-call-counts"]')).toContainText("deepseek: 2");
  await expect(page.locator('[data-ui-region="llm-token-usage"]')).toContainText("deepseek: 80/20");
});
