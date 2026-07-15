import type { DocumentV1, SummaryHistoryEntry } from "./types";

const DEFAULT_HISTORY_LIMIT = 50;

export type SummaryHistoryChangeKind = SummaryHistoryEntry["changeKind"];

export type UpdateIslandSummaryPatch = {
  summaryText?: string;
  summaryReviewed?: boolean;
  summaryGrounding?: string[];
};

export type UpdateIslandSummaryWithHistoryOptions = {
  changeKind?: SummaryHistoryChangeKind;
  note?: string;
  createdAt?: string;
  historyLimit?: number;
  forceHistoryEntry?: boolean;
};

function createEntryId(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }

  return `summary-history-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function updateIslandSummaryWithHistory(
  document: DocumentV1,
  islandId: string,
  patch: UpdateIslandSummaryPatch,
  options: UpdateIslandSummaryWithHistoryOptions = {}
): DocumentV1 {
  let didChange = false;

  const nextIslands = document.islands.map((island) => {
    if (island.id !== islandId) {
      return island;
    }

    const nextIsland = {
      ...island,
      ...patch,
    };

    const currentSummaryText = island.summaryText ?? "";
    const nextSummaryText = nextIsland.summaryText ?? "";
    const summaryTextChanged = currentSummaryText !== nextSummaryText;
    const shouldRecordHistory = summaryTextChanged || options.forceHistoryEntry === true;

    if (!shouldRecordHistory) {
      return nextIsland;
    }

    const fromText = island.summaryText ?? null;
    const toText = nextIsland.summaryText ?? null;
    if (fromText === null && toText === null) {
      return nextIsland;
    }

    const newEntry: SummaryHistoryEntry = {
      id: createEntryId(),
      createdAt: options.createdAt ?? new Date().toISOString(),
      fromText,
      toText,
      fromReviewed: island.summaryReviewed ?? null,
      toReviewed: nextIsland.summaryReviewed ?? null,
      changeKind: options.changeKind ?? "unknown",
      note: options.note,
      groundingIds:
        nextIsland.summaryGrounding && nextIsland.summaryGrounding.length > 0
          ? [...nextIsland.summaryGrounding]
          : undefined,
    };

    const nextHistory = [...(island.summaryHistory ?? []), newEntry];
    const historyLimit = options.historyLimit ?? DEFAULT_HISTORY_LIMIT;
    const trimmedHistory = nextHistory.length > historyLimit ? nextHistory.slice(nextHistory.length - historyLimit) : nextHistory;

    didChange = true;
    return {
      ...nextIsland,
      summaryHistory: trimmedHistory,
    };
  });

  if (!didChange) {
    const islandsUpdated = nextIslands.some((island, index) => island !== document.islands[index]);
    return islandsUpdated
      ? {
          ...document,
          islands: nextIslands,
        }
      : document;
  }

  return {
    ...document,
    islands: nextIslands,
  };
}

/*
Manual test steps:
1) Select an island, edit Summary text, then blur the textarea.
2) Confirm one new entry appears in "Summary history (N)" with correct from/to values.
3) Click "Restore this version" on an older entry and confirm summary text changes and a new rollback entry is appended.
4) Save, reload, and confirm summary history remains.
*/
