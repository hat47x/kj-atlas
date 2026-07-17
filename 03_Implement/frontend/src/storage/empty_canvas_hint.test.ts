import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadEmptyCanvasHintCompleted, saveEmptyCanvasHintCompleted } from "./empty_canvas_hint";
import type { TenantBrowserStorageScope } from "./tenant_scope";

type LocalStorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
  clear: () => void;
};

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

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

  it("separates onboarding completion by tenant scope", () => {
    saveEmptyCanvasHintCompleted(true, tenantA);

    expect(loadEmptyCanvasHintCompleted(tenantA)).toBe(true);
    expect(loadEmptyCanvasHintCompleted(tenantB)).toBe(false);
    expect(loadEmptyCanvasHintCompleted()).toBe(false);
  });
});
