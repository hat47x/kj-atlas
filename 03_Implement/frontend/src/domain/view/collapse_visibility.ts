import type { DocumentV2, Island } from "../types";

function buildIslandsByParentId(islands: Island[]): Map<string, Island[]> {
  const islandsByParentId = new Map<string, Island[]>();

  for (const island of islands) {
    if (!island.parentIslandId) {
      continue;
    }

    const children = islandsByParentId.get(island.parentIslandId) ?? [];
    children.push(island);
    islandsByParentId.set(island.parentIslandId, children);
  }

  return islandsByParentId;
}

export function collectCollapsedIslandIds(islands: Island[], collapsedIslandIds: ReadonlySet<string>): Set<string> {
  const islandsByParentId = buildIslandsByParentId(islands);
  const hiddenIslandIds = new Set<string>();
  const stack = islands.filter((island) => collapsedIslandIds.has(island.id));

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current || hiddenIslandIds.has(current.id)) {
      continue;
    }

    hiddenIslandIds.add(current.id);
    const children = islandsByParentId.get(current.id) ?? [];
    for (const child of children) {
      stack.push(child);
    }
  }

  return hiddenIslandIds;
}

export function collectInitiallyCollapsedIslandIds(islands: Island[]): Set<string> {
  return collectCollapsedIslandIds(
    islands,
    new Set(islands.filter((island) => island.collapsed === true).map((island) => island.id))
  );
}

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
