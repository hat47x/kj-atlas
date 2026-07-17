import { afterEach, describe, expect, it, vi } from "vitest";

import { loadAdvancedUiEnabled, saveAdvancedUiEnabled } from "./advanced_ui";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createLocalStorageMock() {
  const store = new Map<string, string>();
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => store.set(key, value),
  };
}

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("advanced UI storage", () => {
  it("keeps the legacy unscoped preference when scope is omitted", () => {
    vi.stubGlobal("window", { localStorage: createLocalStorageMock() });

    saveAdvancedUiEnabled(true);

    expect(loadAdvancedUiEnabled()).toBe(true);
    expect(loadAdvancedUiEnabled(tenantA)).toBe(false);
  });

  it("separates the preference by tenant scope", () => {
    vi.stubGlobal("window", { localStorage: createLocalStorageMock() });

    saveAdvancedUiEnabled(true, tenantA);
    saveAdvancedUiEnabled(false, tenantB);

    expect(loadAdvancedUiEnabled(tenantA)).toBe(true);
    expect(loadAdvancedUiEnabled(tenantB)).toBe(false);
  });

  it("fails closed when browser storage is unavailable", () => {
    vi.stubGlobal("window", {
      localStorage: {
        getItem: () => {
          throw new Error("storage unavailable");
        },
        setItem: () => {
          throw new Error("storage unavailable");
        },
      },
    });

    expect(loadAdvancedUiEnabled(tenantA)).toBe(false);
    expect(() => saveAdvancedUiEnabled(true, tenantA)).not.toThrow();
  });
});
