import { describe, expect, it } from "vitest";
import { buildHilRsStopReport } from "./hil_rs_stop_report";

describe("buildHilRsStopReport", () => {
  it("builds a normalized stop report for contract mismatch escalation", () => {
    const report = buildHilRsStopReport({
      reproductionSteps: [" open merge panel ", "open merge panel", "trigger reversible synthesis"],
      conflictingFiles: ["03_Implement/frontend/src/domain/hil_rs_contract.ts", " 03_Implement/frontend/src/domain/hil_rs_contract.ts "],
      affectedContractIds: ["A1-REDIFF-IF", " A1-ERROR-IF "],
      judgementRequest: " Confirm whether this is an A1 CDC return case. ",
    });

    expect(report).toEqual({
      reproductionSteps: ["open merge panel", "trigger reversible synthesis"],
      conflictingFiles: ["03_Implement/frontend/src/domain/hil_rs_contract.ts"],
      affectedContractIds: ["A1-REDIFF-IF", "A1-ERROR-IF"],
      judgementRequest: "Confirm whether this is an A1 CDC return case.",
    });
  });

  it("fails fast when required stop-report fields are missing", () => {
    expect(() =>
      buildHilRsStopReport({
        reproductionSteps: [],
        conflictingFiles: ["03_Implement/frontend/src/domain/hil_rs_contract.ts"],
        affectedContractIds: ["A1-CRITIQUE-IF"],
        judgementRequest: "review",
      }),
    ).toThrow("stop report requires reproduction steps");

    expect(() =>
      buildHilRsStopReport({
        reproductionSteps: ["repro"],
        conflictingFiles: [],
        affectedContractIds: ["A1-CRITIQUE-IF"],
        judgementRequest: "review",
      }),
    ).toThrow("stop report requires conflicting files");

    expect(() =>
      buildHilRsStopReport({
        reproductionSteps: ["repro"],
        conflictingFiles: ["path"],
        affectedContractIds: ["A1-CRITIQUE-IF"],
        judgementRequest: "   ",
      }),
    ).toThrow("stop report requires a judgement request");
  });
});
