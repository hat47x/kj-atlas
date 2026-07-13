import type { Page } from "@playwright/test";

export const START_PANEL_TITLE = /^Start work$|^作業を開始$/;
export const START_PANEL_NEW_DOCUMENT = /Create new document|新しい文書を作成/;
export const START_PANEL_SAMPLE = /Open sample|サンプルを開く/;
export const START_PANEL_LOAD_DOCUMENT = /Load document file|文書ファイルを読み込む/;
export const START_PANEL_IMPORT_PACK = /Import review pack|レビューパックを取り込む/;
export const SHARE_REPRODUCE_BUTTON = /Share & Reproduce|共有と再現/;
export const VIEW_BUTTON = /^View$|^表示$/;
export const ADVANCED_UI_BUTTON = /^Advanced$|^詳細$/;
export const SUGGEST_LAYOUT_BUTTON = /Suggest layout|配置を提案/;
export const LOAD_DOCUMENT_BUTTON = /^Load document\.json$|^document\.json を読み込む$/;
export const REPLACE_DOCUMENT_BUTTON = /Replace current document|現在のドキュメントを置換/;
// Matches app.status.import.document_replaced in both locales. Specs must
// use this constant instead of hardcoding the wording -- a vocabulary-sync
// pass changed the strings once already and silently broke 7 specs.
export const DOCUMENT_REPLACED_STATUS = /Replaced the current document|現在のドキュメントを置換しました/;
export const EXPORT_BUNDLE_BUTTON = /Export bundle \(\.zip\)|レビューパックを書き出す \(.zip\)|bundle をエクスポート \(.zip\)/;
export const EXPORT_DOCUMENT_JSON_BUTTON = /Export document JSON|Export doc JSON \(legacy\)|ドキュメントJSONを書き出す（旧式）/;
export const READ_ONLY_INDICATOR = /Read-only mode is active|読み取り専用モードが有効|Read-only|読み取り専用/;
export const EDIT_ISLAND_BOUNDARY_CHECKBOX = /Edit island boundary|島の境界を編集/;
export const SEARCH_CARDS_PLACEHOLDER = /Search cards|カードを検索/;
export const HIDE_NON_MATCHES_CHECKBOX = /Hide non-matches|非一致を非表示/;

export const WORK_MODE_BUTTON = /^Work mode$|^作業モード$/;
export const DIAGNOSTICS_BUNDLE_BUTTON = /Support diagnostics bundle|サポート診断バンドル/;

export function visibilitySelect(page: Page, label: "view" | "pack") {
  const labelPattern = label === "view" ? /View visibility|view の公開範囲/ : /Pack visibility|パックの公開範囲/;
  return page.locator("label").filter({ hasText: labelPattern }).locator("select");
}

// Turns the Advanced UI toggle on if it is not already (it persists in
// localStorage, so after a reload it may already be pressed).
export async function enableAdvancedUiIfNeeded(page: Page): Promise<void> {
  const advancedToggle = page.getByRole("button", { name: ADVANCED_UI_BUTTON });
  if ((await advancedToggle.getAttribute("aria-pressed")) !== "true") {
    await advancedToggle.click();
  }
}

// Workspace IA: advanced work features (merge/patch candidate decisions,
// narrative drafting, diff) live inside the Work mode panel and render only
// while Advanced UI is on. Call after any full page (re)load that needs
// them. Closes the share panel first -- its dialog overlays the toolbar.
export async function openAdvancedWorkMode(page: Page): Promise<void> {
  await closeSharePanelIfOpen(page);
  await enableAdvancedUiIfNeeded(page);
  await page.getByRole("button", { name: WORK_MODE_BUTTON }).click();
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
