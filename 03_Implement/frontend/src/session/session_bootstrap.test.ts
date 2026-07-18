import { describe, expect, it, vi } from "vitest";

import { ApiError } from "../api/client";
import {
  bootstrapTenantSession,
  type TenantSessionBlockReason,
} from "./session_bootstrap";

function validSessionContext(overrides: Record<string, unknown> = {}) {
  return {
    principalId: "user-1",
    activeTenant: { id: "tenant-a", displayName: "Tenant A" },
    availableTenants: [
      { id: "tenant-a", displayName: "Tenant A" },
      { id: "tenant-b", displayName: "Tenant B" },
    ],
    effectiveCapabilities: ["document.write", "document.read"],
    capabilityVersion: "capability-v7",
    ...overrides,
  };
}

describe("tenant session bootstrap", () => {
  it("builds the App storage scope only after validating the session response", async () => {
    const controller = new AbortController();
    const loadSessionContext = vi.fn().mockResolvedValue(validSessionContext());

    const result = await bootstrapTenantSession({
      deployment: "https://atlas.example.test",
      signal: controller.signal,
      loadSessionContext,
    });

    expect(loadSessionContext).toHaveBeenCalledWith({ signal: controller.signal });
    expect(result).toEqual({
      status: "ready",
      sessionContext: {
        ...validSessionContext(),
        effectiveCapabilities: ["document.read", "document.write"],
      },
      storageScope: {
        deployment: "https://atlas.example.test",
        tenantId: "tenant-a",
        principalId: "user-1",
      },
    });
  });

  it("blocks invalid session data without producing a storage scope", async () => {
    const result = await bootstrapTenantSession({
      deployment: "https://atlas.example.test",
      signal: new AbortController().signal,
      loadSessionContext: async () => ({ principalId: "user-1" }),
    });

    expect(result).toEqual({
      status: "blocked",
      reason: "invalid_session_response",
    });
    expect(result).not.toHaveProperty("storageScope");
  });

  it.each<[number, TenantSessionBlockReason]>([
    [401, "authentication_required"],
    [403, "access_denied"],
    [503, "session_unavailable"],
  ])("maps HTTP %s to a stable blocked reason", async (status, reason) => {
    const result = await bootstrapTenantSession({
      deployment: "https://atlas.example.test",
      signal: new AbortController().signal,
      loadSessionContext: async () => {
        throw new ApiError(status, "secret upstream detail", {
          code: "secret_internal_code",
        });
      },
    });

    expect(result).toEqual({ status: "blocked", reason });
    expect(JSON.stringify(result)).not.toContain("secret");
  });

  it("normalizes network failures without reflecting their details", async () => {
    const result = await bootstrapTenantSession({
      deployment: "https://atlas.example.test",
      signal: new AbortController().signal,
      loadSessionContext: async () => {
        throw new Error("secret network endpoint failed");
      },
    });

    expect(result).toEqual({
      status: "blocked",
      reason: "session_unavailable",
    });
  });

  it("blocks an invalid deployment before mounting the App", async () => {
    const result = await bootstrapTenantSession({
      deployment: "",
      signal: new AbortController().signal,
      loadSessionContext: async () => validSessionContext(),
    });

    expect(result).toEqual({
      status: "blocked",
      reason: "invalid_deployment",
    });
  });

  it("propagates lifecycle aborts instead of showing a failure state", async () => {
    const controller = new AbortController();
    const abortError = new DOMException("request aborted", "AbortError");
    const pending = bootstrapTenantSession({
      deployment: "https://atlas.example.test",
      signal: controller.signal,
      loadSessionContext: async () => {
        controller.abort(abortError);
        throw abortError;
      },
    });

    await expect(pending).rejects.toBe(abortError);
  });
});
