import { isViewMode, type ViewMode } from "../domain/view/view_mode";

const VIEW_MODE_STORAGE_KEY = "kj-atlas/view-mode-by-doc";

type ViewModeByDoc = Record<string, ViewMode>;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
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

export function loadViewModeForDocument(docId: string): ViewMode | null {
  if (!docId || !isStorageAvailable()) {
    return null;
  }

  const byDoc = parseViewModeByDoc(window.localStorage.getItem(VIEW_MODE_STORAGE_KEY));
  return byDoc[docId] ?? null;
}

export function saveViewModeForDocument(docId: string, mode: ViewMode): void {
  if (!docId || !isStorageAvailable()) {
    return;
  }

  const byDoc = parseViewModeByDoc(window.localStorage.getItem(VIEW_MODE_STORAGE_KEY));
  byDoc[docId] = mode;
  window.localStorage.setItem(VIEW_MODE_STORAGE_KEY, JSON.stringify(byDoc));
}
