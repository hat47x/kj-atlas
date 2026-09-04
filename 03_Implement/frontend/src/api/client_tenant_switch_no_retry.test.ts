import { afterEach, describe, expect, it, vi } from "vitest";

import { changeActiveTenant } from "./client";
import type { TenantSessionContextV1 } from "./session_context";

const currentSession: TenantSessionContextV1 = {
  principalId: "user-1",
  activeTenant: { id: "tenant-a", displayName: "Tenant A" },
  availableTenants: [
    { id: "tenant-a", displayName: "Tenant A" },
    { id: "tenant-b", displayName: "Tenant B" },
  ],
  effectiveCapabilities: [],
  capabilityVersion: "capability-v1",
  tenantSessionVersion: "version-1",
};

function failedResponse(status: number, code: string): Response {
  return new Response(
    JSON.stringify({ detail: { code, message: "Tenant switch failed." } }),
    {
      status,
      headers: { "Content-Type": "application/json" },
    },
  );
}

describe("changeActiveTenant retry boundary", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it.each([
    [409, "tenant_session_changed"],
    [503, "active_tenant_update_unavailable"],
  ])("does not retry a failed tenant switch (%s)", async (status, code) => {
    const fetchMock = vi.fn().mockResolvedValue(failedResponse(status, code));
    vi.stubGlobal("fetch", fetchMock);

    await expect(changeActiveTenant(currentSession, "tenant-b")).rejects.toMatchObject({
      status,
      code,
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/session/active-tenant",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
