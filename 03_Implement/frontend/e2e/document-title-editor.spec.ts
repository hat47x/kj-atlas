import { expect, test, type Page } from "@playwright/test";

// DATA-GENERATION-01: the DocumentTitleEditor displays the document title (or
// "無題" as a placeholder), switches to an inline edit input on click, and
// conditionally shows an AI suggest-title button based on the configured
// provider.

async function routeEssentials(page: Page, providerKind: string): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ providerKind }),
    });
  });
  // Accept any PUT (triggered by onTitleChange → applyDocumentChange) so the
  // test doesn't stall on an unhandled network request.
  await page.route("**/docs/*", async (route) => {
    if (route.request().method() !== "PUT") {
      await route.fallback();
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"title-editor-test"' },
      body: route.request().postData() ?? "{}",
    });
  });
}

test("displays the document title and enters edit mode on click", async ({ page }) => {
  await routeEssentials(page, "local");
  await page.goto("/?locale=en");

  // Create a new document so the title defaults to the untitled placeholder.
  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.getByTestId("document-title-display")).toBeVisible();

  // Placeholder shown when no title is set (English, matching the ?locale=en
  // navigation above -- QA-MONKEY-19: this previously asserted the Japanese
  // "無題" string while the page was loaded under the English locale).
  await expect(page.getByTestId("document-title-display")).toHaveText("Untitled");

  // Click enters inline edit mode.
  await page.getByTestId("document-title-display").click();
  await expect(page.getByTestId("document-title-input")).toBeVisible();
  await expect(page.getByTestId("document-title-input")).toBeFocused();
});

test("shows the suggest-title button when a provider is configured", async ({ page }) => {
  await routeEssentials(page, "local");
  await page.goto("/?locale=en");

  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.getByTestId("document-title-display")).toBeVisible();
  await expect(page.getByTestId("suggest-title-button")).toBeVisible();

  // Candidates panel and error banner are absent until the suggest action runs.
  await expect(page.getByTestId("title-candidates")).toHaveCount(0);
  await expect(page.getByTestId("title-suggest-error")).toHaveCount(0);
});

test("hides the suggest-title button when the provider is none", async ({ page }) => {
  await routeEssentials(page, "none");
  await page.goto("/?locale=en");

  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.getByTestId("document-title-display")).toBeVisible();
  await expect(page.getByTestId("suggest-title-button")).toHaveCount(0);
});
