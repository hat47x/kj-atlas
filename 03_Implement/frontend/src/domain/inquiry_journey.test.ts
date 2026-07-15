import { describe, expect, it } from "vitest";

import { createRepresentativeInquiryBundle } from "./inquiry_journey.fixture";
import {
  appendRoundRecord,
  type CardLineageEdgeV1,
  type InquiryBundleV1,
  type RoundStage,
  type RoundStatus,
  validateInquiryBundle,
} from "./inquiry_journey";

function cloneBundle(): InquiryBundleV1 {
  return structuredClone(createRepresentativeInquiryBundle());
}

function issueCodes(bundle: InquiryBundleV1): string[] {
  return validateInquiryBundle(bundle).map((issue) => issue.code);
}

describe("validateInquiryBundle", () => {
  it("accepts a representative loopback from R3 to a second R2 iteration", () => {
    const bundle = createRepresentativeInquiryBundle();

    expect(validateInquiryBundle(bundle)).toEqual([]);
    expect(bundle.journey.roundRecords.map((round) => [round.stage, round.iteration])).toEqual([
      ["r2_situation_grasp", 1],
      ["r3_essence_pursuit", 1],
      ["r2_situation_grasp", 2],
    ]);
  });

  it("rejects a parent cycle without trying to linearize the stages", () => {
    const bundle = cloneBundle();
    bundle.journey.roundRecords[0].parentRoundIds = ["round-r2-2"];

    expect(issueCodes(bundle)).toContain("round_cycle");
  });

  it("rejects unknown round stages and status values at the contract boundary", () => {
    const bundle = cloneBundle();
    bundle.journey.roundRecords[0].stage = "r9_unknown" as RoundStage;
    bundle.journey.roundRecords[0].status = "completed" as RoundStatus;

    expect(issueCodes(bundle)).toEqual(expect.arrayContaining(["invalid_round_stage", "invalid_round_status_value"]));
  });

  it("rejects non-canonical or backward timestamps", () => {
    const bundle = cloneBundle();
    bundle.journey.roundRecords[0].updatedAt = "2026-07-14";

    expect(issueCodes(bundle)).toContain("invalid_timestamp");
  });

  it("requires every leaf branch to be represented as a head", () => {
    const bundle = cloneBundle();
    bundle.journey.roundRecords.push({
      roundId: "round-r4-branch",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r4_concept_planning",
      iteration: 1,
      parentRoundIds: ["round-r2-1"],
      status: "working",
      theme: "別の構想を試す",
      inputSnapshotIds: ["snapshot-r2-1"],
    });

    expect(issueCodes(bundle)).toContain("missing_leaf_head");
  });

  it("rejects future or unrelated snapshots as round inputs", () => {
    const bundle = cloneBundle();
    bundle.journey.roundRecords[0].inputSnapshotIds = ["snapshot-r3-1"];

    expect(issueCodes(bundle)).toContain("invalid_input_snapshot");
  });

  it("rejects missing snapshots and malformed integrity digests", () => {
    const bundle = cloneBundle();
    bundle.snapshots[0].canonicalDigest = "sha256:not-a-digest";
    bundle.journey.roundRecords[2].outputSnapshotId = "snapshot-missing";

    expect(issueCodes(bundle)).toEqual(expect.arrayContaining(["invalid_snapshot_digest", "missing_snapshot"]));
  });

  it("requires a unique origin snapshot and unique round references", () => {
    const bundle = cloneBundle();
    bundle.journey.originSnapshotIds.push("snapshot-origin");
    bundle.journey.roundRecords[0].inputSnapshotIds.push("snapshot-origin");
    bundle.journey.roundRecords[1].parentRoundIds.push("round-r2-1");

    expect(issueCodes(bundle)).toEqual(expect.arrayContaining([
      "duplicate_origin_snapshot",
      "duplicate_input_snapshot",
      "duplicate_parent_round",
    ]));
  });

  it("rejects lineage references to missing cards", () => {
    const bundle = cloneBundle();
    const edge = bundle.cardLineage[0];
    if (edge.kind === "carried") {
      edge.to.cardId = "missing-card";
    }

    expect(issueCodes(bundle)).toContain("missing_lineage_card");
  });

  it("rejects lineage that points from a descendant back to an ancestor", () => {
    const bundle = cloneBundle();
    bundle.cardLineage.push({
      lineageId: "lineage-backward",
      kind: "edited",
      from: { snapshotId: "snapshot-r2-2", cardId: "observation-1" },
      to: { snapshotId: "snapshot-r3-1", cardId: "observation-1" },
    });

    expect(issueCodes(bundle)).toContain("invalid_lineage_direction");
  });

  it("requires split lineage to have at least two distinct targets", () => {
    const bundle = cloneBundle();
    bundle.cardLineage.push({
      lineageId: "lineage-invalid-split",
      kind: "split",
      from: { snapshotId: "snapshot-r2-1", cardId: "observation-1" },
      to: [{ snapshotId: "snapshot-r3-1", cardId: "observation-1" }],
    } as unknown as CardLineageEdgeV1);

    expect(issueCodes(bundle)).toContain("invalid_lineage_cardinality");
  });

  it("rejects non-working rounds that have no recoverable snapshot", () => {
    const bundle = cloneBundle();
    delete bundle.journey.roundRecords[2].outputSnapshotId;

    expect(issueCodes(bundle)).toContain("invalid_round_status");
  });
});

describe("appendRoundRecord", () => {
  it("computes the same-stage iteration along the selected ancestry", () => {
    const bundle = createRepresentativeInquiryBundle();
    const sourceJourney = {
      ...bundle.journey,
      roundRecords: bundle.journey.roundRecords.slice(0, 2),
      headRoundIds: ["round-r3-1"],
      defaultHeadRoundId: "round-r3-1",
    };

    const result = appendRoundRecord(sourceJourney, {
      roundId: "round-r2-2-new",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r2_situation_grasp",
      parentRoundIds: ["round-r3-1"],
      status: "working",
      theme: "追加観察で現状を捉え直す",
      inputSnapshotIds: ["snapshot-r3-1"],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }
    expect(result.journey.roundRecords.at(-1)?.iteration).toBe(2);
    expect(result.journey.headRoundIds).toEqual(["round-r2-2-new"]);
    expect(result.journey.updatedAt).toBe("2026-07-15T01:00:00.000Z");
    expect(sourceJourney.roundRecords).toHaveLength(2);
  });

  it("keeps an existing head when branching from a historical round", () => {
    const bundle = createRepresentativeInquiryBundle();
    const result = appendRoundRecord(bundle.journey, {
      roundId: "round-r4-branch",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r4_concept_planning",
      parentRoundIds: ["round-r2-1"],
      status: "working",
      theme: "現状把握から別の構想を試す",
      inputSnapshotIds: ["snapshot-r2-1"],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }
    expect(result.journey.headRoundIds).toEqual(["round-r2-2", "round-r4-branch"]);
    expect(result.journey.defaultHeadRoundId).toBe("round-r4-branch");
  });

  it("fails closed when parent references are duplicated, missing, or have no snapshot", () => {
    const bundle = createRepresentativeInquiryBundle();
    const duplicateParent = appendRoundRecord(bundle.journey, {
      roundId: "round-duplicate-parent",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r4_concept_planning",
      parentRoundIds: ["round-r2-2", "round-r2-2"],
      status: "working",
      theme: "構想",
      inputSnapshotIds: ["snapshot-r2-2"],
    });
    const missingParent = appendRoundRecord(bundle.journey, {
      roundId: "round-new",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r4_concept_planning",
      parentRoundIds: ["missing-round"],
      status: "working",
      theme: "構想",
      inputSnapshotIds: [],
    });

    const journeyWithoutParentSnapshot = cloneBundle().journey;
    delete journeyWithoutParentSnapshot.roundRecords[2].outputSnapshotId;
    const parentWithoutSnapshot = appendRoundRecord(journeyWithoutParentSnapshot, {
      roundId: "round-new",
      createdAt: "2026-07-15T01:00:00.000Z",
      updatedAt: "2026-07-15T01:00:00.000Z",
      stage: "r4_concept_planning",
      parentRoundIds: ["round-r2-2"],
      status: "working",
      theme: "構想",
      inputSnapshotIds: [],
    });

    expect(duplicateParent).toEqual({ ok: false, reason: "duplicate_parent_round" });
    expect(missingParent).toEqual({ ok: false, reason: "missing_parent_round" });
    expect(parentWithoutSnapshot).toEqual({ ok: false, reason: "parent_without_snapshot" });
  });

  it("fails closed when a new round would move the journey clock backward", () => {
    const bundle = createRepresentativeInquiryBundle();
    const result = appendRoundRecord(bundle.journey, {
      roundId: "round-new",
      createdAt: "2026-07-14T23:00:00.000Z",
      updatedAt: "2026-07-14T23:00:00.000Z",
      stage: "r4_concept_planning",
      parentRoundIds: ["round-r2-2"],
      status: "working",
      theme: "構想",
      inputSnapshotIds: ["snapshot-r2-2"],
    });

    expect(result).toEqual({ ok: false, reason: "invalid_timestamp" });
  });
});
