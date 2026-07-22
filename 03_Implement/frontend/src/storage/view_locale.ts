import { isLocale, type Locale } from "../i18n/translate";
import { isViewMode, type ViewMode } from "../domain/view/view_mode";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const VIEW_LOCALE_STORAGE_KEY = "kj-atlas/view-locale-by-doc-view";

type ViewLocaleByDoc = Record<string, Partial<Record<ViewMode, Locale>>>;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function viewLocaleStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(VIEW_LOCALE_STORAGE_KEY, scope) : VIEW_LOCALE_STORAGE_KEY;
}

export function parseViewLocaleByDoc(rawValue: string | null | undefined): ViewLocaleByDoc {
  if (!rawValue) {
    return {};
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }

    const next: ViewLocaleByDoc = {};
    for (const [docId, localesByView] of Object.entries(parsed as Record<string, unknown>)) {
      if (typeof docId !== "string" || docId.length === 0) {
        continue;
      }
      if (!localesByView || typeof localesByView !== "object" || Array.isArray(localesByView)) {
        continue;
      }

      const validLocalesByView: Partial<Record<ViewMode, Locale>> = {};
      for (const [viewMode, locale] of Object.entries(localesByView as Record<string, unknown>)) {
        if (!isViewMode(viewMode) || typeof locale !== "string" || !isLocale(locale)) {
          continue;
        }

        validLocalesByView[viewMode] = locale;
      }

      if (Object.keys(validLocalesByView).length > 0) {
        next[docId] = validLocalesByView;
      }
    }

    return next;
  } catch {
    return {};
  }
}

export function loadViewLocaleForDocumentView(
  docId: string,
  viewMode: ViewMode,
  scope?: TenantBrowserStorageScope,
): Locale | null {
  if (!docId || !isStorageAvailable()) {
    return null;
  }

  const byDoc = parseViewLocaleByDoc(window.localStorage.getItem(viewLocaleStorageKey(scope)));
  return byDoc[docId]?.[viewMode] ?? null;
}

export function saveViewLocaleForDocumentView(
  docId: string,
  viewMode: ViewMode,
  locale: string,
  scope?: TenantBrowserStorageScope,
): void {
  if (!docId || !isLocale(locale) || !isStorageAvailable()) {
    return;
  }

  const storageKey = viewLocaleStorageKey(scope);
  const byDoc = parseViewLocaleByDoc(window.localStorage.getItem(storageKey));
  const previousByView = byDoc[docId] ?? {};
  byDoc[docId] = {
    ...previousByView,
    [viewMode]: locale,
  };

  try {
    window.localStorage.setItem(storageKey, JSON.stringify(byDoc));
  } catch {
    // Storage may be disabled or full. The in-memory locale remains usable.
  }
}
