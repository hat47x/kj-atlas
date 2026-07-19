import type { DocumentV1, EdgeType, EvidenceLink } from "../types";
import { KNOWN_EDGE_TYPES } from "../types";

export type StructureMetrics = {
  cardCount: number;
  islandCount: number;
  evidenceLinkCount: number;
  evidenceLinkDensity: number;
  isolatedCardCount: number;
  isolationRate: number;
  connectedComponentCount: number;
  largestComponentRatio: number;
  connectivityScore: number;
  averageDegree: number;
  degreeP95: number;
  degreeSkewRatio: number;
  bridgeEdgeCount: number;
  islandSizeDistribution: Array<{ size: number; islands: number }>;
  contradictionRatio: number | null;
  reviewedCoverage: number | null;
};

function isTypedEvidenceLinkType(value: unknown): value is EvidenceLink["type"] {
  return value === "supports" || value === "contradicts";
}

function roundTo4(value: number): number {
  return Math.round(value * 10_000) / 10_000;
}


function isTypedEdgeType(value: unknown): value is EdgeType {
  // DOMAIN-KJ-01: all five known relation types count as "typed"; a
  // preserved UNKNOWN type string does not (its vocabulary is not
  // understood, so it cannot contribute to type-based metrics).
  return typeof value === "string" && (KNOWN_EDGE_TYPES as readonly string[]).includes(value);
}

type CardPair = { fromId: string; toId: string };

function toUndirectedPairKey(left: string, right: string): string {
  return left <= right ? `${left}\u0000${right}` : `${right}\u0000${left}`;
}

function buildUniqueUndirectedPairs(pairs: CardPair[]): CardPair[] {
  const seen = new Set<string>();
  const uniquePairs: CardPair[] = [];
  for (const pair of pairs) {
    if (pair.fromId === pair.toId) {
      continue;
    }
    const key = toUndirectedPairKey(pair.fromId, pair.toId);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    uniquePairs.push(pair.fromId <= pair.toId ? pair : { fromId: pair.toId, toId: pair.fromId });
  }
  return uniquePairs.sort((left, right) => {
    const byFrom = left.fromId.localeCompare(right.fromId);
    if (byFrom !== 0) {
      return byFrom;
    }
    return left.toId.localeCompare(right.toId);
  });
}

function percentile95(values: number[]): number {
  if (values.length === 0) {
    return 0;
  }
  const sorted = [...values].sort((left, right) => left - right);
  const rank = Math.max(0, Math.ceil(sorted.length * 0.95) - 1);
  return sorted[Math.min(rank, sorted.length - 1)] ?? 0;
}

function buildGraph(cardIds: string[], undirectedPairs: CardPair[]): Map<string, Set<string>> {
  const adjacency = new Map<string, Set<string>>();
  for (const cardId of cardIds) {
    adjacency.set(cardId, new Set<string>());
  }
  for (const pair of undirectedPairs) {
    const from = adjacency.get(pair.fromId);
    const to = adjacency.get(pair.toId);
    if (!from || !to) {
      continue;
    }
    from.add(pair.toId);
    to.add(pair.fromId);
  }
  return adjacency;
}

function countConnectedComponents(cardIds: string[], adjacency: Map<string, Set<string>>): { count: number; largestSize: number } {
  const visited = new Set<string>();
  let componentCount = 0;
  let largestSize = 0;

  for (const cardId of cardIds) {
    if (visited.has(cardId)) {
      continue;
    }
    componentCount += 1;
    const queue = [cardId];
    visited.add(cardId);
    let queueIndex = 0;
    let size = 0;
    while (queueIndex < queue.length) {
      const current = queue[queueIndex];
      queueIndex += 1;
      if (!current) {
        continue;
      }
      size += 1;
      const neighbors = adjacency.get(current);
      if (!neighbors) {
        continue;
      }
      for (const neighbor of neighbors) {
        if (visited.has(neighbor)) {
          continue;
        }
        visited.add(neighbor);
        queue.push(neighbor);
      }
    }
    if (size > largestSize) {
      largestSize = size;
    }
  }

  return { count: componentCount, largestSize };
}

function countBridgeEdges(cardIds: string[], adjacency: Map<string, Set<string>>): number {
  let time = 0;
  const visited = new Set<string>();
  const discovery = new Map<string, number>();
  const low = new Map<string, number>();
  let bridgeCount = 0;

  const visit = (node: string, parent: string | null): void => {
    visited.add(node);
    time += 1;
    discovery.set(node, time);
    low.set(node, time);

    const neighbors = [...(adjacency.get(node) ?? [])].sort((left, right) => left.localeCompare(right));
    for (const neighbor of neighbors) {
      if (neighbor === parent) {
        continue;
      }
      if (!visited.has(neighbor)) {
        visit(neighbor, node);
        const nodeLow = low.get(node) ?? Number.POSITIVE_INFINITY;
        const neighborLow = low.get(neighbor) ?? Number.POSITIVE_INFINITY;
        low.set(node, Math.min(nodeLow, neighborLow));
        const discoveredNode = discovery.get(node) ?? Number.POSITIVE_INFINITY;
        if (neighborLow > discoveredNode) {
          bridgeCount += 1;
        }
      } else {
        const nodeLow = low.get(node) ?? Number.POSITIVE_INFINITY;
        const discoveredNeighbor = discovery.get(neighbor) ?? Number.POSITIVE_INFINITY;
        low.set(node, Math.min(nodeLow, discoveredNeighbor));
      }
    }
  };

  for (const cardId of cardIds) {
    if (!visited.has(cardId)) {
      visit(cardId, null);
    }
  }

  return bridgeCount;
}

export function computeStructureMetrics(doc: DocumentV1, _view?: { collapsedIslandIds?: string[] }): StructureMetrics {
  const cardCount = doc.cards.length;
  const islandCount = doc.islands.length;
  const allCardIds = doc.cards.map((card) => card.id);
  const knownCardIds = new Set(allCardIds);

  const evidenceLinks = (doc.evidenceLinks ?? []).filter(
    (link) => knownCardIds.has(link.fromCardId) && knownCardIds.has(link.toCardId),
  );

  const evidenceLinkCount = evidenceLinks.length;

  const cardEdgePairs = doc.edges.filter((edge) => {
    if (!knownCardIds.has(edge.fromId) || !knownCardIds.has(edge.toId)) {
      return false;
    }
    if (edge.fromKind !== undefined && edge.fromKind !== "card") {
      return false;
    }
    if (edge.toKind !== undefined && edge.toKind !== "card") {
      return false;
    }
    return true;
  });

  const normalizedPairs = buildUniqueUndirectedPairs([
    ...evidenceLinks.map((link) => ({ fromId: link.fromCardId, toId: link.toCardId })),
    ...cardEdgePairs.map((edge) => ({ fromId: edge.fromId, toId: edge.toId })),
  ]);
  const graph = buildGraph(allCardIds, normalizedPairs);

  const isolatedCardCount = allCardIds.reduce(
    (count, cardId) => ((graph.get(cardId)?.size ?? 0) === 0 ? count + 1 : count),
    0,
  );
  const isolationRate = roundTo4(isolatedCardCount / Math.max(1, cardCount));

  const { count: connectedComponentCount, largestSize } = countConnectedComponents(allCardIds, graph);
  const largestComponentRatio = roundTo4(largestSize / Math.max(1, cardCount));
  const connectivityScore = roundTo4(1 - (Math.max(0, connectedComponentCount - 1) / Math.max(1, cardCount - 1)));
  const degreeP95 = percentile95(allCardIds.map((cardId) => graph.get(cardId)?.size ?? 0));
  const rawAverageDegree = cardCount > 0 ? (normalizedPairs.length * 2) / cardCount : 0;
  const averageDegree = roundTo4(rawAverageDegree);
  const degreeSkewRatio = roundTo4(degreeP95 / Math.max(1, rawAverageDegree));
  const bridgeEdgeCount = countBridgeEdges(allCardIds, graph);

  const evidenceLinkDensity = roundTo4(evidenceLinkCount / Math.max(1, cardCount));

  const islandSizeCounter = new Map<number, number>();
  for (const island of doc.islands) {
    const uniqueValidCardIds = new Set(island.cardIds.filter((cardId) => knownCardIds.has(cardId)));
    const size = uniqueValidCardIds.size;
    islandSizeCounter.set(size, (islandSizeCounter.get(size) ?? 0) + 1);
  }

  const islandSizeDistribution = [...islandSizeCounter.entries()]
    .map(([size, islands]) => ({ size, islands }))
    .sort((left, right) => left.size - right.size);

  const typedEvidenceLinks = evidenceLinks.filter((link) => isTypedEvidenceLinkType((link as { type?: unknown }).type));
  const typedEdges = cardEdgePairs.filter((edge) => {
    if (!isTypedEdgeType((edge as { type?: unknown }).type)) {
      return false;
    }
    return true;
  });

  const relationCount = typedEvidenceLinks.length + typedEdges.length;
  const contradictionLinks = typedEvidenceLinks.filter((link) => link.type === "contradicts").length
    + typedEdges.filter((edge) => edge.type === "negate").length;
  const contradictionRatio = relationCount > 0 ? roundTo4(contradictionLinks / relationCount) : null;

  const hasReviewedFlag = doc.cards.some((card) => typeof card.textReviewed === "boolean");
  const reviewedCount = doc.cards.filter((card) => card.textReviewed === true).length;
  const reviewedCoverage = hasReviewedFlag ? roundTo4(reviewedCount / Math.max(1, cardCount)) : null;

  return {
    cardCount,
    islandCount,
    evidenceLinkCount,
    evidenceLinkDensity,
    isolatedCardCount,
    isolationRate,
    connectedComponentCount,
    largestComponentRatio,
    connectivityScore,
    averageDegree,
    degreeP95,
    degreeSkewRatio,
    bridgeEdgeCount,
    islandSizeDistribution,
    contradictionRatio,
    reviewedCoverage,
  };
}

export type DiagramStructuralMetrics = StructureMetrics;
