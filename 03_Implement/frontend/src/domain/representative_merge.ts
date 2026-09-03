import type { DocumentV1 } from "./types";

type MergeOptions = {
  rewireMembershipAndEdges?: boolean;
};

type MergeResult = {
  nextDocument: DocumentV1;
  representativeCardId: string;
  mergedCardCount: number;
};

function projectedEdgeKey(
  fromKind: "card" | "island",
  fromId: string,
  type: string,
  toKind: "card" | "island",
  toId: string,
): string {
  return JSON.stringify([fromKind, fromId, type, toKind, toId]);
}

function allocateProjectedEdgeId(
  originalEdgeId: string,
  representativeCardId: string,
  usedEdgeIds: Set<string>,
): string {
  const baseId = `representative:${representativeCardId}:${originalEdgeId}`;
  let candidate = baseId;
  let suffix = 2;

  while (usedEdgeIds.has(candidate)) {
    candidate = `${baseId}:${suffix}`;
    suffix += 1;
  }

  usedEdgeIds.add(candidate);
  return candidate;
}

export function createRepresentativeMerge(
  document: DocumentV1,
  selectedCardIds: string[],
  representativeText: string,
  options: MergeOptions = {}
): MergeResult | null {
  const uniqueSelectedCardIds = Array.from(new Set(selectedCardIds));
  if (uniqueSelectedCardIds.length < 2) {
    return null;
  }

  const selectedCardSet = new Set(uniqueSelectedCardIds);
  const selectedCards = document.cards.filter((card) => selectedCardSet.has(card.id));
  if (selectedCards.length < 2) {
    return null;
  }

  const normalizedRepresentativeText = representativeText.trim();
  if (normalizedRepresentativeText.length === 0) {
    return null;
  }

  const representativeCardId = crypto.randomUUID();
  const averageX = selectedCards.reduce((sum, card) => sum + card.x, 0) / selectedCards.length;
  const averageY = selectedCards.reduce((sum, card) => sum + card.y, 0) / selectedCards.length;

  const nextCards = document.cards.map((card) => {
    if (!selectedCardSet.has(card.id)) {
      return card;
    }

    return {
      ...card,
      mergedIntoCardId: representativeCardId,
    };
  });

  nextCards.push({
    id: representativeCardId,
    text: normalizedRepresentativeText,
    x: averageX,
    y: averageY,
    repOf: uniqueSelectedCardIds,
  });

  const rewire = options.rewireMembershipAndEdges === true;

  // 「再配線」は元構造の置換ではなく、代表カード側への投影追加として扱う。
  // 統合元カードの島所属はDocumentに残し、後から統合前の構造へ戻れるようにする。
  const nextIslands = rewire
    ? document.islands.map((island) => {
        const hasMergedMember = island.cardIds.some((cardId) => selectedCardSet.has(cardId));
        if (!hasMergedMember || island.cardIds.includes(representativeCardId)) {
          return island;
        }

        return {
          ...island,
          cardIds: [...island.cardIds, representativeCardId],
        };
      })
    : document.islands;

  const nextEdges = rewire
    ? (() => {
        const usedEdgeIds = new Set(document.edges.map((edge) => edge.id));
        const projectedKeys = new Set<string>();
        const projectedEdges: DocumentV1["edges"] = [];

        for (const edge of document.edges) {
          const fromKind = edge.fromKind ?? "card";
          const toKind = edge.toKind ?? "card";
          const fromSelected = fromKind === "card" && selectedCardSet.has(edge.fromId);
          const toSelected = toKind === "card" && selectedCardSet.has(edge.toId);

          if (!fromSelected && !toSelected) {
            continue;
          }

          const nextFromId = fromSelected ? representativeCardId : edge.fromId;
          const nextToId = toSelected ? representativeCardId : edge.toId;

          // 統合元カード同士の関係は元edgeに残る。代表カードの自己ループへ縮約しない。
          if (fromKind === "card" && toKind === "card" && nextFromId === nextToId) {
            continue;
          }

          const key = projectedEdgeKey(fromKind, nextFromId, edge.type, toKind, nextToId);
          if (projectedKeys.has(key)) {
            continue;
          }
          projectedKeys.add(key);

          projectedEdges.push({
            ...edge,
            id: allocateProjectedEdgeId(edge.id, representativeCardId, usedEdgeIds),
            fromId: nextFromId,
            toId: nextToId,
          });
        }

        return [...document.edges, ...projectedEdges];
      })()
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
