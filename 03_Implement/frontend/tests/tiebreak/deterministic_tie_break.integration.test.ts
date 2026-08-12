import { describe, expect, it } from "vitest";
import cases from "./fb_p2c_deterministic_cases.json";
// DX-CLEANUP-08 (option a): this adapter has no production caller -- it is
// intentionally kept as a thin wrapper for THIS integration test, which runs
// under tests/tiebreak/vitest.config.tiebreak.ts (a separate vitest config).
// It verifies the domain's deterministic tie-break contract end-to-end
// through the worker-shaped entry point. Do not delete it.
import { runDeterministicTieBreakWorker } from "../../src/worker/tiebreak/deterministic_tiebreak_worker_adapter";

const EXPECTED_ORDER = "padding>self_intersection>area_delta>vertex_count";

type FixtureCase = {
  fixtureId: string;
  inputHash: string;
  seed: number;
  candidates: Parameters<typeof runDeterministicTieBreakWorker>[0]["candidates"];
};

describe("FB-P2C deterministic tie-break reproduction", () => {
  it("reproduces stable output hash over 3 repeated runs for same input and seed", () => {
    const target = (cases as FixtureCase[]).find((entry) => entry.fixtureId === "case-a-repeatable");
    expect(target).toBeDefined();

    const run1 = runDeterministicTieBreakWorker(target!);
    const run2 = runDeterministicTieBreakWorker(target!);
    const run3 = runDeterministicTieBreakWorker(target!);

    expect(run1.evidence.outputPolygonHash).toBe(run2.evidence.outputPolygonHash);
    expect(run2.evidence.outputPolygonHash).toBe(run3.evidence.outputPolygonHash);
    expect(run1.evidence.appliedTieBreakOrder).toBe(EXPECTED_ORDER);
  });

  it("keeps paddingViolationCount at zero for accepted fixtures", () => {
    const results = (cases as FixtureCase[]).map((entry) => runDeterministicTieBreakWorker(entry));
    for (const result of results) {
      expect(result.evidence.paddingViolationCount).toBe(0);
      expect(result.evidence.appliedTieBreakOrder).toBe(EXPECTED_ORDER);
    }
  });

  it("prioritizes padding metric before other metrics in conflict case", () => {
    const conflict = (cases as FixtureCase[]).find(
      (entry) => entry.fixtureId === "case-c-padding-priority",
    );
    expect(conflict).toBeDefined();

    const result = runDeterministicTieBreakWorker(conflict!);
    expect(result.evidence.outputPolygonHash).toBe("out-safe");
    expect(result.evidence.paddingViolationCount).toBe(0);
    expect(result.evidence.appliedTieBreakOrder).toBe(EXPECTED_ORDER);
  });
});
