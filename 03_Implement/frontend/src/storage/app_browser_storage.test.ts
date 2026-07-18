import { beforeEach, describe, expect, it, vi } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  assertAppStorageScopeStable,
  createAppBrowserStorage,
} from "./app_browser_storage";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createLocalStorageMock(): Storage {
  const values = new Map<string, string>();
  return {
    get length() {
      return values.size;
    },
    clear() {
      values.clear();
    },
    getItem(key: string) {
      return values.get(key) ?? null;
    },
    key(index: number) {
      return [...values.keys()][index] ?? null;
    },
    removeItem(key: string) {
      values.delete(key);
    },
    setItem(key: string, value: string) {
      values.set(key, value);
    },
  };
}

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

describe("App browser storage boundary", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { localStorage: createLocalStorageMock() });
  });

  it("binds every App persistence operation to one tenant and principal scope", () => {
    const storageA = createAppBrowserStorage(tenantA);
    const storageB = createAppBrowserStorage(tenantB);

    storageA.saveAdvancedUiEnabled(true);
    storageA.saveCurrentReviewerRef("user:sso:a");
    storageA.saveEmptyCanvasHintCompleted(true);
    storageA.pushRecentDocumentId("shared-doc");
    storageA.saveViewLocaleForDocumentView("shared-doc", "explore", "ja");
    storageA.saveViewModeForDocument("shared-doc", "explore");
    storageA.saveViewVisibilityForDocument("shared-doc", {
      viewVisibility: "Org",
      packVisibility: "Restricted",
    });

    expect(storageA.loadAdvancedUiEnabled()).toBe(true);
    expect(storageA.initializeCurrentReviewerRef()).toBe("user:sso:a");
    expect(storageA.loadEmptyCanvasHintCompleted()).toBe(true);
    expect(storageA.loadRecentDocumentIds()).toEqual(["shared-doc"]);
    expect(storageA.loadViewLocaleForDocumentView("shared-doc", "explore")).toBe("ja");
    expect(storageA.loadViewModeForDocument("shared-doc")).toBe("explore");
    expect(storageA.loadViewVisibilityForDocument("shared-doc")).toEqual({
      viewVisibility: "Org",
      packVisibility: "Restricted",
    });

    expect(storageB.loadAdvancedUiEnabled()).toBe(false);
    expect(storageB.loadEmptyCanvasHintCompleted()).toBe(false);
    expect(storageB.loadRecentDocumentIds()).toEqual([]);
    expect(storageB.loadViewLocaleForDocumentView("shared-doc", "explore")).toBeNull();
    expect(storageB.loadViewModeForDocument("shared-doc")).toBeNull();
    expect(storageB.loadViewVisibilityForDocument("shared-doc")).toEqual({
      viewVisibility: "Restricted",
      packVisibility: "Public",
    });
  });

  it("validates and snapshots the injected scope before any storage access", () => {
    const mutableScope = { ...tenantA };
    const storage = createAppBrowserStorage(mutableScope);
    mutableScope.tenantId = "tenant-b";

    expect(storage.scopeIdentity).toContain("tenant-a");
    expect(storage.scope?.tenantId).toBe("tenant-a");
    expect(() => createAppBrowserStorage({ ...tenantA, tenantId: " tenant-a" })).toThrow(
      "tenantId must be a non-empty canonical storage scope value",
    );
  });

  it("requires hard replacement instead of changing scope inside a mounted App", () => {
    const storageA = createAppBrowserStorage(tenantA);
    const storageB = createAppBrowserStorage(tenantB);

    expect(() => assertAppStorageScopeStable(
      storageA.scopeIdentity,
      storageB.scopeIdentity,
    )).toThrow("App storage scope cannot change without a hard document replacement");
    expect(() => assertAppStorageScopeStable(
      storageA.scopeIdentity,
      storageA.scopeIdentity,
    )).not.toThrow();
  });

  it("clears only the bound tenant scope without exposing raw storage to App", () => {
    const storageA = createAppBrowserStorage(tenantA);
    const storageB = createAppBrowserStorage(tenantB);
    storageA.saveAdvancedUiEnabled(true);
    storageA.pushRecentDocumentId("shared-doc");
    storageB.saveAdvancedUiEnabled(true);

    expect(storageA.clearScope()).toBe(2);
    expect(storageA.loadAdvancedUiEnabled()).toBe(false);
    expect(storageA.loadRecentDocumentIds()).toEqual([]);
    expect(storageB.loadAdvancedUiEnabled()).toBe(true);
  });

  it("keeps the existing single-tenant storage keys when no scope is injected", () => {
    const storage = createAppBrowserStorage();
    storage.pushRecentDocumentId("legacy-doc");

    expect(storage.clearScope()).toBe(0);
    expect(storage.scopeIdentity).toBe("legacy-single-tenant");
    expect(window.localStorage.getItem("kj-atlas/recent-doc-ids")).toBe(
      JSON.stringify(["legacy-doc"]),
    );
  });

  it("keeps App persistence behind the scoped facade", () => {
    const appSource = readFileSync(resolve(__dirname, "..", "App.tsx"), "utf8");
    const minimapSource = readFileSync(resolve(__dirname, "..", "ui", "Minimap.tsx"), "utf8");
    const directStorageModules = [
      "advanced_ui",
      "empty_canvas_hint",
      "recent",
      "view_locale",
      "view_mode",
      "view_visibility",
    ];

    for (const moduleName of directStorageModules) {
      expect(appSource).not.toContain(`"./storage/${moduleName}"`);
    }
    expect(appSource).toContain("createAppBrowserStorage(storageScope)");
    expect(appSource).toContain("clearPreviousScope: appStorage.clearScope");
    expect(appSource).not.toContain("window.localStorage");
    expect(appSource).toContain("storageScope={appStorage.scope}");
    expect(minimapSource).toContain("loadMinimapCollapsed(storageScope)");
    expect(minimapSource).toContain("saveMinimapCollapsed(false, storageScope)");
    expect(minimapSource).toContain("saveMinimapCollapsed(true, storageScope)");
  });
});
