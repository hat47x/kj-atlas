import { describe, expect, it } from "vitest";

import {
  InvalidTenantSessionContextError,
  buildBrowserStorageScopeFromSession,
  parseTenantSessionContext,
} from "./session_context";

function validPayload(overrides: Record<string, unknown> = {}) {
  return {
    principalId: "user-1",
    activeTenant: { id: "tenant-a", displayName: "Tenant A" },
    availableTenants: [
      { id: "tenant-a", displayName: "Tenant A" },
      { id: "tenant-b", displayName: "Tenant B" },
    ],
    effectiveCapabilities: ["document.write", "document.read"],
    capabilityVersion: "policy-v7",
    tenantSessionVersion: "session-v1",
    ...overrides,
  };
}

describe("tenant session context", () => {
  it("parses an allowlisted active tenant and normalizes capabilities", () => {
    const context = parseTenantSessionContext(validPayload());

    expect(context.principalId).toBe("user-1");
    expect(context.activeTenant).toEqual({ id: "tenant-a", displayName: "Tenant A" });
    expect(context.effectiveCapabilities).toEqual(["document.read", "document.write"]);
    expect(context.tenantSessionVersion).toBe("session-v1");
  });

  it("rejects an active tenant outside the membership allowlist", () => {
    expect(() => parseTenantSessionContext(validPayload({
      activeTenant: { id: "tenant-x", displayName: "Tenant X" },
    }))).toThrow(InvalidTenantSessionContextError);
  });

  it("rejects duplicate tenant ids and inconsistent display metadata", () => {
    expect(() => parseTenantSessionContext(validPayload({
      availableTenants: [
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-a", displayName: "Spoofed Tenant" },
      ],
    }))).toThrow(InvalidTenantSessionContextError);
    expect(() => parseTenantSessionContext(validPayload({
      activeTenant: { id: "tenant-a", displayName: "Spoofed Tenant" },
    }))).toThrow(InvalidTenantSessionContextError);
  });

  it.each([
    { principalId: " user-1" },
    { principalId: "user-1\n" },
    { capabilityVersion: "" },
    { capabilityVersion: "x".repeat(129) },
    { tenantSessionVersion: "" },
    { tenantSessionVersion: " session-v1" },
    { tenantSessionVersion: "session v1" },
    { tenantSessionVersion: "x".repeat(129) },
    { tenantSessionVersion: "世代-1" },
    { principalId: "x".repeat(257) },
    { principalId: "user\u200b1" },
    { effectiveCapabilities: ["document.read\u007f"] },
    { effectiveCapabilities: ["tenant.root"] },
    { effectiveCapabilities: ["document.read", "document.read"] },
    { effectiveCapabilities: Array(12).fill("document.read") },
    { availableTenants: [] },
    { availableTenants: Array.from({ length: 257 }, (_, index) => ({
      id: `tenant-${index}`,
      displayName: `Tenant ${index}`,
    })) },
    { activeTenant: { id: "tenant-a", displayName: "x".repeat(257) } },
    { email: "hidden@example.invalid" },
    { activeTenant: { id: "tenant-a", displayName: "Tenant A", membershipId: "secret" } },
  ])("rejects non-canonical session values", (overrides) => {
    expect(() => parseTenantSessionContext(validPayload(overrides))).toThrow(
      InvalidTenantSessionContextError,
    );
  });

  it("derives browser storage scope only from validated server fields", () => {
    const context = parseTenantSessionContext(validPayload());

    expect(buildBrowserStorageScopeFromSession(context, "https://atlas.example.test")).toEqual({
      deployment: "https://atlas.example.test",
      tenantId: "tenant-a",
      principalId: "user-1",
    });
  });
});
