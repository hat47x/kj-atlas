import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeClaimTypeMix } from "./claim_type_checks";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    relationSummaries: [],
  };
}

describe("analyzeClaimTypeMix", () => {
  it("treats missing claimType as unknown and is deterministic", () => {
    const doc = buildDoc();
    doc.cards = [
      { id: "c1", text: "", x: 0, y: 0 },
      { id: "c2", text: "", x: 0, y: 0, claimType: "fact" },
      { id: "c3", text: "", x: 0, y: 0, claimType: "claim" },
      { id: "c4", text: "", x: 0, y: 0, claimType: "hypothesis" },
      { id: "c5", text: "", x: 0, y: 0 },
    ];
    doc.islands = [{ id: "I1", cardIds: ["c1", "c2", "c3", "c4", "c5"] }];

    const first = analyzeClaimTypeMix(doc, "2026-01-01T00:00:00.000Z");
    const second = analyzeClaimTypeMix(doc, "2026-01-01T00:00:00.000Z");

    expect(second).toEqual(first);
    expect(first.stats.countsByType.unknown).toBe(2);
    expect(first.findings.some((finding) => finding.code === "T001")).toBe(true);
  });

  it("reports T002, T003 and T004 with thresholds", () => {
    const doc = buildDoc();
    doc.cards = Array.from({ length: 20 }, (_, index) => {
      if (index < 8) {
        return { id: `h${index}`, text: "", x: 0, y: 0, claimType: "hypothesis" as const };
      }
      if (index < 13) {
        return { id: `u${index}`, text: "", x: 0, y: 0 };
      }
      if (index < 18) {
        return { id: `uu${index}`, text: "", x: 0, y: 0 };
      }
      return { id: `c${index}`, text: "", x: 0, y: 0, claimType: "claim" as const };
    });

    doc.islands = [
      { id: "I-h", cardIds: doc.cards.slice(0, 8).map((card) => card.id) },
      { id: "I-u", cardIds: doc.cards.slice(8, 18).map((card) => card.id) },
      { id: "I-small", cardIds: ["c18", "c19"] },
    ];

    const report = analyzeClaimTypeMix(doc, "2026-01-01T00:00:00.000Z");

    expect(report.findings.some((finding) => finding.code === "T002" && finding.islandIds[0] === "I-h")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "T003" && finding.islandIds[0] === "I-u")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "T004")).toBe(true);
    expect(report.stats.islandsChecked).toBe(2);
  });
});
