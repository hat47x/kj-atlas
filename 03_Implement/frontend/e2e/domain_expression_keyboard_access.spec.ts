import { expect, test, type Page } from "@playwright/test";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

const START_PANEL = '[data-panel="start-document-entry"]';

async function routeDomainExpressionFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const document = shouldReturnSample ? buildDomainExpressionDocument() : withoutProductValueContent(buildDomainExpressionDocument());

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"domain-expression-keyboard-access-loaded"' : '"domain-expression-keyboard-access-empty"' },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

async function tabUntilFocused(page: Page, predicate: (element: Element) => boolean, description: string): Promise<void> {
  for (let index = 0; index < 80; index += 1) {
    const matched = await page.evaluate((predicateSource) => {
      const active = document.activeElement;
      if (!active) return false;
      return Function("element", `return (${predicateSource})(element);`)(active) === true;
    }, predicate.toString());

    if (matched) {
      return;
    }

    await page.keyboard.press("Tab");
  }

  throw new Error(`Could not focus ${description} with Tab`);
}

test("domain expression state controls are reachable with keyboard after card selection", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  await expect(page.locator(START_PANEL)).toBeVisible();
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  const targetCard = page.getByRole("option", { name: "ambiguous target claim" });
  await expect(targetCard).toBeVisible();
  await targetCard.focus();
  await expect(targetCard).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(targetCard).toHaveAttribute("aria-selected", "true");

  const selectionSummary = page.locator('[data-panel="selection-context"]');
  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionSummary).toContainText("Card selected");
  await expect(selectionSummary).toContainText("Review state: Unreviewed");
  await expect(selectionPanel).toContainText("Claim type");
  await expect(selectionPanel).toContainText("Unknown");
  await expect(selectionPanel).toContainText("Evidence");
  await expect(selectionPanel).toContainText("supporting field note supports this");
  await expect(selectionPanel).toContainText("contradicting stakeholder signal contradicts this");
  await expect(selectionPanel).toContainText("Critique note");
  await expect(selectionPanel).toContainText("needs review before acceptance");

  await tabUntilFocused(
    page,
    (element) => element instanceof HTMLSelectElement && ["fact", "claim", "hypothesis", "unknown"].includes(element.value),
    "claim type select",
  );
  const isClaimTypeSelectFocused = await page.evaluate(() => document.activeElement instanceof HTMLSelectElement && document.activeElement.value === "unknown");
  expect(isClaimTypeSelectFocused).toBe(true);

  await tabUntilFocused(
    page,
    (element) => element instanceof HTMLInputElement && element.type === "checkbox" && element.closest("label")?.textContent?.includes("Card text reviewed") === true,
    "card text reviewed checkbox",
  );
  await page.keyboard.press("Space");
  await expect(page.getByLabel("Card text reviewed")).toBeChecked();

  await tabUntilFocused(
    page,
    (element) => element instanceof HTMLTextAreaElement && element.placeholder === "Optional feedback about this card",
    "critique note textarea",
  );
  await page.keyboard.press("Control+A");
  await page.keyboard.type("keyboard review note");
  await expect(page.getByPlaceholder("Optional feedback about this card")).toHaveValue("keyboard review note");

  await tabUntilFocused(
    page,
    (element) => element instanceof HTMLInputElement && element.type === "checkbox" && element.closest("label")?.textContent?.includes("too_close") === true,
    "critique tag checkbox",
  );
  await page.keyboard.press("Space");
  await expect(page.getByLabel("too_close")).toBeChecked();
});
