import { describe, expect, it } from "vitest";

import { buildContradictionTraceMd } from "./contradiction_trace";
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
      { id: "inc-claim", text: "Incoming claim", x: 0, y: 0, claimType: "claim" },
      { id: "inc-hyp", text: "Incoming hypothesis", x: 0, y: 0, claimType: "hypothesis" },
      { id: "out-fact", text: "Outgoing fact", x: 0, y: 0, claimType: "fact" },
      { id: "out-unknown", text: "Outgoing unknown", x: 0, y: 0, claimType: "unknown" },
      { id: "f1", text: "Fact one", x: 0, y: 0, claimType: "fact" },
      { id: "f2", text: "Fact two", x: 0, y: 0, claimType: "fact" },
      { id: "f3", text: "Fact target", x: 0, y: 0, claimType: "fact" },
      { id: "chain", text: "Chain node", x: 0, y: 0, claimType: "claim" },
      { id: "branch", text: "Branch node", x: 0, y: 0, claimType: "claim" },
    ],
    edges: [],
    islands: [],
    evidenceLinks: [
      { id: "c1", type: "contradicts", fromCardId: "inc-claim", toCardId: "target" },
      { id: "c2", type: "contradicts", fromCardId: "inc-hyp", toCardId: "target" },
      { id: "c3", type: "contradicts", fromCardId: "target", toCardId: "out-fact" },
      { id: "c4", type: "contradicts", fromCardId: "target", toCardId: "out-unknown" },
      { id: "c5", type: "contradicts", fromCardId: "out-fact", toCardId: "chain" },
      { id: "c6", type: "contradicts", fromCardId: "out-unknown", toCardId: "branch" },
      { id: "c7", type: "contradicts", fromCardId: "chain", toCardId: "target" },
      { id: "s1", type: "supports", fromCardId: "f1", toCardId: "inc-claim" },
      { id: "s2", type: "supports", fromCardId: "f2", toCardId: "out-fact" },
      { id: "s3", type: "supports", fromCardId: "inc-claim", toCardId: "out-unknown" },
      { id: "s4", type: "supports", fromCardId: "f3", toCardId: "target" },
    ],
  };
}

describe("buildContradictionTraceMd", () => {
  it("lists incoming/outgoing contradictions with deterministic ordering and both-side supports", () => {
    const md = buildContradictionTraceMd(makeDoc(), "target", { depthLimit: 1, includeSupports: true });

    expect(md).toContain("## Incoming contradictions");
    expect(md).toContain("## Outgoing contradictions");
    expect(md.indexOf("- [fact] Outgoing fact (id: out-fact)")).toBeLessThan(md.indexOf("- [unknown] Outgoing unknown (id: out-unknown)"));
    expect(md).toContain("⚠ hypothesis-as-contradiction");
    expect(md).toContain("⚠ unknown-type");
    expect(md).toContain("⚠ unsupported-contradiction");
    expect(md).toContain("- Fact supports:");
    expect(md).toContain("Fact target (id: f3)");
    expect(md).toContain("  - This side fact supports:");
    expect(md).toContain("  - Target side fact supports:");
    expect(md).toContain("Fact one (id: f1)");
    expect(md).toContain("Fact two (id: f2)");
    expect(md).toContain("⚠ No fact support");
    expect(md).not.toContain("## Contradiction network");
  });

  it("uses BFS-style network expansion with depth limit and truncation", () => {
    const mdDepth2 = buildContradictionTraceMd(makeDoc(), "target", { depthLimit: 2 });
    expect(mdDepth2).toContain("## Contradiction network (depth 2)");
    expect(mdDepth2).toContain("Chain node (id: chain)");
    expect(mdDepth2).toContain("Branch node (id: branch)");

    const mdDepth1 = buildContradictionTraceMd(makeDoc(), "target", { depthLimit: 1 });
    expect(mdDepth1).not.toContain("## Contradiction network");

    const mdTruncated = buildContradictionTraceMd(makeDoc(), "target", { depthLimit: 3, maxNodes: 1 });
    expect(mdTruncated).toContain("... truncated");
  });

  it("is deterministic and handles missing target", () => {
    const doc = makeDoc();
    const a = buildContradictionTraceMd(doc, "target", { depthLimit: 3, includeSupports: true });
    const b = buildContradictionTraceMd(doc, "target", { depthLimit: 3, includeSupports: true });

    expect(a).toBe(b);
    expect(buildContradictionTraceMd(doc, "missing")).toBe("Error: target card not found (id: missing)");
  });

  it("can omit support sections", () => {
    const md = buildContradictionTraceMd(makeDoc(), "target", { includeSupports: false });
    expect(md).not.toContain("Fact supports:");
    expect(md).not.toContain("This side fact supports");
    expect(md).not.toContain("Target side fact supports");
  });
});
