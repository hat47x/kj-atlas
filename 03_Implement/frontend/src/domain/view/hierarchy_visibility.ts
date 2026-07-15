import type { DocumentV1, Island } from "../types";
import type { HierarchyLevel } from "./hierarchy_level";

export function collectHierarchyHiddenIslandIds(
  islands: Island[],
  islandDepthById: Map<string, number>,
  maxDepth: number | "all",
): Set<string> {
  if (maxDepth === "all") {
    return new Set<string>();
  }

  return new Set(
    islands
      .filter((island) => (islandDepthById.get(island.id) ?? 0) > maxDepth)
      .map((island) => island.id),
  );
}

export function collectHierarchyPlacardHiddenCardIds(document: DocumentV1, level: HierarchyLevel): Set<string> {
  if (level !== "overview") {
    return new Set<string>();
  }

  const placardCardIds = new Set<string>();
  for (const island of document.islands) {
    if (!island.placardCardId) {
      continue;
    }

    if (island.cardIds.includes(island.placardCardId)) {
      placardCardIds.add(island.placardCardId);
    }
  }

  const hidden = new Set<string>();
  for (const island of document.islands) {
    for (const cardId of island.cardIds) {
      if (!placardCardIds.has(cardId)) {
        hidden.add(cardId);
      }
    }
  }

  return hidden;
}

