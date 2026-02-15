import type { DocumentV2, EdgeType, RelationSummary } from "./types";
import type { IslandRelationEdgeSelection } from "./island_relation_explain";

export type SummarizeIslandRelationPayload = {
  doc: DocumentV2;
  islandAId: string;
  islandBId: string;
  relationType: EdgeType | "unknown";
  derived: boolean;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  edgeTexts?: { edgeId: string; type: string; from: string; to: string }[];
  cardTexts: { id: string; text: string }[];
};

function dedupe(ids: string[]): string[] {
  return Array.from(new Set(ids));
}

function truncateStableHashInput(input: string): string {
  return input.slice(0, 96);
}

export function buildRelationSummarySourceSignature(edge: IslandRelationEdgeSelection): string {
  if (!edge.isDerived) {
    return `edge:${edge.edgeId}`;
  }

  const contributingIds = [...(edge.contributingEdgeIds ?? [])].sort((a, b) => a.localeCompare(b));
  const hashInput = truncateStableHashInput(contributingIds.join("|"));
  return `derived:${edge.fromIslandId}:${edge.toIslandId}:${edge.type}:${hashInput}`;
}

export function getGroundingCardIdsForRelationSummary(
  document: DocumentV2,
  edge: IslandRelationEdgeSelection
): string[] {
  if (edge.isDerived) {
    return dedupe(edge.contributingCardIds ?? []);
  }

  const islandA = document.islands.find((island) => island.id === edge.fromIslandId);
  const islandB = document.islands.find((island) => island.id === edge.toIslandId);
  return dedupe([...(islandA?.cardIds ?? []), ...(islandB?.cardIds ?? [])]);
}

export function buildSummarizeIslandRelationPayload(
  document: DocumentV2,
  edge: IslandRelationEdgeSelection
): SummarizeIslandRelationPayload {
  const groundingCardIds = getGroundingCardIdsForRelationSummary(document, edge);
  const groundingEdgeIds = edge.isDerived ? dedupe(edge.contributingEdgeIds ?? []) : [edge.edgeId];
  const cardsById = new Map(document.cards.map((card) => [card.id, card]));
  const edgesById = new Map(document.edges.map((entry) => [entry.id, entry]));

  const cardTexts = groundingCardIds
    .map((cardId) => cardsById.get(cardId))
    .filter((card): card is NonNullable<typeof card> => Boolean(card))
    .map((card) => ({ id: card.id, text: card.text }));

  const edgeTexts = groundingEdgeIds
    .map((edgeId) => edgesById.get(edgeId))
    .filter((entry): entry is NonNullable<typeof entry> => Boolean(entry))
    .map((entry) => ({ edgeId: entry.id, type: entry.type, from: entry.fromId, to: entry.toId }));

  return {
    doc: document,
    islandAId: edge.fromIslandId,
    islandBId: edge.toIslandId,
    relationType: edge.type,
    derived: edge.isDerived,
    groundingCardIds,
    groundingEdgeIds,
    edgeTexts: edgeTexts.length > 0 ? edgeTexts : undefined,
    cardTexts,
  };
}

export function upsertRelationSummary(document: DocumentV2, summary: RelationSummary): DocumentV2 {
  const existing = document.relationSummaries ?? [];
  const next = [...existing];
  const index = next.findIndex((item) => item.sourceSignature === summary.sourceSignature);
  if (index >= 0) {
    next[index] = summary;
  } else {
    next.push(summary);
  }

  return {
    ...document,
    relationSummaries: next,
  };
}

export function getRelationSummaryBySourceSignature(
  document: DocumentV2,
  sourceSignature: string
): RelationSummary | null {
  return document.relationSummaries?.find((item) => item.sourceSignature === sourceSignature) ?? null;
}

// Manual test checklist:
// 1) Select an island-to-island edge (persisted or derived), click "Generate AI relation summary", and verify summary text appears.
// 2) Confirm the draft is labeled unreviewed and reviewed=false is persisted.
// 3) Confirm warnings are shown when returned by API.
// 4) Save and reload document; relation summary remains visible for the same edge sourceSignature.
// 5) Undo/redo after generating summary and after editing summary text; state toggles correctly.
