import { describe, expect, it } from "vitest";

import {
  buildTenantStorageKey,
  clearTenantScopedStorage,
  type TenantBrowserStorageScope,
} from "./tenant_scope";

function scope(overrides: Partial<TenantBrowserStorageScope> = {}): TenantBrowserStorageScope {
  return {
    deployment: "https://atlas.example.test",
    tenantId: "tenant-a",
    principalId: "user-1",
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

describe("tenant browser storage scope", () => {
  it("separates the same base key by deployment, tenant, and principal", () => {
    const baseKey = "sui-sensemaking/recent-doc-ids";

    const keys = new Set([
      buildTenantStorageKey(baseKey, scope()),
      buildTenantStorageKey(baseKey, scope({ deployment: "https://other.example.test" })),
      buildTenantStorageKey(baseKey, scope({ tenantId: "tenant-b" })),
      buildTenantStorageKey(baseKey, scope({ principalId: "user-2" })),
    ]);

    expect(keys.size).toBe(4);
  });

  it("encodes delimiter-like values without namespace collision", () => {
    const withSlash = buildTenantStorageKey("sui-sensemaking/example", scope({ tenantId: "tenant/a" }));
    const withoutSlash = buildTenantStorageKey("sui-sensemaking/example", scope({ tenantId: "tenant%2Fa" }));

    expect(withSlash).not.toBe(withoutSlash);
    expect(withSlash).toContain("tenant%2Fa");
  });

  it.each([
    ["deployment", { deployment: "" }],
    ["deployment", { deployment: "x".repeat(2049) }],
    ["tenantId", { tenantId: " tenant-a" }],
    ["tenantId", { tenantId: "x".repeat(257) }],
    ["tenantId", { tenantId: "tenant\u200ba" }],
    ["principalId", { principalId: "user-1\n" }],
    ["principalId", { principalId: "x".repeat(257) }],
  ])("rejects a non-canonical %s", (_name, overrides) => {
    expect(() => buildTenantStorageKey("sui-sensemaking/example", scope(overrides))).toThrow();
  });

  it("clears only the selected deployment, tenant, and principal scope", () => {
    const targetKey = buildTenantStorageKey("sui-sensemaking/recent-doc-ids", scope());
    const targetSecondKey = buildTenantStorageKey("sui-sensemaking/view-visibility-by-doc", scope());
    const otherTenantKey = buildTenantStorageKey(
      "sui-sensemaking/recent-doc-ids",
      scope({ tenantId: "tenant-b" }),
    );
    const storage = createStorage({
      [targetKey]: "a",
      [targetSecondKey]: "b",
      [otherTenantKey]: "c",
      "sui-sensemaking/legacy": "legacy",
    });

    expect(clearTenantScopedStorage(storage, scope())).toBe(2);
    expect(storage.keys()).toEqual([otherTenantKey, "sui-sensemaking/legacy"]);
  });
});
