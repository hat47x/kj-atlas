import { describe, expect, it } from "vitest";

import {
  P2C_DETERMINISTIC_TIE_BREAK_ORDER,
  isP2CTieBreakOrderFixed,
  selectDeterministicP2CCandidate,
} from "./p2c_tie_break_contract";

describe("p2c_tie_break_contract", () => {
  it("keeps the fixed tie-break order", () => {
    expect(isP2CTieBreakOrderFixed(P2C_DETERMINISTIC_TIE_BREAK_ORDER)).toBe(true);
    expect(
      isP2CTieBreakOrderFixed([
        "padding_compliance",
        "area_delta_minimization",
        "self_intersection_avoidance",
        "vertex_count_minimization",
      ]),
    ).toBe(false);
  });

  it("selects winner by deterministic order", () => {
    const winner = selectDeterministicP2CCandidate([
      {
        candidateId: "b",
        score: {
          padding_compliance: 1,
          self_intersection_avoidance: 1,
          area_delta_minimization: 9,
          vertex_count_minimization: 9,
        },
      },
      {
        candidateId: "a",
        score: {
          padding_compliance: 1,
          self_intersection_avoidance: 2,
          area_delta_minimization: 0,
          vertex_count_minimization: 0,
        },
      },
    ]);

    expect(winner?.candidateId).toBe("a");
  });

  it("falls back to candidateId when all scores are tied", () => {
    const winner = selectDeterministicP2CCandidate([
      {
        candidateId: "b",
        score: {
          padding_compliance: 1,
          self_intersection_avoidance: 1,
          area_delta_minimization: 1,
          vertex_count_minimization: 1,
        },
      },
      {
        candidateId: "a",
        score: {
          padding_compliance: 1,
          self_intersection_avoidance: 1,
          area_delta_minimization: 1,
          vertex_count_minimization: 1,
        },
      },
    ]);

    expect(winner?.candidateId).toBe("a");
  });
});
