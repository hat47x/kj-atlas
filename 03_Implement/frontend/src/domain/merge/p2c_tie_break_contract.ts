export const P2C_TIE_BREAK_SCHEMA_VERSION = "1.0.0" as const;

export const P2C_DETERMINISTIC_TIE_BREAK_ORDER = [
  "padding_compliance",
  "self_intersection_avoidance",
  "area_delta_minimization",
  "vertex_count_minimization",
] as const;

export type P2CTieBreakKey = (typeof P2C_DETERMINISTIC_TIE_BREAK_ORDER)[number];

type TieBreakScore = Record<P2CTieBreakKey, number>;

export type P2CCandidateScore = {
  candidateId: string;
  score: TieBreakScore;
};

export function isP2CTieBreakOrderFixed(order: readonly string[]): boolean {
  return order.join(",") === P2C_DETERMINISTIC_TIE_BREAK_ORDER.join(",");
}

export function selectDeterministicP2CCandidate(candidates: readonly P2CCandidateScore[]): P2CCandidateScore | null {
  if (candidates.length === 0) {
    return null;
  }

  const sorted = [...candidates].sort((left, right) => {
    for (const key of P2C_DETERMINISTIC_TIE_BREAK_ORDER) {
      const delta = right.score[key] - left.score[key];
      if (delta !== 0) {
        return delta;
      }
    }
    return left.candidateId.localeCompare(right.candidateId);
  });

  return sorted[0] ?? null;
}
