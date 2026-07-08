import type { DocumentV2, EdgeType, KnownEdgeType, RelationSummary, RelationSummaryHistoryEntry } from "./types";
import { KNOWN_EDGE_TYPES } from "./types";
import type { IslandRelationEdgeSelection } from "./island_relation_explain";

export type SummarizeIslandRelationPayload = {
  doc: DocumentV2;
  islandAId: string;
  islandBId: string;
  relationType: KnownEdgeType | "unknown";
  derived: boolean;
  groundingCardIds: string[];
  groundingEdgeIds: string[];
  edgeTexts?: { edgeId: string; type: string; from: string; to: string }[];
  cardTexts: { id: string; text: string }[];
};

// DOMAIN-KJ-01: relation summaries record an UNKNOWN preserved edge type as
// "unknown" (honest, since the vocabulary is not understood) rather than the
// display-time "related" fallback used for rendering.
export function normalizeRelationType(type: EdgeType | "unknown"): KnownEdgeType | "unknown" {
  return type === "unknown" || (KNOWN_EDGE_TYPES as readonly string[]).includes(type)
    ? (type as KnownEdgeType | "unknown")
    : "unknown";
}

function dedupe(ids: string[]): string[] {
  return Array.from(new Set(ids));
}

export const RELATION_SUMMARY_HISTORY_LIMIT = 50;
export const RELATION_SUMMARY_TEXT_MAX_LENGTH = 4000;

export type RelationSummaryChangeKind = RelationSummaryHistoryEntry["changeKind"];

export type UpsertRelationSummaryWithHistoryPatch = {
  sourceSignature: string;
  islandAId: string;
  islandBId: string;
  relationType: EdgeType | "unknown";
  derived: boolean;
  newText: string;
  newWarnings?: string[];
  newGroundingCardIds: string[];
  newGroundingEdgeIds: string[];
  changeKind: RelationSummaryChangeKind;
  note?: string;
  newReviewed?: boolean;
};

function createEntryId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `relation-summary-history-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function sameStringList(left?: string[], right?: string[]): boolean {
  const safeLeft = left ?? [];
  const safeRight = right ?? [];
  if (safeLeft.length !== safeRight.length) {
    return false;
  }

  return safeLeft.every((value, index) => value === safeRight[index]);
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
    relationType: normalizeRelationType(edge.type),
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

export function upsertRelationSummaryWithHistory(
  document: DocumentV2,
  patch: UpsertRelationSummaryWithHistoryPatch
): DocumentV2 {
  const existing = document.relationSummaries ?? [];
  const index = existing.findIndex((item) => item.sourceSignature === patch.sourceSignature);
  const previous = index >= 0 ? existing[index] : null;

  const nextText = patch.newText.slice(0, RELATION_SUMMARY_TEXT_MAX_LENGTH);
  const nextReviewed =
    patch.changeKind === "ai"
      ? false
      : typeof patch.newReviewed === "boolean"
        ? patch.newReviewed
        : patch.changeKind === "manual"
          ? true
          : previous?.reviewed ?? false;

  const nextWarnings = patch.newWarnings && patch.newWarnings.length > 0 ? [...patch.newWarnings] : undefined;
  const nextGroundingCardIds = dedupe(patch.newGroundingCardIds);
  const nextGroundingEdgeIds = dedupe(patch.newGroundingEdgeIds);
  const now = new Date().toISOString();

  const nextSummary: RelationSummary = {
    id: previous?.id ?? createEntryId(),
    createdAt: previous?.createdAt ?? now,
    islandAId: patch.islandAId,
    islandBId: patch.islandBId,
    relationType: normalizeRelationType(patch.relationType),
    derived: patch.derived,
    text: nextText,
    reviewed: nextReviewed,
    groundingCardIds: nextGroundingCardIds,
    groundingEdgeIds: nextGroundingEdgeIds,
    warnings: nextWarnings,
    sourceSignature: patch.sourceSignature,
    history: previous?.history,
  };

  const noHistoryChange =
    previous !== null &&
    previous.text === nextSummary.text &&
    previous.reviewed === nextSummary.reviewed &&
    sameStringList(previous.warnings, nextSummary.warnings);

  const noSummaryChange =
    previous !== null &&
    previous.islandAId === nextSummary.islandAId &&
    previous.islandBId === nextSummary.islandBId &&
    previous.relationType === nextSummary.relationType &&
    previous.derived === nextSummary.derived &&
    previous.text === nextSummary.text &&
    previous.reviewed === nextSummary.reviewed &&
    sameStringList(previous.warnings, nextSummary.warnings) &&
    sameStringList(previous.groundingCardIds, nextSummary.groundingCardIds) &&
    sameStringList(previous.groundingEdgeIds, nextSummary.groundingEdgeIds);

  if (noSummaryChange && noHistoryChange) {
    return document;
  }

  if (!noHistoryChange) {
    const newHistoryEntry: RelationSummaryHistoryEntry = {
      id: createEntryId(),
      createdAt: now,
      changeKind: patch.changeKind,
      fromText: previous?.text ?? null,
      toText: nextSummary.text,
      fromReviewed: previous?.reviewed ?? null,
      toReviewed: nextSummary.reviewed,
      warningsSnapshot: nextSummary.warnings,
      groundingCardIdsSnapshot: [...nextSummary.groundingCardIds],
      groundingEdgeIdsSnapshot: [...nextSummary.groundingEdgeIds],
      note: patch.note,
    };

    const nextHistory = [...(previous?.history ?? []), newHistoryEntry];
    nextSummary.history =
      nextHistory.length > RELATION_SUMMARY_HISTORY_LIMIT
        ? nextHistory.slice(nextHistory.length - RELATION_SUMMARY_HISTORY_LIMIT)
        : nextHistory;
  }

  const next = [...existing];
  if (index >= 0) {
    next[index] = nextSummary;
  } else {
    next.push(nextSummary);
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
