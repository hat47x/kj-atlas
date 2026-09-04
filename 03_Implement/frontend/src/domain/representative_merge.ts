import type { Card, DocumentV1, Edge, EdgeEndpointKind } from "./types";

type MergeOptions = {
  rewireMembershipAndEdges?: boolean;
};

type MergeResult = {
  nextDocument: DocumentV1;
  representativeCardId: string;
  mergedCardCount: number;
};

function sortedUniqueIds(ids: Iterable<string>): string[] {
  return [...new Set(ids)].sort((left, right) => left.localeCompare(right));
}

function hasMergeConflict(document: DocumentV1, selectedCards: Card[]): boolean {
  if (selectedCards.some((card) => card.holdState !== undefined)) {
    return true;
  }

  // A source that already points at another representative/canonical card is no
  // longer an independent merge unit. A representative card itself may be merged
  // again; its repOf/sources lineage is flattened onto the new representative below.
  if (selectedCards.some((card) => card.mergedIntoCardId || card.canonicalId)) {
    return true;
  }

  const definedClaimTypes = new Set(
    selectedCards
      .map((card) => card.claimType)
      .filter((claimType): claimType is NonNullable<Card["claimType"]> => claimType !== undefined)
  );
  if (definedClaimTypes.size > 1) {
    return true;
  }

  const selectedCardIds = new Set(selectedCards.map((card) => card.id));
  const hasNegateRelation = document.edges.some((edge) => {
    const fromKind = edge.fromKind ?? "card";
    const toKind = edge.toKind ?? "card";
    return (
      fromKind === "card"
      && toKind === "card"
      && edge.type === "negate"
      && selectedCardIds.has(edge.fromId)
      && selectedCardIds.has(edge.toId)
    );
  });
  if (hasNegateRelation) {
    return true;
  }

  return (document.evidenceLinks ?? []).some(
    (link) =>
      link.type === "contradicts"
      && selectedCardIds.has(link.fromCardId)
      && selectedCardIds.has(link.toCardId)
  );
}

function collectRepresentativeSources(selectedCards: Card[]): string[] {
  const sourceIds = new Set<string>();
  for (const card of selectedCards) {
    sourceIds.add(card.id);
    for (const sourceId of card.repOf ?? []) {
      sourceIds.add(sourceId);
    }
    for (const sourceId of card.sources ?? []) {
      sourceIds.add(sourceId);
    }
  }
  return sortedUniqueIds(sourceIds);
}

function representativeClaimType(selectedCards: Card[]): Card["claimType"] | undefined {
  if (selectedCards.some((card) => card.claimType === undefined)) {
    return undefined;
  }
  const claimTypes = new Set(selectedCards.map((card) => card.claimType));
  return claimTypes.size === 1 ? selectedCards[0]?.claimType : undefined;
}

function projectRepresentativeEdges(
  edges: DocumentV1["edges"],
  selectedCardSet: Set<string>,
  representativeCardId: string
): DocumentV1["edges"] {
  // Keyed by the projected edge's own (direction, other endpoint, type) triple
  // rather than by the source edge's id, so several original edges that would
  // project to the same representative-side relation collapse onto one entry
  // instead of duplicating it. The Map preserves first-seen order.
  const projectedByTriple = new Map<string, Edge>();

  for (const edge of edges) {
    const fromKind: EdgeEndpointKind = edge.fromKind ?? "card";
    const toKind: EdgeEndpointKind = edge.toKind ?? "card";
    const fromSelected = fromKind === "card" && selectedCardSet.has(edge.fromId);
    const toSelected = toKind === "card" && selectedCardSet.has(edge.toId);

    // Keep every original edge as the provenance-bearing relation. An edge
    // internal to the merged set would become a meaningless representative
    // self-loop, so it gets no projected companion.
    if (!fromSelected && !toSelected) {
      continue;
    }
    if (fromSelected && toSelected) {
      continue;
    }

    const direction = fromSelected ? "from" : "to";
    const otherId = fromSelected ? edge.toId : edge.fromId;
    const otherKind = fromSelected ? toKind : fromKind;
    const triple = `${direction}:${otherKind}:${otherId}:${edge.type}`;

    if (projectedByTriple.has(triple)) {
      continue;
    }

    projectedByTriple.set(triple, {
      ...edge,
      // Deterministic from the projected relation itself (not the source edge
      // id), so duplicate-shaped projections naturally share one id and the
      // id space stays disjoint from any existing edge id via the prefix.
      id: `representative-merge:${representativeCardId}:${triple}`,
      fromId: fromSelected ? representativeCardId : edge.fromId,
      toId: toSelected ? representativeCardId : edge.toId,
    });
  }

  return [...edges, ...projectedByTriple.values()];
}

export function createRepresentativeMerge(
  document: DocumentV1,
  selectedCardIds: string[],
  representativeText: string,
  options: MergeOptions = {}
): MergeResult | null {
  const uniqueSelectedCardIds = sortedUniqueIds(selectedCardIds);
  if (uniqueSelectedCardIds.length < 2) {
    return null;
  }

  const selectedCardSet = new Set(uniqueSelectedCardIds);
  const selectedCards = document.cards.filter((card) => selectedCardSet.has(card.id));
  // Never silently downgrade a requested N-card merge into a smaller merge when
  // one of the original cards disappeared between proposal and human acceptance.
  if (selectedCards.length !== uniqueSelectedCardIds.length) {
    return null;
  }
  if (hasMergeConflict(document, selectedCards)) {
    return null;
  }

  const normalizedRepresentativeText = representativeText.trim();
  if (normalizedRepresentativeText.length === 0) {
    return null;
  }

  const representativeCardId = crypto.randomUUID();
  if (document.cards.some((card) => card.id === representativeCardId)) {
    return null;
  }

  const averageX = selectedCards.reduce((sum, card) => sum + card.x, 0) / selectedCards.length;
  const averageY = selectedCards.reduce((sum, card) => sum + card.y, 0) / selectedCards.length;
  const sourceIds = collectRepresentativeSources(selectedCards);
  const claimType = representativeClaimType(selectedCards);

  const nextCards = document.cards.map((card) => {
    if (!selectedCardSet.has(card.id)) {
      return card;
    }

    return {
      ...card,
      // Keep both established lineage vocabularies aligned. Source cards stay
      // physically present, so their original text/meta/KA/provenance remain
      // available for return-checking and residual inspection.
      mergedIntoCardId: representativeCardId,
      canonicalId: representativeCardId,
    };
  });

  nextCards.push({
    id: representativeCardId,
    text: normalizedRepresentativeText,
    x: averageX,
    y: averageY,
    ...(claimType ? { claimType } : {}),
    repOf: uniqueSelectedCardIds,
    sources: sourceIds,
    textReviewed: false,
  });

  const rewire = options.rewireMembershipAndEdges === true;

  const nextIslands = rewire
    ? document.islands.map((island) => {
        const hasMergedMember = island.cardIds.some((cardId) => selectedCardSet.has(cardId));
        if (!hasMergedMember || island.cardIds.includes(representativeCardId)) {
          return island;
        }

        // Preserve source membership as provenance. Merged originals can be
        // hidden by the view, while restoring them still recovers their original
        // island context. The representative is added as the active projection.
        return {
          ...island,
          cardIds: [...island.cardIds, representativeCardId],
        };
      })
    : document.islands;

  const nextEdges = rewire
    ? projectRepresentativeEdges(document.edges, selectedCardSet, representativeCardId)
    : document.edges;

  return {
    nextDocument: {
      ...document,
      cards: nextCards,
      islands: nextIslands,
      edges: nextEdges,
    },
    representativeCardId,
    mergedCardCount: selectedCards.length,
  };
}
