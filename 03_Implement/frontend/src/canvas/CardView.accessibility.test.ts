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

  it("has role button and aria-pressed for screen reader (ADR-0052)", () => {
    const html = renderCard();
    expect(html).toContain('role="button"');
    expect(html).toContain('aria-pressed="false"');
  });

  it("strips button semantics, aria-pressed, and the tab stop from the root while editing (ADR-0052)", () => {
    const html = renderToStaticMarkup(
      createElement(CardView, {
        card: { id: "c1", text: "テストカード", x: 0, y: 0 },
        isSelected: true,
        isEditing: true,
        onMove: vi.fn(),
        onSelect: vi.fn(),
      })
    );

    expect(html).not.toContain('role="button"');
    expect(html).not.toContain("aria-pressed");
    expect(html).toContain('tabindex="-1"');
  });

  it("labels claim type badge with aria-label", () => {
    const html = renderCard({ claimType: "fact" });
    expect(html).toContain('aria-label="カードの主張種別: 事実"');
  });

  it("labels critique indicator with aria-label", () => {
    const html = renderCard({ critique: "something off" });
    expect(html).toContain('aria-label="カードに違和感メモがあります"');
  });

  it("labels hold state badge with accessible title in ja", () => {
    const html = renderCard({ holdState: "held" });
    expect(html).toContain("保留");
  });

  it("gives the labeled unreviewed indicator a valid semantic role", () => {
    const html = renderCard({ textReviewed: false });
    expect(html).toContain('role="img"');
    expect(html).toContain('aria-label="カード本文は未レビューです"');
  });

  it("renders representative count badge", () => {
    const html = renderCard({ repOf: ["s1", "s2"] });
    expect(html).toContain("代表 (2)");
  });

  it("labels protected voice badge without scoring language", () => {
    const html = renderToStaticMarkup(
      createElement(CardView, {
        card: {
          id: "c1",
          text: "孤立したカード",
          x: 0,
          y: 0,
        },
        isSelected: false,
        isProtected: true,
        onMove: vi.fn(),
        onSelect: vi.fn(),
      })
    );

    expect(html).toContain("保護");
    expect(html).toContain('aria-label="保護"');
    expect(html).toContain("無理に分類しなくて構いません");
    expect(html).not.toContain("スコア");
    expect(html).not.toContain("順位");
    expect(html).not.toContain("比率");
  });

  it("uses tabIndex 0 for keyboard focusability", () => {
    const html = renderCard();
    expect(html).toContain('tabindex="0"');
  });
});
