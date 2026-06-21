import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { DomainStateSummary } from "./DomainStateSummary";
import { setActiveLocale } from "../i18n/translate";
import type { Card } from "../domain/types";

function makeCard(overrides: Partial<Card> = {}): Card {
  return { id: "c1", text: "test", x: 0, y: 0, ...overrides };
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("DomainStateSummary", () => {
  it("renders nothing when cards array is empty", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards: [] }));
    expect(html).toBe("");
  });

  it("shows total card count", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard(), makeCard(), makeCard()];
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards }));
    expect(html).toContain("(3)");
  });

  it("shows claim type counts when present", () => {
    setActiveLocale("en");
    const cards: Card[] = [
      makeCard({ id: "f1", claimType: "fact" }),
      makeCard({ id: "f2", claimType: "fact" }),
      makeCard({ id: "h1", claimType: "hypothesis" }),
      makeCard({ id: "u1" }),
    ];
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards }));
    expect(html).toContain("Fact");
    expect(html).toContain("Hyp");
  });

  it("shows unreviewed count", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "a", textReviewed: true }), makeCard({ id: "b" }), makeCard({ id: "c" })];
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards }));
    expect(html).toContain("Unreviewed");
  });

  it("shows critique count", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "a", critique: "something feels off" }), makeCard({ id: "b" })];
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards }));
    expect(html).toContain("Critique");
  });

  it("shows share readiness when safeMode ON with unreviewed items", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "a" }), makeCard({ id: "b" })];
    const html = renderToStaticMarkup(React.createElement(DomainStateSummary, { cards, safeMode: true }));
    expect(html).toContain("hidden when sharing");
  });
});
