import { expect, test, type Page } from "@playwright/test";
import type { DocumentV1 } from "../src/domain/types";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

const START_PANEL = '[data-panel="start-document-entry"]';

async function routeDomainExpressionFixture(page: Page): Promise<{
  enableSample: () => void;
  getStoredDocument: () => DocumentV1;
}> {
  let shouldReturnSample = false;
  let storedDocument = buildDomainExpressionDocument() as unknown as DocumentV1;
  let revision = 0;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/*", async (route) => {
    if (route.request().method() === "PUT") {
      storedDocument = route.request().postDataJSON() as DocumentV1;
      revision += 1;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: `"domain-expression-keyboard-access-${revision}"` },
        body: JSON.stringify(storedDocument),
      });
      return;
    }

    const document = shouldReturnSample
      ? storedDocument
      : withoutProductValueContent(buildDomainExpressionDocument());

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: {
        ETag: shouldReturnSample
          ? `"domain-expression-keyboard-access-${revision}"`
          : '"domain-expression-keyboard-access-empty"',
      },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
    getStoredDocument: () => storedDocument,
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

  const targetCard = page.getByRole("button", { name: "ambiguous target claim" });
  await expect(targetCard).toBeVisible();
  await targetCard.focus();
  await expect(targetCard).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(targetCard).toHaveAttribute("aria-pressed", "true");

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
  await expect(selectionPanel.getByRole("checkbox", { name: "Too close" })).toBeVisible();
  await expect(selectionPanel.getByRole("checkbox", { name: "Too far" })).toBeVisible();
  await expect(selectionPanel.getByRole("checkbox", { name: "Not the same" })).toBeVisible();
  await expect(selectionPanel.getByRole("checkbox", { name: "Feels off" })).toBeVisible();
  await expect(selectionPanel.getByRole("checkbox", { name: "No articulable reason" })).toBeVisible();
  await expect(selectionPanel.locator('[data-domain-flow="critique-reproposal"]')).toContainText(
    "When AI is disabled, the critique remains saved but no reproposal candidate is generated.",
  );

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
    (element) => element instanceof HTMLInputElement && element.type === "checkbox" && element.closest("label")?.textContent?.includes("Too close") === true,
    "critique tag checkbox",
  );
  await page.keyboard.press("Space");
  await expect(page.getByLabel("Too close")).toBeChecked();

  await page.getByRole("button", { name: "Save" }).click();
  await expect.poll(() => fixture.getStoredDocument().cards.find((card) => card.id === "domain-target")?.critique)
    .toBe("keyboard review note");
  await expect.poll(() => fixture.getStoredDocument().cards.find((card) => card.id === "domain-target")?.critiqueTags)
    .toContain("too_close");

  // UX-NAV-02: this cross-navigation link now also switches work-mode's tabs
  // to the "AI suggestion" tab (the critique/reproposal workflow no longer
  // has its own standalone stacked section) before focusing it.
  await page.getByRole("button", { name: "Review reproposal" }).click();
  await expect(page.getByRole("button", { name: "Advanced" })).toHaveAttribute("aria-pressed", "true");
  await expect(page.getByRole("tab", { name: "AI suggestion" })).toHaveAttribute("aria-selected", "true");
  const critiqueWorkflow = page.locator('[data-domain-workflow="critique-reproposal"]');
  await expect(critiqueWorkflow).toBeVisible();
  await expect(critiqueWorkflow).toContainText("Capture critique and re-suggest iteratively");
  await expect(critiqueWorkflow).toContainText("Layout suggestion");
  await expect(critiqueWorkflow).toBeFocused();
});

test("contradiction state control is labeled and persists through save", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  const counterCard = page.getByRole("button", { name: "contradicting stakeholder signal" });
  await expect(counterCard).toBeVisible();
  await counterCard.click();

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toContainText("contradicts: ambiguous target claim");

  const contradictionState = page.getByLabel("Contradiction state for ambiguous target claim");
  await expect(contradictionState).toHaveValue("unconfirmed");
  await contradictionState.selectOption("held");
  await expect(contradictionState).toHaveValue("held");

  await page.getByRole("button", { name: "Save" }).click();
  await expect.poll(() => fixture.getStoredDocument().evidenceLinks.find((link) => link.id === "domain-counter-link")?.contradictionState)
    .toBe("held");
});

test("evidence link editor exposes labeled controls and adds a searched target", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  await page.getByRole("button", { name: "ambiguous target claim" }).click();
  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await selectionPanel.getByRole("button", { name: "Add evidence link..." }).click();

  await expect(selectionPanel.getByLabel("Link type")).toHaveValue("supports");
  await selectionPanel.getByLabel("Search target card").fill("supporting");
  await selectionPanel.getByLabel("Evidence target").selectOption("domain-support");
  await selectionPanel.getByRole("button", { name: "Confirm" }).click();

  await expect(selectionPanel).toContainText("supports: supporting field note");
  await page.getByRole("button", { name: "Save" }).click();
  await expect.poll(() => fixture.getStoredDocument().evidenceLinks.some((link) => (
    link.fromCardId === "domain-target"
    && link.toCardId === "domain-support"
    && link.type === "supports"
  ))).toBe(true);
});

test("share preflight keeps unresolved domain signals visible and unreviewed drafts excluded", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await page.getByRole("button", { name: "ambiguous target claim" }).click();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  const summary = page.getByTestId("share-domain-expression-summary");
  await expect(page.getByText("SafeMode is ON, so unreviewed drafts are excluded.")).toBeVisible();
  await expect(page.getByText("5 review signals remain")).toBeVisible();
  await expect(summary).toContainText("Ambiguity / evidence / review summary");
  await expect(summary).toContainText("Unreviewed: cards 2, islands 0");
  await expect(summary).toContainText("Hold / unknown claims: 1");
  await expect(summary).toContainText("Critique or pending feedback targets: 1");
  await expect(summary).toContainText("Evidence links 2, contradictions 1, evidence gaps 0");
  await expect(summary).toContainText(
    "SafeMode keeps draft and unreviewed body exposure constrained; review or keep holds explicit before sharing.",
  );
  await expect(page.getByLabel("Include unreviewed drafts")).toHaveCount(0);
});

test("keyboard shelf and restore remain stable across saves and reloads", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  const targetCard = page.getByRole("button", { name: "ambiguous target claim" });
  await expect(targetCard).toBeVisible();
  const initialBox = await targetCard.boundingBox();
  expect(initialBox).not.toBeNull();

  await targetCard.focus();
  await page.keyboard.press("Enter");
  await expect(targetCard).toHaveAttribute("aria-pressed", "true");

  await tabUntilFocused(
    page,
    (element) => element instanceof HTMLSelectElement && element.labels?.[0]?.textContent?.includes("Hold state") === true,
    "hold state select",
  );
  const holdStateSelect = page.getByLabel("Hold state");
  await expect(holdStateSelect).toBeFocused();
  await page.keyboard.press("End");
  await expect(holdStateSelect).toHaveValue("shelved");

  await expect(targetCard).toHaveCount(0);
  const shelf = page.getByRole("region", { name: "Shelf (set aside)" });
  await expect(shelf).toContainText("ambiguous target claim");

  const saveButton = page.getByRole("button", { name: "Save" });
  await saveButton.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  const storedAfterShelving = fixture.getStoredDocument();
  expect(storedAfterShelving.cards.find((card) => card.id === "domain-target")?.holdState).toBe("shelved");
  expect(storedAfterShelving.shelf?.map((entry) => entry.cardId)).toContain("domain-target");
  expect(storedAfterShelving.cards.find((card) => card.id === "domain-target")).toMatchObject({ x: 140, y: 130 });

  await page.reload();
  await page.getByRole("button", { name: "Close start panel" }).click();
  await expect(page.getByRole("button", { name: "ambiguous target claim" })).toHaveCount(0);

  const restoredShelf = page.getByRole("region", { name: "Shelf (set aside)" });
  await expect(restoredShelf).toContainText("ambiguous target claim");
  const restoreButton = restoredShelf.getByRole("button", { name: "Restore" });
  await restoreButton.focus();
  await expect(restoreButton).toBeFocused();
  await page.keyboard.press("Enter");

  await expect(restoredShelf).toHaveCount(0);
  const restoredCard = page.getByRole("button", { name: "ambiguous target claim" });
  await expect(restoredCard).toBeVisible();
  const restoredBox = await restoredCard.boundingBox();
  expect(restoredBox).not.toBeNull();
  expect(restoredBox?.x).toBeCloseTo(initialBox?.x ?? 0, 0);
  expect(restoredBox?.y).toBeCloseTo(initialBox?.y ?? 0, 0);

  await saveButton.focus();
  await page.keyboard.press("Enter");
  await expect(page.getByText("Saved", { exact: true })).toBeVisible();

  const storedAfterRestore = fixture.getStoredDocument();
  expect(storedAfterRestore.cards.find((card) => card.id === "domain-target")?.holdState).toBeUndefined();
  expect(storedAfterRestore.shelf ?? []).toHaveLength(0);

  await page.reload();
  await page.getByRole("button", { name: "Close start panel" }).click();
  await expect(page.getByRole("button", { name: "ambiguous target claim" })).toBeVisible();
  await expect(page.getByRole("region", { name: "Shelf (set aside)" })).toHaveCount(0);
});
