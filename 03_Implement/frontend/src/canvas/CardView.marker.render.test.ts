import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { CardView } from "./CardView";
import type { Card } from "../domain/types";

// UX-VISUAL-01 AC-3 (ADR-0048 D1): far-LOD markers must keep the
// needs-attention signal (unreviewed / has critique) discoverable.

const baseCard: Card = { id: "c1", text: "marker card", x: 0, y: 0 };

function renderMarker(card: Card): string {
  return renderToStaticMarkup(
    React.createElement(CardView, {
      card,
      isSelected: false,
      onMove: () => {},
      onSelect: () => {},
      markerMode: true,
    })
  );
}

describe("CardView far-LOD marker attention (UX-VISUAL-01 AC-3)", () => {
  it("renders the neutral slate dot for a reviewed card without critique", () => {
    const html = renderMarker({ ...baseCard, textReviewed: true });
    expect(html).toContain("rgba(100, 116, 139, 0.25)");
    expect(html).not.toContain("rgba(245, 158, 11, 0.45)");
  });

  it("keeps an amber dot for an unreviewed card", () => {
    const html = renderMarker({ ...baseCard, textReviewed: false });
    expect(html).toContain("rgba(245, 158, 11, 0.45)");
  });

  it("keeps an amber dot for a reviewed card that carries a critique", () => {
    const html = renderMarker({
      ...baseCard,
      textReviewed: true,
      critique: "採用前に確認が必要",
      critiqueTags: ["feels_off"],
    });
    expect(html).toContain("rgba(245, 158, 11, 0.45)");
  });
});
