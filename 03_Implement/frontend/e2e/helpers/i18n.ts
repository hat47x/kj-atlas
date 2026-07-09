import type { Page } from "@playwright/test";

export const SHARE_REPRODUCE_BUTTON = /Share & Reproduce|共有と再現/;
export const VIEW_BUTTON = /^View$|^表示$/;
export const ADVANCED_UI_BUTTON = /^Advanced$|^詳細$/;
export const SUGGEST_LAYOUT_BUTTON = /Suggest layout|配置を提案/;
export const LOAD_DOCUMENT_BUTTON = /^Load document\.json$|^document\.json を読み込む$/;
export const REPLACE_DOCUMENT_BUTTON = /Replace current document|現在のドキュメントを置換/;
export const EXPORT_BUNDLE_BUTTON = /Export bundle \(\.zip\)|レビューパックを書き出す \(.zip\)|bundle をエクスポート \(.zip\)/;
export const EXPORT_DOCUMENT_JSON_BUTTON = /Export document JSON|Export doc JSON \(legacy\)|ドキュメントJSONを書き出す（旧式）/;
export const READ_ONLY_INDICATOR = /Read-only mode is active|読み取り専用モードが有効|Read-only|読み取り専用/;
export const EDIT_ISLAND_BOUNDARY_CHECKBOX = /Edit island boundary|島の境界を編集/;
export const SEARCH_CARDS_PLACEHOLDER = /Search cards|カードを検索/;
export const HIDE_NON_MATCHES_CHECKBOX = /Hide non-matches|非一致を非表示/;

export function visibilitySelect(page: Page, label: "view" | "pack") {
  const labelPattern = label === "view" ? /View visibility|view の公開範囲/ : /Pack visibility|パックの公開範囲/;
  return page.locator("label").filter({ hasText: labelPattern }).locator("select");
}

export async function closeSharePanelIfOpen(page: Page): Promise<void> {
  const closeButton = page.getByRole("button", { name: /Close panel|パネルを閉じる/ });
  if (await closeButton.isVisible().catch(() => false)) {
    await closeButton.click();
  }
}

// UX-SHARE-01: any document carrying unreviewed/critique/contradiction
// content shows a pre-share summary gate after "Export bundle" is clicked,
// before the download actually starts (AC-1). Call this right after
// clicking EXPORT_BUNDLE_BUTTON and before awaiting the download event.
export async function continueThroughPreShareGateIfPresent(page: Page): Promise<void> {
  const continueButton = page.getByRole("button", { name: /^Continue$|^続行する$/ });
  if (await continueButton.isVisible().catch(() => false)) {
    await continueButton.click();
  }
}

export async function openLegacyJsonMenu(page: Page): Promise<void> {
  await page.locator("details").filter({ hasText: /Legacy JSON|旧式JSON/ }).evaluate((node) => {
    (node as HTMLDetailsElement).open = true;
  });
}
