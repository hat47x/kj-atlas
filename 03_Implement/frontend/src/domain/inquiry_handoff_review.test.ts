import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "./types";
import { parseInquiryBundleJson, serializeInquiryBundle } from "./inquiry_bundle_io";
import {
  buildInquiryHandoffReview,
  saveInquiryRoundHandoff,
  type InquiryHandoffReviewCandidate,
} from "./inquiry_handoff_review";
import { recordInquiryRound, startInquiryJourney } from "./inquiry_journey_session";

const CREATED_AT = "2026-07-19T00:00:00.000Z";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-handoff-review",
    title: "Waiting at the entrance",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-carry", text: "Visitors stop after reading the sign", x: 0, y: 0 },
      { id: "card-hold", text: "The weather may have affected the result", x: 100, y: 0 },
    ],
    edges: [],
    islands: [],
  };
}

function sequentialIds(): () => string {
  let value = 0;
  return () => String(++value);
}

async function createRecordedBundle() {
  const ids = sequentialIds();
  const document = createDocument();
  const started = await startInquiryJourney(document, { idFactory: ids, now: () => CREATED_AT });
  const recorded = await recordInquiryRound(started, document, "r2_situation_grasp", {
    idFactory: ids,
    now: () => "2026-07-19T00:01:00.000Z",
  });
  if (!recorded.ok) throw new Error(recorded.reason);
  return recorded.bundle;
}

describe("inquiry handoff review", () => {
  it("derives candidates from an immutable result and saves answered items without blocking on pending ones", async () => {
    const bundle = await createRecordedBundle();
    const source = structuredClone(bundle);
    const review = buildInquiryHandoffReview(bundle);

    expect(review.ok).toBe(true);
    if (!review.ok) return;
    expect(review.candidates.map((candidate) => candidate.kind)).toEqual([
      "artifact",
      "artifact",
      "understanding",
      "unresolved_question",
      "fieldwork_request",
    ]);

    const candidates = review.candidates.map((candidate): InquiryHandoffReviewCandidate => {
      if (candidate.kind === "artifact" && candidate.ref.entityId === "card-carry") {
        return { ...candidate, decision: "adopted" };
      }
      if (candidate.kind === "artifact" && candidate.ref.entityId === "card-hold") {
        return { ...candidate, decision: "held" };
      }
      if (candidate.kind === "understanding") {
        return {
          ...candidate,
          value: "The pause begins after the sign is read.",
          decision: "adopted",
        };
      }
      if (candidate.kind === "unresolved_question") {
        return { ...candidate, value: "Does this also occur in fine weather?", decision: "skipped" };
      }
      return candidate;
    });
    const saved = saveInquiryRoundHandoff(bundle, review.roundId, candidates, {
      idFactory: () => "new-request",
      now: () => "2026-07-19T00:02:00.000Z",
    });

    expect(saved.ok).toBe(true);
    if (!saved.ok) return;
    expect(saved.unansweredCount).toBe(1);
    expect(saved.bundle.journey.roundRecords[0]).toMatchObject({
      status: "paused",
      updatedAt: "2026-07-19T00:02:00.000Z",
      handoff: {
        carryoverRefs: [{ entityId: "card-carry", kind: "card" }],
        heldRefs: [{ entityId: "card-hold", kind: "card" }],
        unresolvedQuestions: [],
        fieldworkRequests: [],
        understandingDelta: "The pause begins after the sign is read.",
      },
    });
    expect(saved.bundle.snapshots).toEqual(source.snapshots);
    expect(bundle).toEqual(source);

    const serialized = await serializeInquiryBundle(saved.bundle);
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    expect(await parseInquiryBundleJson(serialized.json)).toEqual({ ok: true, bundle: serialized.bundle });

    const reopened = buildInquiryHandoffReview(saved.bundle, review.roundId);
    expect(reopened.ok).toBe(true);
    if (!reopened.ok) return;
    expect(reopened.candidates.find((candidate) => (
      candidate.kind === "artifact" && candidate.ref.entityId === "card-hold"
    ))?.decision).toBe("held");
  });

  it("marks a fully answered handoff as handed off and rejects missing artifact references", async () => {
    const bundle = await createRecordedBundle();
    const review = buildInquiryHandoffReview(bundle);
    expect(review.ok).toBe(true);
    if (!review.ok) return;

    const answered = review.candidates.map((candidate): InquiryHandoffReviewCandidate => candidate.kind === "artifact"
      ? { ...candidate, decision: "skipped" }
      : { ...candidate, decision: "skipped" });
    const saved = saveInquiryRoundHandoff(bundle, review.roundId, answered, {
      now: () => "2026-07-19T00:03:00.000Z",
    });
    expect(saved.ok).toBe(true);
    if (!saved.ok) return;
    expect(saved.unansweredCount).toBe(0);
    expect(saved.bundle.journey.roundRecords[0].status).toBe("handed_off");

    const invalidCandidates: InquiryHandoffReviewCandidate[] = [{
      candidateId: "artifact:missing:card:missing",
      kind: "artifact",
      artifactKind: "card",
      label: "Missing",
      ref: { snapshotId: "missing", kind: "card", entityId: "missing" },
      decision: "adopted",
    }];
    expect(saveInquiryRoundHandoff(bundle, review.roundId, invalidCandidates)).toEqual({
      ok: false,
      reason: "invalid_handoff",
    });
  });
});
