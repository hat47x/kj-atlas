import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import type { Island } from "../domain/types";
import { IslandView } from "./IslandView";

describe("IslandView accessibility controls", () => {
  const renderIsland = (island: Island) =>
    renderToStaticMarkup(createElement(IslandView, {
      island,
      cards: [{ id: "c1", text: "Card", x: 0, y: 0 }],
      isSelected: false,
      onSelect: vi.fn(),
      onToggleCollapsed: vi.fn(),
      onFocusIsland: vi.fn(),
    }));

  it("renders one primary select control and keeps utility controls separately named", () => {
    const island: Island = {
      id: "island-1",
      title: "Island",
      cardIds: ["c1"],
    };

    const html = renderIsland(island);

    expect((html.match(/aria-label="Select island island-1"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Focus island island-1"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Collapse island island-1"/g) ?? []).length).toBe(1);
    expect(html).not.toContain('aria-label="Select island island-1 Focus island island-1"');
  });

  it("uses one native select button for polygon islands", () => {
    const island: Island = {
      id: "island-poly",
      title: "Polygon island",
      cardIds: ["c1"],
      geometry: {
        type: "polygon",
        points: [
          { x: -10, y: -10 },
          { x: 260, y: -10 },
          { x: 260, y: 130 },
          { x: -10, y: 130 },
        ],
      },
    };

    const html = renderIsland(island);

    expect((html.match(/<button[^>]+aria-label="Select island island-poly"/g) ?? []).length).toBe(1);
    expect(html).not.toContain('role="button"');
    expect(html).toContain('aria-hidden="true" focusable="false"');
  });

  it("keeps collapsed island utility controls out of the select control name", () => {
    const island: Island = {
      id: "island-collapsed",
      title: "Collapsed island",
      cardIds: ["c1"],
      collapsed: true,
    };

    const html = renderIsland(island);

    expect((html.match(/aria-label="Select island island-collapsed"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Expand island island-collapsed"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Peek island island-collapsed"/g) ?? []).length).toBe(1);
    expect(html).not.toContain("Select island island-collapsed Focus island island-collapsed");
    expect(html).not.toContain("Select island island-collapsed Expand island island-collapsed");
    expect(html).not.toContain("Select island island-collapsed Peek island island-collapsed");
  });
});
