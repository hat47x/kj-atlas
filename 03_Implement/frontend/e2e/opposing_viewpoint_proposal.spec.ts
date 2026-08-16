import { expect, test, type Page } from "@playwright/test";
import {
  DOCUMENT_REPLACED_STATUS,
  LOAD_DOCUMENT_BUTTON,
  REPLACE_DOCUMENT_BUTTON,
  SHARE_REPRODUCE_BUTTON,
  closeSharePanelIfOpen,
} from "./helpers/i18n";

// AI-OPPOSE-01 (M4): the opposing-viewpoint proposal surface in the Card
// Inspector is proposal-only — shown with a rationale, never auto-applied, and
// connectable to the card's hold state. The AI route is mocked so this works
// in the standalone E2E mount.

function buildProposalDocument() {
  const now = "2026-08-16T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_e2e_opposing",
    title: "opposing viewpoint fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-claim", text: "待ち時間が長いと利用者は離れる", x: 0, y: 0, textReviewed: true },
      { id: "c-counter", text: "待ち時間が長くても常連は残る", x: 200, y: 0, textReviewed: true },
    ],
    edges: [],
    islands: [{ id: "i1", cardIds: ["c-claim", "c-counter"] }],
    readingOrder: ["i1"],
  };
}

async function loadDocument(page: Page): Promise<void> {
  await page.goto("/");
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: LOAD_DOCUMENT_BUTTON }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "opposing.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildProposalDocument()), "utf-8"),
  });
  await page.getByRole("button", { name: REPLACE_DOCUMENT_BUTTON }).click();
  await expect(page.getByText(DOCUMENT_REPLACED_STATUS)).toBeVisible();
  await closeSharePanelIfOpen(page);
}

test("the opposing-viewpoint proposal is shown proposal-only and can be held", async ({ page }) => {
  // Mock the AI proposal route (backend-less mount).
  await page.route("**/ai/proposals/opposing-viewpoint", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        proposalId: "proposal-e2e-1",
        type: "opposing_viewpoint",
        status: "proposed",
        reviewState: "unreviewed",
        targetCardId: "c-claim",
        opposingText: "逆の状況でも同じ帰結が起きる可能性がある",
        evidenceGap: true,
        rationale: "反例カードが根拠として接続されていない",
        warnings: [],
      }),
    });
  });

  await loadDocument(page);

  // Select the claim card (keyboard interaction, robust to canvas animation).
  const claimCard = page.getByRole("button", { name: /待ち時間が長いと利用者は離れる/ });
  await expect(claimCard).toBeVisible();
  await claimCard.focus();
  await page.keyboard.press("Enter");

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();

  // Request the opposing-viewpoint proposal.
  const proposeButton = selectionPanel.locator('[data-ui-region="propose-opposing-viewpoint"]');
  await expect(proposeButton).toBeVisible();
  await proposeButton.click();

  // Proposal is displayed proposal-only (with rationale + proposal-only note).
  const proposal = selectionPanel.locator('[data-ui-region="opposing-viewpoint-proposal"]');
  await expect(proposal).toBeVisible();
  await expect(proposal).toContainText("逆の状況でも同じ帰結が起きる可能性がある");
  await expect(proposal).toContainText("反例カードが根拠として接続されていない");

  // Hold for review -> proposal dismissed and card transitions to held.
  await selectionPanel.locator('[data-ui-region="hold-opposing-viewpoint"]').click();
  await expect(proposal).toHaveCount(0);
  await expect(selectionPanel.locator('#selected-card-hold-state')).toHaveValue("held");
});
