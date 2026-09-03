import { describe, expect, it, vi } from "vitest";

import type { DocumentV1 } from "./types";
import { createRepresentativeMerge } from "./representative_merge";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc_1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "A", x: 0, y: 0 },
      { id: "c2", text: "B", x: 20, y: 20 },
      { id: "c3", text: "C", x: 40, y: 40 },
    ],
    edges: [
      { id: "e1", fromId: "c1", toId: "c3", type: "related" },
      { id: "e2", fromId: "c3", toId: "c2", type: "negate" },
    ],
    islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
    readingOrder: [],
    narratives: [],
  };
}

describe("representative_merge", () => {
  it("keeps originals and records both representative/canonical lineage vocabularies", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000001");

    const result = createRepresentativeMerge(createDocument(), ["c2", "c1"], "Representative");

    expect(result).not.toBeNull();
    expect(result?.representativeCardId).toBe("00000000-0000-0000-0000-000000000001");
    expect(result?.mergedCardCount).toBe(2);

    const source1 = result?.nextDocument.cards.find((card) => card.id === "c1");
    const source2 = result?.nextDocument.cards.find((card) => card.id === "c2");
    const representative = result?.nextDocument.cards.find(
      (card) => card.id === "00000000-0000-0000-0000-000000000001"
    );

    expect(source1).toMatchObject({
      id: "c1",
      text: "A",
      mergedIntoCardId: "00000000-0000-0000-0000-000000000001",
      canonicalId: "00000000-0000-0000-0000-000000000001",
    });
    expect(source2).toMatchObject({
      id: "c2",
      text: "B",
      mergedIntoCardId: "00000000-0000-0000-0000-000000000001",
      canonicalId: "00000000-0000-0000-0000-000000000001",
    });
    expect(representative).toMatchObject({
      text: "Representative",
      repOf: ["c1", "c2"],
      sources: ["c1", "c2"],
      textReviewed: false,
    });
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2"]);
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")?.fromId).toBe("c1");
  });

  it("flattens prior representative lineage into sources without deleting the intermediate card", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000003");
    const document = createDocument();
    document.cards = [
      { id: "old-rep", text: "AB", x: 0, y: 0, repOf: ["a", "b"], sources: ["a", "b"] },
      { id: "c3", text: "C", x: 40, y: 40 },
      { id: "a", text: "A", x: -20, y: 0, canonicalId: "old-rep", mergedIntoCardId: "old-rep" },
      { id: "b", text: "B", x: -10, y: 0, canonicalId: "old-rep", mergedIntoCardId: "old-rep" },
    ];
    document.edges = [];
    document.islands = [];

    const result = createRepresentativeMerge(document, ["old-rep", "c3"], "ABC");

    expect(result).not.toBeNull();
    const representative = result?.nextDocument.cards.find(
      (card) => card.id === "00000000-0000-0000-0000-000000000003"
    );
    expect(representative?.repOf).toEqual(["c3", "old-rep"]);
    expect(representative?.sources).toEqual(["a", "b", "c3", "old-rep"]);
    expect(result?.nextDocument.cards.find((card) => card.id === "old-rep")?.repOf).toEqual(["a", "b"]);
    expect(result?.nextDocument.cards.find((card) => card.id === "a")?.canonicalId).toBe("old-rep");
  });

  it("propagates claimType only when every source has the same explicit value", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000004");
    const document = createDocument();
    document.cards = document.cards.map((card) =>
      card.id === "c1" || card.id === "c2" ? { ...card, claimType: "fact" as const } : card
    );

    const result = createRepresentativeMerge(document, ["c1", "c2"], "same fact");
    expect(
      result?.nextDocument.cards.find((card) => card.id === "00000000-0000-0000-0000-000000000004")?.claimType
    ).toBe("fact");

    const partlyUnclassified = createDocument();
    partlyUnclassified.cards = partlyUnclassified.cards.map((card) =>
      card.id === "c1" ? { ...card, claimType: "fact" as const } : card
    );
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000005");
    const unclassifiedResult = createRepresentativeMerge(partlyUnclassified, ["c1", "c2"], "mixed certainty");
    expect(
      unclassifiedResult?.nextDocument.cards.find((card) => card.id === "00000000-0000-0000-0000-000000000005")?.claimType
    ).toBeUndefined();
  });

  it("fails closed when a requested source disappeared instead of merging a smaller subset", () => {
    expect(createRepresentativeMerge(createDocument(), ["c1", "c2", "missing"], "Representative")).toBeNull();
  });

  it("fails closed for held, already-merged, contradictory, or differently classified sources", () => {
    const held = createDocument();
    held.cards = held.cards.map((card) => (card.id === "c1" ? { ...card, holdState: "held" as const } : card));
    expect(createRepresentativeMerge(held, ["c1", "c2"], "Representative")).toBeNull();

    const alreadyMerged = createDocument();
    alreadyMerged.cards = alreadyMerged.cards.map((card) =>
      card.id === "c1" ? { ...card, mergedIntoCardId: "existing-rep" } : card
    );
    expect(createRepresentativeMerge(alreadyMerged, ["c1", "c2"], "Representative")).toBeNull();

    const negate = createDocument();
    negate.edges.push({ id: "e-negate", fromId: "c1", toId: "c2", type: "negate" });
    expect(createRepresentativeMerge(negate, ["c1", "c2"], "Representative")).toBeNull();

    const contradicts = createDocument();
    contradicts.evidenceLinks = [
      { id: "ev1", type: "contradicts", fromCardId: "c1", toCardId: "c2", contradictionState: "unconfirmed" },
    ];
    expect(createRepresentativeMerge(contradicts, ["c1", "c2"], "Representative")).toBeNull();

    const differentClaims = createDocument();
    differentClaims.cards = differentClaims.cards.map((card) => {
      if (card.id === "c1") return { ...card, claimType: "fact" as const };
      if (card.id === "c2") return { ...card, claimType: "hypothesis" as const };
      return card;
    });
    expect(createRepresentativeMerge(differentClaims, ["c1", "c2"], "Representative")).toBeNull();
  });

  it("adds representative membership and external edge projections without destroying source provenance", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000002");
    const document = createDocument();
    document.edges.push({ id: "e-internal", fromId: "c1", toId: "c2", type: "equivalence" });

    const result = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual([
      "c1",
      "c2",
      "00000000-0000-0000-0000-000000000002",
    ]);

    // Original edges remain untouched so source-card relation provenance survives.
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")).toMatchObject({
      fromId: "c1",
      toId: "c3",
      type: "related",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")).toMatchObject({
      fromId: "c3",
      toId: "c2",
      type: "negate",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e-internal")).toMatchObject({
      fromId: "c1",
      toId: "c2",
      type: "equivalence",
    });

    expect(
      result?.nextDocument.edges.find(
        (edge) => edge.id === "representative-merge:00000000-0000-0000-0000-000000000002:e1"
      )
    ).toMatchObject({
      fromId: "00000000-0000-0000-0000-000000000002",
      toId: "c3",
      type: "related",
    });
    expect(
      result?.nextDocument.edges.find(
        (edge) => edge.id === "representative-merge:00000000-0000-0000-0000-000000000002:e2"
      )
    ).toMatchObject({
      fromId: "c3",
      toId: "00000000-0000-0000-0000-000000000002",
      type: "negate",
    });
    expect(
      result?.nextDocument.edges.some(
        (edge) =>
          edge.id.startsWith("representative-merge:")
          && edge.fromId === "00000000-0000-0000-0000-000000000002"
          && edge.toId === "00000000-0000-0000-0000-000000000002"
      )
    ).toBe(false);
  });
});
