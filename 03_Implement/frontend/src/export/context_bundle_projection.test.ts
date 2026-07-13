import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import {
  buildContextProjection,
  CONTEXT_PROJECTION_CONSTRAINTS,
  type ContextProjectionConstraint,
} from "./context_bundle_projection";

// EXT-CONN-01 (ADR-0054 stage 1): safety properties of the read-only external
// projection. These lock the SafeMode boundary, the reviewed-only exclusion,
// per-constraint scoping, anti-scoring, and bundleHash determinism BEFORE any
// MCP transport is wired -- the transport is a thin adapter over this core.

function buildDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc_ext_conn_fixture",
    title: "ext-conn projection fixture",
    createdAt: "2026-07-12T00:00:00.000Z",
    updatedAt: "2026-07-12T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "reviewed claim one", x: 0, y: 0, claimType: "claim", textReviewed: true },
      { id: "c2", text: "reviewed fact two", x: 100, y: 0, claimType: "fact", textReviewed: true },
      { id: "c3", text: "unreviewed draft three", x: 200, y: 0, claimType: "unknown", textReviewed: false },
      { id: "c4", text: "reviewed hypothesis four", x: 300, y: 0, claimType: "hypothesis", textReviewed: true },
    ],
    edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "related" }],
    islands: [{ id: "i1", cardIds: ["c1", "c2"], title: "First island" }],
    readingOrder: ["c1", "c2", "c3", "c4"],
    narratives: [],
    evidenceLinks: [
      { id: "ev1", type: "supports", fromCardId: "c2", toCardId: "c1", createdAt: "2026-07-12T00:00:00.000Z" },
      { id: "ev2", type: "contradicts", fromCardId: "c3", toCardId: "c1", createdAt: "2026-07-12T00:00:00.000Z" },
    ],
    mergeSuggestionDecisions: [],
  };
}

describe("buildContextProjection: reviewed-only constraint", () => {
  it("excludes unreviewed cards entirely and exposes reviewed text when SafeMode is OFF", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "reviewed-only", safeMode: false });

    const ids = projection.cards.map((card) => card.id);
    expect(ids).toEqual(["c1", "c2", "c4"]); // c3 (unreviewed) excluded, sorted
    expect(projection.cards.every((card) => card.reviewed)).toBe(true);
    expect(projection.cards.every((card) => card.redacted === false)).toBe(true);
    expect(projection.cards.find((card) => card.id === "c1")?.text).toBe("reviewed claim one");
    // counts still report the whole document, not just the projected subset.
    expect(projection.counts).toEqual({ reviewed: 3, unreviewed: 1, redacted: 0 });
  });

  it("redacts even reviewed card text when SafeMode is ON (external surface == share boundary)", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "reviewed-only", safeMode: true });

    expect(projection.cards.map((card) => card.id)).toEqual(["c1", "c2", "c4"]);
    expect(projection.cards.every((card) => card.redacted)).toBe(true);
    for (const card of projection.cards) {
      expect(card.text).not.toContain("reviewed");
      expect(card.text.startsWith("[REDACTED]")).toBe(true);
    }
    expect(projection.counts.redacted).toBe(3);
  });
});

describe("buildContextProjection: evidence vs contradiction scoping", () => {
  it("evidence constraint surfaces only supports links and their endpoint cards", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "evidence", safeMode: false });

    expect(projection.evidence).toEqual([{ from: "c2", to: "c1" }]);
    expect(projection.contradictions).toEqual([]);
    expect(projection.cards.map((card) => card.id).sort()).toEqual(["c1", "c2"]);
  });

  it("contradiction constraint surfaces only contradicts links and their endpoint cards", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "contradiction", safeMode: false });

    expect(projection.contradictions).toEqual([{ from: "c3", to: "c1" }]);
    expect(projection.evidence).toEqual([]);
    expect(projection.cards.map((card) => card.id).sort()).toEqual(["c1", "c3"]);
  });

  it("redacts an unreviewed endpoint card even inside the contradiction subset", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "contradiction", safeMode: false });

    const c3 = projection.cards.find((card) => card.id === "c3");
    expect(c3?.reviewed).toBe(false);
    expect(c3?.redacted).toBe(true);
    expect(c3?.text).not.toContain("unreviewed draft three");
  });
});

describe("buildContextProjection: summary constraint", () => {
  it("emits no card nodes but keeps counts, islands, and full-document relations", async () => {
    const projection = await buildContextProjection({ doc: buildDoc(), constraint: "summary", safeMode: false });

    expect(projection.cards).toEqual([]);
    expect(projection.counts).toEqual({ reviewed: 3, unreviewed: 1, redacted: 0 });
    expect(projection.islands).toEqual([{ id: "i1", title: "First island" }]);
    expect(projection.relations).toEqual([{ from: "c1", to: "c2", type: "related" }]);
    // summary carries both link structures.
    expect(projection.evidence).toEqual([{ from: "c2", to: "c1" }]);
    expect(projection.contradictions).toEqual([{ from: "c3", to: "c1" }]);
  });
});

describe("buildContextProjection: invariants across all constraints", () => {
  it("never emits score/rank/confidence/priority anywhere in the output", async () => {
    for (const constraint of CONTEXT_PROJECTION_CONSTRAINTS) {
      for (const safeMode of [true, false]) {
        const projection = await buildContextProjection({ doc: buildDoc(), constraint, safeMode });
        const serialized = JSON.stringify(projection);
        expect(serialized, `${constraint}/${safeMode}`).not.toMatch(/score|rank|confidence|priority|readiness/i);
      }
    }
  });

  it("produces a deterministic bundleHash for identical inputs", async () => {
    const run = (): Promise<string> =>
      buildContextProjection({ doc: buildDoc(), constraint: "reviewed-only", safeMode: false }).then((p) => p.bundleHash);
    expect(await run()).toBe(await run());
  });

  it("changes bundleHash when SafeMode flips (exposure state is part of what was shared)", async () => {
    const off = await buildContextProjection({ doc: buildDoc(), constraint: "reviewed-only", safeMode: false });
    const on = await buildContextProjection({ doc: buildDoc(), constraint: "reviewed-only", safeMode: true });
    expect(off.bundleHash).not.toBe(on.bundleHash);
  });

  it("never puts withheld original text into the hash payload (redacted text hashes as null)", async () => {
    // Two docs whose ONLY difference is the body of an unreviewed card that is
    // redacted in this projection: the hash must be identical because the real
    // text was never exposed and must not leak through the correlation hash.
    const docA = buildDoc();
    const docB = buildDoc();
    docB.cards = docB.cards.map((card) => (card.id === "c3" ? { ...card, text: "totally different secret" } : card));

    const a = await buildContextProjection({ doc: docA, constraint: "contradiction", safeMode: false });
    const b = await buildContextProjection({ doc: docB, constraint: "contradiction", safeMode: false });
    // c3 is unreviewed -> redacted in both; its differing body must not change the hash.
    expect(a.bundleHash).toBe(b.bundleHash);
  });

  it("accepts every declared constraint literal", async () => {
    const constraints: ContextProjectionConstraint[] = [...CONTEXT_PROJECTION_CONSTRAINTS];
    for (const constraint of constraints) {
      const projection = await buildContextProjection({ doc: buildDoc(), constraint, safeMode: false });
      expect(projection.constraint).toBe(constraint);
      expect(projection.schemaVersion).toBe("context-projection.v1");
      expect(projection.baseDocSignature).toBe("doc_ext_conn_fixture:2026-07-12T00:00:00.000Z");
    }
  });
});
