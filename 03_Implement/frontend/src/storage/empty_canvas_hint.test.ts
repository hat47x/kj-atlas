import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadEmptyCanvasHintCompleted, saveEmptyCanvasHintCompleted } from "./empty_canvas_hint";

type LocalStorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
  clear: () => void;
};

function createMockStorage(): LocalStorageLike {
  const store = new Map<string, string>();
  return {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => {
      store.set(key, value);
    },
    removeItem: (key) => {
      store.delete(key);
    },
    clear: () => {
      store.clear();
    },
  };
}

describe("empty canvas hint storage", () => {
  beforeEach(() => {
    const storage = createMockStorage();
    Object.defineProperty(globalThis, "window", {
      value: { localStorage: storage },
      configurable: true,
      writable: true,
    });
    window.localStorage.clear();
    vi.restoreAllMocks();
  });

  it("defaults to showing the hint", () => {
    expect(loadEmptyCanvasHintCompleted()).toBe(false);
  });

  it("persists completion and supports reset", () => {
    saveEmptyCanvasHintCompleted(true);
    expect(loadEmptyCanvasHintCompleted()).toBe(true);

    saveEmptyCanvasHintCompleted(false);
    expect(loadEmptyCanvasHintCompleted()).toBe(false);
  });
});
