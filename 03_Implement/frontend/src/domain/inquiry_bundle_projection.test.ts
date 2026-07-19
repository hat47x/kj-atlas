import { describe, expect, it } from "vitest";

import { parseInquiryBundleJson, serializeInquiryBundle } from "./inquiry_bundle_io";
import { deriveInquiryRoundBundle } from "./inquiry_bundle_projection";
import { createRepresentativeInquiryBundle } from "./inquiry_journey.fixture";
import { validateInquiryBundle } from "./inquiry_journey";

describe("deriveInquiryRoundBundle", () => {
  it("creates a self-contained selected-round bundle without mutating its source", async () => {
    const source = createRepresentativeInquiryBundle();
    const before = structuredClone(source);
    const result = deriveInquiryRoundBundle(source, "round-r3-1");

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(source).toEqual(before);
    expect(result.bundle.journey.roundRecords.map((round) => round.roundId)).toEqual([
      "round-r2-1",
      "round-r3-1",
    ]);
    expect(result.bundle.journey.headRoundIds).toEqual(["round-r3-1"]);
    expect(result.bundle.journey.defaultHeadRoundId).toBe("round-r3-1");
    expect(result.bundle.snapshots.map((snapshot) => snapshot.snapshotId)).toEqual([
      "snapshot-origin",
      "snapshot-r2-1",
      "snapshot-r3-1",
    ]);
    expect(result.bundle.cardLineage.map((edge) => edge.lineageId)).toEqual([
      "lineage-origin-situation",
      "lineage-situation-essence",
      "lineage-hypothesis",
    ]);
    expect(validateInquiryBundle(result.bundle)).toEqual([]);

    const serialized = await serializeInquiryBundle(result.bundle);
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    expect(await parseInquiryBundleJson(serialized.json)).toEqual({ ok: true, bundle: serialized.bundle });
  });

  it("returns a full independent copy when the selected round is the only head", () => {
    const source = createRepresentativeInquiryBundle();
    const result = deriveInquiryRoundBundle(source, "round-r2-2");

    expect(result).toEqual({ ok: true, bundle: source });
    if (!result.ok) return;
    expect(result.bundle).not.toBe(source);
    expect(result.bundle.snapshots[0]).not.toBe(source.snapshots[0]);
  });

  it("rejects a missing round and an invalid source bundle", () => {
    const source = createRepresentativeInquiryBundle();
    expect(deriveInquiryRoundBundle(source, "missing-round")).toEqual({
      ok: false,
      reason: "round_not_found",
    });

    source.journey.roundRecords[1].parentRoundIds = ["missing-parent"];
    const invalid = deriveInquiryRoundBundle(source, "round-r3-1");
    expect(invalid.ok).toBe(false);
    if (invalid.ok) return;
    expect(invalid.reason).toBe("invalid_bundle");
  });

  it("fails closed when an included handoff references a snapshot outside the selected path", () => {
    const source = createRepresentativeInquiryBundle();
    source.journey.roundRecords[1].handoff = {
      carryoverRefs: [{
        snapshotId: "snapshot-r2-2",
        kind: "card",
        entityId: "unexpected-observation-1",
      }],
      heldRefs: [],
      unresolvedQuestions: [],
      fieldworkRequests: [],
    };

    expect(deriveInquiryRoundBundle(source, "round-r3-1")).toEqual({
      ok: false,
      reason: "dependency_outside_scope",
      snapshotIds: ["snapshot-r2-2"],
    });
  });

  it("fails closed instead of truncating a split lineage across the selected boundary", () => {
    const source = createRepresentativeInquiryBundle();
    source.cardLineage.push({
      lineageId: "lineage-cross-scope-split",
      kind: "split",
      from: { snapshotId: "snapshot-r2-1", cardId: "observation-1" },
      to: [
        { snapshotId: "snapshot-r3-1", cardId: "observation-1" },
        { snapshotId: "snapshot-r2-2", cardId: "observation-1" },
      ],
    });

    expect(validateInquiryBundle(source)).toEqual([]);
    expect(deriveInquiryRoundBundle(source, "round-r3-1")).toEqual({
      ok: false,
      reason: "dependency_outside_scope",
      snapshotIds: ["snapshot-r2-2"],
    });
  });

  it("omits a retired lineage that belongs only to an excluded descendant", () => {
    const source = createRepresentativeInquiryBundle();
    source.cardLineage.push({
      lineageId: "lineage-retired-on-excluded-descendant",
      kind: "retired",
      from: { snapshotId: "snapshot-r2-2", cardId: "observation-1" },
    });

    const result = deriveInquiryRoundBundle(source, "round-r3-1");
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.bundle.cardLineage.map((edge) => edge.lineageId)).not.toContain(
      "lineage-retired-on-excluded-descendant"
    );
  });
});
