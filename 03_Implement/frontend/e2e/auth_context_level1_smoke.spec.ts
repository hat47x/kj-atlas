import { expect, test } from "@playwright/test";

test("auth: smoke keeps read-only boundary visible", async ({ page }) => {
  await page.goto("/?locale=en&readOnly=true");

  await expect(page.getByText("Read-only mode is active. Editing actions are disabled.")).toBeVisible();
  await expect(page.getByRole("button", { name: "Share & Reproduce" })).toBeVisible();
});
