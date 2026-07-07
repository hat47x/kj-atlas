const MINIMAP_COLLAPSED_STORAGE_KEY = "kj-atlas/minimap-collapsed";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function loadMinimapCollapsed(): boolean {
  if (!isStorageAvailable()) {
    return false;
  }

  return window.localStorage.getItem(MINIMAP_COLLAPSED_STORAGE_KEY) === "true";
}

export function saveMinimapCollapsed(collapsed: boolean): void {
  if (!isStorageAvailable()) {
    return;
  }

  if (collapsed) {
    window.localStorage.setItem(MINIMAP_COLLAPSED_STORAGE_KEY, "true");
    return;
  }

  window.localStorage.removeItem(MINIMAP_COLLAPSED_STORAGE_KEY);
}
