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
    const drifted: P2CFixtureBundle = {
      ...FIXTURE,
      appliedTieBreakOrder: "padding>area_delta>self_intersection>vertex_count",
    };

    expect(() => runP2CMockValidation(drifted)).toThrowError("appliedTieBreakOrder mismatch");
  });
});
