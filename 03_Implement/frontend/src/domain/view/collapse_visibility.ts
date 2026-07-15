import type { DocumentV1, Island } from "../types";
import { validateIslandVisibilityContractV1, type ContractValidationResult, type IslandVisibilityContractV1 } from "../contracts/island_contracts";

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

export function getCollapsedHiddenCardIds(doc: Pick<DocumentV1, "islands">, collapsedIslandIds: ReadonlySet<string>): Set<string> {
  const hiddenDescendantIslandIds = collectHiddenDescendantIslandIds(doc.islands, collapsedIslandIds);
  const hiddenCardIds = new Set<string>();

  for (const island of doc.islands) {
    if (!collapsedIslandIds.has(island.id) && !hiddenDescendantIslandIds.has(island.id)) {
      continue;
    }

    for (const cardId of island.cardIds) {
      hiddenCardIds.add(cardId);
    }
  }

  return hiddenCardIds;
}

export function collectHiddenDescendantIslandIds(islands: Island[], collapsedIslandIds: ReadonlySet<string>): Set<string> {
  const islandsByParentId = buildIslandsByParentId(islands);
  const hiddenDescendantIslandIds = new Set<string>();

  for (const islandId of collapsedIslandIds) {
    const stack = [...(islandsByParentId.get(islandId) ?? [])];
    while (stack.length > 0) {
      const current = stack.pop();
      if (!current || hiddenDescendantIslandIds.has(current.id)) {
        continue;
      }

      hiddenDescendantIslandIds.add(current.id);
      for (const child of islandsByParentId.get(current.id) ?? []) {
        stack.push(child);
      }
    }
  }

  return hiddenDescendantIslandIds;
}

export function buildIslandVisibilityContractPayload(
  doc: Pick<DocumentV1, "islands">,
  collapsedIslandIds: ReadonlySet<string>,
  islandId: string,
): ContractValidationResult<IslandVisibilityContractV1> {
  if (islandId.length === 0) {
    return { ok: false, error: "island.id is required" };
  }

  if (!doc.islands.some((island) => island.id === islandId)) {
    return { ok: false, error: `unknown island.id: ${islandId}` };
  }

  const knownIslandIds = new Set(doc.islands.map((island) => island.id));
  const unknownCollapsedIslandIds = [...collapsedIslandIds].filter((collapsedId) => !knownIslandIds.has(collapsedId));
  if (unknownCollapsedIslandIds.length > 0) {
    const firstUnknownCollapsedIslandId = unknownCollapsedIslandIds.sort()[0];
    return { ok: false, error: `unknown collapsed island.id: ${firstUnknownCollapsedIslandId}` };
  }

  const hiddenDescendantIslandIds = [...collectHiddenDescendantIslandIds(doc.islands, collapsedIslandIds)].sort();
  const hiddenCardIds = [...getCollapsedHiddenCardIds(doc, collapsedIslandIds)].sort();

  return validateIslandVisibilityContractV1({
    island: {
      id: islandId,
      isCollapsed: collapsedIslandIds.has(islandId),
    },
    view: {
      hiddenDescendantIslandIds,
      hiddenCardIds,
    },
  });
}
