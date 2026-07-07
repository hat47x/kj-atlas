import type { DocumentV2, Edge, EdgeType } from "./types";

export type DerivedIslandEdge = {
  id: string;
  fromId: string;
  toId: string;
  fromKind: "island";
  // "card" here always means a lone-wolf card (belongs to zero islands) —
  // ADR-0048 D2, Round 5: relations to a still-visible remaining card are
  // promoted to the island's placard, distinct from island-island promotion.
  toKind: "island" | "card";
  type: EdgeType;
  isDerived: true;
  aggregateCount: number;
  contributingEdgeIds: string[];
  contributingCardIds: string[];
};

function normalizeUndirectedIslands(a: string, b: string): [string, string] {
  return a <= b ? [a, b] : [b, a];
}

function edgeEndpointKind(edge: Edge, endpoint: "from" | "to"): "card" | "island" {
  const rawKind = endpoint === "from" ? edge.fromKind : edge.toKind;
  return rawKind === "island" ? "island" : "card";
}

function getIslandEndpointsForEdgeEndpoint(document: DocumentV2, edge: Edge, endpoint: "from" | "to"): string[] {
  const endpointId = endpoint === "from" ? edge.fromId : edge.toId;
  const kind = edgeEndpointKind(edge, endpoint);
  if (kind === "island") {
    return [endpointId];
  }

  return getIslandsForCard(document, endpointId);
}

export function getIslandsForCard(document: DocumentV2, cardId: string): string[] {
  const islandIds: string[] = [];

  for (const island of document.islands) {
    if (island.cardIds.includes(cardId)) {
      islandIds.push(island.id);
    }
  }

  return islandIds;
}

export function getDerivedIslandEdges(document: DocumentV2): DerivedIslandEdge[] {
  const realCardIdSet = new Set(document.cards.map((card) => card.id));
  const aggregate = new Map<
    string,
    {
      fromId: string;
      toId: string;
      toKind: "island" | "card";
      type: EdgeType;
      contributingEdgeIds: string[];
      contributingCardIds: Set<string>;
    }
  >();

  const addContribution = (key: string, fromId: string, toId: string, toKind: "island" | "card", edge: Edge, fromKind: "card" | "island", edgeToKind: "card" | "island") => {
    const current = aggregate.get(key);
    if (current) {
      current.contributingEdgeIds.push(edge.id);
      if (fromKind === "card") {
        current.contributingCardIds.add(edge.fromId);
      }
      if (edgeToKind === "card") {
        current.contributingCardIds.add(edge.toId);
      }
      return;
    }

    const contributingCardIds = new Set<string>();
    if (fromKind === "card") {
      contributingCardIds.add(edge.fromId);
    }
    if (edgeToKind === "card") {
      contributingCardIds.add(edge.toId);
    }

    aggregate.set(key, { fromId, toId, toKind, type: edge.type, contributingEdgeIds: [edge.id], contributingCardIds });
  };

  for (const edge of document.edges) {
    const fromKind = edgeEndpointKind(edge, "from");
    const toKind = edgeEndpointKind(edge, "to");

    // Persisted island-to-island edges are rendered as-is. Do not duplicate them as derived edges.
    if (fromKind === "island" && toKind === "island") {
      continue;
    }

    const fromIslandIds = getIslandEndpointsForEdgeEndpoint(document, edge, "from");
    const toIslandIds = getIslandEndpointsForEdgeEndpoint(document, edge, "to");

    if (fromIslandIds.length === 0 && toIslandIds.length === 0) {
      // Neither endpoint belongs to any island (lone wolf <-> lone wolf, or
      // a persisted card-card edge with no island involvement at all) — out
      // of scope for island-relation escalation; unaffected by this rule.
      continue;
    }

    if (fromIslandIds.length > 0 && toIslandIds.length > 0) {
      // Both endpoints resolve to island(s): existing island<->island
      // promotion, same-island pairs internalized (silently dropped).
      for (const fromIslandId of fromIslandIds) {
        for (const toIslandId of toIslandIds) {
          if (fromIslandId === toIslandId) {
            continue;
          }
          const [normalizedFromId, normalizedToId] = normalizeUndirectedIslands(fromIslandId, toIslandId);
          const key = `derived-island:${normalizedFromId}|${normalizedToId}|${edge.type}`;
          addContribution(key, normalizedFromId, normalizedToId, "island", edge, fromKind, toKind);
        }
      }
      continue;
    }

    // Exactly one side resolves to island(s); the other is a lone-wolf card
    // (still visible at far LOD per lodShowLoneWolvesWhenFar) — promote to
    // island-placard <-> card, matching ADR-0048 D2's "残存カードへの関係=
    // 表札へ昇格" rule. Guard against dangling/malformed references (an
    // endpoint id that isn't a real card at all): those are simply dropped,
    // same as before this change, rather than promoted to a bogus card.
    const islandIds = fromIslandIds.length > 0 ? fromIslandIds : toIslandIds;
    const loneWolfCardId = fromIslandIds.length > 0 ? edge.toId : edge.fromId;
    if (!realCardIdSet.has(loneWolfCardId)) {
      continue;
    }
    for (const islandId of islandIds) {
      const key = `derived-card:${islandId}|${loneWolfCardId}|${edge.type}`;
      addContribution(key, islandId, loneWolfCardId, "card", edge, fromKind, toKind);
    }
  }

  return Array.from(aggregate.entries())
    .map(([id, value]) => ({
      id,
      fromId: value.fromId,
      toId: value.toId,
      fromKind: "island" as const,
      toKind: value.toKind,
      type: value.type,
      isDerived: true as const,
      aggregateCount: value.contributingEdgeIds.length,
      contributingEdgeIds: value.contributingEdgeIds,
      contributingCardIds: Array.from(value.contributingCardIds),
    }))
    .sort((a, b) => a.id.localeCompare(b.id));
}
