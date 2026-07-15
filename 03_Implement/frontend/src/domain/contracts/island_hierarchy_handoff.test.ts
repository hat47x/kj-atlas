import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { validateIslandHierarchyContractV1 } from "./island_contracts";
import {
  evaluateIslandHierarchyA3GoNoGo,
  projectIslandHierarchyContractV1,
  toIslandHierarchyValidationLog,
  validateIslandHierarchyRoundTrip,
} from "./island_hierarchy_handoff";

function createHierarchyDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-hierarchy",
    createdAt: "2026-03-01T00:00:00.000Z",
    updatedAt: "2026-03-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-root", text: "root", x: 0, y: 0 },
      { id: "c-child", text: "child", x: 10, y: 0 },
      { id: "c-grand", text: "grand", x: 20, y: 0 },
    ],
    edges: [],
    islands: [
      { id: "root", cardIds: ["c-root"] },
      { id: "child", cardIds: ["c-child"], parentIslandId: "root" },
      { id: "grand", cardIds: ["c-grand"], parentIslandId: "child" },
    ],
  };
}

describe("projectIslandHierarchyContractV1", () => {
  it("projects parent/child edges from DocumentV1 islands", () => {
    const projected = projectIslandHierarchyContractV1(createHierarchyDocument());

    expect(projected).toEqual({
      schemaVersion: "1",
      islands: [
        { id: "root", parentIslandId: null, childIslandIds: ["child"] },
        { id: "child", parentIslandId: "root", childIslandIds: ["grand"] },
        { id: "grand", parentIslandId: "child", childIslandIds: [] },
      ],
    });
  });
});

describe("A2→A3 handoff logs", () => {
  it("builds Go logs for M1/M2 and fail logs for M3/M4", () => {
    const m1 = toIslandHierarchyValidationLog(
      "M1",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [{ id: "root", parentIslandId: null, childIslandIds: [] }],
      }),
      "A2",
      "root island accepted",
    );

    const m2 = toIslandHierarchyValidationLog(
      "M2",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [
          { id: "root", parentIslandId: null, childIslandIds: ["child"] },
          { id: "child", parentIslandId: "root", childIslandIds: ["grand"] },
          { id: "grand", parentIslandId: "child", childIslandIds: [] },
        ],
      }),
      "A2",
      "3-level hierarchy accepted",
    );

    const m3 = toIslandHierarchyValidationLog(
      "M3",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [{ id: "child", parentIslandId: "unknown", childIslandIds: [] }],
      }),
      "A1",
      "missing parent rejected",
    );

    const m4 = toIslandHierarchyValidationLog(
      "M4",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [
          { id: "a", parentIslandId: "b", childIslandIds: ["b"] },
          { id: "b", parentIslandId: "a", childIslandIds: ["a"] },
        ],
      }),
      "A1",
      "cycle rejected",
    );

    expect(evaluateIslandHierarchyA3GoNoGo([m1, m2, m3, m4])).toEqual({ go: true, reason: "go" });
  });

  it("returns NoGo when required case is missing", () => {
    const m1 = toIslandHierarchyValidationLog(
      "M1",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [{ id: "root", parentIslandId: null, childIslandIds: [] }],
      }),
      "A2",
      "root island accepted",
    );

    const m2 = toIslandHierarchyValidationLog(
      "M2",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [
          { id: "root", parentIslandId: null, childIslandIds: ["child"] },
          { id: "child", parentIslandId: "root", childIslandIds: [] },
        ],
      }),
      "A2",
      "2-level hierarchy accepted",
    );

    const m4 = toIslandHierarchyValidationLog(
      "M4",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [
          { id: "a", parentIslandId: "b", childIslandIds: ["b"] },
          { id: "b", parentIslandId: "a", childIslandIds: ["a"] },
        ],
      }),
      "A1",
      "cycle rejected",
    );

    expect(evaluateIslandHierarchyA3GoNoGo([m1, m2, m4])).toEqual({ go: false, reason: "missing mock case: M3" });
  });

  it("returns NoGo when duplicate mock case is provided", () => {
    const m1 = toIslandHierarchyValidationLog(
      "M1",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [{ id: "root", parentIslandId: null, childIslandIds: [] }],
      }),
      "A2",
      "root island accepted",
    );

    expect(evaluateIslandHierarchyA3GoNoGo([m1, m1])).toEqual({ go: false, reason: "duplicate mock case: M1" });
  });

  it("returns NoGo when contract version mismatches", () => {
    const m1 = toIslandHierarchyValidationLog(
      "M1",
      validateIslandHierarchyContractV1({
        schemaVersion: "2.0.0",
        islands: [{ id: "root", parentIslandId: null, childIslandIds: [] }],
      }),
      "A2",
      "root island accepted",
    );
    const mismatched = {
      ...m1,
      contractVersion: "IslandVisibilityContractV1",
    } as unknown as (typeof m1);

    expect(evaluateIslandHierarchyA3GoNoGo([mismatched])).toEqual({
      go: false,
      reason: "contract version mismatch: IslandVisibilityContractV1",
    });
  });
});

describe("validateIslandHierarchyRoundTrip", () => {
  it("keeps hierarchy valid after serialize/deserialize roundtrip", () => {
    const result = validateIslandHierarchyRoundTrip(createHierarchyDocument());
    expect(result.ok).toBe(true);
  });
});
