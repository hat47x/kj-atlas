import { afterEach, describe, expect, it, vi } from "vitest";

import { loadViewModeForDocument, parseViewModeByDoc, saveViewModeForDocument } from "./view_mode";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createLocalStorageMock() {
  const store = new Map<string, string>();
  return {
    getItem: (key: string) => store.get(key) ?? null,
    setItem: (key: string, value: string) => store.set(key, value),
    removeItem: (key: string) => store.delete(key),
    clear: () => store.clear(),
    key: (index: number) => [...store.keys()][index] ?? null,
    get length() {
      return store.size;
    },
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

describe("parseViewModeByDoc", () => {
  it("returns empty object for empty or invalid payload", () => {
    expect(parseViewModeByDoc(null)).toEqual({});
    expect(parseViewModeByDoc("")).toEqual({});
    expect(parseViewModeByDoc("not-json")).toEqual({});
    expect(parseViewModeByDoc("[]")).toEqual({});
    expect(parseViewModeByDoc("123")).toEqual({});
  });

  it("keeps only known mode entries keyed by non-empty doc id", () => {
    expect(
      parseViewModeByDoc(
        JSON.stringify({
          docA: "explore",
          docB: "review",
          docC: "summary",
          docD: "invalid",
          "": "review",
          1: "explore",
        }),
      ),
    ).toEqual({
      docA: "explore",
      docB: "review",
      docC: "summary",
      "1": "explore",
    });
  });

  it("separates the same document id by tenant scope", () => {
    vi.stubGlobal("window", { localStorage: createLocalStorageMock() });

    saveViewModeForDocument("shared-doc", "review", tenantA);
    saveViewModeForDocument("shared-doc", "summary", tenantB);

    expect(loadViewModeForDocument("shared-doc", tenantA)).toBe("review");
    expect(loadViewModeForDocument("shared-doc", tenantB)).toBe("summary");
  });

  it("keeps the legacy unscoped storage contract when scope is omitted", () => {
    vi.stubGlobal("window", { localStorage: createLocalStorageMock() });

    saveViewModeForDocument("docA", "explore");

    expect(loadViewModeForDocument("docA")).toBe("explore");
    expect(loadViewModeForDocument("docA", tenantA)).toBeNull();
  });
});
