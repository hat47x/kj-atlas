import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import type { Island } from "../domain/types";
import { IslandView } from "./IslandView";

describe("IslandView accessibility controls", () => {
  it("renders one primary select control and keeps utility controls separately named", () => {
    const island: Island = {
      id: "island-1",
      title: "Island",
      cardIds: ["c1"],
    };

    const html = renderToStaticMarkup(createElement(IslandView, {
      island,
      cards: [{ id: "c1", text: "Card", x: 0, y: 0 }],
      isSelected: false,
      onSelect: vi.fn(),
      onToggleCollapsed: vi.fn(),
      onFocusIsland: vi.fn(),
    }));

    expect((html.match(/aria-label="Select island island-1"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Focus island island-1"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="Collapse island island-1"/g) ?? []).length).toBe(1);
    expect(html).not.toContain('aria-label="Select island island-1 Focus island island-1"');
  });
});
