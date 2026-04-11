import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { PatchWorkspacePanel } from "./PatchWorkspacePanel";

describe("PatchWorkspacePanel", () => {
  it("renders CE3 workspace controls and recovery guidance", () => {
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        candidates: [
          { id: "cand-1", label: "cand-1 (3 cards)" },
          { id: "cand-2", label: "cand-2 (2 cards)" },
        ],
      })
    );

    expect(html).toContain("CE3 Patch workspace");
    expect(html).toContain("Adopt");
    expect(html).toContain("Hold");
    expect(html).toContain("Reject");
    expect(html).toContain("Roll back last workspace decision");
    expect(html).toContain("Run current preset");
    expect(html).toContain("phase: idle");
    expect(html).toContain("No saved presets.");
    expect(html).toContain("Audit transitions");
    expect(html).toContain("Normalized query");
    expect(html).toContain("Recovery path:");
  });

  it("disables preset and decision controls in read-only mode", () => {
    const html = renderToStaticMarkup(
      React.createElement(PatchWorkspacePanel, {
        isReadOnly: true,
        candidates: [{ id: "cand-1", label: "cand-1 (3 cards)" }],
      })
    );

    expect(html).toContain('data-testid="ce3-adopt" disabled=""');
    expect(html).toContain('data-testid="ce3-hold" disabled=""');
    expect(html).toContain('data-testid="ce3-reject" disabled=""');
    expect(html).toMatch(/data-testid="ce3-preset-name"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-scope"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-depth"[^>]*disabled=""/);
    expect(html).toMatch(/data-testid="ce3-preset-filters"[^>]*disabled=""/);
    expect(html).toContain('data-testid="ce3-run-inline-preset" disabled=""');
  });
});
