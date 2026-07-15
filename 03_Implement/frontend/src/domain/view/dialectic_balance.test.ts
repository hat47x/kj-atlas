import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeDialecticBalance } from "./dialectic_balance";

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

describe("analyzeDialecticBalance", () => {
  it("is deterministic and computes core ratios", () => {
    const doc = makeDoc();
    doc.cards = [
      { id: "f1", text: "f1", x: 0, y: 0, claimType: "fact" },
      { id: "h1", text: "h1", x: 0, y: 0, claimType: "hypothesis" },
      { id: "h2", text: "h2", x: 0, y: 0, claimType: "hypothesis" },
      { id: "c1", text: "c1", x: 0, y: 0, claimType: "claim" },
      { id: "c2", text: "c2", x: 0, y: 0, claimType: "claim" },
      { id: "c3", text: "c3", x: 0, y: 0, claimType: "claim" },
      { id: "c4", text: "c4", x: 0, y: 0, claimType: "claim" },
      { id: "c5", text: "c5", x: 0, y: 0, claimType: "claim" },
      { id: "u1", text: "u1", x: 0, y: 0, claimType: "unknown" },
      { id: "u2", text: "u2", x: 0, y: 0, claimType: "unknown" },
    ];
    doc.evidenceLinks = [
      { id: "s1", type: "supports", fromCardId: "f1", toCardId: "h1" },
      { id: "x1", type: "contradicts", fromCardId: "c1", toCardId: "h1" },
      { id: "x2", type: "contradicts", fromCardId: "u1", toCardId: "u2" },
    ];

    const first = analyzeDialecticBalance(doc);
    const second = analyzeDialecticBalance(doc);

    expect(first.findings.map((finding) => finding.code)).toEqual(second.findings.map((finding) => finding.code));
    expect(first.stats.hypothesisCount).toBe(2);
    expect(first.stats.hypothesisWithSupportCount).toBe(1);
    expect(first.stats.hypothesisWithContradictionCount).toBe(1);
    expect(first.stats.claimWithContradictionCount).toBe(0);
  });

  it("triggers B001/B002/B003/B004/B005/B006 under expected conditions", () => {
    const collapse = makeDoc();
    collapse.cards = Array.from({ length: 11 }, (_, idx) => ({ id: `k${idx}`, text: `k${idx}`, x: 0, y: 0, claimType: "unknown" as const }));
    const collapseReport = analyzeDialecticBalance(collapse);
    expect(collapseReport.findings.some((finding) => finding.code === "B006")).toBe(true);

    const doc = makeDoc();
    doc.cards = [
      { id: "f1", text: "f1", x: 0, y: 0, claimType: "fact" },
      { id: "f2", text: "f2", x: 0, y: 0, claimType: "fact" },
      { id: "h1", text: "h1", x: 0, y: 0, claimType: "hypothesis" },
      { id: "h2", text: "h2", x: 0, y: 0, claimType: "hypothesis" },
      { id: "h3", text: "h3", x: 0, y: 0, claimType: "hypothesis" },
      { id: "h4", text: "h4", x: 0, y: 0, claimType: "hypothesis" },
      { id: "c1", text: "c1", x: 0, y: 0, claimType: "claim" },
      { id: "c2", text: "c2", x: 0, y: 0, claimType: "claim" },
      { id: "c3", text: "c3", x: 0, y: 0, claimType: "claim" },
      { id: "c4", text: "c4", x: 0, y: 0, claimType: "claim" },
      { id: "c5", text: "c5", x: 0, y: 0, claimType: "claim" },
      { id: "u1", text: "u1", x: 0, y: 0, claimType: "unknown" },
      { id: "u2", text: "u2", x: 0, y: 0, claimType: "unknown" },
    ];
    doc.evidenceLinks = [
      { id: "s1", type: "supports", fromCardId: "f1", toCardId: "h1" },
      { id: "x1", type: "contradicts", fromCardId: "c1", toCardId: "h1" },
      { id: "x2", type: "contradicts", fromCardId: "u1", toCardId: "u2" },
    ];

    const report = analyzeDialecticBalance(doc);
    expect(report.findings.some((finding) => finding.code === "B001")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "B002")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "B003")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "B004")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "B005")).toBe(true);
  });

  it("handles 200 cards deterministically", () => {
    const doc = makeDoc();
    doc.cards = Array.from({ length: 200 }, (_, index) => {
      const claimType = index % 4 === 0 ? "fact" : index % 4 === 1 ? "claim" : index % 4 === 2 ? "hypothesis" : "unknown";
      return { id: `c${index}`, text: `card ${index}`, x: index * 5, y: index * 3, claimType } as const;
    });
    doc.evidenceLinks = Array.from({ length: 180 }, (_, index) => ({
      id: `e${index}`,
      type: index % 3 === 0 ? "contradicts" : "supports",
      fromCardId: `c${index}`,
      toCardId: `c${index + 1}`,
    }));

    const startedAt = Date.now();
    const first = analyzeDialecticBalance(doc);
    const elapsedMs = Date.now() - startedAt;
    const second = analyzeDialecticBalance(doc);

    expect(first.findings).toEqual(second.findings);
    expect(first.stats.totalCards).toBe(200);
    expect(elapsedMs).toBeLessThan(1000);
  });
});
