export type IslandHierarchyContractV1Island = {
  id: string;
  parentIslandId: string | null;
  childIslandIds: string[];
};

export type IslandHierarchyContractV1Document = {
  schemaVersion: string;
  islands: IslandHierarchyContractV1Island[];
};

export type IslandVisibilityContractV1 = {
  island: {
    id: string;
    isCollapsed: boolean;
  };
  view: {
    hiddenDescendantIslandIds: string[];
    hiddenCardIds: string[];
  };
};

export type ContractValidationResult<T> =
  | { ok: true; value: T }
  | { ok: false; error: string };

export function validateIslandHierarchyContractV1(
  value: IslandHierarchyContractV1Document,
): ContractValidationResult<IslandHierarchyContractV1Document> {
  if (!value.schemaVersion) {
    return { ok: false, error: "schemaVersion is required" };
  }

  const islandById = new Map<string, IslandHierarchyContractV1Island>();
  for (const island of value.islands) {
    if (islandById.has(island.id)) {
      return { ok: false, error: `duplicate island id: ${island.id}` };
    }

    const childSet = new Set(island.childIslandIds);
    if (childSet.size !== island.childIslandIds.length) {
      return { ok: false, error: `duplicate childIslandIds in island: ${island.id}` };
    }

    islandById.set(island.id, island);
  }

  for (const island of value.islands) {
    if (island.parentIslandId !== null && !islandById.has(island.parentIslandId)) {
      return { ok: false, error: `missing parent island: ${island.parentIslandId}` };
    }

    for (const childId of island.childIslandIds) {
      const child = islandById.get(childId);
      if (!child) {
        return { ok: false, error: `missing child island: ${childId}` };
      }

      if (child.parentIslandId !== island.id) {
        return { ok: false, error: `parent/child link mismatch: ${island.id} -> ${childId}` };
      }
    }
  }

  const visitState = new Map<string, "visiting" | "visited">();
  const walk = (islandId: string): boolean => {
    const state = visitState.get(islandId);
    if (state === "visiting") {
      return true;
    }
    if (state === "visited") {
      return false;
    }

    visitState.set(islandId, "visiting");
    const island = islandById.get(islandId);
    if (!island) {
      return false;
    }

    for (const childId of island.childIslandIds) {
      if (walk(childId)) {
        return true;
      }
    }

    visitState.set(islandId, "visited");
    return false;
  };

  for (const island of value.islands) {
    if (walk(island.id)) {
      return { ok: false, error: `cycle detected: ${island.id}` };
    }
  }

  return { ok: true, value };
}

export function validateIslandVisibilityContractV1(
  value: IslandVisibilityContractV1,
): ContractValidationResult<IslandVisibilityContractV1> {
  if (!value.island.id) {
    return { ok: false, error: "island.id is required" };
  }

  const hiddenDescendantSet = new Set(value.view.hiddenDescendantIslandIds);
  if (hiddenDescendantSet.size !== value.view.hiddenDescendantIslandIds.length) {
    return { ok: false, error: "hiddenDescendantIslandIds must be unique" };
  }

  const hiddenCardSet = new Set(value.view.hiddenCardIds);
  if (hiddenCardSet.size !== value.view.hiddenCardIds.length) {
    return { ok: false, error: "hiddenCardIds must be unique" };
  }

  return { ok: true, value };
}
