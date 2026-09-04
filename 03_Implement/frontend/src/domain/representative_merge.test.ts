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
    const REP = "00000000-0000-0000-0000-000000000002";
    vi.spyOn(crypto, "randomUUID").mockReturnValue(REP);
    const document = createDocument();
    document.edges.push({ id: "e-internal", fromId: "c1", toId: "c2", type: "equivalence" });

    const result = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    // AC: 統合元カードの島所属が残った上で、代表カードが同じ島へ追加される。
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2", REP]);

    // AC: 既存edgeのID・端点・typeがそのまま残る（統合元カードと非統合カード間、統合元カード同士とも）。
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")).toEqual({
      id: "e1",
      fromId: "c1",
      toId: "c3",
      type: "related",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")).toEqual({
      id: "e2",
      fromId: "c3",
      toId: "c2",
      type: "negate",
    });
    // AC: 統合元カード同士のedgeは元edgeだけを保持し、代表カードの自己ループを生成しない。
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e-internal")).toEqual({
      id: "e-internal",
      fromId: "c1",
      toId: "c2",
      type: "equivalence",
    });

    // AC: 統合元カードと外部カードを結ぶ関係は、代表カード側の投影edgeとしても利用できる。
    expect(
      result?.nextDocument.edges.find((edge) => edge.id === `representative-merge:${REP}:from:card:c3:related`)
    ).toMatchObject({
      fromId: REP,
      toId: "c3",
      type: "related",
    });
    expect(
      result?.nextDocument.edges.find((edge) => edge.id === `representative-merge:${REP}:to:card:c3:negate`)
    ).toMatchObject({
      fromId: "c3",
      toId: REP,
      type: "negate",
    });

    // Exactly two projected edges: the internal c1-c2 edge produced none.
    const projected = result?.nextDocument.edges.filter((edge) => edge.id.startsWith("representative-merge:"));
    expect(projected).toHaveLength(2);
    expect(projected?.some((edge) => edge.fromId === REP && edge.toId === REP)).toBe(false);
  });

  it("再配線なしでは島所属・edgeを一切変更しない (no-rewire path is provably unchanged)", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000006");
    const document = createDocument();

    const withoutOption = createRepresentativeMerge(document, ["c1", "c2"], "Representative");
    const withExplicitFalse = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: false,
    });

    for (const result of [withoutOption, withExplicitFalse]) {
      expect(result).not.toBeNull();
      // Same array reference: nextIslands/nextEdges fall through to the
      // original document arrays untouched, not a rebuilt equivalent copy.
      expect(result?.nextDocument.islands).toBe(document.islands);
      expect(result?.nextDocument.edges).toBe(document.edges);
      expect(result?.nextDocument.islands).toEqual([{ id: "i1", cardIds: ["c1", "c2"] }]);
      expect(result?.nextDocument.edges).toEqual([
        { id: "e1", fromId: "c1", toId: "c3", type: "related" },
        { id: "e2", fromId: "c3", toId: "c2", type: "negate" },
      ]);
    }
  });

  it("dedupes projected edges that share the same (representative, other card, type) triple", () => {
    const REP = "00000000-0000-0000-0000-000000000007";
    vi.spyOn(crypto, "randomUUID").mockReturnValue(REP);
    const document = createDocument();
    // Two independent source→external edges of the same type, from different
    // merged-away source cards, both pointing at the same external card.
    document.edges = [
      { id: "e1", fromId: "c1", toId: "c3", type: "related" },
      { id: "e2", fromId: "c2", toId: "c3", type: "related" },
    ];

    const result = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    // Both original edges are preserved individually...
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")).toEqual({
      id: "e1",
      fromId: "c1",
      toId: "c3",
      type: "related",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")).toEqual({
      id: "e2",
      fromId: "c2",
      toId: "c3",
      type: "related",
    });
    // ...but they collapse into exactly one projected edge, not two.
    const projected = result?.nextDocument.edges.filter((edge) => edge.id.startsWith("representative-merge:"));
    expect(projected).toHaveLength(1);
    expect(projected?.[0]).toMatchObject({
      id: `representative-merge:${REP}:from:card:c3:related`,
      fromId: REP,
      toId: "c3",
      type: "related",
    });
  });

  it("adds the representative card to every island a source card belonged to", () => {
    const REP = "00000000-0000-0000-0000-000000000008";
    vi.spyOn(crypto, "randomUUID").mockReturnValue(REP);
    const document = createDocument();
    document.islands = [
      { id: "i1", cardIds: ["c1", "c2"] },
      { id: "i2", cardIds: ["c1", "c3"] },
      { id: "i3", cardIds: ["c3"] },
    ];

    const result = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    expect(result?.nextDocument.islands).toEqual([
      { id: "i1", cardIds: ["c1", "c2", REP] },
      { id: "i2", cardIds: ["c1", "c3", REP] },
      { id: "i3", cardIds: ["c3"] },
    ]);
  });
});
