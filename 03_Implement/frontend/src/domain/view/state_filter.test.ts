import { describe, expect, it } from "vitest";

import type { DocumentV2 } from "../types";
import {
  collectCardIdsWithEvidence,
  createEmptyDomainStateFilter,
  isDomainStateFilterActive,
  selectCardIdsByDomainState,
  toggleDomainStateFilter,
} from "./state_filter";

function buildDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      // reviewed, has evidence, no critique
      { id: "c1", text: "reviewed+evidence", x: 0, y: 0, textReviewed: true },
      // unreviewed (default), no evidence, no critique
      { id: "c2", text: "bare", x: 0, y: 0 },
      // unreviewed, no evidence, has critique (free text)
      { id: "c3", text: "critique-text", x: 0, y: 0, critique: "something feels off" },
      // reviewed, no evidence, has critique (tags)
      { id: "c4", text: "critique-tags", x: 0, y: 0, textReviewed: true, critiqueTags: ["too_close"] },
    ],
    edges: [],
    islands: [],
    evidenceLinks: [
      { id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" },
    ],
  };
}

describe("DOMAIN-EXPR-01 state_filter", () => {
  it("empty filter is inactive and returns every card id", () => {
    const doc = buildDoc();
    const filter = createEmptyDomainStateFilter();
    expect(isDomainStateFilterActive(filter)).toBe(false);
    expect(selectCardIdsByDomainState(doc, filter)).toEqual(new Set(["c1", "c2", "c3", "c4"]));
  });

  it("collects card ids that appear on either end of an evidence link", () => {
    const doc = buildDoc();
    expect(collectCardIdsWithEvidence(doc)).toEqual(new Set(["c1", "c2"]));
  });

  it("filters unreviewed cards (textReviewed !== true)", () => {
    const doc = buildDoc();
    const filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "unreviewed");
    expect(selectCardIdsByDomainState(doc, filter)).toEqual(new Set(["c2", "c3"]));
  });

  it("filters cards with no evidence link on either end", () => {
    const doc = buildDoc();
    const filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "no_evidence");
    // c1 and c2 are on the evidence link, so only c3 and c4 have no evidence.
    expect(selectCardIdsByDomainState(doc, filter)).toEqual(new Set(["c3", "c4"]));
  });

  it("filters cards that carry a critique (free text or tags)", () => {
    const doc = buildDoc();
    const filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "has_critique");
    expect(selectCardIdsByDomainState(doc, filter)).toEqual(new Set(["c3", "c4"]));
  });

  it("combines active filters with AND semantics", () => {
    const doc = buildDoc();
    // unreviewed AND has_critique -> only c3 (c4 is reviewed)
    let filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "unreviewed");
    filter = toggleDomainStateFilter(filter, "has_critique");
    expect(selectCardIdsByDomainState(doc, filter)).toEqual(new Set(["c3"]));
  });

  it("toggling the same kind twice clears it", () => {
    let filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "unreviewed");
    expect(isDomainStateFilterActive(filter)).toBe(true);
    filter = toggleDomainStateFilter(filter, "unreviewed");
    expect(isDomainStateFilterActive(filter)).toBe(false);
  });

  it("is read-only: does not mutate the input document", () => {
    const doc = buildDoc();
    const snapshot = JSON.stringify(doc);
    const filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "no_evidence");
    selectCardIdsByDomainState(doc, filter);
    expect(JSON.stringify(doc)).toEqual(snapshot);
  });
});
