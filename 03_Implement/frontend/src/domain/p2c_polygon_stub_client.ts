import {
  buildP2CMockValidationLog,
  evaluateP2CA3StartCondition,
  P2C_A2_HANDOFF_ID,
  P2C_DETERMINISTIC_TIE_BREAK_ORDER,
  type Point,
} from "./p2c_polygon_handoff";

export const P2C_APPLIED_TIE_BREAK_ORDER = "padding>self_intersection>area_delta>vertex_count" as const;

export type P2CFixtureCase = {
  mockCaseId: "A" | "B" | "C";
  seed: number;
  padding: number;
  points: readonly Point[];
};

export type P2CFixtureBundle = {
  schemaVersion: "1.0.0";
  handoffId: typeof P2C_A2_HANDOFF_ID;
  appliedTieBreakOrder: typeof P2C_APPLIED_TIE_BREAK_ORDER;
  cases: readonly P2CFixtureCase[];
};

export type P2CStubRunResult = {
  handoffId: typeof P2C_A2_HANDOFF_ID;
  appliedTieBreakOrder: typeof P2C_APPLIED_TIE_BREAK_ORDER;
  logs: ReturnType<typeof buildP2CMockValidationLog>[];
  goNoGo: ReturnType<typeof evaluateP2CA3StartCondition>;
};

export function runP2CMockValidation(bundle: P2CFixtureBundle): P2CStubRunResult {
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
    logs,
    goNoGo: evaluateP2CA3StartCondition(logs, { gateApproved: true, a2VerifyPass: true }),
  };
}
