import { getCardWorldBounds, getIslandWorldBounds, type BoundsRect } from "../geometry/bounds";
import type { Card, DocumentV1, Island } from "../types";

const LABEL_SNIPPET_MAX = 64;

export type ReadingMode = "islands" | "islands+cards";

export type ReadingPathViewState = {
  readingMode: ReadingMode;
  reviewedOnly: boolean;
};

export type ReadingItem = {
  kind: "island" | "card";
  id: string;
  label: string;
  reviewed: boolean;
  bounds: BoundsRect;
};

function byTopLeft(a: BoundsRect, b: BoundsRect): number {
  if (a.y !== b.y) {
    return a.y - b.y;
  }

  return a.x - b.x;
}

function clipLabel(value: string | undefined): string {
  const trimmed = (value ?? "").trim();
  if (trimmed.length === 0) {
    return "(untitled)";
  }

  if (trimmed.length <= LABEL_SNIPPET_MAX) {
    return trimmed;
  }

  return `${trimmed.slice(0, LABEL_SNIPPET_MAX)}…`;
}

function buildIslandLabel(island: Island): string {
  if (island.title && island.title.trim().length > 0) {
    return clipLabel(island.title);
  }

  if (island.summaryText && island.summaryText.trim().length > 0) {
    return clipLabel(island.summaryText);
  }

  return "(untitled island)";
}

function buildCardLabel(card: Card): string {
  return clipLabel(card.text) || "(untitled card)";
}

function isIslandSummaryReviewed(island: Island): boolean {
  const summaryText = island.summaryText?.trim() ?? "";
  if (summaryText.length === 0) {
    return true;
  }

  return island.summaryReviewed === true;
}

export function buildReadingList(doc: DocumentV1, viewState: ReadingPathViewState): ReadingItem[] {
  const cardsById = new Map(doc.cards.map((card) => [card.id, card]));
  const orderedItems: ReadingItem[] = [];

  const islandsByBounds = doc.islands
    .map((island) => {
      const bounds = getIslandWorldBounds(island, cardsById);
      if (!bounds) {
        return null;
      }

      return { island, bounds };
    })
    .filter((entry): entry is { island: Island; bounds: BoundsRect } => entry !== null)
    .sort((a, b) => byTopLeft(a.bounds, b.bounds));

  const includedCardIds = new Set<string>();

  for (const { island, bounds } of islandsByBounds) {
    const reviewed = isIslandSummaryReviewed(island);
    const includeIsland = !viewState.reviewedOnly || reviewed;

    if (includeIsland) {
      orderedItems.push({
        kind: "island",
        id: island.id,
        label: buildIslandLabel(island),
        reviewed,
        bounds,
      });
    }

    if (viewState.readingMode === "islands+cards") {
      const memberCards = island.cardIds
        .map((cardId) => cardsById.get(cardId))
        .filter((card): card is Card => Boolean(card))
        .map((card) => ({ card, bounds: getCardWorldBounds(card) }))
        .sort((a, b) => byTopLeft(a.bounds, b.bounds));

      for (const { card, bounds: cardBounds } of memberCards) {
        includedCardIds.add(card.id);
        orderedItems.push({
          kind: "card",
          id: card.id,
          label: buildCardLabel(card),
          reviewed: true,
          bounds: cardBounds,
        });
      }
    }
  }

  if (viewState.readingMode === "islands+cards") {
    const loneCards = doc.cards
      .filter((card) => !includedCardIds.has(card.id))
      .map((card) => ({ card, bounds: getCardWorldBounds(card) }))
      .sort((a, b) => byTopLeft(a.bounds, b.bounds));

    for (const { card, bounds } of loneCards) {
      orderedItems.push({
        kind: "card",
        id: card.id,
        label: buildCardLabel(card),
        reviewed: true,
        bounds,
      });
    }
  }

  return orderedItems;
}

export function clampReadingIndex(index: number, listLength: number): number {
  if (listLength <= 0) {
    return 0;
  }

  if (index < 0) {
    return 0;
  }

  if (index >= listLength) {
    return listLength - 1;
  }

  return index;
}
