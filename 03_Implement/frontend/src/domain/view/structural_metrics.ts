import type { DocumentV2, EdgeType, EvidenceLink } from "../types";

export type DiagramStructuralMetrics = {
  cardCount: number;
  islandCount: number;
  evidenceLinkDensity: number;
  isolatedCardsCount: number;
  islandSizeDistribution: Array<{ size: number; islands: number }>;
  contradictionRatio: number | null;
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

export function computeDiagramStructuralMetrics(doc: DocumentV2): DiagramStructuralMetrics {
  const cardCount = doc.cards.length;
  const islandCount = doc.islands.length;
  const knownCardIds = new Set(doc.cards.map((card) => card.id));

  const evidenceLinks = (doc.evidenceLinks ?? []).filter(
    (link) => knownCardIds.has(link.fromCardId) && knownCardIds.has(link.toCardId),
  );

  const incidentCardIds = new Set<string>();
  for (const link of evidenceLinks) {
    incidentCardIds.add(link.fromCardId);
    incidentCardIds.add(link.toCardId);
  }

  const isolatedCardsCount = doc.cards.reduce((count, card) => (incidentCardIds.has(card.id) ? count : count + 1), 0);

  const maxDirectedLinks = cardCount > 1 ? cardCount * (cardCount - 1) : 0;
  const evidenceLinkDensity = maxDirectedLinks === 0 ? 0 : roundTo4(evidenceLinks.length / maxDirectedLinks);

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
  const typedEdges = doc.edges.filter((edge) => {
    if (!knownCardIds.has(edge.fromId) || !knownCardIds.has(edge.toId)) {
      return false;
    }
    if (!isTypedEdgeType((edge as { type?: unknown }).type)) {
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

  const relationCount = typedEvidenceLinks.length + typedEdges.length;
  const contradictionLinks = typedEvidenceLinks.filter((link) => link.type === "contradicts").length
    + typedEdges.filter((edge) => edge.type === "negate").length;
  const contradictionRatio = relationCount > 0 ? roundTo4(contradictionLinks / relationCount) : null;

  return {
    cardCount,
    islandCount,
    evidenceLinkDensity,
    isolatedCardsCount,
    islandSizeDistribution,
    contradictionRatio,
  };
}
