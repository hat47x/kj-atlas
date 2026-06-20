const FIXED_TIMESTAMP = "2026-06-04T00:00:00.000Z";

export function buildFirstMeaningfulMapDocument(
  cardTexts = ["first value user problem", "first value observation memo", "first value decision anchor"],
) {
  return {
    version: 2,
    id: "doc_first_meaningful_map_mouse",
    title: "First meaningful map mouse fixture",
    createdAt: FIXED_TIMESTAMP,
    updatedAt: FIXED_TIMESTAMP,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `mouse-value-card-${index + 1}`,
      text,
      x: 140 + index * 270,
      y: 150 + (index % 2) * 150,
      textReviewed: index === 0,
    })),
    edges: [],
    islands: [],
    readingOrder: cardTexts.map((_, index) => `mouse-value-card-${index + 1}`),
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

export function buildDomainExpressionDocument() {
  return {
    version: 2,
    id: "doc_domain_expression_keyboard_access",
    title: "domain expression keyboard access fixture",
    createdAt: FIXED_TIMESTAMP,
    updatedAt: FIXED_TIMESTAMP,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "domain-target",
        text: "ambiguous target claim",
        x: 140,
        y: 130,
        claimType: "unknown",
        textReviewed: false,
        critique: "needs review before acceptance",
        critiqueTags: ["unclear_boundary"],
      },
      {
        id: "domain-support",
        text: "supporting field note",
        x: 430,
        y: 130,
        claimType: "fact",
        textReviewed: true,
      },
      {
        id: "domain-counter",
        text: "contradicting stakeholder signal",
        x: 430,
        y: 290,
        claimType: "claim",
        textReviewed: false,
      },
    ],
    edges: [],
    islands: [
      {
        id: "domain-island",
        title: "unresolved review cluster",
        cardIds: ["domain-target", "domain-support", "domain-counter"],
      },
    ],
    readingOrder: ["domain-target", "domain-support", "domain-counter"],
    evidenceLinks: [
      {
        id: "domain-support-link",
        type: "supports",
        fromCardId: "domain-support",
        toCardId: "domain-target",
        createdAt: FIXED_TIMESTAMP,
      },
      {
        id: "domain-counter-link",
        type: "contradicts",
        fromCardId: "domain-counter",
        toCardId: "domain-target",
        createdAt: FIXED_TIMESTAMP,
      },
    ],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

export function buildReviewPackTraceDocument() {
  return {
    version: 2,
    id: "doc_review_pack_trace_export",
    title: "review pack trace export fixture",
    createdAt: FIXED_TIMESTAMP,
    updatedAt: FIXED_TIMESTAMP,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-target", text: "trace target claim", x: 140, y: 130, claimType: "claim", textReviewed: true },
      { id: "c-support", text: "supporting field note", x: 430, y: 130, claimType: "fact", textReviewed: true },
      { id: "c-counter", text: "contradicting stakeholder signal", x: 430, y: 290, claimType: "claim", textReviewed: false },
    ],
    edges: [],
    islands: [
      {
        id: "i-review",
        title: "reviewable trace package",
        cardIds: ["c-target", "c-support", "c-counter"],
      },
    ],
    readingOrder: ["c-target", "c-support", "c-counter"],
    evidenceLinks: [
      { id: "e-support", type: "supports", fromCardId: "c-support", toCardId: "c-target", createdAt: FIXED_TIMESTAMP },
      { id: "e-counter", type: "contradicts", fromCardId: "c-counter", toCardId: "c-target", createdAt: FIXED_TIMESTAMP },
    ],
    narratives: [],
    mergeSuggestionDecisions: [],
  };
}

export function withoutProductValueContent<
  T extends { cards: unknown[]; islands: unknown[]; evidenceLinks: unknown[]; readingOrder: unknown[] },
>(document: T): T {
  return {
    ...document,
    cards: [],
    islands: [],
    evidenceLinks: [],
    readingOrder: [],
  };
}
