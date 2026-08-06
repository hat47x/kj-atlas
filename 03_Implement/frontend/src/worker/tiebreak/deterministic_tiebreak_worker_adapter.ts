import {
  DETERMINISTIC_TIE_BREAK_ORDER,
  pickDeterministicTieBreakWinner,
  toReproductionEvidence,
  type ReproductionEvidence,
  type TieBreakCandidate,
} from "../../domain/tiebreak/deterministic_tie_break";

export type DeterministicTieBreakWorkerRequest = {
  fixtureId: string;
  inputHash: string;
  seed: number;
  candidates: TieBreakCandidate[];
};

export type DeterministicTieBreakWorkerResponse = {
  fixtureId: string;
  evidence: ReproductionEvidence;
};

export const runDeterministicTieBreakWorker = (
  request: DeterministicTieBreakWorkerRequest,
): DeterministicTieBreakWorkerResponse => {
  const result = pickDeterministicTieBreakWinner(
    request.candidates,
    DETERMINISTIC_TIE_BREAK_ORDER,
  );

  return {
    fixtureId: request.fixtureId,
    evidence: toReproductionEvidence(request.inputHash, request.seed, result),
  };
};
