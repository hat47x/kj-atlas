import {
  P2A02_CONTRACT_ID,
  P2A02_CONTRACT_VERSION,
  P2A_A1_CONTRACT_LOCK,
  type P2AA1ContractLock,
  type P2AImplementationReadiness,
  type P2AMockFixture,
  type P2AMockCaseId,
  type P2AValidationLog,
} from "./contract";

const REQUIRED_CASES: readonly P2AMockCaseId[] = ["M1", "M2", "M3", "M4"] as const;

export function validateP2AA1ContractLock(lock: P2AA1ContractLock): { ok: boolean; errors: string[] } {
  const errors: string[] = [];

  if (lock.contractId !== P2A02_CONTRACT_ID) {
    errors.push("contractId mismatch");
  }

  if (lock.contractVersion !== P2A02_CONTRACT_VERSION) {
    errors.push("contractVersion mismatch");
  }

  for (const field of P2A_A1_CONTRACT_LOCK.requiredFields) {
    if (!lock.requiredFields.includes(field)) {
      errors.push(`required field missing: ${field}`);
    }
  }

  for (const invariant of P2A_A1_CONTRACT_LOCK.invariants) {
    if (!lock.invariants.includes(invariant)) {
      errors.push(`invariant missing: ${invariant}`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export function validateP2AA2FixtureSignature(fixtures: readonly P2AMockFixture[]): { ok: boolean; errors: string[] } {
  const errors: string[] = [];
  const seenCases = new Set<P2AMockCaseId>();

  for (const fixture of fixtures) {
    const payload = fixture.payload;

    if (payload.contractId !== P2A02_CONTRACT_ID) {
      errors.push(`${fixture.fixtureId}: invalid contractId`);
    }

    if (payload.contractVersion !== P2A02_CONTRACT_VERSION) {
      errors.push(`${fixture.fixtureId}: invalid contractVersion`);
    }

    if (payload.mockCaseId !== fixture.mockCaseId) {
      errors.push(`${fixture.fixtureId}: payload mockCaseId mismatch`);
    }

    if (payload.evidence.trim().length === 0) {
      errors.push(`${fixture.fixtureId}: empty evidence`);
    }

    if (seenCases.has(fixture.mockCaseId)) {
      errors.push(`${fixture.fixtureId}: duplicate mockCaseId=${fixture.mockCaseId}`);
    }
    seenCases.add(fixture.mockCaseId);
  }

  for (const requiredCase of REQUIRED_CASES) {
    if (!seenCases.has(requiredCase)) {
      errors.push(`missing fixture for ${requiredCase}`);
    }
  }

  return { ok: errors.length === 0, errors };
}

export function toP2AValidationLedger(fixtures: readonly P2AMockFixture[]): P2AValidationLog[] {
  return fixtures.map((fixture) => ({
    contractId: P2A02_CONTRACT_ID,
    contractVersion: P2A02_CONTRACT_VERSION,
    mockCaseId: fixture.mockCaseId,
    validationResult: fixture.payload.validationResult,
    ownerOfFix: fixture.payload.ownerOfFix,
    evidence: fixture.payload.evidence,
  }));
}

export function evaluateP2AA3Proceed(logs: readonly P2AValidationLog[]): { go: boolean; reason: string } {
  const byCase = new Map<P2AMockCaseId, P2AValidationLog>();

  for (const log of logs) {
    if (byCase.has(log.mockCaseId)) {
      return { go: false, reason: `duplicate mock case: ${log.mockCaseId}` };
    }

    if (log.contractId !== P2A02_CONTRACT_ID || log.contractVersion !== P2A02_CONTRACT_VERSION) {
      return { go: false, reason: "contract freeze mismatch" };
    }

    byCase.set(log.mockCaseId, log);
  }

  for (const requiredCase of REQUIRED_CASES) {
    if (!byCase.has(requiredCase)) {
      return { go: false, reason: `missing mock case: ${requiredCase}` };
    }
  }

  const m1 = byCase.get("M1");
  const m2 = byCase.get("M2");
  const m3 = byCase.get("M3");
  const m4 = byCase.get("M4");

  if (!m1 || !m2 || !m3 || !m4) {
    return { go: false, reason: "mock case unpack failed" };
  }

  if (m1.validationResult !== "pass" || m2.validationResult !== "pass" || m3.validationResult !== "pass") {
    return { go: false, reason: "M1/M2/M3 must be pass" };
  }

  if (m4.validationResult !== "fail") {
    return { go: false, reason: "M4 must be fail" };
  }

  if (m1.ownerOfFix !== "A3" || m2.ownerOfFix !== "A3" || m3.ownerOfFix !== "A3") {
    return { go: false, reason: "M1/M2/M3 ownerOfFix must be A3" };
  }

  if (m4.ownerOfFix !== "A2") {
    return { go: false, reason: "M4 ownerOfFix must be A2" };
  }

  return { go: true, reason: "go" };
}

export function buildP2AImplementationReadiness(logs: readonly P2AValidationLog[]): P2AImplementationReadiness {
  const proceed = evaluateP2AA3Proceed(logs);
  if (proceed.go) {
    return {
      implementationReadiness: "go",
      acceptedMockCases: ["M1", "M2", "M3"],
      blockedMockCases: ["M4"],
      rollbackTrigger: [],
      notes: ["GoNoGo passed (M1/M2/M3=pass and M4=fail)"],
    };
  }

  return {
    implementationReadiness: "no-go",
    acceptedMockCases: [],
    blockedMockCases: [...REQUIRED_CASES],
    rollbackTrigger: [proceed.reason],
    notes: ["Rollback to A2 fixed ledger and resolve ownerOfFix / contract mismatch"],
  };
}
