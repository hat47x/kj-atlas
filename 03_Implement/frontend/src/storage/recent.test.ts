import { beforeEach, describe, expect, it, vi } from "vitest";

import { loadRecentDocumentIds, pushRecentDocumentId } from "./recent";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createMockStorage() {
  const values = new Map<string, string>();
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
    clear: () => values.clear(),
  };
}

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = {
  ...tenantA,
  tenantId: "tenant-b",
};

describe("recent document storage", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { localStorage: createMockStorage() });
  });

  it("keeps the same document id isolated per tenant scope", () => {
    pushRecentDocumentId("shared-doc", tenantA);
    pushRecentDocumentId("tenant-a-only", tenantA);
    pushRecentDocumentId("shared-doc", tenantB);
    pushRecentDocumentId("tenant-b-only", tenantB);

    expect(loadRecentDocumentIds(tenantA)).toEqual(["tenant-a-only", "shared-doc"]);
    expect(loadRecentDocumentIds(tenantB)).toEqual(["tenant-b-only", "shared-doc"]);
  });

  it("preserves the legacy single-tenant storage key when scope is omitted", () => {
    pushRecentDocumentId("legacy-doc");

    expect(loadRecentDocumentIds()).toEqual(["legacy-doc"]);
    expect(loadRecentDocumentIds(tenantA)).toEqual([]);
  });
});
