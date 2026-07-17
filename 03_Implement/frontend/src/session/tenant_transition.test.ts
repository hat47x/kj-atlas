import { describe, expect, it, vi } from "vitest";

import { buildTenantStorageKey, type TenantBrowserStorageScope } from "../storage/tenant_scope";
import { executeTenantSessionTransition } from "./tenant_transition";

const previousScope: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const otherScope: TenantBrowserStorageScope = { ...previousScope, tenantId: "tenant-b" };

function nextSessionContext(overrides: Record<string, unknown> = {}) {
  return {
    principalId: "user-1",
    activeTenant: { id: "tenant-b", displayName: "Tenant B" },
    availableTenants: [
      { id: "tenant-a", displayName: "Tenant A" },
      { id: "tenant-b", displayName: "Tenant B" },
    ],
    effectiveCapabilities: ["document.read"],
    capabilityVersion: "policy-v2",
    ...overrides,
  };
}

function createStorage(initial: Record<string, string>) {
  const values = new Map(Object.entries(initial));
  return {
    get length() {
      return values.size;
    },
    key(index: number) {
      return [...values.keys()][index] ?? null;
    },
    removeItem(key: string) {
      values.delete(key);
    },
    keys() {
      return [...values.keys()];
    },
  };
}

describe("tenant session transition", () => {
  it("cleans runtime resources, clears only the previous scope, and hard reloads", () => {
    const previousRecent = buildTenantStorageKey("recent", previousScope);
    const previousView = buildTenantStorageKey("view", previousScope);
    const otherRecent = buildTenantStorageKey("recent", otherScope);
    const storage = createStorage({
      [previousRecent]: "a",
      [previousView]: "b",
      [otherRecent]: "c",
      "kj-atlas/legacy": "legacy",
    });
    const cleanupOrder: string[] = [];
    const replaceDocument = vi.fn();

    const result = executeTenantSessionTransition({
      nextSessionContext: nextSessionContext(),
      deployment: "https://atlas.example.test",
      previousScope,
      storage,
      cleanupSteps: [
        () => cleanupOrder.push("abort-requests"),
        () => cleanupOrder.push("dispose-workers"),
        () => cleanupOrder.push("revoke-object-urls"),
        () => cleanupOrder.push("clear-memory"),
      ],
      replaceDocument,
    });

    expect(cleanupOrder).toEqual([
      "abort-requests",
      "dispose-workers",
      "revoke-object-urls",
      "clear-memory",
    ]);
    expect(storage.keys()).toEqual([otherRecent, "kj-atlas/legacy"]);
    expect(result).toEqual({
      nextScope: otherScope,
      clearedStorageEntries: 2,
      cleanupFailureCount: 0,
      storageClearFailed: false,
    });
    expect(replaceDocument).toHaveBeenCalledOnce();
  });

  it("rejects an unverified session response before cleanup or navigation", () => {
    const cleanup = vi.fn();
    const replaceDocument = vi.fn();

    expect(() => executeTenantSessionTransition({
      nextSessionContext: nextSessionContext({
        activeTenant: { id: "tenant-x", displayName: "Tenant X" },
      }),
      deployment: "https://atlas.example.test",
      previousScope,
      storage: createStorage({}),
      cleanupSteps: [cleanup],
      replaceDocument,
    })).toThrow("Invalid tenant session context");
    expect(cleanup).not.toHaveBeenCalled();
    expect(replaceDocument).not.toHaveBeenCalled();
  });

  it("continues to hard replacement when cleanup or storage clearing fails", () => {
    const replaceDocument = vi.fn();
    const result = executeTenantSessionTransition({
      nextSessionContext: nextSessionContext(),
      deployment: "https://atlas.example.test",
      previousScope,
      storage: {
        get length(): number {
          throw new Error("storage unavailable");
        },
        key: () => null,
        removeItem: () => undefined,
      },
      cleanupSteps: [
        () => {
          throw new Error("worker unavailable");
        },
      ],
      replaceDocument,
    });

    expect(result.cleanupFailureCount).toBe(1);
    expect(result.storageClearFailed).toBe(true);
    expect(replaceDocument).toHaveBeenCalledOnce();
  });

  it("derives the next scope from a principal change returned by the server", () => {
    const result = executeTenantSessionTransition({
      nextSessionContext: nextSessionContext({ principalId: "user-2" }),
      deployment: "https://atlas.example.test",
      previousScope,
      storage: createStorage({}),
      cleanupSteps: [],
      replaceDocument: () => undefined,
    });

    expect(result.nextScope).toEqual({
      deployment: "https://atlas.example.test",
      tenantId: "tenant-b",
      principalId: "user-2",
    });
  });
});
