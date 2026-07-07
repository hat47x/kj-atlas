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

  it("labels unreviewed indicator with aria-label", () => {
    const html = renderCard({ textReviewed: false });
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
        isProtectedVoice: true,
        onMove: vi.fn(),
        onSelect: vi.fn(),
      })
    );

    expect(html).toContain("保護");
    expect(html).toContain('aria-label="保護対象です。無理に分類しないカードです"');
    expect(html).not.toContain("スコア");
    expect(html).not.toContain("順位");
    expect(html).not.toContain("比率");
  });

  it("uses tabIndex 0 for keyboard focusability", () => {
    const html = renderCard();
    expect(html).toContain('tabindex="0"');
  });
});
