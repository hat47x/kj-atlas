import { afterEach, describe, expect, it, vi } from "vitest";

import { loadViewLocaleForDocumentView, parseViewLocaleByDoc, saveViewLocaleForDocumentView } from "./view_locale";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createLocalStorageMock(initial: Record<string, string> = {}) {
  const store = new Map<string, string>(Object.entries(initial));
  return {
    getItem(key: string) {
      return store.has(key) ? store.get(key)! : null;
    },
    setItem(key: string, value: string) {
      store.set(key, value);
    },
    removeItem(key: string) {
      store.delete(key);
    },
    clear() {
      store.clear();
    },
    dump() {
      return Object.fromEntries(store.entries());
    },
  };
}

afterEach(() => {
  vi.unstubAllGlobals();
});

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

describe("parseViewLocaleByDoc", () => {
  it("returns empty object for empty or invalid payload", () => {
    expect(parseViewLocaleByDoc(null)).toEqual({});
    expect(parseViewLocaleByDoc("")).toEqual({});
    expect(parseViewLocaleByDoc("not-json")).toEqual({});
    expect(parseViewLocaleByDoc("[]")).toEqual({});
    expect(parseViewLocaleByDoc("123")).toEqual({});
  });

  it("keeps only known locale entries keyed by non-empty doc id and known view", () => {
    expect(
      parseViewLocaleByDoc(
        JSON.stringify({
          docA: { explore: "ja", review: "en", summary: "ja", invalidView: "en", explore2: "ja" },
          docB: { review: "fr" },
          "": { explore: "ja" },
          docC: "ja",
          1: { summary: "en" },
        }),
      ),
    ).toEqual({
      docA: { explore: "ja", review: "en", summary: "ja" },
      "1": { summary: "en" },
    });
  });

  it("saves and loads locale by doc + view mode", () => {
    const storage = createLocalStorageMock();
    vi.stubGlobal("window", { localStorage: storage });

    saveViewLocaleForDocumentView("docA", "explore", "en");
    saveViewLocaleForDocumentView("docA", "review", "ja");

    expect(loadViewLocaleForDocumentView("docA", "explore")).toBe("en");
    expect(loadViewLocaleForDocumentView("docA", "review")).toBe("ja");
    expect(loadViewLocaleForDocumentView("docA", "summary")).toBeNull();
  });

  it("ignores unknown locale and keeps existing mapping", () => {
    const storage = createLocalStorageMock({
      "kj-atlas/view-locale-by-doc-view": JSON.stringify({ docA: { explore: "en" } }),
    });
    vi.stubGlobal("window", { localStorage: storage });

    saveViewLocaleForDocumentView("docA", "explore", "fr");

    expect(loadViewLocaleForDocumentView("docA", "explore")).toBe("en");
    expect(storage.dump()["kj-atlas/view-locale-by-doc-view"]).toBe(JSON.stringify({ docA: { explore: "en" } }));
  });

  it("separates the same document and view by tenant scope", () => {
    const storage = createLocalStorageMock();
    vi.stubGlobal("window", { localStorage: storage });

    saveViewLocaleForDocumentView("shared-doc", "explore", "ja", tenantA);
    saveViewLocaleForDocumentView("shared-doc", "explore", "en", tenantB);

    expect(loadViewLocaleForDocumentView("shared-doc", "explore", tenantA)).toBe("ja");
    expect(loadViewLocaleForDocumentView("shared-doc", "explore", tenantB)).toBe("en");
  });

  it("keeps the legacy unscoped storage contract when scope is omitted", () => {
    const storage = createLocalStorageMock();
    vi.stubGlobal("window", { localStorage: storage });

    saveViewLocaleForDocumentView("docA", "review", "ja");

    expect(loadViewLocaleForDocumentView("docA", "review")).toBe("ja");
    expect(loadViewLocaleForDocumentView("docA", "review", tenantA)).toBeNull();
  });
});
