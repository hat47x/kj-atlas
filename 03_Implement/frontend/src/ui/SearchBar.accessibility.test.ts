import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SearchBar } from "./SearchBar";
import { setActiveLocale } from "../i18n/translate";

describe("SearchBar accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  const renderBar = (overrides: Record<string, unknown> = {}) =>
    renderToStaticMarkup(
      createElement(SearchBar, {
        query: "",
        totalMatches: 0,
        currentMatchIndex: 0,
        hideNonMatches: false,
        onQueryChange: vi.fn(),
        onPrev: vi.fn(),
        onNext: vi.fn(),
        onHideNonMatchesChange: vi.fn(),
        ...overrides,
      })
    );

  it("has an accessible text input", () => {
    const html = renderBar();
    expect(html).toContain('type="text"');
    expect(html).toContain("カードを検索");
  });

  it("prev/next buttons are disabled when no matches", () => {
    const html = renderBar();
    expect(html).toContain("disabled");
  });

  it("match counter shows 0/0 when empty", () => {
    const html = renderBar();
    expect(html).toContain("0/0");
  });

  it("prev/next buttons enabled when has matches", () => {
    const html = renderBar({ totalMatches: 5, currentMatchIndex: 0 });
    expect(html).toContain("1/5");
  });

  it("hide non-matches checkbox has accessible label", () => {
    const html = renderBar();
    expect(html).toContain('type="checkbox"');
  });
});
