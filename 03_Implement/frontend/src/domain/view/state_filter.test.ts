import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../types";
import {
  collectCardIdsWithEvidence,
  createEmptyDomainStateFilter,
  isDomainStateFilterActive,
  selectCardIdsByDomainState,
  toggleDomainStateFilter,
} from "./state_filter";

const document: DocumentV1 = {
  version: 1,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "reviewed", x: 0, y: 0, textReviewed: true },
    { id: "c2", text: "bare", x: 0, y: 0 },
    { id: "c3", text: "critique", x: 0, y: 0, critique: "feels off" },
  ],
  edges: [],
  islands: [],
  evidenceLinks: [{ id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" }],
};

describe("domain state filter", () => {
  it("supports inactive and toggled filter states", () => {
    const empty = createEmptyDomainStateFilter();
    expect(isDomainStateFilterActive(empty)).toBe(false);
    const active = toggleDomainStateFilter(empty, "unreviewed");
    expect(isDomainStateFilterActive(active)).toBe(true);
    expect(selectCardIdsByDomainState(document, active)).toEqual(new Set(["c2", "c3"]));
  });

  it("combines filters with AND semantics", () => {
    let filter = toggleDomainStateFilter(createEmptyDomainStateFilter(), "no_evidence");
    filter = toggleDomainStateFilter(filter, "has_critique");
    expect(collectCardIdsWithEvidence(document)).toEqual(new Set(["c1", "c2"]));
    expect(selectCardIdsByDomainState(document, filter)).toEqual(new Set(["c3"]));
  });
});
