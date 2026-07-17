import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const RECENT_DOC_IDS_STORAGE_KEY = "kj-atlas/recent-doc-ids";
const MAX_RECENT_DOC_IDS = 10;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function recentStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(RECENT_DOC_IDS_STORAGE_KEY, scope) : RECENT_DOC_IDS_STORAGE_KEY;
}

export function loadRecentDocumentIds(scope?: TenantBrowserStorageScope): string[] {
  if (!isStorageAvailable()) {
    return [];
  }

  const rawValue = window.localStorage.getItem(recentStorageKey(scope));
  if (!rawValue) {
    return [];
  }

  try {
    const parsed = JSON.parse(rawValue) as unknown;
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed.filter((item): item is string => typeof item === "string" && item.length > 0).slice(0, MAX_RECENT_DOC_IDS);
  } catch {
    return [];
  }
}

export function pushRecentDocumentId(docId: string, scope?: TenantBrowserStorageScope): string[] {
  if (!docId) {
    return loadRecentDocumentIds(scope);
  }

  const current = loadRecentDocumentIds(scope).filter((id) => id !== docId);
  const next = [docId, ...current].slice(0, MAX_RECENT_DOC_IDS);

  if (isStorageAvailable()) {
    window.localStorage.setItem(recentStorageKey(scope), JSON.stringify(next));
  }

  return next;
}
