import { describe, expect, it } from "vitest";

import fixtureRaw from "../../tests/fixtures/fb_p2c_01/polygon_autofit_cases.json?raw";
import { P2C_A2_HANDOFF_ID } from "./p2c_polygon_handoff";
import {
  P2C_APPLIED_TIE_BREAK_ORDER,
  runP2CMockValidation,
  type P2CFixtureBundle,
} from "./p2c_polygon_stub_client";

const FIXTURE = JSON.parse(fixtureRaw) as P2CFixtureBundle;

describe("p2c_polygon_stub_client", () => {
  it("replays fixture + stub in integration grain and keeps deterministic hashes", () => {
    const first = runP2CMockValidation(FIXTURE);
    const second = runP2CMockValidation(FIXTURE);

    expect(first.handoffId).toBe(P2C_A2_HANDOFF_ID);
    expect(first.appliedTieBreakOrder).toBe(P2C_APPLIED_TIE_BREAK_ORDER);
    expect(first.logs).toHaveLength(3);
    expect(first.logs.map((log) => log.outputPolygonHash)).toEqual(second.logs.map((log) => log.outputPolygonHash));
    expect(first.logs.map((log) => log.paddingViolationCount)).toEqual([0, 0, 0]);
    expect(first.goNoGo).toEqual({ go: true, reason: "go" });
  });

  it("fails fast when fixture tie-break order drifts from A1 contract", () => {
    const drifted = {
      ...FIXTURE,
      appliedTieBreakOrder: "padding>area_delta>self_intersection>vertex_count",
    } as unknown as P2CFixtureBundle;

    expect(() => runP2CMockValidation(drifted)).toThrowError("appliedTieBreakOrder mismatch");
  });

  it("fails fast when fixture schemaVersion drifts", () => {
    const drifted = {
      ...FIXTURE,
      schemaVersion: "2.0.0",
    } as unknown as P2CFixtureBundle;

    expect(() => runP2CMockValidation(drifted)).toThrowError("unsupported schemaVersion: 2.0.0");
  });

  it("fails fast when required case is missing from bundle", () => {
    const drifted = {
      ...FIXTURE,
      cases: FIXTURE.cases.filter((item) => item.mockCaseId !== "C"),
    } as unknown as P2CFixtureBundle;

    expect(() => runP2CMockValidation(drifted)).toThrowError("missing mockCaseId: C");
  });

  it("fails fast when point values are non-finite", () => {
    const driftedCases = [...FIXTURE.cases];
    driftedCases[0] = {
      ...driftedCases[0],
      points: [{ ...driftedCases[0].points[0], x: Number.NaN }, ...driftedCases[0].points.slice(1)],
    };
    const drifted = {
      ...FIXTURE,
      cases: driftedCases,
    } as unknown as P2CFixtureBundle;

    expect(() => runP2CMockValidation(drifted)).toThrowError("cases[0].points[0].x must be a finite number");
  });
});
