import { describe, expect, it } from "vitest";

import {
  DETERMINISTIC_TIE_BREAK_ORDER,
  pickDeterministicTieBreakWinner,
  toReproductionEvidence,
  type TieBreakCandidate,
} from "./deterministic_tie_break";

const makeCandidate = (
  candidateId: string,
  metrics: TieBreakCandidate["metrics"],
): TieBreakCandidate => ({
  candidateId,
  outputPolygonHash: `hash-${candidateId}`,
  paddingViolationCount: metrics.padding,
  metrics,
});

describe("deterministic_tie_break", () => {
  it("throws when candidates are empty", () => {
    expect(() => pickDeterministicTieBreakWinner([])).toThrowError(
      "pickDeterministicTieBreakWinner requires at least one candidate",
    );
  });

  it("resolves ties in declared order and records audit trail", () => {
    const result = pickDeterministicTieBreakWinner([
      makeCandidate("b", {
        padding: 0,
        self_intersection: 1,
        area_delta: 3,
        vertex_count: 5,
      }),
      makeCandidate("a", {
        padding: 0,
        self_intersection: 1,
        area_delta: 2,
        vertex_count: 6,
      }),
      makeCandidate("c", {
        padding: 1,
        self_intersection: 0,
        area_delta: 0,
        vertex_count: 0,
      }),
    ]);

    expect(result.appliedTieBreakOrder).toBe(DETERMINISTIC_TIE_BREAK_ORDER.join(">"));
    expect(result.winner.candidateId).toBe("a");
    expect(result.auditTrail).toEqual([
      {
        step: 3,
        key: "area_delta",
        winnerMetric: 2,
        loserMetric: 3,
        winnerId: "a",
        loserId: "b",
      },
      {
        step: 1,
        key: "padding",
        winnerMetric: 0,
        loserMetric: 1,
        winnerId: "a",
        loserId: "c",
      },
    ]);
  });

  it("maps winner data into reproduction evidence", () => {
    const result = pickDeterministicTieBreakWinner([
      makeCandidate("winner", {
        padding: 0,
        self_intersection: 0,
        area_delta: 0,
        vertex_count: 4,
      }),
    ]);

    expect(toReproductionEvidence("input-hash", 7, result)).toEqual({
      inputHash: "input-hash",
      seed: 7,
      appliedTieBreakOrder: DETERMINISTIC_TIE_BREAK_ORDER.join(">"),
      outputPolygonHash: "hash-winner",
      paddingViolationCount: 0,
    });
  });
});
