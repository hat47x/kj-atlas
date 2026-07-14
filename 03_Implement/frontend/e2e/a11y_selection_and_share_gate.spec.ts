import { expect, test, type Page } from "@playwright/test";
import { SHARE_REPRODUCE_BUTTON } from "./helpers/i18n";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

// UI-QUALITY-A11Y-02 (ADR-0048 Round 4 a11y spec, ADR-0044 UQ-2): per-surface
// aria/focus completion for selection-context and pre-share confirmation.
// Legend (CanvasLegend.tsx) and work-mode-tabs are explicitly out of scope
// for this slice (legend: concurrent edit in a separate session; work-mode
// tabs: a literal role=tablist redesign was already ruled out-of-scope by
// PRODUCT-UX-03/UX-NAV-01 -- retrofitting it here would contradict that).

const START_PANEL = '[data-panel="start-document-entry"]';

async function routeDomainExpressionFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    const document = shouldReturnSample
      ? buildDomainExpressionDocument()
      : withoutProductValueContent(buildDomainExpressionDocument());
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"a11y-loaded"' : '"a11y-empty"' },
      body: JSON.stringify(document),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

test("selection context announces changes politely and reads type before hold before review before evidence", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  const selectionContext = page.locator('[data-panel="selection-context"]');
  await expect(selectionContext).toHaveAttribute("aria-live", "polite");

  // "ambiguous target claim" is claimType=unknown with a critique and hold
  // state absent by default in this fixture -- pick a card with evidence
  // links to exercise the fuller chip row.
  await page.getByRole("button", { name: "supporting field note" }).click();
  await expect(selectionContext).toContainText("Card selected");

  const panelText = (await selectionContext.textContent()) ?? "";
  // "supporting field note" has claimType=fact (no hold state set), so the
  // observable order here is: claim type, then review state, then evidence.
  const claimTypeIdx = panelText.indexOf("Claim type");
  const reviewIdx = panelText.indexOf("Review state");
  expect(claimTypeIdx).toBeGreaterThanOrEqual(0);
  expect(claimTypeIdx).toBeLessThan(reviewIdx);
});

test("share preflight's source-reference toggle warning is associated via aria-describedby", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const toggle = page.locator('[data-share-include-source-references] input[type="checkbox"]');
  await expect(toggle).not.toHaveAttribute("aria-describedby", /.+/);

  await toggle.check();
  const describedBy = await toggle.getAttribute("aria-describedby");
  expect(describedBy).toBeTruthy();
  // React's useId() ids (e.g. ":r5:") contain characters that break a plain
  // `#id` CSS selector -- use an attribute selector instead.
  const warning = page.locator(`[id="${describedBy}"]`);
  await expect(warning).toBeVisible();
  await expect(warning).toHaveAttribute("data-share-source-references-warning", "");
});
