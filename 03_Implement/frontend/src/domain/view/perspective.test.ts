import { describe, expect, it } from "vitest";

import type { DocumentV2 } from "../types";
import { computePerspectiveRendering } from "./perspective";

const baseDoc: DocumentV2 = {
  version: 2,
  id: "doc",
  createdAt: "2025-01-01T00:00:00.000Z",
  updatedAt: "2025-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c-fact", text: "fact", x: 0, y: 0, claimType: "fact" },
    { id: "c-claim", text: "claim", x: 0, y: 0, claimType: "claim" },
    { id: "c-h", text: "hyp", x: 0, y: 0, claimType: "hypothesis" },
    { id: "c-u", text: "unknown", x: 0, y: 0 },
  ],
  edges: [],
  islands: [{ id: "i-1", cardIds: ["c-claim"], summaryReviewed: false }],
  evidenceLinks: [{ id: "e-1", type: "supports", fromCardId: "c-fact", toCardId: "c-claim" }],
};

describe("computePerspectiveRendering", () => {
  it("returns strict filter set for facts mode", () => {
    const result = computePerspectiveRendering(
      baseDoc,
      { perspectiveMode: "facts", perspectiveStrictFilter: true },
      { selectedCardId: null },
    );

    expect(result.visibleCardIds ? [...result.visibleCardIds] : null).toEqual(["c-fact"]);
  });

  it("dims non-matching cards for dim mode", () => {
    const result = computePerspectiveRendering(
      baseDoc,
      { perspectiveMode: "claims", perspectiveStrictFilter: false },
      { selectedCardId: null },
    );

    expect([...result.dimCardIds]).toEqual(["c-fact", "c-h", "c-u"]);
  });

  it("enables evidence overlay and dims outside neighborhood in evidence mode", () => {
    const result = computePerspectiveRendering(
      baseDoc,
      { perspectiveMode: "evidence" },
      { selectedCardId: "c-fact" },
    );

    expect(result.overlay.evidenceEnabled).toBe(true);
    expect(result.overlay.mode).toBe("supports");
    expect(result.overlay.scope).toBe("selection");
    expect([...result.dimCardIds]).toEqual(["c-h", "c-u"]);
  });

  it("shows selection hint in evidence mode without selected card", () => {
    const result = computePerspectiveRendering(
      baseDoc,
      { perspectiveMode: "evidence" },
      { selectedCardId: null },
    );

    expect(result.notes).toContain("Select a card to explore neighborhood.");
  });

  it("highlights review targets", () => {
    const result = computePerspectiveRendering(
      baseDoc,
      { perspectiveMode: "review" },
      { selectedCardId: null },
    );

    expect([...result.highlightCardIds]).toEqual(["c-claim", "c-u"]);
  });
});
