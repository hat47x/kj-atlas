/**
 * Non-authoritative cache of recently opened document IDs.
 *
 * Per DATA-MODEL-OPS-02 D1, this localStorage entry is a convenience cache only —
 * the server `GET /docs` response (id/title/updatedAt allowlist) is the source of truth.
 * When cache and server disagree, the server wins.
 */
const RECENT_DOC_IDS_STORAGE_KEY = "kj-atlas/recent-doc-ids";
const MAX_RECENT_DOC_IDS = 10;

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function loadRecentDocumentIds(): string[] {
  if (!isStorageAvailable()) {
    return [];
  }

  const rawValue = window.localStorage.getItem(RECENT_DOC_IDS_STORAGE_KEY);
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

export function pushRecentDocumentId(docId: string): string[] {
  if (!docId) {
    return loadRecentDocumentIds();
  }

  const current = loadRecentDocumentIds().filter((id) => id !== docId);
  const next = [docId, ...current].slice(0, MAX_RECENT_DOC_IDS);

  if (isStorageAvailable()) {
    window.localStorage.setItem(RECENT_DOC_IDS_STORAGE_KEY, JSON.stringify(next));
  }

  return next;
}

