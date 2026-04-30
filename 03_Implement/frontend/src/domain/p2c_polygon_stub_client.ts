import {
  buildP2CMockValidationLog,
  evaluateP2CA3StartCondition,
  P2C_A2_HANDOFF_ID,
  type Point,
} from "./p2c_polygon_handoff";
import {
  P2C_DETERMINISTIC_TIE_BREAK_ORDER,
  P2C_TIE_BREAK_CONTRACT_ID,
  P2C_TIE_BREAK_SCHEMA_VERSION,
} from "./merge/p2c_tie_break_contract";

export const P2C_APPLIED_TIE_BREAK_ORDER = "padding>self_intersection>area_delta>vertex_count" as const;

export type P2CFixtureCase = {
  mockCaseId: "A" | "B" | "C";
  seed: number;
  padding: number;
  points: readonly Point[];
};

export type P2CFixtureBundle = {
  schemaVersion: typeof P2C_TIE_BREAK_SCHEMA_VERSION;
  tieBreakContractId: typeof P2C_TIE_BREAK_CONTRACT_ID;
  handoffId: typeof P2C_A2_HANDOFF_ID;
  appliedTieBreakOrder: typeof P2C_APPLIED_TIE_BREAK_ORDER;
  cases: readonly P2CFixtureCase[];
};

export type P2CStubRunResult = {
  handoffId: typeof P2C_A2_HANDOFF_ID;
  appliedTieBreakOrder: typeof P2C_APPLIED_TIE_BREAK_ORDER;
  tieBreakContractId: typeof P2C_TIE_BREAK_CONTRACT_ID;
  logs: ReturnType<typeof buildP2CMockValidationLog>[];
  goNoGo: ReturnType<typeof evaluateP2CA3StartCondition>;
};

const P2C_REQUIRED_CASES = ["A", "B", "C"] as const;

function assertFiniteNumber(value: number, fieldPath: string): void {
  if (!Number.isFinite(value)) {
    throw new Error(`${fieldPath} must be a finite number`);
  }
}

function assertBundleContract(bundle: P2CFixtureBundle): void {
  if (bundle.schemaVersion !== P2C_TIE_BREAK_SCHEMA_VERSION) {
    throw new Error(`unsupported schemaVersion: ${bundle.schemaVersion}`);
  }

  if (bundle.tieBreakContractId !== P2C_TIE_BREAK_CONTRACT_ID) {
    throw new Error(`unexpected tieBreakContractId: ${bundle.tieBreakContractId}`);
  }

  const seenCases = new Set<P2CFixtureCase["mockCaseId"]>();
  for (const [caseIndex, testCase] of bundle.cases.entries()) {
    if (seenCases.has(testCase.mockCaseId)) {
      throw new Error(`duplicate mockCaseId: ${testCase.mockCaseId}`);
    }
    seenCases.add(testCase.mockCaseId);

    assertFiniteNumber(testCase.seed, `cases[${caseIndex}].seed`);
    assertFiniteNumber(testCase.padding, `cases[${caseIndex}].padding`);
    for (const [pointIndex, point] of testCase.points.entries()) {
      assertFiniteNumber(point.x, `cases[${caseIndex}].points[${pointIndex}].x`);
      assertFiniteNumber(point.y, `cases[${caseIndex}].points[${pointIndex}].y`);
    }
  }

  for (const requiredCase of P2C_REQUIRED_CASES) {
    if (!seenCases.has(requiredCase)) {
      throw new Error(`missing mockCaseId: ${requiredCase}`);
    }
  }
}

export function runP2CMockValidation(bundle: P2CFixtureBundle): P2CStubRunResult {
  assertBundleContract(bundle);

  if (bundle.handoffId !== P2C_A2_HANDOFF_ID) {
    throw new Error(`unexpected handoffId: ${bundle.handoffId}`);
  }
  if (bundle.appliedTieBreakOrder !== P2C_APPLIED_TIE_BREAK_ORDER) {
    throw new Error("appliedTieBreakOrder mismatch");
  }

  const logs = bundle.cases.map((testCase) =>
    buildP2CMockValidationLog(testCase.mockCaseId, testCase.points, testCase.seed, testCase.padding),
  );

  for (const log of logs) {
    if (log.tieBreakOrder.join(">") !== P2C_DETERMINISTIC_TIE_BREAK_ORDER.join(">")) {
      throw new Error("deterministic tie-break contract changed");
    }
  }

  return {
    handoffId: P2C_A2_HANDOFF_ID,
    appliedTieBreakOrder: P2C_APPLIED_TIE_BREAK_ORDER,
    tieBreakContractId: P2C_TIE_BREAK_CONTRACT_ID,
    logs,
    goNoGo: evaluateP2CA3StartCondition(logs, { gateApproved: true, a2VerifyPass: true }),
  };
}
