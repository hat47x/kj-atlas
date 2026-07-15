import { describe, expect, it } from "vitest";

import { updateIslandSummaryWithHistory } from "./summary_history_ops";
import type { DocumentV1 } from "./types";

function makeDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [
      {
        id: "island-1",
        cardIds: [],
        summaryText: "before",
        summaryReviewed: false,
      },
    ],
    readingOrder: [],
    narratives: [],
  };
}

describe("summary_history_ops", () => {
  it("records one history entry for a summary text change", () => {
    const result = updateIslandSummaryWithHistory(
      makeDocument(),
      "island-1",
      { summaryText: "after", summaryReviewed: true },
      { changeKind: "manual", createdAt: "2026-01-02T00:00:00.000Z" }
    );

    const history = result.islands[0].summaryHistory ?? [];
    expect(history).toHaveLength(1);
    expect(history[0]).toMatchObject({
      createdAt: "2026-01-02T00:00:00.000Z",
      fromText: "before",
      toText: "after",
      fromReviewed: false,
      toReviewed: true,
      changeKind: "manual",
    });
  });

  it("does not add history when summary text does not change", () => {
    const document = makeDocument();
    const result = updateIslandSummaryWithHistory(document, "island-1", { summaryText: "before", summaryReviewed: true });

    expect(result.islands[0].summaryHistory).toBeUndefined();
    expect(result.islands[0].summaryReviewed).toBe(true);
  });

  it("can force a history entry even when summary text is unchanged", () => {
    const document = makeDocument();
    const result = updateIslandSummaryWithHistory(
      document,
      "island-1",
      { summaryText: "before", summaryReviewed: false },
      { changeKind: "manual", note: "rollback:noop", forceHistoryEntry: true }
    );

    const history = result.islands[0].summaryHistory ?? [];
    expect(history).toHaveLength(1);
    expect(history[0].fromText).toBe("before");
    expect(history[0].toText).toBe("before");
    expect(history[0].note).toBe("rollback:noop");
  });

  it("trims history from the oldest entries when over limit", () => {
    let document = makeDocument();

    for (let index = 0; index < 55; index += 1) {
      document = updateIslandSummaryWithHistory(
        document,
        "island-1",
        { summaryText: `v-${index}` },
        { createdAt: `2026-01-02T00:00:${String(index).padStart(2, "0")}.000Z` }
      );
    }

    const history = document.islands[0].summaryHistory ?? [];
    expect(history).toHaveLength(50);
    expect(history[0].toText).toBe("v-5");
    expect(history[history.length - 1].toText).toBe("v-54");
  });
  it("appends a new entry when restoring a previous summary version", () => {
    let document = updateIslandSummaryWithHistory(
      makeDocument(),
      "island-1",
      { summaryText: "v2", summaryReviewed: true },
      { changeKind: "manual", createdAt: "2026-01-02T00:00:00.000Z" }
    );

    document = updateIslandSummaryWithHistory(
      document,
      "island-1",
      { summaryText: "before", summaryReviewed: false },
      { changeKind: "manual", note: "rollback:entry-1", createdAt: "2026-01-02T00:01:00.000Z" }
    );

    const history = document.islands[0].summaryHistory ?? [];
    expect(history).toHaveLength(2);
    expect(document.islands[0].summaryText).toBe("before");
    expect(history[1].fromText).toBe("v2");
    expect(history[1].toText).toBe("before");
    expect(history[1].note).toBe("rollback:entry-1");
  });

});
