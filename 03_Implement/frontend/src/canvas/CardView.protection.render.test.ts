import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { CardView } from "./CardView";
import type { Card } from "../domain/types";
import { setActiveLocale } from "../i18n/translate";

// UX-VISUAL-02 (ADR-0048 D3): a lone-wolf card carries a deterministic,
// non-scoring "protection" mark. Neutral slate (amber reserved for hold/critique).

const baseCard: Card = { id: "c1", text: "lone wolf card", x: 0, y: 0 };

function render(card: Card, isProtected: boolean): string {
  return renderToStaticMarkup(
    React.createElement(CardView, {
      card,
      isSelected: false,
      onMove: () => {},
      onSelect: () => {},
      isProtected,
    })
  );
}

describe("CardView protection mark (UX-VISUAL-02)", () => {
  it("renders the protection pill when isProtected is true", () => {
    setActiveLocale("en");
    const html = render(baseCard, true);
    expect(html).toContain("Protected");
    // Neutral slate, not amber (amber #f59e0b is reserved for hold/critique).
    expect(html).toContain("#f8fafc");
  });

  it("does not render the protection pill when isProtected is false", () => {
    setActiveLocale("en");
    const html = render(baseCard, false);
    expect(html).not.toContain("Protected");
    // No meta-row at all for a bare card.
    expect(html).not.toContain("data-card-meta-row");
  });

  it("never emits scoring vocabulary (rank/score/percent) for the mark", () => {
    setActiveLocale("en");
    // textReviewed: true avoids the unrelated unreviewed dot (whose CSS uses "50%").
    const html = render({ ...baseCard, claimType: "claim", textReviewed: true }, true);
    expect(html).toContain("Protected");
    expect(html).not.toMatch(/\brank\b|\bscore\b|\bpercent\b/i);
  });
});
