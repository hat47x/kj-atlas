import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  loadViewVisibilityForDocument,
  parsePersistedVisibilityByDoc,
  saveViewVisibilityForDocument,
} from "./view_visibility";
import type { TenantBrowserStorageScope } from "./tenant_scope";

type LocalStorageLike = {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  clear: () => void;
};

function createMockStorage(): LocalStorageLike {
  const store = new Map<string, string>();
  return {
    getItem: (key) => store.get(key) ?? null,
    setItem: (key, value) => {
      store.set(key, value);
    },
    clear: () => {
      store.clear();
    },
  };
}

describe("view_visibility storage", () => {
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

  it("parses only supported visibility enums", () => {
    const parsed = parsePersistedVisibilityByDoc(JSON.stringify({
      "doc-1": { viewVisibility: "Org", packVisibility: "Unlisted" },
      "doc-2": { viewVisibility: "public", packVisibility: "FriendsOnly" },
      "doc-3": null,
    }));

    expect(parsed).toEqual({
      "doc-1": { viewVisibility: "Org", packVisibility: "Unlisted" },
    });
  });

  it("returns default fallback values for missing or invalid entries", () => {
    expect(loadViewVisibilityForDocument("doc-a")).toEqual({ viewVisibility: "Restricted", packVisibility: "Public" });

    window.localStorage.setItem("kj-atlas/view-visibility-by-doc", JSON.stringify({
      "doc-a": { viewVisibility: "Restricted" },
      "doc-b": { packVisibility: "Org" },
      "doc-c": { viewVisibility: "FriendsOnly", packVisibility: "Public" },
    }));

    expect(loadViewVisibilityForDocument("doc-a")).toEqual({ viewVisibility: "Restricted", packVisibility: "Public" });
    expect(loadViewVisibilityForDocument("doc-b")).toEqual({ viewVisibility: "Restricted", packVisibility: "Org" });
    expect(loadViewVisibilityForDocument("doc-c")).toEqual({ viewVisibility: "Restricted", packVisibility: "Public" });
  });

  it("persists both view and pack visibility for reload", () => {
    saveViewVisibilityForDocument("doc-save", { viewVisibility: "Public", packVisibility: "Restricted" });

    expect(loadViewVisibilityForDocument("doc-save")).toEqual({ viewVisibility: "Public", packVisibility: "Restricted" });
  });

  it("isolates the same document id across tenant scopes", () => {
    const tenantA: TenantBrowserStorageScope = {
      deployment: "https://atlas.example.test",
      tenantId: "tenant-a",
      principalId: "user-1",
    };
    const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

    saveViewVisibilityForDocument(
      "shared-doc",
      { viewVisibility: "Org", packVisibility: "Restricted" },
      tenantA,
    );
    saveViewVisibilityForDocument(
      "shared-doc",
      { viewVisibility: "Unlisted", packVisibility: "Public" },
      tenantB,
    );

    expect(loadViewVisibilityForDocument("shared-doc", tenantA)).toEqual({
      viewVisibility: "Org",
      packVisibility: "Restricted",
    });
    expect(loadViewVisibilityForDocument("shared-doc", tenantB)).toEqual({
      viewVisibility: "Unlisted",
      packVisibility: "Public",
    });
  });
});
