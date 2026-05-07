export type HilRsStopReportInput = {
  reproductionSteps: string[];
  conflictingFiles: string[];
  judgementRequest: string;
  affectedContractIds: string[];
};

export type HilRsStopReport = {
  reproductionSteps: string[];
  conflictingFiles: string[];
  judgementRequest: string;
  affectedContractIds: string[];
};

function normalizedUnique(values: string[]): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  for (const value of values) {
    const normalized = value.trim();
    if (!normalized || seen.has(normalized)) continue;
    seen.add(normalized);
    result.push(normalized);
  }
  return result;
}

export function buildHilRsStopReport(input: HilRsStopReportInput): HilRsStopReport {
  const reproductionSteps = normalizedUnique(input.reproductionSteps);
  const conflictingFiles = normalizedUnique(input.conflictingFiles);
  const affectedContractIds = normalizedUnique(input.affectedContractIds);
  const judgementRequest = input.judgementRequest.trim();

  if (reproductionSteps.length === 0) throw new Error("stop report requires reproduction steps");
  if (conflictingFiles.length === 0) throw new Error("stop report requires conflicting files");
  if (!judgementRequest) throw new Error("stop report requires a judgement request");
  if (affectedContractIds.length === 0) throw new Error("stop report requires affected contract IDs");

  return {
    reproductionSteps,
    conflictingFiles,
    judgementRequest,
    affectedContractIds,
  };
}
