// @vitest-environment happy-dom

import React, { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import {
  redirectToTenantSessionLogin,
  TenantSessionBlockedView,
  TenantSessionBootstrapGate,
  TenantSessionLoadingView,
} from "./TenantSessionBootstrapGate";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

const validSession = {
  principalId: "user-1",
  activeTenant: { id: "tenant-1", displayName: "Tenant One" },
  availableTenants: [{ id: "tenant-1", displayName: "Tenant One" }],
  effectiveCapabilities: ["document.read"],
  capabilityVersion: "v1",
  tenantSessionVersion: "v1",
};

async function flushReactWork(): Promise<void> {
  await Promise.resolve();
  await Promise.resolve();
}

async function mountBootstrapGate(
  props: Parameters<typeof TenantSessionBootstrapGate>[0],
): Promise<{ container: HTMLElement; root: Root }> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(TenantSessionBootstrapGate, props));
    await flushReactWork();
  });
  return { container, root };
}

afterEach(async () => {
  while (roots.length > 0) {
    const root = roots.pop();
    if (root) {
      await act(async () => root.unmount());
    }
  }
  document.body.replaceChildren();
  setActiveLocale("ja");
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("tenant session bootstrap gate", () => {
  it("keeps tenant content unmounted while session bootstrap is pending", async () => {
    const renderApp = vi.fn();
    const { container } = await mountBootstrapGate({
      deployment: "https://atlas.example.test",
      loadSessionContext: async () => new Promise(() => undefined),
      renderApp,
    });

    expect(container.querySelector('[role="status"]')).not.toBeNull();
    expect(container.querySelector('[aria-busy="true"]')).not.toBeNull();
    expect(container.textContent).toContain("利用環境を確認しています");
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("fails closed on an invalid session response without mounting App", async () => {
    const renderApp = vi.fn();
    const { container } = await mountBootstrapGate({
      deployment: "https://atlas.example.test",
      loadSessionContext: async () => ({ principalId: "user-1" }),
      renderApp,
    });

    expect(container.querySelector('[role="alert"]')).not.toBeNull();
    expect(container.textContent).toContain("アクセスを確認できません");
    expect(container.querySelector("button")?.textContent).toContain("再試行");
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("hands a validated tenant session and storage scope to App", async () => {
    const renderApp = vi.fn((result) => React.createElement(
      "div",
      { "data-testid": "tenant-app" },
      `${result.sessionContext.activeTenant.id}:${result.storageScope.tenantId}`,
    ));
    const loadSessionContext = vi.fn(async () => validSession);
    const { container } = await mountBootstrapGate({
      deployment: "https://atlas.example.test",
      loadSessionContext,
      renderApp,
    });

    expect(loadSessionContext).toHaveBeenCalledTimes(1);
    expect(renderApp).toHaveBeenCalledTimes(1);
    const ready = renderApp.mock.calls[0]?.[0];
    expect(ready?.status).toBe("ready");
    if (ready?.status === "ready") {
      expect(ready.sessionContext.activeTenant.id).toBe("tenant-1");
      expect(ready.storageScope.tenantId).toBe("tenant-1");
      expect(ready.storageScope.deployment).toBe("https://atlas.example.test");
    }
    expect(container.querySelector('[data-testid="tenant-app"]')?.textContent).toContain("tenant-1");
  });

  it("retries a transient session failure and can recover to ready", async () => {
    const loadSessionContext = vi.fn()
      .mockRejectedValueOnce(new Error("temporary outage"))
      .mockResolvedValueOnce(validSession);
    const renderApp = vi.fn(() => React.createElement("div", null, "ready after retry"));
    const { container } = await mountBootstrapGate({
      deployment: "https://atlas.example.test",
      loadSessionContext,
      renderApp,
    });

    expect(container.querySelector('[role="alert"]')).not.toBeNull();
    const retry = container.querySelector("button");
    expect(retry?.textContent).toContain("再試行");

    await act(async () => {
      retry?.click();
      await flushReactWork();
    });

    expect(loadSessionContext).toHaveBeenCalledTimes(2);
    expect(renderApp).toHaveBeenCalledTimes(1);
    expect(container.textContent).toContain("ready after retry");
  });

  it("aborts the in-flight bootstrap when the gate unmounts", async () => {
    let receivedSignal: AbortSignal | undefined;
    const loadSessionContext = vi.fn(({ signal }: { signal?: AbortSignal }) => {
      receivedSignal = signal;
      return new Promise(() => undefined);
    });
    const { root } = await mountBootstrapGate({
      deployment: "https://atlas.example.test",
      loadSessionContext,
      renderApp: vi.fn(),
    });

    expect(receivedSignal?.aborted).toBe(false);
    await act(async () => root.unmount());
    const index = roots.indexOf(root);
    if (index >= 0) {
      roots.splice(index, 1);
    }

    expect(receivedSignal?.aborted).toBe(true);
  });
});

describe("tenant session bootstrap views", () => {
  it("renders every failure as an accessible blocked state", () => {
    for (const reason of [
      "authentication_required",
      "access_denied",
      "session_unavailable",
      "invalid_session_response",
      "invalid_deployment",
    ] as const) {
      const html = renderToStaticMarkup(React.createElement(
        TenantSessionBlockedView,
        { reason, onRetry: () => undefined },
      ));

      expect(html).toContain('role="alert"');
      expect(html).toContain("アクセスを確認できません");
      expect(html).toContain("<button");
      if (reason === "authentication_required") {
        expect(html).toContain("サインイン");
      } else {
        expect(html).toContain("再試行");
      }
      expect(html).not.toContain("user-1");
      expect(html).not.toContain("tenant-a");
    }
  });

  it("starts SaaS authentication through the same-origin BFF endpoint", () => {
    const assign = vi.fn();

    redirectToTenantSessionLogin({ assign } as Pick<Location, "assign">);

    expect(assign).toHaveBeenCalledOnce();
    expect(assign).toHaveBeenCalledWith("/session/login");
  });

  it("keeps the pre-App state available in English", () => {
    setActiveLocale("en");
    const loadingHtml = renderToStaticMarkup(
      React.createElement(TenantSessionLoadingView),
    );
    const blockedHtml = renderToStaticMarkup(React.createElement(
      TenantSessionBlockedView,
      { reason: "session_unavailable", onRetry: () => undefined },
    ));

    expect(loadingHtml).toContain("Checking your access");
    expect(blockedHtml).toContain("We couldn’t verify access");
    expect(blockedHtml).toContain("Retry");
  });
});
