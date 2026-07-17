import { buildTenantStorageKey, type TenantBrowserStorageScope } from "./tenant_scope";

const ADVANCED_UI_STORAGE_KEY = "kj-atlas.advanced-ui-enabled";

function advancedUiStorageKey(scope?: TenantBrowserStorageScope): string {
  return scope ? buildTenantStorageKey(ADVANCED_UI_STORAGE_KEY, scope) : ADVANCED_UI_STORAGE_KEY;
}

export function loadAdvancedUiEnabled(scope?: TenantBrowserStorageScope): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    return window.localStorage.getItem(advancedUiStorageKey(scope)) === "true";
  } catch {
    return false;
  }
}

export function saveAdvancedUiEnabled(
  enabled: boolean,
  scope?: TenantBrowserStorageScope,
): void {
  if (typeof window === "undefined") {
    return;
  }
  try {
    window.localStorage.setItem(advancedUiStorageKey(scope), String(enabled));
  } catch {
    // Storage may be disabled. The in-memory preference remains usable.
  }
}
