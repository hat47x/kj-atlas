import { describe, expect, it } from "vitest";

import { P2BDecisionLogMockStore, type MergeDecisionRecord } from "./p2b_decision_log_mock";

function record(partial: Partial<MergeDecisionRecord>): MergeDecisionRecord {
  return {
    decisionId: partial.decisionId ?? "d-1",
    groupId: partial.groupId ?? "g-1",
    action: partial.action ?? "accept",
    selectedCardIds: partial.selectedCardIds ?? ["c-1"],
    note: partial.note ?? "note",
    decidedBy: partial.decidedBy ?? "human",
    decidedAt: partial.decidedAt ?? "2026-03-14T00:00:00.000Z",
    snapshotVersion: partial.snapshotVersion ?? "s-1",
  };
}

describe("p2b_decision_log_mock", () => {
  it("restores in append order for same snapshot", () => {
    const store = new P2BDecisionLogMockStore();
    store.append(record({ decisionId: "d-1", action: "accept" }));
    store.append(record({ decisionId: "d-2", action: "partial" }));
    store.append(record({ decisionId: "d-3", action: "reject" }));
    store.append(record({ decisionId: "d-4", action: "defer" }));

    expect(store.restore("s-1").map((entry) => entry.action)).toEqual(["accept", "partial", "reject", "defer"]);
  });

  it("filters by group and snapshot independently", () => {
    const store = new P2BDecisionLogMockStore();
    store.append(record({ decisionId: "d-1", groupId: "g-1", snapshotVersion: "s-1" }));
    store.append(record({ decisionId: "d-2", groupId: "g-2", snapshotVersion: "s-1" }));
    store.append(record({ decisionId: "d-3", groupId: "g-1", snapshotVersion: "s-2" }));

    expect(store.listByGroup("g-1").map((entry) => entry.decisionId)).toEqual(["d-1", "d-3"]);
    expect(store.restore("s-1").map((entry) => entry.decisionId)).toEqual(["d-1", "d-2"]);
  });

  it("keeps decision logs append-only (no implicit representative finalization)", () => {
    const store = new P2BDecisionLogMockStore();
    const base = record({ decisionId: "d-1", action: "accept", selectedCardIds: ["c-1", "c-2"] });
    store.append(base);

    const restored = store.restore("s-1");
    expect(restored).toHaveLength(1);
    expect(restored[0]?.selectedCardIds).toEqual(["c-1", "c-2"]);
    expect(restored[0]).not.toHaveProperty("representativeCardId");
  });

  it("ignores invalid action entries during restore", () => {
    const store = new P2BDecisionLogMockStore();
    store.append(record({ decisionId: "d-1", action: "accept" }));
    store.append(record({ decisionId: "d-x", action: "invalid" as MergeDecisionRecord["action"] }));
    store.append(record({ decisionId: "d-2", action: "defer" }));

    expect(store.restore("s-1").map((entry) => entry.decisionId)).toEqual(["d-1", "d-2"]);
  });

  it("restores copied card IDs (mutating restored data does not rewrite log)", () => {
    const store = new P2BDecisionLogMockStore();
    store.append(record({ decisionId: "d-1", selectedCardIds: ["c-1"] }));

    const restored = store.restore("s-1");
    restored[0]?.selectedCardIds.push("c-2");

    expect(store.restore("s-1")[0]?.selectedCardIds).toEqual(["c-1"]);
  });

});
