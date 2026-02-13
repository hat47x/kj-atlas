import { isCanonicalCard, type Card, type DocumentV2 } from "./types";

const DEFAULT_CARD_TEXT_LIMIT = 200;

export type GroundingCardItem = {
  id: string;
  text: string;
  kind: "canonical" | "source";
  canonicalId?: string;
};

export type GroundingEntry = {
  anchor: string;
  sourceId: string;
  kind: "card" | "island" | "missing";
  islandTitle?: string;
  islandSummaryText?: string;
  islandSummaryReviewed?: boolean;
  islandMembers?: GroundingCardItem[];
  card?: GroundingCardItem;
};

export function toGroundingCardItem(card: Card, maxTextLength = DEFAULT_CARD_TEXT_LIMIT): GroundingCardItem {
  const normalizedText = card.text.trim();
  const text = normalizedText.length > maxTextLength ? `${normalizedText.slice(0, maxTextLength)}…` : normalizedText;

  if (isCanonicalCard(card)) {
    return {
      id: card.id,
      text,
      kind: "canonical",
    };
  }

  return {
    id: card.id,
    text,
    kind: "source",
    canonicalId: card.canonicalId,
  };
}

export function buildNarrativeGrounding(
  document: DocumentV2,
  options: {
    basedOnReadingOrder?: string[];
    hideSourceCards: boolean;
    maxTextLength?: number;
  }
): GroundingEntry[] {
  const readingOrder =
    options.basedOnReadingOrder !== undefined ? options.basedOnReadingOrder : (document.readingOrder ?? []);

  const cardsById = new Map(document.cards.map((card) => [card.id, card]));
  const islandsById = new Map(document.islands.map((island) => [island.id, island]));

  return readingOrder.map((entryId, index) => {
    const island = islandsById.get(entryId);
    if (island) {
      const islandCardIdSet = new Set(island.cardIds);
      const members = document.cards
        .filter((card) => {
          if (islandCardIdSet.has(card.id)) {
            return options.hideSourceCards ? isCanonicalCard(card) : true;
          }

          if (options.hideSourceCards) {
            return false;
          }

          return card.canonicalId !== undefined && islandCardIdSet.has(card.canonicalId);
        })
        .map((card) => toGroundingCardItem(card, options.maxTextLength));

      return {
        anchor: `#${index + 1}`,
        sourceId: entryId,
        kind: "island",
        islandTitle: island.title?.trim() || `Island ${island.id}`,
        islandSummaryText: island.summaryText?.trim() || undefined,
        islandSummaryReviewed: island.summaryReviewed,
        islandMembers: members,
      } satisfies GroundingEntry;
    }

    const card = cardsById.get(entryId);
    if (card) {
      return {
        anchor: `#${index + 1}`,
        sourceId: entryId,
        kind: "card",
        card: toGroundingCardItem(card, options.maxTextLength),
      } satisfies GroundingEntry;
    }

    return {
      anchor: `#${index + 1}`,
      sourceId: entryId,
      kind: "missing",
    } satisfies GroundingEntry;
  });
}
