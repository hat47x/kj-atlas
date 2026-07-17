import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY = "kj-atlas/empty-canvas-hint-completed";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function emptyCanvasHintStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope
    ? buildTenantStorageKey(EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY, scope)
    : EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY;
}

export function loadEmptyCanvasHintCompleted(scope?: TenantBrowserStorageScope): boolean {
  if (!isStorageAvailable()) {
    return false;
  }

  return window.localStorage.getItem(emptyCanvasHintStorageKey(scope)) === "true";
}

export function saveEmptyCanvasHintCompleted(
  completed: boolean,
  scope?: TenantBrowserStorageScope,
): void {
  if (!isStorageAvailable()) {
    return;
  }

  const storageKey = emptyCanvasHintStorageKey(scope);
  if (completed) {
    window.localStorage.setItem(storageKey, "true");
    return;
  }

  window.localStorage.removeItem(storageKey);
}
