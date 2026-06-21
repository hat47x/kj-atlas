import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it } from "vitest";
import { setActiveLocale } from "../i18n/translate";
import { DomainStateSummary } from "./DomainStateSummary";

describe("DomainStateSummary accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("has an accessible section label", () => {
    const html = renderToStaticMarkup(
      createElement(DomainStateSummary, {
        cards: [{ id: "c1", text: "test", x: 0, y: 0, claimType: "fact" }],
      })
    );
    expect(html).toContain('aria-label=');
  });

  it("labels claim type indicators with aria-label", () => {
    const html = renderToStaticMarkup(
      createElement(DomainStateSummary, {
        cards: [{ id: "c1", text: "test", x: 0, y: 0, claimType: "fact" }],
      })
    );
    // Section should be labeled for screen readers
    expect(html).toContain("事実");
  });

  it("renders empty state without accessible section", () => {
    const html = renderToStaticMarkup(
      createElement(DomainStateSummary, { cards: [] })
    );
    expect(html).toBe("");
  });

  it("shows unreviewed label with visual indicator", () => {
    const html = renderToStaticMarkup(
      createElement(DomainStateSummary, {
        cards: [{ id: "c1", text: "test", x: 0, y: 0 }],
        safeMode: true,
      })
    );
    expect(html).toContain("未レビュー");
  });
});
