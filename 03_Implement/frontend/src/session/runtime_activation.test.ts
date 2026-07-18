import { describe, expect, it, vi } from "vitest";

import {
  resolveRuntimeEntryMode,
  verifyTenantSessionRuntimePolicy,
} from "./runtime_activation";

describe("runtime entry activation", () => {
  it.each([undefined, "local-dev", "evaluation", "enterprise-production"])(
    "keeps %s on the local-first entry",
    (runtimeProfile) => {
      expect(resolveRuntimeEntryMode(runtimeProfile)).toBe("single-tenant");
    },
  );

  it("requires tenant bootstrap only for the reserved SaaS profile", () => {
    expect(resolveRuntimeEntryMode("saas-multitenant")).toBe(
      "tenant-session-required",
    );
  });

  it.each([null, "", " SaaS-multitenant ", "shared-production"])(
    "blocks invalid build profile %s without fallback",
    (runtimeProfile) => {
      expect(resolveRuntimeEntryMode(runtimeProfile)).toBe("invalid");
    },
  );

  it("accepts only a matching strict server policy", async () => {
    const loadPolicy = vi.fn().mockResolvedValue({
      tenantSessionMode: "tenant-session-required",
    });
    const controller = new AbortController();

    await expect(verifyTenantSessionRuntimePolicy({
      signal: controller.signal,
      loadPolicy,
    })).resolves.toBe(true);
    expect(loadPolicy).toHaveBeenCalledWith({ signal: controller.signal });
  });

  it.each([
    { tenantSessionMode: "single-tenant" },
    { tenantSessionMode: "tenant-session-required", runtimeProfile: "saas-multitenant" },
    { tenantSessionMode: "required" },
  ])("blocks a mismatched or invalid server policy", async (policy) => {
    await expect(verifyTenantSessionRuntimePolicy({
      signal: new AbortController().signal,
      loadPolicy: async () => policy,
    })).resolves.toBe(false);
  });

  it("blocks policy transport failures and preserves lifecycle abort", async () => {
    await expect(verifyTenantSessionRuntimePolicy({
      signal: new AbortController().signal,
      loadPolicy: async () => { throw new Error("upstream detail"); },
    })).resolves.toBe(false);

    const controller = new AbortController();
    controller.abort();
    await expect(verifyTenantSessionRuntimePolicy({
      signal: controller.signal,
      loadPolicy: async () => ({ tenantSessionMode: "tenant-session-required" }),
    })).rejects.toMatchObject({ name: "AbortError" });
  });
});
