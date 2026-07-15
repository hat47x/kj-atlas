import type { DocumentV2 } from "./types";

export const INQUIRY_SCHEMA_VERSION = "1.0.0" as const;

export const ROUND_STAGES = [
  "r1_problem_setting",
  "r2_situation_grasp",
  "r3_essence_pursuit",
  "r4_concept_planning",
  "r5_concrete_measures",
  "r6_procedure_planning",
] as const;

export const ROUND_STATUSES = ["working", "paused", "handed_off", "superseded"] as const;

export type RoundStage = (typeof ROUND_STAGES)[number];
export type RoundStatus = (typeof ROUND_STATUSES)[number];
export type RoundArtifactKind = "card" | "island" | "narrative" | "relation_summary";

export type RoundArtifactRefV1 = {
  snapshotId: string;
  kind: RoundArtifactKind;
  entityId: string;
};

export type CardAddressV1 = {
  snapshotId: string;
  cardId: string;
};

export type FieldworkOutcomeV1 = {
  kind: "answered" | "no_result" | "unexpected";
  responseCardRefs: CardAddressV1[];
  note?: string;
};

export type FieldworkRequestV1 = {
  requestId: string;
  question: string;
  outcome?: FieldworkOutcomeV1;
};

export type RoundHandoffV1 = {
  carryoverRefs: RoundArtifactRefV1[];
  heldRefs: RoundArtifactRefV1[];
  unresolvedQuestions: string[];
  fieldworkRequests: FieldworkRequestV1[];
  understandingDelta?: string;
};

export type RoundRecordV1 = {
  roundId: string;
  createdAt: string;
  updatedAt: string;
  stage: RoundStage;
  iteration: number;
  parentRoundIds: string[];
  status: RoundStatus;
  theme: string;
  inputSnapshotIds: string[];
  outputSnapshotId?: string;
  handoff?: RoundHandoffV1;
};

export type InquiryJourneyV1 = {
  schemaVersion: typeof INQUIRY_SCHEMA_VERSION;
  journeyId: string;
  title: string;
  originSnapshotIds: string[];
  roundRecords: RoundRecordV1[];
  headRoundIds: string[];
  defaultHeadRoundId?: string;
  createdAt: string;
  updatedAt: string;
};

export type RoundSnapshotV1 = {
  schemaVersion: typeof INQUIRY_SCHEMA_VERSION;
  snapshotId: string;
  createdAt: string;
  canonicalDigest: `sha256:${string}`;
  document: DocumentV2;
};

type OneToOneLineageKind = "carried" | "edited";

export type CardLineageEdgeV1 =
  | {
      lineageId: string;
      kind: OneToOneLineageKind;
      from: CardAddressV1;
      to: CardAddressV1;
    }
  | {
      lineageId: string;
      kind: "derived";
      from: [CardAddressV1, ...CardAddressV1[]];
      to: CardAddressV1;
    }
  | {
      lineageId: string;
      kind: "split";
      from: CardAddressV1;
      to: [CardAddressV1, CardAddressV1, ...CardAddressV1[]];
    }
  | {
      lineageId: string;
      kind: "merged";
      from: [CardAddressV1, CardAddressV1, ...CardAddressV1[]];
      to: CardAddressV1;
    }
  | {
      lineageId: string;
      kind: "new";
      to: CardAddressV1;
    }
  | {
      lineageId: string;
      kind: "retired";
      from: CardAddressV1;
    };

export type InquiryBundleV1 = {
  schemaVersion: typeof INQUIRY_SCHEMA_VERSION;
  journey: InquiryJourneyV1;
  snapshots: RoundSnapshotV1[];
  cardLineage: CardLineageEdgeV1[];
};

export type InquiryValidationIssueCode =
  | "schema_version"
  | "invalid_timestamp"
  | "duplicate_round_id"
  | "invalid_round_stage"
  | "invalid_round_status_value"
  | "duplicate_parent_round"
  | "missing_parent_round"
  | "round_cycle"
  | "invalid_iteration"
  | "invalid_round_status"
  | "duplicate_head_round"
  | "invalid_head_round"
  | "missing_leaf_head"
  | "invalid_default_head"
  | "duplicate_snapshot_id"
  | "missing_origin_snapshot"
  | "duplicate_origin_snapshot"
  | "invalid_snapshot_digest"
  | "duplicate_snapshot_card_id"
  | "missing_snapshot"
  | "duplicate_output_snapshot"
  | "unowned_snapshot"
  | "duplicate_input_snapshot"
  | "invalid_input_snapshot"
  | "duplicate_lineage_id"
  | "invalid_lineage_cardinality"
  | "missing_lineage_card"
  | "invalid_lineage_direction"
  | "missing_handoff_artifact";

export type InquiryValidationIssue = {
  code: InquiryValidationIssueCode;
  path: string;
};

export type AppendRoundResult =
  | { ok: true; journey: InquiryJourneyV1 }
  | { ok: false; reason: "duplicate_round_id" | "duplicate_parent_round" | "missing_parent_round" | "parent_without_snapshot" | "invalid_timestamp" };

function findDuplicates(values: readonly string[]): Set<string> {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      duplicates.add(value);
    }
    seen.add(value);
  }
  return duplicates;
}

function collectAncestorIds(roundId: string, roundsById: ReadonlyMap<string, RoundRecordV1>): Set<string> {
  const ancestors = new Set<string>();
  const pending = [...(roundsById.get(roundId)?.parentRoundIds ?? [])];
  while (pending.length > 0) {
    const parentId = pending.pop() as string;
    if (ancestors.has(parentId)) {
      continue;
    }
    ancestors.add(parentId);
    const parent = roundsById.get(parentId);
    if (parent) {
      pending.push(...parent.parentRoundIds);
    }
  }
  return ancestors;
}

function expectedIteration(round: RoundRecordV1, roundsById: ReadonlyMap<string, RoundRecordV1>): number {
  const ancestors = collectAncestorIds(round.roundId, roundsById);
  let previousMaximum = 0;
  for (const ancestorId of ancestors) {
    const ancestor = roundsById.get(ancestorId);
    if (ancestor?.stage === round.stage) {
      previousMaximum = Math.max(previousMaximum, ancestor.iteration);
    }
  }
  return previousMaximum + 1;
}

function getArtifactIds(snapshot: RoundSnapshotV1, kind: RoundArtifactKind): Set<string> {
  if (kind === "card") {
    return new Set(snapshot.document.cards.map((card) => card.id));
  }
  if (kind === "island") {
    return new Set(snapshot.document.islands.map((island) => island.id));
  }
  if (kind === "narrative") {
    return new Set((snapshot.document.narratives ?? []).map((narrative) => narrative.id));
  }
  return new Set((snapshot.document.relationSummaries ?? []).map((summary) => summary.id));
}

function getLineageAddresses(edge: CardLineageEdgeV1): { from: CardAddressV1[]; to: CardAddressV1[] } {
  if (edge.kind === "new") {
    return { from: [], to: [edge.to] };
  }
  if (edge.kind === "retired") {
    return { from: [edge.from], to: [] };
  }
  return {
    from: Array.isArray(edge.from) ? edge.from : [edge.from],
    to: Array.isArray(edge.to) ? edge.to : [edge.to],
  };
}

function addressKey(address: CardAddressV1): string {
  return `${address.snapshotId}\u0000${address.cardId}`;
}

function isCanonicalTimestamp(value: string): boolean {
  const timestamp = Date.parse(value);
  return !Number.isNaN(timestamp) && new Date(timestamp).toISOString() === value;
}

export function appendRoundRecord(
  journey: InquiryJourneyV1,
  record: Omit<RoundRecordV1, "iteration">
): AppendRoundResult {
  const roundsById = new Map(journey.roundRecords.map((round) => [round.roundId, round]));
  if (roundsById.has(record.roundId)) {
    return { ok: false, reason: "duplicate_round_id" };
  }
  if (findDuplicates(record.parentRoundIds).size > 0) {
    return { ok: false, reason: "duplicate_parent_round" };
  }
  if (
    !isCanonicalTimestamp(record.createdAt)
    || !isCanonicalTimestamp(record.updatedAt)
    || Date.parse(record.updatedAt) < Date.parse(record.createdAt)
    || Date.parse(record.updatedAt) < Date.parse(journey.updatedAt)
  ) {
    return { ok: false, reason: "invalid_timestamp" };
  }

  for (const parentId of record.parentRoundIds) {
    const parent = roundsById.get(parentId);
    if (!parent) {
      return { ok: false, reason: "missing_parent_round" };
    }
    if (!parent.outputSnapshotId) {
      return { ok: false, reason: "parent_without_snapshot" };
    }
  }

  const ancestors = new Set<string>();
  for (const parentId of record.parentRoundIds) {
    ancestors.add(parentId);
    for (const ancestorId of collectAncestorIds(parentId, roundsById)) {
      ancestors.add(ancestorId);
    }
  }

  let previousMaximum = 0;
  for (const ancestorId of ancestors) {
    const ancestor = roundsById.get(ancestorId);
    if (ancestor?.stage === record.stage) {
      previousMaximum = Math.max(previousMaximum, ancestor.iteration);
    }
  }

  const nextRecord: RoundRecordV1 = { ...record, iteration: previousMaximum + 1 };
  const nextHeads = journey.headRoundIds.filter((headId) => !record.parentRoundIds.includes(headId));
  nextHeads.push(record.roundId);

  return {
    ok: true,
    journey: {
      ...journey,
      roundRecords: [...journey.roundRecords, nextRecord],
      headRoundIds: nextHeads,
      defaultHeadRoundId: record.roundId,
      updatedAt: record.updatedAt,
    },
  };
}

export function validateInquiryBundle(bundle: InquiryBundleV1): InquiryValidationIssue[] {
  const issues: InquiryValidationIssue[] = [];
  const addIssue = (code: InquiryValidationIssueCode, path: string) => issues.push({ code, path });

  if (bundle.schemaVersion !== INQUIRY_SCHEMA_VERSION) {
    addIssue("schema_version", "schemaVersion");
  }
  if (bundle.journey.schemaVersion !== INQUIRY_SCHEMA_VERSION) {
    addIssue("schema_version", "journey.schemaVersion");
  }
  if (
    !isCanonicalTimestamp(bundle.journey.createdAt)
    || !isCanonicalTimestamp(bundle.journey.updatedAt)
    || Date.parse(bundle.journey.updatedAt) < Date.parse(bundle.journey.createdAt)
  ) {
    addIssue("invalid_timestamp", "journey.updatedAt");
  }

  const rounds = bundle.journey.roundRecords;
  const roundsById = new Map(rounds.map((round) => [round.roundId, round]));
  for (const duplicateId of findDuplicates(rounds.map((round) => round.roundId))) {
    addIssue("duplicate_round_id", `journey.roundRecords.${duplicateId}`);
  }

  for (const round of rounds) {
    if (
      !isCanonicalTimestamp(round.createdAt)
      || !isCanonicalTimestamp(round.updatedAt)
      || Date.parse(round.updatedAt) < Date.parse(round.createdAt)
    ) {
      addIssue("invalid_timestamp", `journey.roundRecords.${round.roundId}.updatedAt`);
    }
    if (!(ROUND_STAGES as readonly unknown[]).includes(round.stage)) {
      addIssue("invalid_round_stage", `journey.roundRecords.${round.roundId}.stage`);
    }
    if (!(ROUND_STATUSES as readonly unknown[]).includes(round.status)) {
      addIssue("invalid_round_status_value", `journey.roundRecords.${round.roundId}.status`);
    }
    for (const duplicateParentId of findDuplicates(round.parentRoundIds)) {
      addIssue("duplicate_parent_round", `journey.roundRecords.${round.roundId}.parentRoundIds.${duplicateParentId}`);
    }
    for (const parentId of round.parentRoundIds) {
      if (!roundsById.has(parentId)) {
        addIssue("missing_parent_round", `journey.roundRecords.${round.roundId}.parentRoundIds.${parentId}`);
      }
    }
    if (!Number.isSafeInteger(round.iteration) || round.iteration < 1 || round.iteration !== expectedIteration(round, roundsById)) {
      addIssue("invalid_iteration", `journey.roundRecords.${round.roundId}.iteration`);
    }
    if (round.status !== "working" && !round.outputSnapshotId) {
      addIssue("invalid_round_status", `journey.roundRecords.${round.roundId}.outputSnapshotId`);
    }
  }

  const visitState = new Map<string, "visiting" | "visited">();
  const visit = (roundId: string): void => {
    const state = visitState.get(roundId);
    if (state === "visiting") {
      addIssue("round_cycle", `journey.roundRecords.${roundId}.parentRoundIds`);
      return;
    }
    if (state === "visited") {
      return;
    }
    visitState.set(roundId, "visiting");
    for (const parentId of roundsById.get(roundId)?.parentRoundIds ?? []) {
      if (roundsById.has(parentId)) {
        visit(parentId);
      }
    }
    visitState.set(roundId, "visited");
  };
  for (const round of rounds) {
    visit(round.roundId);
  }

  const duplicateHeads = findDuplicates(bundle.journey.headRoundIds);
  for (const duplicateId of duplicateHeads) {
    addIssue("duplicate_head_round", `journey.headRoundIds.${duplicateId}`);
  }
  const parentIds = new Set(rounds.flatMap((round) => round.parentRoundIds));
  const leafIds = new Set(rounds.map((round) => round.roundId).filter((roundId) => !parentIds.has(roundId)));
  const headIds = new Set(bundle.journey.headRoundIds);
  for (const headId of headIds) {
    if (!roundsById.has(headId) || !leafIds.has(headId)) {
      addIssue("invalid_head_round", `journey.headRoundIds.${headId}`);
    }
  }
  for (const leafId of leafIds) {
    if (!headIds.has(leafId)) {
      addIssue("missing_leaf_head", `journey.headRoundIds.${leafId}`);
    }
  }
  if (
    bundle.journey.defaultHeadRoundId !== undefined
    && !headIds.has(bundle.journey.defaultHeadRoundId)
  ) {
    addIssue("invalid_default_head", "journey.defaultHeadRoundId");
  }

  const snapshotsById = new Map(bundle.snapshots.map((snapshot) => [snapshot.snapshotId, snapshot]));
  for (const duplicateId of findDuplicates(bundle.snapshots.map((snapshot) => snapshot.snapshotId))) {
    addIssue("duplicate_snapshot_id", `snapshots.${duplicateId}`);
  }
  for (const snapshot of bundle.snapshots) {
    if (snapshot.schemaVersion !== INQUIRY_SCHEMA_VERSION) {
      addIssue("schema_version", `snapshots.${snapshot.snapshotId}.schemaVersion`);
    }
    if (!/^sha256:[0-9a-f]{64}$/.test(snapshot.canonicalDigest)) {
      addIssue("invalid_snapshot_digest", `snapshots.${snapshot.snapshotId}.canonicalDigest`);
    }
    if (!isCanonicalTimestamp(snapshot.createdAt)) {
      addIssue("invalid_timestamp", `snapshots.${snapshot.snapshotId}.createdAt`);
    }
    for (const duplicateCardId of findDuplicates(snapshot.document.cards.map((card) => card.id))) {
      addIssue("duplicate_snapshot_card_id", `snapshots.${snapshot.snapshotId}.document.cards.${duplicateCardId}`);
    }
  }

  const originIds = new Set(bundle.journey.originSnapshotIds);
  if (bundle.journey.originSnapshotIds.length === 0) {
    addIssue("missing_origin_snapshot", "journey.originSnapshotIds");
  }
  for (const duplicateOriginId of findDuplicates(bundle.journey.originSnapshotIds)) {
    addIssue("duplicate_origin_snapshot", `journey.originSnapshotIds.${duplicateOriginId}`);
  }
  for (const originId of originIds) {
    if (!snapshotsById.has(originId)) {
      addIssue("missing_snapshot", `journey.originSnapshotIds.${originId}`);
    }
  }

  const outputOwners = new Map<string, string>();
  for (const round of rounds) {
    if (!round.outputSnapshotId) {
      continue;
    }
    if (!snapshotsById.has(round.outputSnapshotId)) {
      addIssue("missing_snapshot", `journey.roundRecords.${round.roundId}.outputSnapshotId`);
    }
    const previousOwner = outputOwners.get(round.outputSnapshotId);
    if (previousOwner) {
      addIssue("duplicate_output_snapshot", `journey.roundRecords.${round.roundId}.outputSnapshotId`);
    } else {
      outputOwners.set(round.outputSnapshotId, round.roundId);
    }
    if (originIds.has(round.outputSnapshotId)) {
      addIssue("duplicate_output_snapshot", `journey.roundRecords.${round.roundId}.outputSnapshotId`);
    }
  }

  for (const snapshot of bundle.snapshots) {
    if (!originIds.has(snapshot.snapshotId) && !outputOwners.has(snapshot.snapshotId)) {
      addIssue("unowned_snapshot", `snapshots.${snapshot.snapshotId}`);
    }
  }

  for (const round of rounds) {
    const ancestorIds = collectAncestorIds(round.roundId, roundsById);
    for (const duplicateInputId of findDuplicates(round.inputSnapshotIds)) {
      addIssue("duplicate_input_snapshot", `journey.roundRecords.${round.roundId}.inputSnapshotIds.${duplicateInputId}`);
    }
    for (const inputId of round.inputSnapshotIds) {
      if (!snapshotsById.has(inputId)) {
        addIssue("missing_snapshot", `journey.roundRecords.${round.roundId}.inputSnapshotIds.${inputId}`);
        continue;
      }
      const ownerId = outputOwners.get(inputId);
      if (!originIds.has(inputId) && (!ownerId || !ancestorIds.has(ownerId))) {
        addIssue("invalid_input_snapshot", `journey.roundRecords.${round.roundId}.inputSnapshotIds.${inputId}`);
      }
    }

    const handoffRefs = [
      ...(round.handoff?.carryoverRefs ?? []),
      ...(round.handoff?.heldRefs ?? []),
    ];
    for (const ref of handoffRefs) {
      const snapshot = snapshotsById.get(ref.snapshotId);
      if (!snapshot || !getArtifactIds(snapshot, ref.kind).has(ref.entityId)) {
        addIssue("missing_handoff_artifact", `journey.roundRecords.${round.roundId}.handoff.${ref.entityId}`);
      }
    }
    for (const request of round.handoff?.fieldworkRequests ?? []) {
      for (const ref of request.outcome?.responseCardRefs ?? []) {
        const snapshot = snapshotsById.get(ref.snapshotId);
        if (!snapshot || !snapshot.document.cards.some((card) => card.id === ref.cardId)) {
          addIssue("missing_handoff_artifact", `journey.roundRecords.${round.roundId}.handoff.${request.requestId}`);
        }
      }
    }
  }

  for (const duplicateId of findDuplicates(bundle.cardLineage.map((edge) => edge.lineageId))) {
    addIssue("duplicate_lineage_id", `cardLineage.${duplicateId}`);
  }

  for (const edge of bundle.cardLineage) {
    const addresses = getLineageAddresses(edge);
    if (
      (edge.kind === "split" && addresses.to.length < 2)
      || (edge.kind === "merged" && addresses.from.length < 2)
      || (edge.kind === "derived" && addresses.from.length < 1)
      || findDuplicates(addresses.from.map(addressKey)).size > 0
      || findDuplicates(addresses.to.map(addressKey)).size > 0
    ) {
      addIssue("invalid_lineage_cardinality", `cardLineage.${edge.lineageId}`);
    }

    for (const address of [...addresses.from, ...addresses.to]) {
      const snapshot = snapshotsById.get(address.snapshotId);
      if (!snapshot || !snapshot.document.cards.some((card) => card.id === address.cardId)) {
        addIssue("missing_lineage_card", `cardLineage.${edge.lineageId}.${address.snapshotId}.${address.cardId}`);
      }
    }

    for (const target of addresses.to) {
      const targetOwner = outputOwners.get(target.snapshotId);
      if (!targetOwner) {
        addIssue("invalid_lineage_direction", `cardLineage.${edge.lineageId}.to`);
        continue;
      }
      const targetAncestors = collectAncestorIds(targetOwner, roundsById);
      for (const source of addresses.from) {
        const sourceOwner = outputOwners.get(source.snapshotId);
        if (!originIds.has(source.snapshotId) && (!sourceOwner || !targetAncestors.has(sourceOwner))) {
          addIssue("invalid_lineage_direction", `cardLineage.${edge.lineageId}.from`);
        }
      }
    }
  }

  return issues;
}
