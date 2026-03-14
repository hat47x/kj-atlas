import { describe, expect, it } from "vitest";

import {
  buildP2CMockValidationLog,
  evaluateP2CA3StartCondition,
  P2C_A2_HANDOFF_ID,
  P2C_DETERMINISTIC_TIE_BREAK_ORDER,
  toPolygonInputHash,
} from "./p2c_polygon_handoff";

const fixture = [
  { x: 90, y: 80 },
  { x: 250, y: 72 },
  { x: 318, y: 156 },
  { x: 282, y: 248 },
  { x: 154, y: 290 },
  { x: 78, y: 188 },
] as const;

describe("p2c_polygon_handoff", () => {
  it("builds deterministic A2 mock log with fixed comparison keys", () => {
    const first = buildP2CMockValidationLog("A", fixture, 20260314, 24);
    const second = buildP2CMockValidationLog("A", fixture, 20260314, 24);

    expect(first.handoffId).toBe(P2C_A2_HANDOFF_ID);
    expect(first.inputHash).toBe(second.inputHash);
    expect(first.outputPolygonHash).toBe(second.outputPolygonHash);
    expect(first.paddingViolationCount).toBe(0);
    expect(first.tieBreakOrder).toEqual(P2C_DETERMINISTIC_TIE_BREAK_ORDER);
  });

  it("fails start condition when tie-break order is changed", () => {
    const validA = buildP2CMockValidationLog("A", fixture, 1, 24);
    const validB = buildP2CMockValidationLog("B", fixture.slice(0, 3), 1, 8);
    const validC = buildP2CMockValidationLog("C", fixture, 2, 36);

    const result = evaluateP2CA3StartCondition(
      [
        validA,
        validB,
        {
          ...validC,
          tieBreakOrder: [...validC.tieBreakOrder].reverse(),
        },
      ],
      { gateApproved: true, a2VerifyPass: true }
    );

    expect(result).toEqual({ go: false, reason: "tieBreakOrderChanged=true" });
  });

  it("returns Go for A/B/C with Gate0 approved and A2 verify pass", () => {
    const logs = [
      buildP2CMockValidationLog("A", fixture, 1, 24),
      buildP2CMockValidationLog("B", fixture.slice(0, 3), 2, 12),
      buildP2CMockValidationLog("C", fixture, 3, 36),
    ];

    const result = evaluateP2CA3StartCondition(logs, { gateApproved: true, a2VerifyPass: true });

    expect(result).toEqual({ go: true, reason: "go" });
  });

  it("includes seed into input hash contract", () => {
    const hashA = toPolygonInputHash(fixture, 1);
    const hashB = toPolygonInputHash(fixture, 2);
    expect(hashA).not.toBe(hashB);
  });
});
