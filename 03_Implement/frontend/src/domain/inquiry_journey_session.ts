import type { DocumentV1 } from "./types";
import { diffDocuments } from "./diff/doc_diff";
import {
  INQUIRY_SCHEMA_VERSION,
  appendRoundRecord,
  type CardAddressV1,
  type CardLineageEdgeV1,
  type InquiryBundleV1,
  type RoundSnapshotV1,
  type RoundStage,
} from "./inquiry_journey";
import { computeRoundSnapshotDigest } from "./inquiry_bundle_io";

type SessionOptions = {
  idFactory?: () => string;
  now?: () => string;
};

type RecordSessionOptions = SessionOptions & {
  parentRoundId?: string;
};

export type RecordInquiryRoundResult =
  | { ok: true; bundle: InquiryBundleV1 }
  | { ok: false; reason: "missing_input_snapshot" | "invalid_round" };

export type InquiryRoundComparisonSummary = {
  cards: number;
  islands: number;
  relationSummaries: number;
  readingOrderChanged: boolean;
};

export type CompareInquiryRoundsResult =
  | { ok: true; summary: InquiryRoundComparisonSummary }
  | { ok: false; reason: "round_not_found" | "snapshot_not_found" };

export type InquiryCardLineageNode = {
  address: CardAddressV1;
  text: string;
  source?: string;
  round?: { roundId: string; stage: RoundStage; iteration: number };
  viaKind?: CardLineageEdgeV1["kind"];
};

export type TraceInquiryCardLineageResult =
  | { ok: true; target: InquiryCardLineageNode; ancestors: InquiryCardLineageNode[] }
  | { ok: false; reason: "card_not_found" };

function addressKey(address: CardAddressV1): string {
  return `${address.snapshotId}\u0000${address.cardId}`;
}

function lineageSources(edge: CardLineageEdgeV1): CardAddressV1[] {
  if (edge.kind === "new") return [];
  return Array.isArray(edge.from) ? edge.from : [edge.from];
}

function lineageTargets(edge: CardLineageEdgeV1): CardAddressV1[] {
  if (edge.kind === "retired") return [];
  return Array.isArray(edge.to) ? edge.to : [edge.to];
}

export function traceInquiryCardLineage(
  bundle: InquiryBundleV1,
  targetAddress: CardAddressV1
): TraceInquiryCardLineageResult {
  const snapshots = new Map(bundle.snapshots.map((snapshot) => [snapshot.snapshotId, snapshot]));
  const roundsBySnapshot = new Map(
    bundle.journey.roundRecords
      .filter((round) => round.outputSnapshotId)
      .map((round) => [round.outputSnapshotId as string, round])
  );
  const buildNode = (address: CardAddressV1, viaKind?: CardLineageEdgeV1["kind"]): InquiryCardLineageNode | null => {
    const card = snapshots.get(address.snapshotId)?.document.cards.find((candidate) => candidate.id === address.cardId);
    if (!card) return null;
    const round = roundsBySnapshot.get(address.snapshotId);
    return {
      address,
      text: card.text,
      ...(card.meta?.source ? { source: card.meta.source } : {}),
      ...(round ? { round: { roundId: round.roundId, stage: round.stage, iteration: round.iteration } } : {}),
      ...(viaKind ? { viaKind } : {}),
    };
  };
  const target = buildNode(targetAddress);
  if (!target) return { ok: false, reason: "card_not_found" };

  const ancestors: InquiryCardLineageNode[] = [];
  const visited = new Set<string>([addressKey(targetAddress)]);
  const queue: CardAddressV1[] = [targetAddress];
  while (queue.length > 0) {
    const current = queue.shift() as CardAddressV1;
    for (const edge of bundle.cardLineage) {
      if (!lineageTargets(edge).some((address) => addressKey(address) === addressKey(current))) continue;
      for (const source of lineageSources(edge)) {
        const key = addressKey(source);
        if (visited.has(key)) continue;
        visited.add(key);
        const node = buildNode(source, edge.kind);
        if (!node) continue;
        ancestors.push(node);
        queue.push(source);
      }
    }
  }
  return { ok: true, target, ancestors };
}

export function inquiryBundleOriginatesFromDocument(bundle: InquiryBundleV1, documentId: string): boolean {
  const originIds = new Set(bundle.journey.originSnapshotIds);
  return bundle.snapshots.some((snapshot) => originIds.has(snapshot.snapshotId) && snapshot.document.id === documentId);
}

export function compareInquiryRounds(
  bundle: InquiryBundleV1,
  fromRoundId: string,
  toRoundId: string
): CompareInquiryRoundsResult {
  const fromRound = bundle.journey.roundRecords.find((round) => round.roundId === fromRoundId);
  const toRound = bundle.journey.roundRecords.find((round) => round.roundId === toRoundId);
  if (!fromRound || !toRound) return { ok: false, reason: "round_not_found" };

  const fromSnapshot = bundle.snapshots.find((snapshot) => snapshot.snapshotId === fromRound.outputSnapshotId);
  const toSnapshot = bundle.snapshots.find((snapshot) => snapshot.snapshotId === toRound.outputSnapshotId);
  if (!fromSnapshot || !toSnapshot) return { ok: false, reason: "snapshot_not_found" };

  const diff = diffDocuments(fromSnapshot.document, toSnapshot.document);
  return {
    ok: true,
    summary: {
      cards: diff.cards.added.length + diff.cards.removed.length + diff.cards.changedText.length,
      islands:
        diff.islands.added.length
        + diff.islands.removed.length
        + diff.islands.membershipChanged.length
        + diff.islands.summaryChanged.length,
      relationSummaries:
        diff.relationSummaries.added.length
        + diff.relationSummaries.removed.length
        + diff.relationSummaries.changedText.length
        + diff.relationSummaries.changedReviewed.length
        + diff.relationSummaries.warningsChanged.length,
      readingOrderChanged: diff.readingOrder.changed,
    },
  };
}

function defaultIdFactory(): string {
  return crypto.randomUUID();
}

function createSnapshot(
  snapshotId: string,
  createdAt: string,
  document: DocumentV1,
  canonicalDigest: `sha256:${string}`
): RoundSnapshotV1 {
  return {
    schemaVersion: INQUIRY_SCHEMA_VERSION,
    snapshotId,
    createdAt,
    canonicalDigest,
    document: structuredClone(document),
  };
}

export async function startInquiryJourney(
  document: DocumentV1,
  options: SessionOptions = {}
): Promise<InquiryBundleV1> {
  const idFactory = options.idFactory ?? defaultIdFactory;
  const createdAt = (options.now ?? (() => new Date().toISOString()))();
  const snapshotId = `snapshot-${idFactory()}`;
  const snapshot = createSnapshot(
    snapshotId,
    createdAt,
    document,
    await computeRoundSnapshotDigest(document)
  );

  return {
    schemaVersion: INQUIRY_SCHEMA_VERSION,
    journey: {
      schemaVersion: INQUIRY_SCHEMA_VERSION,
      journeyId: `journey-${idFactory()}`,
      title: document.title?.trim() || document.id,
      originSnapshotIds: [snapshotId],
      roundRecords: [],
      headRoundIds: [],
      createdAt,
      updatedAt: createdAt,
    },
    snapshots: [snapshot],
    cardLineage: [],
  };
}

function buildCardLineage(
  fromSnapshot: RoundSnapshotV1,
  toSnapshot: RoundSnapshotV1,
  idFactory: () => string
): CardLineageEdgeV1[] {
  const fromCards = new Map(fromSnapshot.document.cards.map((card) => [card.id, card]));
  const toCards = new Map(toSnapshot.document.cards.map((card) => [card.id, card]));
  const lineage: CardLineageEdgeV1[] = [];

  for (const [cardId, card] of toCards) {
    const previous = fromCards.get(cardId);
    if (!previous) {
      lineage.push({
        lineageId: `lineage-${idFactory()}`,
        kind: "new",
        to: { snapshotId: toSnapshot.snapshotId, cardId },
      });
      continue;
    }
    lineage.push({
      lineageId: `lineage-${idFactory()}`,
      kind: previous.text === card.text ? "carried" : "edited",
      from: { snapshotId: fromSnapshot.snapshotId, cardId },
      to: { snapshotId: toSnapshot.snapshotId, cardId },
    });
  }

  for (const cardId of fromCards.keys()) {
    if (!toCards.has(cardId)) {
      lineage.push({
        lineageId: `lineage-${idFactory()}`,
        kind: "retired",
        from: { snapshotId: fromSnapshot.snapshotId, cardId },
      });
    }
  }
  return lineage;
}

export async function recordInquiryRound(
  bundle: InquiryBundleV1,
  document: DocumentV1,
  stage: RoundStage,
  options: RecordSessionOptions = {}
): Promise<RecordInquiryRoundResult> {
  const idFactory = options.idFactory ?? defaultIdFactory;
  const recordedAt = (options.now ?? (() => new Date().toISOString()))();
  const parentRoundId = options.parentRoundId ?? bundle.journey.defaultHeadRoundId;
  const parentRound = parentRoundId
    ? bundle.journey.roundRecords.find((round) => round.roundId === parentRoundId)
    : undefined;
  if (parentRoundId && !parentRound) return { ok: false, reason: "invalid_round" };
  const inputSnapshotId = parentRound?.outputSnapshotId ?? bundle.journey.originSnapshotIds[0];
  const inputSnapshot = bundle.snapshots.find((snapshot) => snapshot.snapshotId === inputSnapshotId);
  if (!inputSnapshot) return { ok: false, reason: "missing_input_snapshot" };

  const outputSnapshot = createSnapshot(
    `snapshot-${idFactory()}`,
    recordedAt,
    document,
    await computeRoundSnapshotDigest(document)
  );
  const appended = appendRoundRecord(bundle.journey, {
    roundId: `round-${idFactory()}`,
    createdAt: recordedAt,
    updatedAt: recordedAt,
    stage,
    parentRoundIds: parentRoundId ? [parentRoundId] : [],
    status: "paused",
    theme: document.title?.trim() || document.id,
    inputSnapshotIds: [inputSnapshot.snapshotId],
    outputSnapshotId: outputSnapshot.snapshotId,
  });
  if (!appended.ok) return { ok: false, reason: "invalid_round" };

  return {
    ok: true,
    bundle: {
      ...bundle,
      journey: appended.journey,
      snapshots: [...bundle.snapshots, outputSnapshot],
      cardLineage: [
        ...bundle.cardLineage,
        ...buildCardLineage(inputSnapshot, outputSnapshot, idFactory),
      ],
    },
  };
}
