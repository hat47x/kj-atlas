import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { buildEvidenceAdjacency, getEvidenceNeighborhood } from "./evidence_overlay";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    evidenceLinks: [],
  };
}

describe("evidence_overlay", () => {
  it("builds deterministic adjacency maps", () => {
    const doc = makeDoc();
    doc.evidenceLinks = [
      { id: "e3", type: "supports", fromCardId: "c", toCardId: "a" },
      { id: "e1", type: "supports", fromCardId: "a", toCardId: "b" },
      { id: "e2", type: "contradicts", fromCardId: "b", toCardId: "c" },
    ];

    const adjacency = buildEvidenceAdjacency(doc);
    expect(adjacency.outSupports.get("a")?.map((edge) => edge.id)).toEqual(["e1"]);
    expect(adjacency.inSupports.get("a")?.map((edge) => edge.id)).toEqual(["e3"]);
    expect(adjacency.outContradicts.get("b")?.map((edge) => edge.id)).toEqual(["e2"]);
  });

  it("finds neighborhood across incoming + outgoing hops", () => {
    const doc = makeDoc();
    doc.evidenceLinks = [
      { id: "s1", type: "supports", fromCardId: "a", toCardId: "b" },
      { id: "s2", type: "supports", fromCardId: "c", toCardId: "a" },
      { id: "s3", type: "supports", fromCardId: "d", toCardId: "c" },
      { id: "x1", type: "contradicts", fromCardId: "d", toCardId: "a" },
    ];

    const adjacency = buildEvidenceAdjacency(doc);
    const depth1 = getEvidenceNeighborhood("a", adjacency, "supports", 1);
    expect([...depth1.nodes].sort()).toEqual(["a", "b", "c"]);
    expect([...depth1.edges].sort()).toEqual(["s1", "s2"]);

    const depth2 = getEvidenceNeighborhood("a", adjacency, "supports", 2);
    expect([...depth2.nodes].sort()).toEqual(["a", "b", "c", "d"]);
    expect([...depth2.edges].sort()).toEqual(["s1", "s2", "s3"]);

    const both = getEvidenceNeighborhood("a", adjacency, "both", 1);
    expect([...both.edges].sort()).toEqual(["s1", "s2", "x1"]);
  });
});
