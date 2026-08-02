import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { Island } from "../domain/types";
import { setActiveLocale } from "../i18n/translate";
import { IslandView } from "./IslandView";

describe("IslandView accessibility controls", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  const renderIsland = (island: Island, options: { isProtected?: boolean; safeMode?: boolean } = {}) =>
    renderToStaticMarkup(createElement(IslandView, {
      island,
      cards: [
        { id: "c1", text: "Card 1", x: 0, y: 0 },
        { id: "c2", text: "Card 2", x: 260, y: 0 },
        { id: "c3", text: "Card 3", x: 520, y: 0 },
      ],
      isSelected: false,
      onSelect: vi.fn(),
      onToggleCollapsed: vi.fn(),
      onFocusIsland: vi.fn(),
      isProtected: options.isProtected,
      safeMode: options.safeMode,
    }));

  it("renders one primary select control and keeps utility controls separately named", () => {
    const island: Island = {
      id: "island-1",
      title: "Island",
      cardIds: ["c1"],
    };

    const html = renderIsland(island);

    expect((html.match(/aria-label="島 island-1 を選択"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="島 island-1 を表示"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="島 island-1 を折りたたむ"/g) ?? []).length).toBe(1);
    expect(html).not.toContain('aria-label="島 island-1 を選択 島 island-1 を表示"');
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

    expect((html.match(/<button[^>]+aria-label="島 island-poly を選択"/g) ?? []).length).toBe(1);
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

    expect((html.match(/aria-label="島 island-collapsed を選択"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="島 island-collapsed を展開"/g) ?? []).length).toBe(1);
    expect((html.match(/aria-label="島 island-collapsed のカードを一時表示"/g) ?? []).length).toBe(1);
    expect(html).not.toContain("島 island-collapsed を選択 島 island-collapsed を表示");
    expect(html).not.toContain("島 island-collapsed を選択 島 island-collapsed を展開");
    expect(html).not.toContain("島 island-collapsed を選択 島 island-collapsed のカードを一時表示");
  });

  it("labels small island protection without scoring language", () => {
    const island: Island = {
      id: "island-small",
      title: "Small island",
      cardIds: ["c1", "c2"],
    };

    const html = renderIsland(island, { isProtected: true });

    expect(html).toContain("保護");
    expect(html).toContain('aria-label="保護"');
    expect(html).toContain("無理にまとめなくて構いません");
    expect(html).not.toContain("スコア");
    expect(html).not.toContain("順位");
    expect(html).not.toContain("比率");
  });

  it("does not mark larger islands as protected", () => {
    const island: Island = {
      id: "island-large",
      title: "Large island",
      cardIds: ["c1", "c2", "c3"],
    };

    const html = renderIsland(island);

    expect(html).not.toContain('aria-label="保護対象です。無理に分類しない島です"');
  });

  it("can label a larger island when it is the only critique target", () => {
    const island: Island = {
      id: "island-critique",
      title: "Critique island",
      cardIds: ["c1", "c2", "c3"],
      critique: "ここだけ気になる",
    };

    const html = renderIsland(island, { isProtected: true });

    expect(html).toContain("保護");
    expect(html).toContain('aria-label="保護"');
    expect(html).toContain("無理にまとめなくて構いません");
  });

  it("does not resolve a legacy island image while SafeMode is on", () => {
    const island: Island = {
      id: "island-image",
      title: "Image island",
      cardIds: ["c1"],
      imageUrl: "https://images.example.test/sensitive.png",
      imageReviewed: true,
    };

    expect(renderIsland(island, { safeMode: true })).not.toContain("images.example.test");
    expect(renderIsland(island, { safeMode: false })).toContain("images.example.test");
  });

  it("renders a representative cue beside the title as a decorative fixed-size mark", () => {
    const island: Island = {
      id: "island-cue",
      title: "Cue island",
      cardIds: ["c1"],
      representativeCue: {
        kind: "preset_svg",
        cueId: "shape-circle",
        altText: "Circle",
      },
    };

    const html = renderIsland(island, { safeMode: true });

    expect(html).toContain('data-representative-visual-cue="shape-circle"');
    expect(html).toContain('width="20" height="20"');
    expect(html).toContain('aria-hidden="true"');
    expect(html).not.toContain('aria-label="Circle"');
    expect(html).not.toContain("http");
  });
});
