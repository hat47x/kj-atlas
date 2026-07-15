import { describe, expect, it } from "vitest";

import { buildEvidenceTraceMd } from "./evidence_trace";
import type { DocumentV1 } from "../types";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2025-01-01T00:00:00.000Z",
    updatedAt: "2025-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "target", text: "Target claim", x: 0, y: 0, claimType: "claim" },
      { id: "fact-b", text: "Fact B", x: 0, y: 0, claimType: "fact" },
      { id: "claim-a", text: "Claim A", x: 0, y: 0, claimType: "claim" },
      { id: "hyp-c", text: "Hyp C", x: 0, y: 0, claimType: "hypothesis" },
      { id: "unknown-d", text: "Unknown D", x: 0, y: 0, claimType: "unknown" },
      { id: "loop", text: "Loop", x: 0, y: 0, claimType: "claim" },
    ],
    edges: [],
    islands: [],
    evidenceLinks: [
      { id: "l1", type: "supports", fromCardId: "claim-a", toCardId: "target" },
      { id: "l2", type: "supports", fromCardId: "fact-b", toCardId: "target" },
      { id: "l3", type: "supports", fromCardId: "hyp-c", toCardId: "target" },
      { id: "l4", type: "supports", fromCardId: "unknown-d", toCardId: "target" },
      { id: "l5", type: "supports", fromCardId: "loop", toCardId: "claim-a" },
      { id: "l6", type: "supports", fromCardId: "claim-a", toCardId: "loop" },
      { id: "l7", type: "supports", fromCardId: "fact-b", toCardId: "claim-a" },
      { id: "l8", type: "contradicts", fromCardId: "unknown-d", toCardId: "target" },
    ],
  };
}

describe("buildEvidenceTraceMd", () => {
  it("uses incoming supports with deterministic order and markers", () => {
    const md = buildEvidenceTraceMd(makeDoc(), "target", { depthLimit: 3 });

    expect(md).toContain("## Supports (up to depth 3)");
    expect(md.indexOf("- [fact] Fact B (id: fact-b) ✓ fact-evidence")).toBeLessThan(md.indexOf("- [claim] Claim A (id: claim-a)"));
    expect(md).toContain("- [hypothesis] Hyp C (id: hyp-c) ⚠ hypothesis-as-evidence");
    expect(md).toContain("- [unknown] Unknown D (id: unknown-d) ⚠ unknown-type");
    expect(md).toContain("- [claim] Loop (id: loop)");
    expect(md).toContain("(see above)");
  });

  it("respects depth and stopAtFacts", () => {
    const mdDepth1 = buildEvidenceTraceMd(makeDoc(), "target", { depthLimit: 1 });
    expect(mdDepth1).not.toContain("Loop (id: loop)");

    const stopAtFactDoc: DocumentV1 = {
      version: 1,
      id: "doc-stop",
      createdAt: "2025-01-01T00:00:00.000Z",
      updatedAt: "2025-01-01T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "target", text: "Target", x: 0, y: 0, claimType: "claim" },
        { id: "fact", text: "Fact", x: 0, y: 0, claimType: "fact" },
        { id: "child", text: "Child", x: 0, y: 0, claimType: "claim" },
      ],
      edges: [],
      islands: [],
      evidenceLinks: [
        { id: "s1", type: "supports", fromCardId: "fact", toCardId: "target" },
        { id: "s2", type: "supports", fromCardId: "child", toCardId: "fact" },
      ],
    };

    const mdWithoutStop = buildEvidenceTraceMd(stopAtFactDoc, "target", { depthLimit: 3, stopAtFacts: false });
    const mdWithStop = buildEvidenceTraceMd(stopAtFactDoc, "target", { depthLimit: 3, stopAtFacts: true });
    expect(mdWithoutStop).toContain("  - [claim] Child (id: child)");
    expect(mdWithStop).not.toContain("  - [claim] Child (id: child)");
  });

  it("supports include/exclude type toggles, maxNodes truncation, and missing target", () => {
    const mdExcludeUnknown = buildEvidenceTraceMd(makeDoc(), "target", { includeUnknown: false });
    expect(mdExcludeUnknown).not.toContain("Unknown D");

    const mdExcludeHypothesis = buildEvidenceTraceMd(makeDoc(), "target", { includeHypothesis: false });
    expect(mdExcludeHypothesis).not.toContain("Hyp C");

    const mdFactsOnly = buildEvidenceTraceMd(makeDoc(), "target", {
      includeFact: true,
      includeClaim: false,
      includeHypothesis: false,
      includeUnknown: false,
    });
    expect(mdFactsOnly).toContain("Fact B");
    expect(mdFactsOnly).not.toContain("Claim A");

    const mdTruncated = buildEvidenceTraceMd(makeDoc(), "target", { maxNodes: 1, depthLimit: 5 });
    expect(mdTruncated).toContain("truncated (maxNodes reached)");

    expect(buildEvidenceTraceMd(makeDoc(), "missing")).toBe("Error: target card not found (id: missing)");
  });

  it("redacts card text in safe mode", () => {
    const doc = makeDoc();
    doc.cards = doc.cards.map((card) => ({ ...card, text: card.id === "target" ? "SECRET_TEXT_DO_NOT_LEAK" : card.text }));
    const md = buildEvidenceTraceMd(doc, "target", { safeMode: true });

    expect(md).toContain("card:target");
    expect(md).not.toContain("SECRET_TEXT_DO_NOT_LEAK");
  });

  it("is deterministic for same input", () => {
    const doc = makeDoc();
    const a = buildEvidenceTraceMd(doc, "target", { depthLimit: 4, includeUnknown: true });
    const b = buildEvidenceTraceMd(doc, "target", { depthLimit: 4, includeUnknown: true });
    expect(a).toBe(b);
  });
});
