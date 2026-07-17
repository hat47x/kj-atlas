import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadMinimapCollapsed, saveMinimapCollapsed } from "./minimap_collapsed";
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

describe("minimap collapsed storage", () => {
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

  it("defaults to expanded (not collapsed)", () => {
    expect(loadMinimapCollapsed()).toBe(false);
  });

  it("persists collapse state and supports re-expansion", () => {
    saveMinimapCollapsed(true);
    expect(loadMinimapCollapsed()).toBe(true);

    saveMinimapCollapsed(false);
    expect(loadMinimapCollapsed()).toBe(false);
  });

  it("separates minimap preference by tenant scope", () => {
    saveMinimapCollapsed(true, tenantA);

    expect(loadMinimapCollapsed(tenantA)).toBe(true);
    expect(loadMinimapCollapsed(tenantB)).toBe(false);
    expect(loadMinimapCollapsed()).toBe(false);
  });
});
