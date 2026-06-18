import { describe, expect, it, vi } from "vitest";
import { applyHilRsRediffPayload } from "./hil_rs_apply";
import type { Document } from "./types";
import type { HilRsRediffPayload } from "./hil_rs_contract";

const BASE: Document = {
  version: 2,
  id: "d1",
  createdAt: "2026-03-10T00:00:00.000Z",
  updatedAt: "2026-03-10T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [{ id: "c1", text: "alpha", x: 0, y: 0 }],
  edges: [],
  islands: [],
};

const PAYLOAD: HilRsRediffPayload = {
  schemaVersion: "1.0.0",
  proposalId: "p1",
  basedOnIteration: 1,
  traceKey: "c1",
  diffOps: [
    { opId: "op-add", opType: "add", targetRef: "card:c2", before: null, after: { id: "c2", text: "beta", x: 10, y: 20 } },
    { opId: "op-move", opType: "move", targetRef: "card:c1", before: { x: 0, y: 0 }, after: { x: 4, y: 8 } },
    { opId: "op-remove", opType: "remove", targetRef: "card:c2", before: { id: "c2" }, after: null },
  ],
};

describe("applyHilRsRediffPayload", () => {
  it("applies reversible add/move/remove ops and returns op audit", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-04-30T00:00:00.000Z"));
    const result = applyHilRsRediffPayload(BASE, PAYLOAD);
    vi.useRealTimers();

    expect(result.appliedOpIds).toEqual(["op-add", "op-move", "op-remove"]);
    expect(result.skippedOpIds).toEqual([]);
    expect(result.document.cards).toEqual([{ id: "c1", text: "alpha", x: 4, y: 8 }]);
    expect(result.document.updatedAt).toBe("2026-04-30T00:00:00.000Z");
    expect(BASE.cards).toEqual([{ id: "c1", text: "alpha", x: 0, y: 0 }]);
  });

  it("skips unsupported or invalid operations without mutating review protections", () => {
    const result = applyHilRsRediffPayload(BASE, {
      ...PAYLOAD,
      diffOps: [
        { opId: "bad-kind", opType: "regroup", targetRef: "island:i1", before: null, after: { id: "i1" } },
        { opId: "bad-move", opType: "move", targetRef: "card:c1", before: { x: 0, y: 0 }, after: { x: "4", y: 8 } },
      ],
    });

    expect(result.appliedOpIds).toEqual([]);
    expect(result.skippedOpIds).toEqual(["bad-kind", "bad-move"]);
    expect(result.document.cards[0].textReviewed).toBeUndefined();
  });

  it("rejects rediff operations that attempt to inject review state", () => {
    const result = applyHilRsRediffPayload(BASE, {
      ...PAYLOAD,
      diffOps: [
        {
          opId: "review-injection",
          opType: "add",
          targetRef: "card:c2",
          before: null,
          after: { id: "c2", text: "beta", x: 10, y: 20, textReviewed: true },
        },
      ],
    });

    expect(result.appliedOpIds).toEqual([]);
    expect(result.skippedOpIds).toEqual(["review-injection"]);
    expect(result.document.cards).toEqual(BASE.cards);
  });
});
