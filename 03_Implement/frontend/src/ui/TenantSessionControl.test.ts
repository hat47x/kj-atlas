import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { TenantSessionContextV1 } from "../api/session_context";
import { setActiveLocale } from "../i18n/translate";
import {
  resolveAllowedTenantSelection,
  TenantSessionControl,
} from "./TenantSessionControl";

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

describe("tenant session control", () => {
  afterEach(() => setActiveLocale("ja"));

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
