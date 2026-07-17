import { beforeEach, describe, expect, it, vi } from "vitest";

import type { QueryPreset } from "../domain/patch/workspace/ce3_patch_workspace";
import { loadQueryPresets, saveQueryPresets } from "./query_presets";
import type { TenantBrowserStorageScope } from "./tenant_scope";

function createMockStorage() {
  const values = new Map<string, string>();
  return {
    getItem: (key: string) => values.get(key) ?? null,
    setItem: (key: string, value: string) => values.set(key, value),
  };
}

const tenantA: TenantBrowserStorageScope = {
  deployment: "https://atlas.example.test",
  tenantId: "tenant-a",
  principalId: "user-1",
};
const tenantB: TenantBrowserStorageScope = { ...tenantA, tenantId: "tenant-b" };

function preset(id: string, name: string): QueryPreset {
  return {
    id,
    name,
    scope: "selection",
    depth: 2,
    filters: ["unreviewed"],
  };
}

describe("QueryPreset tenant storage", () => {
  beforeEach(() => {
    vi.stubGlobal("window", { localStorage: createMockStorage() });
  });

  it("keeps saved presets isolated by tenant scope", () => {
    saveQueryPresets([preset("preset-a", "Tenant A preset")], tenantA);
    saveQueryPresets([preset("preset-b", "Tenant B preset")], tenantB);

    expect(loadQueryPresets(tenantA).map((item) => item.id)).toEqual(["preset-a"]);
    expect(loadQueryPresets(tenantB).map((item) => item.id)).toEqual(["preset-b"]);
  });

  it("preserves the legacy single-tenant key when scope is omitted", () => {
    saveQueryPresets([preset("legacy", "Legacy preset")]);

    expect(loadQueryPresets().map((item) => item.id)).toEqual(["legacy"]);
    expect(loadQueryPresets(tenantA)).toEqual([]);
  });

  it("normalizes persisted depth and filters within the selected scope", () => {
    saveQueryPresets([
      {
        ...preset("normalize", "Normalize"),
        depth: 1.9,
        filters: [" Zeta ", "alpha", "ALPHA"],
      },
    ], tenantA);

    expect(loadQueryPresets(tenantA)).toEqual([
      {
        ...preset("normalize", "Normalize"),
        depth: 1,
        filters: ["alpha", "zeta"],
      },
    ]);
  });
});
