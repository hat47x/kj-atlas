import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const MINIMAP_COLLAPSED_STORAGE_KEY = "kj-atlas/minimap-collapsed";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function minimapCollapsedStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(MINIMAP_COLLAPSED_STORAGE_KEY, scope) : MINIMAP_COLLAPSED_STORAGE_KEY;
}

export function loadMinimapCollapsed(scope?: TenantBrowserStorageScope): boolean {
  if (!isStorageAvailable()) {
    return false;
  }

  return window.localStorage.getItem(minimapCollapsedStorageKey(scope)) === "true";
}

export function saveMinimapCollapsed(
  collapsed: boolean,
  scope?: TenantBrowserStorageScope,
): void {
  if (!isStorageAvailable()) {
    return;
  }

  const storageKey = minimapCollapsedStorageKey(scope);
  if (collapsed) {
    window.localStorage.setItem(storageKey, "true");
    return;
  }

  window.localStorage.removeItem(storageKey);
}
