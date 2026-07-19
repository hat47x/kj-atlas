import {
  type FieldworkRequestV1,
  type InquiryBundleV1,
  type RoundArtifactKind,
  type RoundArtifactRefV1,
  type RoundHandoffV1,
  validateInquiryBundle,
} from "./inquiry_journey";

export type InquiryHandoffReviewDecision = "pending" | "adopted" | "held" | "skipped";

export type InquiryHandoffArtifactCandidate = {
  candidateId: string;
  kind: "artifact";
  artifactKind: RoundArtifactKind;
  label: string;
  ref: RoundArtifactRefV1;
  decision: InquiryHandoffReviewDecision;
};

export type InquiryHandoffTextCandidate = {
  candidateId: string;
  kind: "understanding" | "unresolved_question" | "fieldwork_request";
  value: string;
  originalValue: string;
  decision: Exclude<InquiryHandoffReviewDecision, "held">;
  fieldworkRequest?: FieldworkRequestV1;
};

export type InquiryHandoffReviewCandidate =
  | InquiryHandoffArtifactCandidate
  | InquiryHandoffTextCandidate;

export type BuildInquiryHandoffReviewResult =
  | { ok: true; roundId: string; candidates: InquiryHandoffReviewCandidate[] }
  | { ok: false; reason: "round_not_found" | "snapshot_not_found" };

export type SaveInquiryRoundHandoffResult =
  | { ok: true; bundle: InquiryBundleV1; unansweredCount: number }
  | { ok: false; reason: "round_not_found" | "invalid_handoff" };

type SaveInquiryRoundHandoffOptions = {
  idFactory?: () => string;
  now?: () => string;
};

function artifactKey(ref: RoundArtifactRefV1): string {
  return `${ref.snapshotId}\u0000${ref.kind}\u0000${ref.entityId}`;
}

function artifactCandidateId(ref: RoundArtifactRefV1): string {
  return `artifact:${ref.snapshotId}:${ref.kind}:${ref.entityId}`;
}

function defaultIdFactory(): string {
  return crypto.randomUUID();
}

function addArtifactCandidate(
  candidates: InquiryHandoffArtifactCandidate[],
  known: Set<string>,
  ref: RoundArtifactRefV1,
  label: string,
  carryover: Set<string>,
  held: Set<string>
): void {
  const key = artifactKey(ref);
  if (known.has(key)) return;
  known.add(key);
  candidates.push({
    candidateId: artifactCandidateId(ref),
    kind: "artifact",
    artifactKind: ref.kind,
    label,
    ref,
    decision: held.has(key) ? "held" : carryover.has(key) ? "adopted" : "pending",
  });
}

function artifactLabel(bundle: InquiryBundleV1, ref: RoundArtifactRefV1): string {
  const document = bundle.snapshots.find((snapshot) => snapshot.snapshotId === ref.snapshotId)?.document;
  if (!document) return ref.entityId;
  if (ref.kind === "card") {
    return document.cards.find((card) => card.id === ref.entityId)?.text ?? ref.entityId;
  }
  if (ref.kind === "island") {
    const island = document.islands.find((candidate) => candidate.id === ref.entityId);
    return island?.title?.trim() || island?.summaryText?.trim() || ref.entityId;
  }
  if (ref.kind === "narrative") {
    return document.narratives?.find((narrative) => narrative.id === ref.entityId)?.title ?? ref.entityId;
  }
  return document.relationSummaries?.find((summary) => summary.id === ref.entityId)?.text ?? ref.entityId;
}

export function buildInquiryHandoffReview(
  bundle: InquiryBundleV1,
  roundId = bundle.journey.defaultHeadRoundId
): BuildInquiryHandoffReviewResult {
  const round = bundle.journey.roundRecords.find((candidate) => candidate.roundId === roundId);
  if (!round) return { ok: false, reason: "round_not_found" };
  const snapshot = bundle.snapshots.find((candidate) => candidate.snapshotId === round.outputSnapshotId);
  if (!snapshot) return { ok: false, reason: "snapshot_not_found" };

  const carryover = new Set((round.handoff?.carryoverRefs ?? []).map(artifactKey));
  const held = new Set((round.handoff?.heldRefs ?? []).map(artifactKey));
  const known = new Set<string>();
  const artifactCandidates: InquiryHandoffArtifactCandidate[] = [];
  const add = (ref: RoundArtifactRefV1, label: string) => {
    addArtifactCandidate(artifactCandidates, known, ref, label, carryover, held);
  };

  for (const card of snapshot.document.cards) {
    add({ snapshotId: snapshot.snapshotId, kind: "card", entityId: card.id }, card.text);
  }
  for (const island of snapshot.document.islands) {
    add(
      { snapshotId: snapshot.snapshotId, kind: "island", entityId: island.id },
      island.title?.trim() || island.summaryText?.trim() || island.id
    );
  }
  for (const narrative of snapshot.document.narratives ?? []) {
    add({ snapshotId: snapshot.snapshotId, kind: "narrative", entityId: narrative.id }, narrative.title);
  }
  for (const summary of snapshot.document.relationSummaries ?? []) {
    add({ snapshotId: snapshot.snapshotId, kind: "relation_summary", entityId: summary.id }, summary.text);
  }
  for (const ref of [...(round.handoff?.carryoverRefs ?? []), ...(round.handoff?.heldRefs ?? [])]) {
    add(ref, artifactLabel(bundle, ref));
  }

  const textCandidates: InquiryHandoffTextCandidate[] = [];
  const understanding = round.handoff?.understandingDelta ?? "";
  textCandidates.push({
    candidateId: "understanding",
    kind: "understanding",
    value: understanding,
    originalValue: understanding,
    decision: understanding.trim() ? "adopted" : "pending",
  });

  const unresolved = round.handoff?.unresolvedQuestions ?? [];
  if (unresolved.length === 0) {
    textCandidates.push({
      candidateId: "unresolved:new",
      kind: "unresolved_question",
      value: "",
      originalValue: "",
      decision: "pending",
    });
  } else {
    unresolved.forEach((value, index) => textCandidates.push({
      candidateId: `unresolved:${index}`,
      kind: "unresolved_question",
      value,
      originalValue: value,
      decision: "adopted",
    }));
  }

  const fieldwork = round.handoff?.fieldworkRequests ?? [];
  if (fieldwork.length === 0) {
    textCandidates.push({
      candidateId: "fieldwork:new",
      kind: "fieldwork_request",
      value: "",
      originalValue: "",
      decision: "pending",
    });
  } else {
    fieldwork.forEach((request) => textCandidates.push({
      candidateId: `fieldwork:${request.requestId}`,
      kind: "fieldwork_request",
      value: request.question,
      originalValue: request.question,
      decision: "adopted",
      fieldworkRequest: structuredClone(request),
    }));
  }

  return { ok: true, roundId: round.roundId, candidates: [...artifactCandidates, ...textCandidates] };
}

function uniqueArtifactRefs(
  candidates: InquiryHandoffReviewCandidate[],
  decision: "adopted" | "held"
): RoundArtifactRefV1[] {
  const seen = new Set<string>();
  const refs: RoundArtifactRefV1[] = [];
  for (const candidate of candidates) {
    if (candidate.kind !== "artifact" || candidate.decision !== decision) continue;
    const key = artifactKey(candidate.ref);
    if (seen.has(key)) continue;
    seen.add(key);
    refs.push({ ...candidate.ref });
  }
  return refs;
}

function buildHandoff(
  candidates: InquiryHandoffReviewCandidate[],
  idFactory: () => string
): RoundHandoffV1 {
  const unresolvedQuestions = candidates
    .filter((candidate): candidate is InquiryHandoffTextCandidate => (
      candidate.kind === "unresolved_question"
      && candidate.decision === "adopted"
      && Boolean(candidate.value.trim())
    ))
    .map((candidate) => candidate.value.trim());
  const fieldworkRequests = candidates
    .filter((candidate): candidate is InquiryHandoffTextCandidate => (
      candidate.kind === "fieldwork_request"
      && candidate.decision === "adopted"
      && Boolean(candidate.value.trim())
    ))
    .map((candidate) => {
      const question = candidate.value.trim();
      const existing = candidate.fieldworkRequest;
      return {
        requestId: existing?.requestId ?? `fieldwork-${idFactory()}`,
        question,
        ...(existing?.outcome && candidate.originalValue.trim() === question
          ? { outcome: structuredClone(existing.outcome) }
          : {}),
      };
    });
  const understanding = candidates.find((candidate): candidate is InquiryHandoffTextCandidate => (
    candidate.kind === "understanding"
    && candidate.decision === "adopted"
    && Boolean(candidate.value.trim())
  ));
  return {
    carryoverRefs: uniqueArtifactRefs(candidates, "adopted"),
    heldRefs: uniqueArtifactRefs(candidates, "held"),
    unresolvedQuestions,
    fieldworkRequests,
    ...(understanding ? { understandingDelta: understanding.value.trim() } : {}),
  };
}

export function saveInquiryRoundHandoff(
  bundle: InquiryBundleV1,
  roundId: string,
  candidates: InquiryHandoffReviewCandidate[],
  options: SaveInquiryRoundHandoffOptions = {}
): SaveInquiryRoundHandoffResult {
  const roundIndex = bundle.journey.roundRecords.findIndex((round) => round.roundId === roundId);
  if (roundIndex < 0) return { ok: false, reason: "round_not_found" };
  const updatedAt = (options.now ?? (() => new Date().toISOString()))();
  const unansweredCount = candidates.filter((candidate) => (
    candidate.decision === "pending"
    || (candidate.kind !== "artifact" && candidate.decision === "adopted" && !candidate.value.trim())
  )).length;
  const handoff = buildHandoff(candidates, options.idFactory ?? defaultIdFactory);
  const nextRounds = bundle.journey.roundRecords.map((round, index) => index === roundIndex
    ? {
        ...round,
        updatedAt,
        status: unansweredCount > 0 ? "paused" as const : "handed_off" as const,
        handoff,
      }
    : round);
  const nextBundle: InquiryBundleV1 = {
    ...bundle,
    journey: {
      ...bundle.journey,
      roundRecords: nextRounds,
      updatedAt,
    },
  };
  if (validateInquiryBundle(nextBundle).length > 0) {
    return { ok: false, reason: "invalid_handoff" };
  }
  return { ok: true, bundle: nextBundle, unansweredCount };
}
