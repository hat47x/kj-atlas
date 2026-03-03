import { expect, test } from "@playwright/test";

type LocaleCase = {
  locale: "ja" | "en";
  query: string;
  safeModeLockedText: RegExp;
};

const LOCALE_CASES: LocaleCase[] = [
  {
    locale: "ja",
    query: "?locale=ja&readOnly=1",
    safeModeLockedText: /固定マスク対象: Share \/ Review Pack（無効化できません）。/,
  },
  {
    locale: "en",
    query: "?locale=en&readOnly=1",
    safeModeLockedText: /Locked redaction contexts: Share \/ Review Pack \(cannot be disabled\)\./,
  },
];

test("safe mode locked contexts and readonly action block stay locale-equivalent", async ({ page }) => {
  for (const localeCase of LOCALE_CASES) {
    await page.goto(`/${localeCase.query}`);

    await expect(page.getByRole("button", { name: /Suggest layout/ }).first()).toBeDisabled();
    await page.getByRole("button", { name: /Share & Reproduce|共有と再現/ }).click();
    await expect(page.getByText(localeCase.safeModeLockedText)).toBeVisible();
  }
});
