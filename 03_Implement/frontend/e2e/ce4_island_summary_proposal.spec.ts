import { expect, test, type Page } from "@playwright/test";
import {
  DOCUMENT_REPLACED_STATUS,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  closeSharePanelIfOpen,
  enableAdvancedUiIfNeeded,
} from "./helpers/i18n";

// CE4 proposal chain (query -> bundle -> proposal -> adopt/reject): the island
// summary proposal is shown proposal-only (status "proposed", never auto-applied),
// and the human adopt records the decision before the summary is applied locally
// as an unreviewed draft. AI routes are mocked so this works in the standalone
// E2E mount. Closes the scenario-doc gap: "UI 層 E2E（CE4 proposal 連鎖）".

function buildCe4Document() {
  const now = "2026-08-16T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_e2e_ce4",
    title: "ce4 proposal fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-wait", text: "待ち時間が長いと感じた", x: 0, y: 0, textReviewed: true },
      { id: "c-serv", text: "接客は丁寧だった", x: 200, y: 0, textReviewed: true },
    ],
    edges: [],
    islands: [{ id: "island-ce4", cardIds: ["c-wait", "c-serv"] }],
    readingOrder: ["island-ce4"],
  };
}

const ADOPTED_SUMMARY = "待ち時間の改善が主訴であり、接客体験の質が定着要因である";

async function loadDocument(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "ce4.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildCe4Document()), "utf-8"),
  });
  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await closeSharePanelIfOpen(page);
}

test("the island-summary proposal is proposal-only and adopt records the decision", async ({ page }) => {
  // Mock the CE4 proposal routes (backend-less mount).
  await page.route("**/ai/proposals/island-summary", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        proposalId: "proposal-ce4-1",
        type: "island_summary",
        status: "proposed",
        sourceBundleHash: "mock:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        diff: {
          entityType: "island_summary",
          targetId: "island-ce4",
          field: "summaryText",
          after: ADOPTED_SUMMARY,
          groundingIds: ["c-wait", "c-serv"],
          warnings: [],
        },
        rationale: "2枚のカードを統合した下書き要約",
      }),
    });
  });
  await page.route("**/ai/proposals/audit", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        recorded: true,
        eventId: "evt-ce4-1",
        proposalId: "proposal-ce4-1",
        status: "accepted",
        reviewState: "unreviewed",
        recordedAt: "2026-08-16T00:00:00.000Z",
      }),
    });
  });
  // The adopt applies the summary locally and marks the doc dirty; let the
  // persistence PUT succeed so no save-error status overrides the adopt message.
  await page.route("**/docs/doc_e2e_ce4", async (route) => {
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

  // The "Suggest AI summary" button lives behind the advanced-UI disclosure.
  await enableAdvancedUiIfNeeded(page);

  // Select the island (keyboard interaction, robust to canvas animation).
  const islandSelect = page.getByRole("button", { name: /島 island-ce4 を選択|Select island island-ce4/ });
  await expect(islandSelect).toBeVisible();
  await islandSelect.focus();
  await page.keyboard.press("Enter");

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();

  // Request the island-summary proposal (CE4 propose).
  await selectionPanel.getByRole("button", { name: /Suggest AI summary|AI 要約を提案/ }).click();

  // Proposal is displayed proposal-only: proposalId + status + patch preview.
  await expect(selectionPanel.getByText("proposal-ce4-1")).toBeVisible();
  await expect(selectionPanel.getByText(ADOPTED_SUMMARY)).toBeVisible();

  // Adopt: records the decision (audit route) and consumes the proposal.
  await selectionPanel.getByRole("button", { name: /Adopt|採用/ }).click();

  await expect(
    page.getByText(/Adopted the island summary draft. It remains unreviewed|島の要約ドラフトを採用しました。未レビューの状態です/)
  ).toBeVisible();
  await expect(selectionPanel.getByText("proposal-ce4-1")).toHaveCount(0);
});
