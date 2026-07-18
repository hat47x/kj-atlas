import React from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { TenantSessionRuntimeGate } from "./TenantSessionRuntimeGate";

describe("tenant session runtime gate", () => {
  it("starts with no tenant App content mounted", () => {
    const renderApp = vi.fn();
    const html = renderToStaticMarkup(React.createElement(
      TenantSessionRuntimeGate,
      {
        deployment: "https://atlas.example.test",
        loadPolicy: async () => new Promise(() => undefined),
        renderApp,
      },
    ));

    expect(html).toContain('role="status"');
    expect(html).toContain('aria-busy="true"');
    expect(renderApp).not.toHaveBeenCalled();
  });

  it("remains wired to the production entry point and scoped App", () => {
    const mainSource = readFileSync(resolve(__dirname, "..", "main.tsx"), "utf8");

    expect(mainSource).toContain("resolveRuntimeEntryMode");
    expect(mainSource).toContain('runtimeEntryMode === "tenant-session-required"');
    expect(mainSource).toContain("<TenantSessionRuntimeGate");
    expect(mainSource).toContain("<App storageScope={result.storageScope}");
    expect(mainSource).toContain('runtimeEntryMode === "invalid"');
  });
});
