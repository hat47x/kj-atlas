import { describe, expect, it } from "vitest";

import { analyzeEvidenceGaps } from "./evidence_gap_checks";
import type { DocumentV2 } from "../types";

function makeDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "fact1", text: "F1", x: 0, y: 0, claimType: "fact" },
      { id: "hyp1", text: "H1", x: 0, y: 0, claimType: "hypothesis" },
      { id: "claim1", text: "C1", x: 0, y: 0, claimType: "claim" },
    ],
    edges: [],
    islands: [],
    evidenceLinks: [{ id: "l1", type: "supports", fromCardId: "fact1", toCardId: "hyp1" }],
  };
}

describe("analyzeEvidenceGaps", () => {
  it("reports unsupported claim and unused facts deterministically", () => {
    const report = analyzeEvidenceGaps(makeDoc());
    expect(report.stats.claimsWithNoFactSupport).toBe(1);
    expect(report.findings.some((f) => f.code === "E002" && f.cardIds[0] === "claim1")).toBe(true);
    expect(report.stats.factsUnusedAsEvidence).toBe(0);
  });
});
