const EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY = "kj-atlas/empty-canvas-hint-completed";

function isStorageAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

export function loadEmptyCanvasHintCompleted(): boolean {
  if (!isStorageAvailable()) {
    return false;
  }

  return window.localStorage.getItem(EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY) === "true";
}

export function saveEmptyCanvasHintCompleted(completed: boolean): void {
  if (!isStorageAvailable()) {
    return;
  }

  if (completed) {
    window.localStorage.setItem(EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY, "true");
    return;
  }

  window.localStorage.removeItem(EMPTY_CANVAS_HINT_COMPLETED_STORAGE_KEY);
}
