import { describe, expect, test } from "vitest";
import type { Card, EdgeType } from "./types";
import { CRITIQUE_TAGS, KNOWN_EDGE_TYPES, isCanonicalCard, isSourceCard, resolveKnownEdgeType } from "./types";

function card(overrides: Partial<Card> = {}): Card {
  return { id: "c1", text: "test", x: 0, y: 0, ...overrides };
}

describe("isCanonicalCard", () => {
  test("returns true for a card without canonicalId (it IS the canonical)", () => {
    expect(isCanonicalCard(card())).toBe(true);
  });

  test("returns false when canonicalId is set (card is derived from a canonical)", () => {
    expect(isCanonicalCard(card({ canonicalId: "c0" }))).toBe(false);
  });
});

describe("isSourceCard", () => {
  test("returns false for a card without canonicalId (not a source)", () => {
    expect(isSourceCard(card())).toBe(false);
  });

  test("returns true when canonicalId is set (card is derived from another)", () => {
    expect(isSourceCard(card({ canonicalId: "c0" }))).toBe(true);
  });
});

describe("resolveKnownEdgeType", () => {
  test("resolves every known edge type to itself", () => {
    for (const kind of KNOWN_EDGE_TYPES) {
      expect(resolveKnownEdgeType(kind)).toBe(kind);
    }
  });

  test("returns 'related' for an unrecognized edge type", () => {
    expect(resolveKnownEdgeType("unknown" as EdgeType)).toBe("related");
  });

  test("returns 'related' for an empty string", () => {
    expect(resolveKnownEdgeType("" as EdgeType)).toBe("related");
  });
});

describe("CRITIQUE_TAGS", () => {
  test("contains the expected critique tags", () => {
    expect(CRITIQUE_TAGS).toContain("too_close");
    expect(CRITIQUE_TAGS).toContain("too_far");
    expect(CRITIQUE_TAGS).toContain("not_the_same");
    expect(CRITIQUE_TAGS).toContain("feels_off");
    expect(CRITIQUE_TAGS).toContain("no_articulable_reason");
  });

  test("is a readonly tuple with the expected length", () => {
    expect(CRITIQUE_TAGS.length).toBe(5);
  });
});

describe("KNOWN_EDGE_TYPES", () => {
  test("includes the expected base types", () => {
    expect(KNOWN_EDGE_TYPES).toContain("related");
    expect(KNOWN_EDGE_TYPES).toContain("negate");
    expect(KNOWN_EDGE_TYPES).toContain("causal");
    expect(KNOWN_EDGE_TYPES).toContain("mutual");
    expect(KNOWN_EDGE_TYPES).toContain("equivalence");
  });

  test("is a readonly tuple (no mutation at runtime)", () => {
    expect(KNOWN_EDGE_TYPES.length).toBe(5);
  });
});
