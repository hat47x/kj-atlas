import { expect, test, type Page } from "@playwright/test";
import {
  DOCUMENT_REPLACED_STATUS,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  WORK_MODE_BUTTON,
  closeSharePanelIfOpen,
  enableAdvancedUiIfNeeded,
} from "./helpers/i18n";

// KJ-AB-CROSS-CHECK-01: the narrative A/B cross-check surfaces issues with a
// direction (a_missing_in_b / b_missing_in_a) and totals. This freezes the UI
// surface: select a narrative in the work-mode Narrative tab, run "Check
// consistency", and the past-checks summary reports the issue count. The AI
// route is mocked so this works in the standalone E2E mount.

function buildAbDocument() {
  const now = "2026-08-16T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_e2e_ab",
    title: "ab check fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "利用者は待ち時間を問題視している", x: 0, y: 0, textReviewed: true },
      { id: "c2", text: "接客品質は評価が高い", x: 200, y: 0, textReviewed: true },
    ],
    edges: [],
    islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
    readingOrder: ["i1"],
    narratives: [
      {
        id: "narr-1",
        title: "test narrative",
        text: "待ち時間の改善が主訴である",
        basedOnReadingOrder: ["i1"],
        reviewed: false,
        checks: [],
      },
    ],
  };
}

async function loadDocument(page: Page): Promise<void> {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "ab.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildAbDocument()), "utf-8"),
  });
  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await closeSharePanelIfOpen(page);
}

test("the narrative A/B check surfaces a_missing_in_b issues with counts", async ({ page }) => {
  // Mock the A/B cross-check route (backend-less mount).
  await page.route("**/ai/check-narrative", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        issues: [
          {
            severity: "info",
            message: "ナラティブが島i1に触れていない（a_missing_in_b）",
            references: [{ id: "i1", kind: "island" }],
            direction: "a_missing_in_b",
          },
        ],
        counts: { bMissingInA: 0, aMissingInB: 1 },
      }),
    });
  });
  // The check attaches to the selected narrative and marks the doc dirty; let
  // the persistence PUT succeed so no save-error status overrides the result.
  await page.route("**/docs/doc_e2e_ab", async (route) => {
    if (route.request().method() === "PUT") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: route.request().postData() ?? "{}",
      });
    } else {
      await route.continue();
    }
  });

  await loadDocument(page);
  await enableAdvancedUiIfNeeded(page);

  // Open work mode and the Narrative tab.
  await page.getByRole("button", { name: WORK_MODE_BUTTON }).click();
  await page.getByRole("tab", { name: "Narrative" }).click();

  // Select the pre-seeded narrative (sets the narrative text, enabling the check).
  await page.getByRole("button", { name: /test narrative/ }).click();

  // Run the A/B cross-check.
  await page.getByRole("button", { name: /Check consistency/ }).click();

  // The past-checks summary reports the single a_missing_in_b issue.
  await expect(page.getByText(/issues: 1/)).toBeVisible();

  // The current "Consistency issues" section surfaces the A/B direction
  // (KJ-AB-CROSS-CHECK-01). The message may also appear in the expanded
  // past-check, so scope the assertion with .first().
  await expect(page.getByText("Consistency issues")).toBeVisible();
  await expect(page.getByText(/a_missing_in_b/).first()).toBeVisible();
});
