import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeEvidenceGaps } from "./evidence_gap_checks";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    evidenceLinks: [],
  };
}

describe("analyzeEvidenceGaps", () => {
  it("reports deterministic findings for unsupported hypotheses/claims and unused facts", () => {
    const doc = makeDoc();
    doc.cards = [
      { id: "f1", text: "fact a", x: 0, y: 0, claimType: "fact" },
      { id: "f2", text: "fact b", x: 0, y: 0, claimType: "fact" },
      { id: "h1", text: "hypothesis", x: 0, y: 0, claimType: "hypothesis" },
      { id: "c1", text: "claim", x: 0, y: 0, claimType: "claim" },
    ];

    doc.evidenceLinks = [{ id: "l1", type: "supports", fromCardId: "f1", toCardId: "c1" }];

    const first = analyzeEvidenceGaps(doc);
    const second = analyzeEvidenceGaps(doc);

    expect(first.findings.map((finding) => `${finding.code}:${finding.cardIds.join(",")}`)).toEqual(
      second.findings.map((finding) => `${finding.code}:${finding.cardIds.join(",")}`)
    );
    expect(first.stats.hypothesesWithNoFactSupport).toBe(1);
    expect(first.stats.claimsWithNoFactSupport).toBe(0);
    expect(first.stats.factsUnusedAsEvidence).toBe(1);
  });

  it("reports E004 when contradiction has no fact support on either side", () => {
    const doc = makeDoc();
    doc.cards = [
      { id: "a", text: "A", x: 0, y: 0, claimType: "claim" },
      { id: "b", text: "B", x: 0, y: 0, claimType: "hypothesis" },
      { id: "f", text: "fact", x: 0, y: 0, claimType: "fact" },
    ];
    doc.evidenceLinks = [{ id: "cx", type: "contradicts", fromCardId: "a", toCardId: "b" }];

    const report = analyzeEvidenceGaps(doc);
    expect(report.findings.some((finding) => finding.code === "E004")).toBe(true);

    doc.evidenceLinks.push({ id: "sx", type: "supports", fromCardId: "f", toCardId: "a" });
    const grounded = analyzeEvidenceGaps(doc);
    expect(grounded.findings.some((finding) => finding.code === "E004")).toBe(false);
  });
});
