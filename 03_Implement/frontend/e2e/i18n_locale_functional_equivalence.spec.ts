import { expect, test } from "@playwright/test";
import { SHARE_REPRODUCE_BUTTON, SUGGEST_LAYOUT_BUTTON } from "./helpers/i18n";

type LocaleCase = {
  locale: "ja" | "en";
  query: string;
  safeModeLockedText: RegExp;
};

const LOCALE_CASES: LocaleCase[] = [
  {
    locale: "ja",
    query: "?locale=ja&readOnly=1",
    safeModeLockedText: /固定マスク対象: 共有 \/ レビューパック（無効化できません）。/,
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

    await expect(page.getByRole("button", { name: SUGGEST_LAYOUT_BUTTON }).first()).toBeDisabled();
    await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
    await expect(page.getByText(localeCase.safeModeLockedText)).toBeVisible();
  }
});
