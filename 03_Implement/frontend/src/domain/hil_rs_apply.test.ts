import { describe, expect, it, vi } from "vitest";
import { applyHilRsRediffPayload } from "./hil_rs_apply";
import type { Document, DocumentV1 } from "./types";
import type { HilRsRediffPayload } from "./hil_rs_contract";

const BASE: Document = {
  version: 1,
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

  it("preserves critique data after reproposal apply (DOMAIN-EXPR-03: critique persists through reproposal loop)", () => {
    const docWithCritique: DocumentV1 = {
      version: 1,
      id: "d1",
      createdAt: "2026-03-10T00:00:00.000Z",
      updatedAt: "2026-03-10T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "alpha", x: 0, y: 0, critique: "too close to c2", critiqueTags: ["too_close"] },
        { id: "c2", text: "beta", x: 50, y: 50, critique: "feels like a different group", critiqueTags: ["feels_off"] },
      ],
      edges: [],
      islands: [],
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "crit-1",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-09T00:00:00.000Z",
          iteration: 1,
          comment: "too close to c2",
        },
      ],
    };

    const moveC1: HilRsRediffPayload = {
      schemaVersion: "1.0.0",
      proposalId: "p-move",
      basedOnIteration: 1,
      traceKey: "c1",
      diffOps: [
        { opId: "move-c1", opType: "move", targetRef: "card:c1", before: { x: 0, y: 0 }, after: { x: 100, y: 100 } },
      ],
    };

    const result = applyHilRsRediffPayload(docWithCritique, moveC1);

    // Move op applied
    expect(result.appliedOpIds).toEqual(["move-c1"]);
    expect(result.skippedOpIds).toEqual([]);

    // Card critique text and tags preserved after apply
    const c1 = result.document.cards.find((c) => c.id === "c1")!;
    expect(c1.critique).toBe("too close to c2");
    expect(c1.critiqueTags).toEqual(["too_close"]);
    expect(c1.x).toBe(100);
    expect(c1.y).toBe(100);

    const c2 = result.document.cards.find((c) => c.id === "c2")!;
    expect(c2.critique).toBe("feels like a different group");
    expect(c2.critiqueTags).toEqual(["feels_off"]);
    expect(c2.x).toBe(50);
    expect(c2.y).toBe(50);

    // critiqueInputs preserved
    expect((result.document as DocumentV1).critiqueInputs).toEqual(docWithCritique.critiqueInputs);

    // Original document unmodified (immutable apply)
    expect(docWithCritique.cards[0].x).toBe(0);
    expect(docWithCritique.cards[0].y).toBe(0);
    expect(docWithCritique.cards[0].critique).toBe("too close to c2");
  });
});
