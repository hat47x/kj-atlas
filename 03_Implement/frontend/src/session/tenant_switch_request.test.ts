import { describe, expect, it, vi } from "vitest";

import type { TenantSessionContextV1 } from "../api/session_context";
import type { TenantBrowserStorageScope } from "../storage/tenant_scope";
import { requestTenantSessionTransition } from "./tenant_switch_request";

const deployment = "https://atlas.example.test";
const previousScope: TenantBrowserStorageScope = {
  deployment,
  principalId: "user-1",
  tenantId: "tenant-a",
};

const currentSession: TenantSessionContextV1 = {
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

function nextSession(overrides: Partial<TenantSessionContextV1> = {}) {
  return {
    ...currentSession,
    activeTenant: { id: "tenant-b", displayName: "Tenant B" },
    capabilityVersion: "policy-v2",
    tenantSessionVersion: "session-v2",
    ...overrides,
  };
}

function createStorage() {
  const keys = new Map<string, string>();
  return {
    get length() {
      return keys.size;
    },
    key(index: number) {
      return [...keys.keys()][index] ?? null;
    },
    removeItem(key: string) {
      keys.delete(key);
    },
  };
}

function request(overrides: Record<string, unknown> = {}) {
  return requestTenantSessionTransition({
    currentSessionContext: currentSession,
    requestedTenantId: "tenant-b",
    deployment,
    previousScope,
    storage: createStorage(),
    cleanupSteps: [],
    hasUnsavedChanges: false,
    signal: new AbortController().signal,
    changeTenant: async () => nextSession(),
    replaceDocument: () => undefined,
    ...overrides,
  });
}

describe("tenant switch request", () => {
  it("changes only to an allowlisted tenant and performs hard replacement", async () => {
    const order: string[] = [];
    const changeTenant = vi.fn(async () => {
      order.push("post");
      return nextSession();
    });

    await expect(request({
      changeTenant,
      notifySessionChanged: () => order.push("notify"),
      cleanupSteps: [() => order.push("cleanup")],
      replaceDocument: () => order.push("replace"),
    })).resolves.toMatchObject({
      status: "transitioned",
      transition: {
        nextScope: { ...previousScope, tenantId: "tenant-b" },
      },
    });
    expect(order).toEqual(["post", "notify", "cleanup", "replace"]);
    expect(changeTenant).toHaveBeenCalledWith(
      currentSession,
      "tenant-b",
      { signal: expect.any(AbortSignal) },
    );
  });

  it("does nothing when the active tenant is selected", async () => {
    const changeTenant = vi.fn();
    await expect(request({
      requestedTenantId: "tenant-a",
      changeTenant,
    })).resolves.toEqual({ status: "unchanged" });
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("rejects free input and previous-scope mismatch before confirmation or POST", async () => {
    const requestUnsavedDecision = vi.fn();
    const changeTenant = vi.fn();
    await expect(request({
      requestedTenantId: "attacker-tenant",
      hasUnsavedChanges: true,
      requestUnsavedDecision,
      changeTenant,
    })).rejects.toThrow("Invalid tenant session context");
    await expect(request({
      previousScope: { ...previousScope, tenantId: "tenant-x" },
      hasUnsavedChanges: true,
      requestUnsavedDecision,
      changeTenant,
    })).rejects.toThrow("Invalid tenant session context");
    expect(requestUnsavedDecision).not.toHaveBeenCalled();
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("requires scoped cleanup capability before changing the server session", async () => {
    const changeTenant = vi.fn();
    await expect(request({
      storage: undefined,
      clearPreviousScope: undefined,
      changeTenant,
    })).rejects.toThrow("Invalid tenant session context");
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("uses the App storage facade cleanup after a verified change", async () => {
    const clearPreviousScope = vi.fn(() => 3);
    await expect(request({
      storage: undefined,
      clearPreviousScope,
    })).resolves.toMatchObject({
      status: "transitioned",
      transition: { clearedStorageEntries: 3 },
    });
    expect(clearPreviousScope).toHaveBeenCalledOnce();
  });

  it("cancels without saving, POST, cleanup, or replacement", async () => {
    const saveUnsavedChanges = vi.fn();
    const changeTenant = vi.fn();
    const cleanup = vi.fn();
    const replaceDocument = vi.fn();
    await expect(request({
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => "cancel",
      saveUnsavedChanges,
      changeTenant,
      cleanupSteps: [cleanup],
      replaceDocument,
    })).resolves.toEqual({ status: "cancelled" });
    expect(saveUnsavedChanges).not.toHaveBeenCalled();
    expect(changeTenant).not.toHaveBeenCalled();
    expect(cleanup).not.toHaveBeenCalled();
    expect(replaceDocument).not.toHaveBeenCalled();
  });

  it("blocks the switch when saving fails", async () => {
    const changeTenant = vi.fn();
    await expect(request({
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => "save",
      saveUnsavedChanges: async () => false,
      changeTenant,
    })).resolves.toEqual({ status: "save-failed" });
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("saves before POST and allows an explicit discard path", async () => {
    const saveOrder: string[] = [];
    await expect(request({
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => "save",
      saveUnsavedChanges: async () => {
        saveOrder.push("save");
        return true;
      },
      changeTenant: async () => {
        saveOrder.push("post");
        return nextSession();
      },
    })).resolves.toMatchObject({ status: "transitioned" });
    expect(saveOrder).toEqual(["save", "post"]);

    const saveUnsavedChanges = vi.fn();
    await expect(request({
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => "discard",
      saveUnsavedChanges,
    })).resolves.toMatchObject({ status: "transitioned" });
    expect(saveUnsavedChanges).not.toHaveBeenCalled();
  });

  it("rejects missing or unknown unsaved decisions without POST", async () => {
    const changeTenant = vi.fn();
    await expect(request({
      hasUnsavedChanges: true,
      changeTenant,
    })).rejects.toThrow("Invalid tenant session context");
    await expect(request({
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => "continue",
      changeTenant,
    })).rejects.toThrow("Invalid tenant session context");
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("rejects a changed principal or unexpected active tenant before cleanup", async () => {
    const cleanup = vi.fn();
    const replaceDocument = vi.fn();
    await expect(request({
      changeTenant: async () => nextSession({ principalId: "user-2" }),
      cleanupSteps: [cleanup],
      replaceDocument,
    })).rejects.toThrow("Invalid tenant session context");
    await expect(request({
      changeTenant: async () => currentSession,
      cleanupSteps: [cleanup],
      replaceDocument,
    })).rejects.toThrow("Invalid tenant session context");
    expect(cleanup).not.toHaveBeenCalled();
    expect(replaceDocument).not.toHaveBeenCalled();
  });

  it("rejects an unchanged tenant session version before cleanup", async () => {
    const cleanup = vi.fn();
    const replaceDocument = vi.fn();
    await expect(request({
      changeTenant: async () => nextSession({ tenantSessionVersion: "session-v1" }),
      cleanupSteps: [cleanup],
      replaceDocument,
    })).rejects.toThrow("Invalid tenant session context");
    expect(cleanup).not.toHaveBeenCalled();
    expect(replaceDocument).not.toHaveBeenCalled();
  });

  it("honors abort before confirmation and before POST", async () => {
    const controller = new AbortController();
    controller.abort();
    await expect(request({ signal: controller.signal })).rejects.toMatchObject({
      name: "AbortError",
    });

    const confirmationController = new AbortController();
    const changeTenant = vi.fn();
    await expect(request({
      signal: confirmationController.signal,
      hasUnsavedChanges: true,
      requestUnsavedDecision: async () => {
        confirmationController.abort();
        return "discard";
      },
      changeTenant,
    })).rejects.toMatchObject({ name: "AbortError" });
    expect(changeTenant).not.toHaveBeenCalled();
  });

  it("still replaces the old tenant after a verified server change", async () => {
    const controller = new AbortController();
    const replaceDocument = vi.fn();
    await expect(request({
      signal: controller.signal,
      changeTenant: async () => {
        controller.abort();
        return nextSession();
      },
      replaceDocument,
    })).resolves.toMatchObject({ status: "transitioned" });
    expect(replaceDocument).toHaveBeenCalledOnce();
  });

  it("continues replacement when advisory cross-tab notification fails", async () => {
    const replaceDocument = vi.fn();
    await expect(request({
      notifySessionChanged: () => {
        throw new Error("channel unavailable");
      },
      replaceDocument,
    })).resolves.toMatchObject({ status: "transitioned" });
    expect(replaceDocument).toHaveBeenCalledOnce();
  });
});
