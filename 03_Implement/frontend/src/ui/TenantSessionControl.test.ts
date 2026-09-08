// @vitest-environment happy-dom

import React, { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import type { TenantSessionContextV1 } from "../api/session_context";
import { setActiveLocale } from "../i18n/translate";
import {
  resolveAllowedTenantSelection,
  TenantSessionControl,
} from "./TenantSessionControl";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

function sessionContext(
  availableTenants: TenantSessionContextV1["availableTenants"],
): TenantSessionContextV1 {
  return {
    principalId: "user-1",
    activeTenant: availableTenants[0]!,
    availableTenants,
    effectiveCapabilities: ["document.read"],
    capabilityVersion: "capability-v7",
    tenantSessionVersion: "session-v1",
  };
}

async function mountTenantSessionControl(
  props: Parameters<typeof TenantSessionControl>[0],
): Promise<HTMLElement> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(TenantSessionControl, props));
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
  setActiveLocale("ja");
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("tenant session control", () => {
  it("shows a non-interactive active-tenant label for one membership", () => {
    const html = renderToStaticMarkup(React.createElement(TenantSessionControl, {
      sessionContext: sessionContext([
        { id: "tenant-a", displayName: "テナントA" },
      ]),
      onRequestTenantChange: vi.fn(),
    }));

    expect(html).toContain('data-tenant-control="label"');
    expect(html).toContain("ワークスペース");
    expect(html).toContain("テナントA");
    expect(html).toContain("現在のワークスペース: テナントA");
    expect(html).not.toContain("<select");
    expect(html).not.toContain("tenant-a");
  });

  it("offers only server-returned memberships when switching is available", () => {
    const html = renderToStaticMarkup(React.createElement(TenantSessionControl, {
      sessionContext: sessionContext([
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ]),
      onRequestTenantChange: vi.fn(),
    }));

    expect(html).toContain('data-tenant-control="switcher"');
    expect(html).toContain("<select");
    expect(html.match(/<option/g)).toHaveLength(2);
    expect(html).toContain('value="tenant-a"');
    expect(html).toContain('value="tenant-b"');
    expect(html).not.toContain("input");
  });

  it("routes real select changes through the verified tenant allowlist", async () => {
    const onRequestTenantChange = vi.fn();
    const container = await mountTenantSessionControl({
      sessionContext: sessionContext([
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ]),
      onRequestTenantChange,
    });
    const select = container.querySelector("select");
    expect(select).not.toBeNull();
    if (!select) {
      throw new Error("tenant switcher was not rendered");
    }

    await act(async () => {
      select.value = "tenant-b";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });
    expect(onRequestTenantChange).toHaveBeenCalledTimes(1);
    expect(onRequestTenantChange).toHaveBeenLastCalledWith("tenant-b");

    onRequestTenantChange.mockClear();
    const injected = document.createElement("option");
    injected.value = "attacker-tenant";
    injected.textContent = "Injected tenant";
    select.append(injected);
    await act(async () => {
      select.value = "attacker-tenant";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });
    expect(onRequestTenantChange).not.toHaveBeenCalled();

    await act(async () => {
      select.value = "tenant-a";
      select.dispatchEvent(new Event("change", { bubbles: true }));
    });
    expect(onRequestTenantChange).not.toHaveBeenCalled();
  });

  it("disables the switcher and announces a pending change", () => {
    const html = renderToStaticMarkup(React.createElement(TenantSessionControl, {
      sessionContext: sessionContext([
        { id: "tenant-a", displayName: "Tenant A" },
        { id: "tenant-b", displayName: "Tenant B" },
      ]),
      isChanging: true,
      onRequestTenantChange: vi.fn(),
    }));

    expect(html).toContain("disabled");
    expect(html).toContain('aria-busy="true"');
    expect(html).toContain('role="status"');
    expect(html).toContain("切り替えています");
  });

  it("ignores the active tenant, free input, and invalid session data", () => {
    const context = sessionContext([
      { id: "tenant-a", displayName: "Tenant A" },
      { id: "tenant-b", displayName: "Tenant B" },
    ]);

    expect(resolveAllowedTenantSelection(context, "tenant-b")).toBe("tenant-b");
    expect(resolveAllowedTenantSelection(context, "tenant-a")).toBeNull();
    expect(resolveAllowedTenantSelection(context, "attacker-tenant")).toBeNull();
    expect(resolveAllowedTenantSelection({ principalId: "user-1" }, "tenant-b")).toBeNull();
  });

  it("uses the same accessible contract in English", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(TenantSessionControl, {
      sessionContext: sessionContext([
        { id: "tenant-a", displayName: "Tenant A" },
      ]),
      onRequestTenantChange: vi.fn(),
    }));

    expect(html).toContain("Workspace");
    expect(html).toContain("Current workspace: Tenant A");
  });
});
