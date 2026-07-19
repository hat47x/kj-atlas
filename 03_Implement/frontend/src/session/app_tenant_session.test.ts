import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { resolveAppTenantSession } from "./app_tenant_session";

const sessionContext = {
  principalId: "user-1",
  activeTenant: { id: "tenant-a", displayName: "Tenant A" },
  availableTenants: [
    { id: "tenant-a", displayName: "Tenant A" },
    { id: "tenant-b", displayName: "Tenant B" },
  ],
  effectiveCapabilities: ["document.read"],
  capabilityVersion: "policy-v1",
  tenantSessionVersion: "session-v1",
};

describe("App tenant session boundary", () => {
  it("preserves the existing single-tenant App when no session is injected", () => {
    expect(resolveAppTenantSession({})).toBeUndefined();
  });

  it("accepts only a session matching the injected storage scope", () => {
    expect(resolveAppTenantSession({
      sessionContext,
      storageScope: {
        deployment: "https://atlas.example.test",
        principalId: "user-1",
        tenantId: "tenant-a",
      },
    })).toEqual(sessionContext);
  });

  it.each([
    undefined,
    {
      deployment: "https://atlas.example.test",
      principalId: "user-2",
      tenantId: "tenant-a",
    },
    {
      deployment: "https://atlas.example.test",
      principalId: "user-1",
      tenantId: "tenant-b",
    },
  ])("rejects a missing or mismatched storage scope", (storageScope) => {
    expect(() => resolveAppTenantSession({
      sessionContext,
      storageScope,
    })).toThrow("Invalid tenant session context");
  });

  it("revalidates injected session data instead of trusting its TypeScript type", () => {
    expect(() => resolveAppTenantSession({
      sessionContext: { ...sessionContext, role: "admin" },
      storageScope: {
        deployment: "https://atlas.example.test",
        principalId: "user-1",
        tenantId: "tenant-a",
      },
    })).toThrow("Invalid tenant session context");
  });

  it("keeps the prepared App host wired but disabled at the production entry", () => {
    const appSource = readFileSync(resolve(__dirname, "..", "App.tsx"), "utf8");
    const mainSource = readFileSync(resolve(__dirname, "..", "main.tsx"), "utf8");

    expect(appSource).toContain("resolveAppTenantSession");
    expect(appSource).toContain("requestTenantSessionTransition");
    expect(appSource).toContain("installTenantSessionCoherenceBoundary");
    expect(appSource).toContain("publishSessionChanged");
    expect(appSource).toContain("<TenantSessionControl");
    expect(appSource).toContain("<TenantChangeConfirmationDialog");
    expect(appSource).toContain('tenantSwitchUiState.status === "switching"');
    expect(appSource).toContain('tenantSwitchUiState.status === "blocked"');
    expect(mainSource).toContain("<App storageScope={result.storageScope} />");
    expect(mainSource).not.toContain("tenantSessionContext={result.sessionContext}");
  });
});
