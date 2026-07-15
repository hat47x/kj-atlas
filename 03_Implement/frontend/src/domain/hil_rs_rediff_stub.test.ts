import { describe, expect, it } from "vitest";
import { buildHilRsRediffStub } from "./hil_rs_rediff_stub";
import type { DocumentV1 } from "./types";

const CURRENT_DOC: DocumentV1 = {
  version: 1,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "alpha", x: 0, y: 0 },
    { id: "c2", text: "beta", x: 10, y: 10 },
  ],
  islands: [],
  edges: [],
};

describe("buildHilRsRediffStub", () => {
  it("builds reversible diff ops for add/move/remove", () => {
    const suggested: DocumentV1 = {
      ...CURRENT_DOC,
      cards: [
        { id: "c1", text: "alpha", x: 2, y: 3 },
        { id: "c3", text: "gamma", x: 20, y: 20 },
      ],
    };

    const payload = buildHilRsRediffStub(CURRENT_DOC, suggested, {
      suggestionId: "proposal-1",
      iteration: 2,
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "card:c1:2",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 2,
        },
      ],
    });

    expect(payload).not.toBeNull();
    expect(payload?.traceKey).toContain("card:c1:2");
    expect(payload?.diffOps.map((op) => op.opType)).toEqual(["add", "move", "remove"]);
  });


  it("normalizes traceKey ordering and deduplicates critique IDs", () => {
    const suggested: DocumentV1 = {
      ...CURRENT_DOC,
      cards: [{ id: "c1", text: "alpha", x: 2, y: 3 }],
    };

    const payload = buildHilRsRediffStub(CURRENT_DOC, suggested, {
      suggestionId: "proposal-2",
      iteration: 2,
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "island:i1:2",
          targetRef: "island:i1",
          critiqueType: "feels_off",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 2,
        },
        {
          schemaVersion: "1.0.0",
          critiqueId: "card:c1:2",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 2,
        },
        {
          schemaVersion: "1.0.0",
          critiqueId: "card:c1:2",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 2,
        },
      ],
    });

    expect(payload).not.toBeNull();
    expect(payload?.traceKey).toBe("trace:card:c1:2+island:i1:2");
  });


  it("keeps deterministic diff op ordering regardless of suggested card order", () => {
    const suggested: DocumentV1 = {
      ...CURRENT_DOC,
      cards: [
        { id: "c3", text: "gamma", x: 20, y: 20 },
        { id: "c1", text: "alpha", x: 2, y: 3 },
      ],
    };

    const payload = buildHilRsRediffStub(CURRENT_DOC, suggested, {
      suggestionId: "proposal-ordered",
      iteration: 2,
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "card:c1:2",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 2,
        },
      ],
    });

    expect(payload).not.toBeNull();
    expect(payload?.diffOps.map((op) => op.opId)).toEqual(["op:add:c3", "op:move:c1", "op:remove:c2"]);
  });


  it("returns null when critique inputs are missing", () => {
    const suggested: DocumentV1 = {
      ...CURRENT_DOC,
      cards: [
        { id: "c1", text: "alpha", x: 2, y: 3 },
        { id: "c3", text: "gamma", x: 20, y: 20 },
      ],
    };

    const payload = buildHilRsRediffStub(CURRENT_DOC, suggested, {
      suggestionId: "proposal-1",
      iteration: 2,
      critiqueInputs: [],
    });

    expect(payload).toBeNull();
  });

  it("returns null when critique inputs violate A1-CRITIQUE-IF", () => {
    const suggested: DocumentV1 = {
      ...CURRENT_DOC,
      cards: [{ id: "c1", text: "alpha", x: 2, y: 3 }],
    };

    const payload = buildHilRsRediffStub(CURRENT_DOC, suggested, {
      suggestionId: "proposal-1",
      iteration: 2,
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "card:c1:2",
          targetRef: "card:c1",
          critiqueType: "too_close",
          createdAt: "2026-03-11T00:00:00.000Z",
          iteration: 1,
        },
      ],
    });

    expect(payload).toBeNull();
  });

  it("returns null when there are no structural changes", () => {
    const payload = buildHilRsRediffStub(CURRENT_DOC, CURRENT_DOC, {
      suggestionId: "proposal-1",
      iteration: 2,
      critiqueInputs: [],
    });

    expect(payload).toBeNull();
  });
});
