import type { DocumentV1, Island, RelationSummary } from "../types";

export type CardTextChange = {
  id: string;
  aText: string;
  bText: string;
};

export type IslandMembershipChange = {
  id: string;
  addedCardIds: string[];
  removedCardIds: string[];
};

export type IslandSummaryChange = {
  id: string;
  aSummary?: string;
  bSummary?: string;
  aReviewed?: boolean;
  bReviewed?: boolean;
};

export type RelationSummaryTextChange = {
  id: string;
  aText: string;
  bText: string;
};

export type RelationSummaryReviewedChange = {
  id: string;
  aReviewed: boolean;
  bReviewed: boolean;
};

export type RelationSummaryWarningsChange = {
  id: string;
  aWarnings: string[];
  bWarnings: string[];
};

export type DiffResult = {
  cards: {
    added: string[];
    removed: string[];
    changedText: CardTextChange[];
  };
  islands: {
    added: string[];
    removed: string[];
    membershipChanged: IslandMembershipChange[];
    summaryChanged: IslandSummaryChange[];
  };
  relationSummaries: {
    added: string[];
    removed: string[];
    changedText: RelationSummaryTextChange[];
    changedReviewed: RelationSummaryReviewedChange[];
    warningsChanged: RelationSummaryWarningsChange[];
  };
  readingOrder: {
    changed: boolean;
    firstDifferingIndex: number;
    aOrder: string[];
    bOrder: string[];
  };
};

function sortedIds(values: Iterable<string>): string[] {
  return Array.from(values).sort((a, b) => a.localeCompare(b));
}

function toIslandMap(islands: Island[]): Map<string, Island> {
  return new Map(islands.map((island) => [island.id, island]));
}

function normalizeWarnings(summary: RelationSummary): string[] {
  return sortedIds(summary.warnings ?? []);
}

function firstDifferingIndex(a: string[], b: string[]): number {
  const minLength = Math.min(a.length, b.length);
  for (let index = 0; index < minLength; index += 1) {
    if (a[index] !== b[index]) {
      return index;
    }
  }

  return a.length === b.length ? -1 : minLength;
}

export function diffDocuments(a: DocumentV1, b: DocumentV1): DiffResult {
  const aCards = new Map(a.cards.map((card) => [card.id, card]));
  const bCards = new Map(b.cards.map((card) => [card.id, card]));

  const cardAdded = sortedIds(b.cards.map((card) => card.id).filter((id) => !aCards.has(id)));
  const cardRemoved = sortedIds(a.cards.map((card) => card.id).filter((id) => !bCards.has(id)));
  const cardChangedText: CardTextChange[] = sortedIds(a.cards.map((card) => card.id).filter((id) => bCards.has(id)))
    .map((id) => ({ id, aText: aCards.get(id)?.text ?? "", bText: bCards.get(id)?.text ?? "" }))
    .filter((entry) => entry.aText !== entry.bText);

  const aIslands = toIslandMap(a.islands);
  const bIslands = toIslandMap(b.islands);

  const islandAdded = sortedIds(b.islands.map((island) => island.id).filter((id) => !aIslands.has(id)));
  const islandRemoved = sortedIds(a.islands.map((island) => island.id).filter((id) => !bIslands.has(id)));

  const sharedIslandIds = sortedIds(a.islands.map((island) => island.id).filter((id) => bIslands.has(id)));

  const islandMembershipChanged: IslandMembershipChange[] = sharedIslandIds
    .map((id) => {
      const aCardIds = new Set(aIslands.get(id)?.cardIds ?? []);
      const bCardIds = new Set(bIslands.get(id)?.cardIds ?? []);
      const addedCardIds = sortedIds(Array.from(bCardIds).filter((cardId) => !aCardIds.has(cardId)));
      const removedCardIds = sortedIds(Array.from(aCardIds).filter((cardId) => !bCardIds.has(cardId)));
      return { id, addedCardIds, removedCardIds };
    })
    .filter((entry) => entry.addedCardIds.length > 0 || entry.removedCardIds.length > 0);

  const islandSummaryChanged: IslandSummaryChange[] = sharedIslandIds
    .map((id) => {
      const aIsland = aIslands.get(id);
      const bIsland = bIslands.get(id);
      return {
        id,
        aSummary: aIsland?.summaryText,
        bSummary: bIsland?.summaryText,
        aReviewed: aIsland?.summaryReviewed,
        bReviewed: bIsland?.summaryReviewed,
      };
    })
    .filter((entry) => entry.aSummary !== entry.bSummary || entry.aReviewed !== entry.bReviewed);

  const aRelationSummaries = new Map((a.relationSummaries ?? []).map((entry) => [entry.id, entry]));
  const bRelationSummaries = new Map((b.relationSummaries ?? []).map((entry) => [entry.id, entry]));

  const relationAdded = sortedIds(Array.from(bRelationSummaries.keys()).filter((id) => !aRelationSummaries.has(id)));
  const relationRemoved = sortedIds(Array.from(aRelationSummaries.keys()).filter((id) => !bRelationSummaries.has(id)));
  const sharedRelationIds = sortedIds(Array.from(aRelationSummaries.keys()).filter((id) => bRelationSummaries.has(id)));

  const relationChangedText: RelationSummaryTextChange[] = sharedRelationIds
    .map((id) => ({
      id,
      aText: aRelationSummaries.get(id)?.text ?? "",
      bText: bRelationSummaries.get(id)?.text ?? "",
    }))
    .filter((entry) => entry.aText !== entry.bText);

  const relationChangedReviewed: RelationSummaryReviewedChange[] = sharedRelationIds
    .map((id) => ({
      id,
      aReviewed: aRelationSummaries.get(id)?.reviewed ?? false,
      bReviewed: bRelationSummaries.get(id)?.reviewed ?? false,
    }))
    .filter((entry) => entry.aReviewed !== entry.bReviewed);

  const relationWarningsChanged: RelationSummaryWarningsChange[] = sharedRelationIds
    .map((id) => ({
      id,
      aWarnings: normalizeWarnings(aRelationSummaries.get(id) as RelationSummary),
      bWarnings: normalizeWarnings(bRelationSummaries.get(id) as RelationSummary),
    }))
    .filter((entry) => entry.aWarnings.join("\u0000") !== entry.bWarnings.join("\u0000"));

  const aOrder = a.readingOrder ?? [];
  const bOrder = b.readingOrder ?? [];
  const readingOrderFirstDiff = firstDifferingIndex(aOrder, bOrder);

  return {
    cards: {
      added: cardAdded,
      removed: cardRemoved,
      changedText: cardChangedText,
    },
    islands: {
      added: islandAdded,
      removed: islandRemoved,
      membershipChanged: islandMembershipChanged,
      summaryChanged: islandSummaryChanged,
    },
    relationSummaries: {
      added: relationAdded,
      removed: relationRemoved,
      changedText: relationChangedText,
      changedReviewed: relationChangedReviewed,
      warningsChanged: relationWarningsChanged,
    },
    readingOrder: {
      changed: readingOrderFirstDiff !== -1,
      firstDifferingIndex: readingOrderFirstDiff,
      aOrder: [...aOrder],
      bOrder: [...bOrder],
    },
  };
}
