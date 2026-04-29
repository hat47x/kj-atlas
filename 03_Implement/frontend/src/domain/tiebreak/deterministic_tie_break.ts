export const DETERMINISTIC_TIE_BREAK_ORDER = [
  "padding",
  "self_intersection",
  "area_delta",
  "vertex_count",
] as const;

export type TieBreakKey = (typeof DETERMINISTIC_TIE_BREAK_ORDER)[number];

export type TieBreakCandidate = {
  candidateId: string;
  outputPolygonHash: string;
  paddingViolationCount: number;
  metrics: Record<TieBreakKey, number>;
};

export type TieBreakAuditEntry = {
  step: number;
  key: TieBreakKey;
  winnerMetric: number;
  loserMetric: number;
  winnerId: string;
  loserId: string;
};

export type TieBreakResult = {
  winner: TieBreakCandidate;
  appliedTieBreakOrder: string;
  auditTrail: TieBreakAuditEntry[];
};

const asOrder = (order: readonly TieBreakKey[]): string => order.join(">");

const compareByKey = (
  left: TieBreakCandidate,
  right: TieBreakCandidate,
  key: TieBreakKey,
): number => {
  const leftMetric = left.metrics[key];
  const rightMetric = right.metrics[key];
  if (leftMetric !== rightMetric) {
    return leftMetric - rightMetric;
  }
  return 0;
};

const compareWithAudit = (
  left: TieBreakCandidate,
  right: TieBreakCandidate,
  order: readonly TieBreakKey[],
): { winner: TieBreakCandidate; loser: TieBreakCandidate; auditTrail: TieBreakAuditEntry[] } => {
  const auditTrail: TieBreakAuditEntry[] = [];

  for (let i = 0; i < order.length; i += 1) {
    const key = order[i];
    const delta = compareByKey(left, right, key);
    if (delta !== 0) {
      const winner = delta < 0 ? left : right;
      const loser = delta < 0 ? right : left;
      auditTrail.push({
        step: i + 1,
        key,
        winnerMetric: winner.metrics[key],
        loserMetric: loser.metrics[key],
        winnerId: winner.candidateId,
        loserId: loser.candidateId,
      });
      return { winner, loser, auditTrail };
    }
  }

  const winner = left.candidateId.localeCompare(right.candidateId) <= 0 ? left : right;
  const loser = winner === left ? right : left;
  auditTrail.push({
    step: order.length + 1,
    key: "vertex_count",
    winnerMetric: winner.metrics.vertex_count,
    loserMetric: loser.metrics.vertex_count,
    winnerId: winner.candidateId,
    loserId: loser.candidateId,
  });
  return { winner, loser, auditTrail };
};

export const pickDeterministicTieBreakWinner = (
  candidates: readonly TieBreakCandidate[],
  order: readonly TieBreakKey[] = DETERMINISTIC_TIE_BREAK_ORDER,
): TieBreakResult => {
  if (candidates.length === 0) {
    throw new Error("pickDeterministicTieBreakWinner requires at least one candidate");
  }

  const [first, ...rest] = candidates;
  let winner = first;
  const mergedAudit: TieBreakAuditEntry[] = [];

  for (const candidate of rest) {
    const compared = compareWithAudit(winner, candidate, order);
    winner = compared.winner;
    mergedAudit.push(...compared.auditTrail);
  }

  return {
    winner,
    appliedTieBreakOrder: asOrder(order),
    auditTrail: mergedAudit,
  };
};

export type ReproductionEvidence = {
  inputHash: string;
  seed: number;
  appliedTieBreakOrder: string;
  outputPolygonHash: string;
  paddingViolationCount: number;
};

export const toReproductionEvidence = (
  inputHash: string,
  seed: number,
  result: TieBreakResult,
): ReproductionEvidence => ({
  inputHash,
  seed,
  appliedTieBreakOrder: result.appliedTieBreakOrder,
  outputPolygonHash: result.winner.outputPolygonHash,
  paddingViolationCount: result.winner.paddingViolationCount,
});
