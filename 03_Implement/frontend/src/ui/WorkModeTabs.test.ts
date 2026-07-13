import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { WorkModeTabs, type WorkModeTabDef } from "./WorkModeTabs";

// UX-NAV-02 (resolves ADR-0052 C-5): structural/markup contract for the
// work-mode role=tablist container. Static-markup only (this codebase's
// established convention for UI component unit tests, see e.g.
// StartPanel.accessibility.test.ts) -- keyboard/focus/click interaction is
// covered by e2e/work_mode_tabs.spec.ts against a real browser DOM.

function buildTabs(): WorkModeTabDef[] {
  return [
    { id: "diff", label: "差分", content: React.createElement("div", { "data-testid": "diff-content" }, "diff-marker") },
    { id: "merge", label: "選択マージ", content: React.createElement("div", { "data-testid": "merge-content" }, "merge-marker") },
    { id: "suggestion", label: "AI提案", content: React.createElement("div", { "data-testid": "suggestion-content" }, "suggestion-marker") },
    { id: "diagnostics", label: "診断", content: React.createElement("div", { "data-testid": "diagnostics-content" }, "diagnostics-marker") },
    { id: "narrative", label: "文章化", content: React.createElement("div", { "data-testid": "narrative-content" }, "narrative-marker") },
  ];
}

function render(): string {
  return renderToStaticMarkup(React.createElement(WorkModeTabs, { tabs: buildTabs() }));
}

describe("WorkModeTabs markup contract", () => {
  it("renders a tablist with one tab button per tab, all as role=tab", () => {
    const html = render();
    expect(html).toContain('role="tablist"');
    expect((html.match(/role="tab"/g) ?? []).length).toBe(5);
    expect((html.match(/role="tabpanel"/g) ?? []).length).toBe(5);
  });

  it("marks only the first tab active: aria-selected, roving tabIndex 0, and initial-focus marker", () => {
    const html = render();

    expect(html).toContain('id="work-mode-tab-diff" aria-selected="true" aria-controls="work-mode-panel-diff" tabindex="0" data-work-mode-initial-focus="true"');
    expect(html).toContain('id="work-mode-tab-merge" aria-selected="false" aria-controls="work-mode-panel-merge" tabindex="-1"');
    expect(html).toContain('id="work-mode-tab-suggestion" aria-selected="false"');
    expect(html).toContain('id="work-mode-tab-diagnostics" aria-selected="false"');
    expect(html).toContain('id="work-mode-tab-narrative" aria-selected="false"');
    // Exactly one tab carries the initial-focus marker.
    expect((html.match(/data-work-mode-initial-focus="true"/g) ?? []).length).toBe(1);
  });

  it("hides every tabpanel except the active one, via the native hidden attribute (mounted, not unmounted)", () => {
    const html = render();

    expect(html).toContain('id="work-mode-panel-diff" aria-labelledby="work-mode-tab-diff"');
    expect(html).not.toMatch(/id="work-mode-panel-diff"[^>]*hidden/);
    for (const id of ["merge", "suggestion", "diagnostics", "narrative"]) {
      const panelMatch = new RegExp(`id="work-mode-panel-${id}"[^>]*hidden`);
      expect(html, id).toMatch(panelMatch);
    }

    // All 5 panels' content is present in markup even while hidden --
    // confirms "mounted+hidden", not conditionally rendered/unmounted.
    expect(html).toContain("diff-marker");
    expect(html).toContain("merge-marker");
    expect(html).toContain("suggestion-marker");
    expect(html).toContain("diagnostics-marker");
    expect(html).toContain("narrative-marker");
  });

  it("labels the tablist and orders tabs diff/merge/suggestion/diagnostics/narrative", () => {
    const html = render();
    const order = ["work-mode-tab-diff", "work-mode-tab-merge", "work-mode-tab-suggestion", "work-mode-tab-diagnostics", "work-mode-tab-narrative"]
      .map((id) => html.indexOf(`id="${id}"`));
    expect(order.every((index) => index !== -1)).toBe(true);
    expect(order).toEqual([...order].sort((a, b) => a - b));
  });
});
