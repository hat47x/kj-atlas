import type { DocumentV1, EdgeType, KnownEdgeType } from "./types";
import { resolveKnownEdgeType } from "./types";

export type IslandRelationEdgeSelection = {
  edgeId: string;
  fromIslandId: string;
  toIslandId: string;
  type: EdgeType;
  isDerived: boolean;
  contributingEdgeIds?: string[];
  contributingCardIds?: string[];
};

export type IslandRelationExplanation = {
  title: string;
  body: string;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
};

const EDGE_TYPE_LABELS: Record<KnownEdgeType, string> = {
  related: "RELATED",
  negate: "NEGATE",
  causal: "CAUSAL",
  mutual: "MUTUAL",
  equivalence: "EQUIVALENCE",
};

function edgeTypeLabel(type: EdgeType): string {
  // DOMAIN-KJ-01: unknown preserved types resolve to "related" for display.
  return EDGE_TYPE_LABELS[resolveKnownEdgeType(type)];
}

function uniqueSortedIds(ids: Iterable<string>): string[] {
  return Array.from(new Set(ids)).sort((a, b) => a.localeCompare(b));
}

function sortCardIdsDeterministically(document: DocumentV1, cardIds: string[]): string[] {
  const uniqueIds = Array.from(new Set(cardIds));
  const readingOrder = document.readingOrder ?? [];
  if (readingOrder.length === 0) {
    return uniqueIds.sort((a, b) => a.localeCompare(b));
  }

  const readingOrderIndexById = new Map<string, number>();
  for (let index = 0; index < readingOrder.length; index += 1) {
    readingOrderIndexById.set(readingOrder[index], index);
  }

  return uniqueIds.sort((a, b) => {
    const aIndex = readingOrderIndexById.get(a);
    const bIndex = readingOrderIndexById.get(b);

    if (aIndex !== undefined && bIndex !== undefined) {
      return aIndex - bIndex || a.localeCompare(b);
    }

    if (aIndex !== undefined) {
      return -1;
    }

    if (bIndex !== undefined) {
      return 1;
    }

    return a.localeCompare(b);
  });
}

function getIslandLabel(document: DocumentV1, islandId: string): string {
  const island = document.islands.find((entry) => entry.id === islandId);
  return island?.title?.trim() || islandId;
}

function getCardSnippet(document: DocumentV1, cardId: string): string {
  const card = document.cards.find((entry) => entry.id === cardId);
  if (!card) {
    return `${cardId} (missing card)`;
  }

  const normalized = card.text.replace(/\s+/g, " ").trim();
  if (normalized.length === 0) {
    return `${card.id}: (empty text)`;
  }

  const preview = normalized.length > 120 ? `${normalized.slice(0, 117)}...` : normalized;
  return `${card.id}: ${preview}`;
}

export function buildIslandRelationExplanation(
  document: DocumentV1,
  edgeSelection: IslandRelationEdgeSelection
): IslandRelationExplanation {
  const title = `Relation: ${getIslandLabel(document, edgeSelection.fromIslandId)} ↔ ${getIslandLabel(document, edgeSelection.toIslandId)}`;

  const groundingEdgeIds = edgeSelection.isDerived
    ? uniqueSortedIds(edgeSelection.contributingEdgeIds ?? [])
    : [edgeSelection.edgeId];

  const groundingCardCandidates = edgeSelection.contributingCardIds ?? [];

  const sortedGroundingCardIds = sortCardIdsDeterministically(document, groundingCardCandidates);
  const groundingCardIds = edgeSelection.isDerived ? sortedGroundingCardIds.slice(0, 10) : sortedGroundingCardIds;

  const bodyLines: string[] = [`Type: ${edgeTypeLabel(edgeSelection.type)}`];

  if (edgeSelection.isDerived) {
    bodyLines.push(`This relation is derived from ${groundingEdgeIds.length} underlying links.`);
  }

  bodyLines.push("Grounding cards:");
  if (groundingCardIds.length === 0) {
    bodyLines.push("- (none)");
  } else {
    for (const cardId of groundingCardIds) {
      bodyLines.push(`- ${getCardSnippet(document, cardId)}`);
    }
  }

  return {
    title,
    body: bodyLines.join("\n"),
    groundingCardIds,
    groundingEdgeIds,
  };
}

export function formatIslandRelationExplanationMarkdown(explanation: IslandRelationExplanation): string {
  const markdownLines = [
    `## ${explanation.title}`,
    "",
    explanation.body,
    "",
    `Grounding edge IDs: ${explanation.groundingEdgeIds.length === 0 ? "(none)" : explanation.groundingEdgeIds.join(", ")}`,
    `Grounding card IDs: ${explanation.groundingCardIds.length === 0 ? "(none)" : explanation.groundingCardIds.join(", ")}`,
  ];

  return markdownLines.join("\n");
}
