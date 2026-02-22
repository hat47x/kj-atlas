import type { DocumentV2, EdgeType, EvidenceLink } from "../types";

export type StructureMetrics = {
  cardCount: number;
  islandCount: number;
  evidenceLinkCount: number;
  evidenceLinkDensity: number;
  isolatedCardCount: number;
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
  return value === "related" || value === "negate";
}

export function computeStructureMetrics(doc: DocumentV2, _view?: { collapsedIslandIds?: string[] }): StructureMetrics {
  const cardCount = doc.cards.length;
  const islandCount = doc.islands.length;
  const knownCardIds = new Set(doc.cards.map((card) => card.id));

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

  const incidentCardIds = new Set<string>();
  for (const link of evidenceLinks) {
    incidentCardIds.add(link.fromCardId);
    incidentCardIds.add(link.toCardId);
  }
  for (const edge of cardEdgePairs) {
    incidentCardIds.add(edge.fromId);
    incidentCardIds.add(edge.toId);
  }

  const isolatedCardCount = doc.cards.reduce((count, card) => (incidentCardIds.has(card.id) ? count : count + 1), 0);

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
    islandSizeDistribution,
    contradictionRatio,
    reviewedCoverage,
  };
}

export type DiagramStructuralMetrics = StructureMetrics;

export const computeDiagramStructuralMetrics = computeStructureMetrics;
