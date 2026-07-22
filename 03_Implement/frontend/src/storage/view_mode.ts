import { isViewMode, type ViewMode } from "../domain/view/view_mode";
import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const VIEW_MODE_STORAGE_KEY = "kj-atlas/view-mode-by-doc";

type ViewModeByDoc = Record<string, ViewMode>;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function viewModeStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(VIEW_MODE_STORAGE_KEY, scope) : VIEW_MODE_STORAGE_KEY;
}

export function parseViewModeByDoc(rawValue: string | null | undefined): ViewModeByDoc {
  if (!rawValue) {
    return {};
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }

    const next: ViewModeByDoc = {};
    for (const [docId, mode] of Object.entries(parsed as Record<string, unknown>)) {
      if (typeof docId !== "string" || docId.length === 0) {
        continue;
      }
      if (isViewMode(mode)) {
        next[docId] = mode;
      }
    }

    return next;
  } catch {
    return {};
  }
}

export function loadViewModeForDocument(
  docId: string,
  scope?: TenantBrowserStorageScope,
): ViewMode | null {
  if (!docId || !isStorageAvailable()) {
    return null;
  }

  const byDoc = parseViewModeByDoc(window.localStorage.getItem(viewModeStorageKey(scope)));
  return byDoc[docId] ?? null;
}

export function saveViewModeForDocument(
  docId: string,
  mode: ViewMode,
  scope?: TenantBrowserStorageScope,
): void {
  if (!docId || !isStorageAvailable()) {
    return;
  }

  const storageKey = viewModeStorageKey(scope);
  const byDoc = parseViewModeByDoc(window.localStorage.getItem(storageKey));
  byDoc[docId] = mode;
  try {
    window.localStorage.setItem(storageKey, JSON.stringify(byDoc));
  } catch {
    // Storage may be disabled or full. The in-memory view mode remains usable.
  }
}
