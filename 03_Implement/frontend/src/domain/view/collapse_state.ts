import type { DocumentV1, Island } from "../types";

export type SetIslandCollapsedResult = {
  changed: boolean;
  nextDocument: DocumentV1;
  rejectedReason?: "island-not-found";
};

function updateIslandCollapsed(island: Island, islandId: string, collapsed: boolean): Island {
  if (island.id !== islandId || island.collapsed === collapsed) {
    return island;
  }

  return {
    ...island,
    collapsed,
  };
}

export function setIslandCollapsed(document: DocumentV1, islandId: string, collapsed: boolean): SetIslandCollapsedResult {
  let found = false;
  let changed = false;

  const nextIslands = document.islands.map((island) => {
    if (island.id !== islandId) {
      return island;
    }

    found = true;
    const nextIsland = updateIslandCollapsed(island, islandId, collapsed);
    if (nextIsland !== island) {
      changed = true;
    }
    return nextIsland;
  });

  if (!found || !changed) {
    if (!found) {
      return { changed: false, nextDocument: document, rejectedReason: "island-not-found" };
    }

    return { changed: false, nextDocument: document };
  }

  return {
    changed: true,
    nextDocument: {
      ...document,
      islands: nextIslands,
    },
  };
}

export function setAllIslandsCollapsed(document: DocumentV1, collapsed: boolean): { changed: boolean; nextDocument: DocumentV1 } {
  let changed = false;
  const nextIslands = document.islands.map((island) => {
    if (island.collapsed === collapsed) {
      return island;
    }

    changed = true;
    return {
      ...island,
      collapsed,
    };
  });

  if (!changed) {
    return { changed: false, nextDocument: document };
  }

  return {
    changed: true,
    nextDocument: {
      ...document,
      islands: nextIslands,
    },
  };
}
