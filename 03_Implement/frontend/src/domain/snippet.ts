import type { DocumentV1 } from "./types";

export function buildReadingOrderSnippets(document: DocumentV1): Record<string, string | undefined> {
  const snippets: Record<string, string | undefined> = {};

  for (const card of document.cards) {
    snippets[card.id] = card.text;
  }

  for (const island of document.islands) {
    snippets[island.id] = island.summaryText ?? island.title;
  }

  return snippets;
}
