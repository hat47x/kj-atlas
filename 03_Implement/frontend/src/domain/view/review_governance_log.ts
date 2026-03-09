import { sanitizeMergeAuditLog, type MergeAuditEntry } from "./audit_log";
import { sanitizeReviewEvents, type ReviewEvent } from "./review_events";

export const REVIEW_GOVERNANCE_LOG_LIMIT = 2000;

export type ReviewRedactionMode = "none" | "strip-identities" | "strip-all";

type GovernanceEntryRef = {
  kind: "merge" | "review";
  index: number;
  createdAt: string;
  id: string;
};

function sortRefs(left: GovernanceEntryRef, right: GovernanceEntryRef): number {
  const createdCompared = left.createdAt.localeCompare(right.createdAt);
  if (createdCompared !== 0) {
    return createdCompared;
  }

  if (left.kind !== right.kind) {
    return left.kind.localeCompare(right.kind);
  }

  return left.id.localeCompare(right.id);
}

function sortByCreatedAtThenId<T extends { createdAt: string; id: string }>(left: T, right: T): number {
  const createdCompared = left.createdAt.localeCompare(right.createdAt);
  if (createdCompared !== 0) {
    return createdCompared;
  }

  return left.id.localeCompare(right.id);
}

function dedupeByIdKeepingLatest<T extends { id: string; createdAt: string }>(entries: T[]): T[] {
  const byId = new Map<string, T>();
  for (const entry of [...entries].sort(sortByCreatedAtThenId)) {
    byId.set(entry.id, entry);
  }

  return [...byId.values()].sort(sortByCreatedAtThenId);
}

export function normalizeReviewGovernanceLogs(input: {
  mergeAuditLog?: unknown;
  reviewEvents?: unknown;
  maxEntries?: number;
  redactionMode?: ReviewRedactionMode;
}): { mergeAuditLog?: MergeAuditEntry[]; reviewEvents?: ReviewEvent[] } {
  const maxEntries = Math.max(1, input.maxEntries ?? REVIEW_GOVERNANCE_LOG_LIMIT);
  const redactionMode = input.redactionMode ?? "none";
  const hasMergeAuditLog = input.mergeAuditLog !== undefined;
  const hasReviewEvents = input.reviewEvents !== undefined;
  const mergeAuditLog = hasMergeAuditLog ? dedupeByIdKeepingLatest(sanitizeMergeAuditLog(input.mergeAuditLog, { maxEntries })) : [];
  const reviewEvents = hasReviewEvents ? dedupeByIdKeepingLatest(sanitizeReviewEvents(input.reviewEvents, { maxEvents: maxEntries })) : [];

  const refs: GovernanceEntryRef[] = [
    ...mergeAuditLog.map((entry, index) => ({ kind: "merge" as const, index, createdAt: entry.createdAt, id: entry.id })),
    ...reviewEvents.map((entry, index) => ({ kind: "review" as const, index, createdAt: entry.createdAt, id: entry.id })),
  ].sort(sortRefs);

  const trimStartIndex = Math.max(0, refs.length - maxEntries);
  const keepRefs = refs.slice(trimStartIndex);
  const keepMergeIndexes = new Set<number>();
  const keepReviewIndexes = new Set<number>();
  for (const ref of keepRefs) {
    if (ref.kind === "merge") {
      keepMergeIndexes.add(ref.index);
    } else {
      keepReviewIndexes.add(ref.index);
    }
  }

  const trimmedMergeAuditLog = mergeAuditLog.filter((_, index) => keepMergeIndexes.has(index));
  const trimmedReviewEvents = reviewEvents.filter((_, index) => keepReviewIndexes.has(index));

  if (redactionMode === "strip-all") {
    return { ...(hasMergeAuditLog ? { mergeAuditLog: trimmedMergeAuditLog } : {}) };
  }

  if (redactionMode === "strip-identities") {
    return {
      ...(hasMergeAuditLog ? { mergeAuditLog: trimmedMergeAuditLog } : {}),
      ...(hasReviewEvents
        ? {
            reviewEvents: trimmedReviewEvents.map((entry) => {
              const { reviewerRef: _reviewerRef, ...next } = entry;
              return next;
            }),
          }
        : {}),
    };
  }

  return {
    ...(hasMergeAuditLog ? { mergeAuditLog: trimmedMergeAuditLog } : {}),
    ...(hasReviewEvents ? { reviewEvents: trimmedReviewEvents } : {}),
  };
}
