import { describe, expect, it } from "vitest";

import { buildNarrativeGrounding } from "./grounding";
import type { DocumentV1 } from "./types";

const baseDocument: DocumentV1 = {
  version: 1,
  id: "doc-1",
  title: "Doc",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "Canonical one", x: 0, y: 0 },
    { id: "c1-src", text: "Source one", x: 10, y: 0, canonicalId: "c1" },
    { id: "c2", text: "Canonical two", x: 0, y: 10 },
  ],
  edges: [],
  islands: [
    {
      id: "i1",
      title: "Island A",
      cardIds: ["c1", "c2"],
      summaryText: "Island summary",
      summaryReviewed: false,
    },
  ],
  readingOrder: ["i1", "c1-src"],
};

describe("buildNarrativeGrounding", () => {
  it("falls back to document readingOrder and filters source cards when hidden", () => {
    const grounding = buildNarrativeGrounding(baseDocument, { hideSourceCards: true });

    expect(grounding).toHaveLength(2);
    expect(grounding[0]?.anchor).toBe("#1");
    expect(grounding[0]?.kind).toBe("island");
    expect(grounding[0]?.islandMembers?.map((item) => item.id)).toEqual(["c1", "c2"]);
    expect(grounding[0]?.islandSummaryReviewed).toBe(false);
  });

  it("uses narrative basedOnReadingOrder when provided and includes source cards when visible", () => {
    const grounding = buildNarrativeGrounding(baseDocument, {
      basedOnReadingOrder: ["i1"],
      hideSourceCards: false,
    });

    expect(grounding).toHaveLength(1);
    expect(grounding[0]?.islandMembers?.map((item) => item.id)).toEqual(["c1", "c1-src", "c2"]);
    expect(grounding[0]?.islandMembers?.[1]?.kind).toBe("source");
    expect(grounding[0]?.islandMembers?.[1]?.canonicalId).toBe("c1");
  });
});
