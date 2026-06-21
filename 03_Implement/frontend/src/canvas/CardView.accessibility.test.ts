import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { CardView } from "./CardView";
import { setActiveLocale } from "../i18n/translate";

describe("CardView accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  const renderCard = (overrides: Record<string, unknown> = {}) =>
    renderToStaticMarkup(
      createElement(CardView, {
        card: {
          id: "c1",
          text: "テストカード",
          x: 0,
          y: 0,
          ...overrides,
        },
        isSelected: false,
        onMove: vi.fn(),
        onSelect: vi.fn(),
      })
    );

  it("has role option and aria-selected for screen reader", () => {
    const html = renderCard();
    expect(html).toContain('role="option"');
    expect(html).toContain('aria-selected="false"');
  });

  it("labels claim type badge with aria-label", () => {
    const html = renderCard({ claimType: "fact" });
    expect(html).toContain('aria-label="Card claim type: fact"');
  });

  it("labels critique indicator with aria-label", () => {
    const html = renderCard({ critique: "something off" });
    expect(html).toContain('aria-label="Card has critique note"');
  });

  it("labels hold state badge with aria-label", () => {
    const html = renderCard({ holdState: "held" });
    expect(html).toContain('aria-label="Card hold state: held"');
  });

  it("labels unreviewed indicator with aria-label", () => {
    const html = renderCard({ textReviewed: false });
    expect(html).toContain('aria-label="Card text is unreviewed"');
  });

  it("renders representative count badge with aria label", () => {
    const html = renderCard({ repOf: ["s1", "s2"] });
    expect(html).toContain("Rep (2)");
  });

  it("uses tabIndex 0 for keyboard focusability", () => {
    const html = renderCard();
    expect(html).toContain('tabindex="0"');
  });
});
