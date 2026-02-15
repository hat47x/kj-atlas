import type { DocumentV2, Edge, EdgeType } from "./types";

export type DerivedIslandEdge = {
  id: string;
  fromId: string;
  toId: string;
  fromKind: "island";
  toKind: "island";
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
  const aggregate = new Map<
    string,
    {
      fromId: string;
      toId: string;
      type: EdgeType;
      contributingEdgeIds: string[];
      contributingCardIds: Set<string>;
    }
  >();

  for (const edge of document.edges) {
    const fromKind = edgeEndpointKind(edge, "from");
    const toKind = edgeEndpointKind(edge, "to");

    // Persisted island-to-island edges are rendered as-is. Do not duplicate them as derived edges.
    if (fromKind === "island" && toKind === "island") {
      continue;
    }

    const fromIslandIds = getIslandEndpointsForEdgeEndpoint(document, edge, "from");
    const toIslandIds = getIslandEndpointsForEdgeEndpoint(document, edge, "to");

    if (fromIslandIds.length === 0 || toIslandIds.length === 0) {
      continue;
    }

    for (const fromIslandId of fromIslandIds) {
      for (const toIslandId of toIslandIds) {
        if (fromIslandId === toIslandId) {
          continue;
        }

        const [normalizedFromId, normalizedToId] = normalizeUndirectedIslands(fromIslandId, toIslandId);
        const key = `derived-island:${normalizedFromId}|${normalizedToId}|${edge.type}`;
        const current = aggregate.get(key);

        if (current) {
          current.contributingEdgeIds.push(edge.id);
          if (fromKind === "card") {
            current.contributingCardIds.add(edge.fromId);
          }
          if (toKind === "card") {
            current.contributingCardIds.add(edge.toId);
          }
          continue;
        }

        const contributingCardIds = new Set<string>();
        if (fromKind === "card") {
          contributingCardIds.add(edge.fromId);
        }
        if (toKind === "card") {
          contributingCardIds.add(edge.toId);
        }

        aggregate.set(key, {
          fromId: normalizedFromId,
          toId: normalizedToId,
          type: edge.type,
          contributingEdgeIds: [edge.id],
          contributingCardIds,
        });
      }
    }
  }

  return Array.from(aggregate.entries())
    .map(([id, value]) => ({
      id,
      fromId: value.fromId,
      toId: value.toId,
      fromKind: "island" as const,
      toKind: "island" as const,
      type: value.type,
      isDerived: true as const,
      aggregateCount: value.contributingEdgeIds.length,
      contributingEdgeIds: value.contributingEdgeIds,
      contributingCardIds: Array.from(value.contributingCardIds),
    }))
    .sort((a, b) => a.id.localeCompare(b.id));
}
