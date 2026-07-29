import { expect, test } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";

const CREATED_AT = "2026-07-29T00:00:00.000Z";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-inquiry-end-confirmation",
    title: "End confirmation fixture",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "card-1", text: "Initial observation", x: 100, y: 100 }],
    edges: [],
    islands: [],
  };
}

async function openInquiryPanel(page: import("@playwright/test").Page, document: DocumentV1) {
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Close start panel" }).click();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const chooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const chooser = await chooserPromise;
  await chooser.setFiles({
    name: "end-confirmation-document.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(document), "utf8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible();
  await page.getByRole("button", { name: "Close panel" }).click();

  await page.getByRole("button", { name: "Advanced" }).click();
  await page.getByRole("button", { name: "Work mode" }).click();
  await page.getByRole("tab", { name: "Inquiry" }).click();
  return page.locator('[data-panel="inquiry-journey-prototype"]');
}

// DOMAIN-W-ITERATION-01 AC-13 / T10 (Claude Design P35): "end inquiry" is a
// destructive operation and must offer the same save/discard/cancel
// alertdialog pattern as A-1 (TenantChangeConfirmationDialog), with focus
// management and keyboard support verified at 390px.
test("DOMAIN-W-ITERATION-01 offers save/discard/cancel when ending an inquiry, with keyboard focus and Escape=cancel", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const panel = await openInquiryPanel(page, createDocument());

  await panel.locator('[data-domain-action="start-inquiry-journey-prototype"]').click();
  await expect(panel.getByText("Changes are not saved automatically. Save an inquiry file before closing this view.")).toBeVisible();

  const endButton = panel.getByRole("button", { name: "Close on-screen inquiry" });
  await endButton.focus();
  await endButton.press("Enter");

  const dialog = page.getByRole("alertdialog", { name: "End this inquiry?" });
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText("Unsaved changes will be lost. Confirm that you saved an inquiry file.");

  const cancelButton = dialog.getByRole("button", { name: "Continue" });
  await expect(cancelButton).toBeFocused();

  // Escape maps to cancel and returns to the ongoing-inquiry view without losing state.
  await page.keyboard.press("Escape");
  await expect(dialog).toBeHidden();
  await expect(panel.getByText("Changes are not saved automatically. Save an inquiry file before closing this view.")).toBeVisible();

  // Re-open and cancel via the button itself (not just Escape).
  await endButton.focus();
  await endButton.press("Enter");
  await expect(dialog).toBeVisible();
  await dialog.getByRole("button", { name: "Continue" }).click();
  await expect(dialog).toBeHidden();
  await expect(panel.getByText("Changes are not saved automatically. Save an inquiry file before closing this view.")).toBeVisible();

  // Tab from the last focusable button wraps back to cancel (focus trap).
  await endButton.focus();
  await endButton.press("Enter");
  await expect(dialog).toBeVisible();
  const saveButton = dialog.getByRole("button", { name: "Save and end" });
  await saveButton.focus();
  await page.keyboard.press("Tab");
  await expect(dialog.getByRole("button", { name: "Continue" })).toBeFocused();

  expect(await dialog.evaluate((element) => element.getBoundingClientRect().right)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: testInfo.outputPath("inquiry-end-confirmation-390px.png"), fullPage: true });

  // Discard: the on-screen inquiry is cleared and the start view returns.
  await dialog.getByRole("button", { name: "Close without saving" }).click();
  await expect(dialog).toBeHidden();
  await expect(panel.getByRole("button", { name: "Start from the current document" })).toBeVisible();
});

test("DOMAIN-W-ITERATION-01 save-and-end downloads the bundle before clearing the on-screen inquiry", async ({ page }) => {
  const panel = await openInquiryPanel(page, createDocument());
  await panel.locator('[data-domain-action="start-inquiry-journey-prototype"]').click();
  await expect(panel.getByText("Changes are not saved automatically. Save an inquiry file before closing this view.")).toBeVisible();

  await panel.getByRole("button", { name: "Close on-screen inquiry" }).click();
  const dialog = page.getByRole("alertdialog", { name: "End this inquiry?" });
  await expect(dialog).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await dialog.getByRole("button", { name: "Save and end" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toContain("kj-atlas-inquiry.json");

  await expect(dialog).toBeHidden();
  await expect(panel.getByRole("button", { name: "Start from the current document" })).toBeVisible();
});
