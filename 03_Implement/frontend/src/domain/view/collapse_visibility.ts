import type { DocumentV2 } from "../types";

export function getCollapsedHiddenCardIds(doc: Pick<DocumentV2, "islands">, collapsedIslandIds: ReadonlySet<string>): Set<string> {
  const hiddenCardIds = new Set<string>();

  for (const island of doc.islands) {
    if (!collapsedIslandIds.has(island.id)) {
      continue;
    }

    for (const cardId of island.cardIds) {
      hiddenCardIds.add(cardId);
    }
  }

  return hiddenCardIds;
}
