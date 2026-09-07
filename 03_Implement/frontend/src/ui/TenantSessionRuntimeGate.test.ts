// @vitest-environment happy-dom

import React, { act } from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRoot, type Root } from "react-dom/client";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { TenantSessionRuntimeGate } from "./TenantSessionRuntimeGate";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

async function flushReactWork(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
}

async function mountRuntimeGate(
  props: Parameters<typeof TenantSessionRuntimeGate>[0],
): Promise<HTMLElement> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(TenantSessionRuntimeGate, props));
    await flushReactWork();
  });
  return container;
}

afterEach(async () => {
  while (roots.length > 0) {
    const root = roots.pop();
    if (root) {
      await act(async () => root.unmount());
    }
  }
  document.body.replaceChildren();
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("tenant session runtime gate", () => {
  it("starts with no tenant App content mounted while policy verification is pending", async () => {
    const renderApp = vi.fn();
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => new Promise(() => undefined),
      renderApp,
    });

    expect(container.querySelector('[role="status"]')).not.toBeNull();
    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("blocks when runtime policy does not require a tenant session", async () => {
    const renderApp = vi.fn();
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => ({ tenantSessionMode: "single-tenant" }),
      renderApp,
    });

    expect(container.querySelector('[role="alert"]')).not.toBeNull();
    expect(container.querySelector("button")).not.toBeNull();
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("hands verified runtime policy to tenant session bootstrap and mounts scoped App", async () => {
    const renderApp = vi.fn(() => React.createElement(
      "div",
      { "data-testid": "tenant-app" },
      "ready",
    ));
    const loadSessionContext = vi.fn(async () => ({
      principalId: "user-1",
      activeTenant: { id: "tenant-1", displayName: "Tenant One" },
      availableTenants: [{ id: "tenant-1", displayName: "Tenant One" }],
      effectiveCapabilities: ["document.read"],
      capabilityVersion: "v1",
      tenantSessionVersion: "v1",
    }));
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy: async () => ({ tenantSessionMode: "tenant-session-required" }),
      loadSessionContext,
      renderApp,
    });

    expect(loadSessionContext).toHaveBeenCalledTimes(1);
    expect(renderApp).toHaveBeenCalledTimes(1);
    expect(container.querySelector('[data-testid="tenant-app"]')?.textContent).toBe("ready");
  });

  it("retries runtime policy verification and can recover from blocked to ready", async () => {
    const loadPolicy = vi.fn()
      .mockResolvedValueOnce({ tenantSessionMode: "single-tenant" })
      .mockResolvedValueOnce({ tenantSessionMode: "tenant-session-required" });
    const loadSessionContext = vi.fn(async () => ({
      principalId: "user-1",
      activeTenant: { id: "tenant-1", displayName: "Tenant One" },
      availableTenants: [{ id: "tenant-1", displayName: "Tenant One" }],
      effectiveCapabilities: ["document.read"],
      capabilityVersion: "v1",
      tenantSessionVersion: "v1",
    }));
    const renderApp = vi.fn(() => React.createElement("div", null, "ready after retry"));
    const container = await mountRuntimeGate({
      deployment: "https://atlas.example.test",
      loadPolicy,
      loadSessionContext,
      renderApp,
    });

    const retry = container.querySelector("button");
    expect(retry).not.toBeNull();
    await act(async () => {
      retry?.click();
      await flushReactWork();
    });

    expect(loadPolicy).toHaveBeenCalledTimes(2);
    expect(loadSessionContext).toHaveBeenCalledTimes(1);
    expect(renderApp).toHaveBeenCalledTimes(1);
    expect(container.textContent).toContain("ready after retry");
  });

  it("remains wired to the production entry point and scoped App", () => {
    const mainSource = readFileSync(resolve(__dirname, "..", "main.tsx"), "utf8");

    expect(mainSource).toContain("resolveRuntimeEntryMode");
    expect(mainSource).toContain('runtimeEntryMode === "tenant-session-required"');
    expect(mainSource).toContain("<TenantSessionRuntimeGate");
    expect(mainSource).toContain("storageScope={result.storageScope}");
    expect(mainSource).toContain("tenantSessionContext={result.sessionContext}");
    expect(mainSource).toContain('runtimeEntryMode === "invalid"');
  });
});
