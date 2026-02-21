import type { MergeItem } from "../../diff/merge_items";

export const MERGE_AUDIT_LOG_LIMIT = 50;
export const MERGE_AUDIT_DETAILS_LIMIT = 200;

type MergeAuditWarning = "stripped_disallowed_fields";

export type MergeAuditSource = {
  kind: "zip" | "unknown";
  fileName?: string;
  packId?: string;
};

export type MergeAuditIdList = {
  ids: string[];
  truncatedCount?: number;
};

export type MergeAuditEntityIds = {
  cards?: MergeAuditIdList;
  islands?: MergeAuditIdList;
  evidence?: MergeAuditIdList;
};

export type MergeAuditEntry = {
  id: string;
  createdAt: string;
  source: MergeAuditSource;
  summary: {
    totalItems: number;
    byKind: Record<string, number>;
    warnings?: MergeAuditWarning[];
  };
  details: {
    itemIds?: MergeAuditIdList;
    entityIds?: MergeAuditEntityIds;
  };
};

export type MergeAuditAppendOptions = {
  maxEntries?: number;
  maxIdsPerEntry?: number;
};

const DISALLOWED_FIELD_NAMES = new Set(["text", "body", "content", "summarytext"]);

function isDisallowedFieldName(value: string): boolean {
  const normalized = value.toLowerCase().replace(/[^a-z]/g, "");
  if (DISALLOWED_FIELD_NAMES.has(normalized)) {
    return true;
  }

  return normalized.endsWith("text") || normalized.endsWith("body") || normalized.endsWith("content") || normalized.endsWith("summarytext");
}

function assertNoDisallowedText(value: unknown, path: string): void {
  if (!import.meta.env.DEV || !value || typeof value !== "object") {
    return;
  }

  for (const [key, nextValue] of Object.entries(value as Record<string, unknown>)) {
    if (isDisallowedFieldName(key)) {
      throw new Error(`merge audit privacy guard rejected \"${path}.${key}\"`);
    }

    assertNoDisallowedText(nextValue, `${path}.${key}`);
  }
}

function dedupe(values: string[]): string[] {
  const next: string[] = [];
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      continue;
    }

    seen.add(value);
    next.push(value);
  }

  return next;
}

function toLimitedIdList(values: string[], limit: number): MergeAuditIdList | undefined {
  const unique = dedupe(values);
  if (unique.length === 0) {
    return undefined;
  }

  const ids = unique.slice(0, limit);
  const truncatedCount = unique.length - ids.length;
  return {
    ids,
    ...(truncatedCount > 0 ? { truncatedCount } : {}),
  };
}

function hasAnyEntityIds(value: MergeAuditEntityIds): boolean {
  return Boolean(value.cards || value.islands || value.evidence);
}

function addWarning(summary: MergeAuditEntry["summary"], warning: MergeAuditWarning): MergeAuditEntry["summary"] {
  const warnings = summary.warnings ?? [];
  if (warnings.includes(warning)) {
    return summary;
  }

  return { ...summary, warnings: [...warnings, warning] };
}

function readStringArray(value: unknown): string[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter((entry): entry is string => typeof entry === "string");
}

function sanitizeEntry(input: unknown, maxIdsPerEntry: number): MergeAuditEntry | null {
  if (!input || typeof input !== "object") {
    return null;
  }

  const candidate = input as Record<string, unknown>;
  if (typeof candidate.id !== "string" || typeof candidate.createdAt !== "string") {
    return null;
  }

  const sourceRaw = candidate.source;
  if (!sourceRaw || typeof sourceRaw !== "object") {
    return null;
  }

  const source = sourceRaw as Record<string, unknown>;
  if (source.kind !== "zip" && source.kind !== "unknown") {
    return null;
  }

  const summaryRaw = candidate.summary;
  if (!summaryRaw || typeof summaryRaw !== "object") {
    return null;
  }

  const summaryInput = summaryRaw as Record<string, unknown>;
  if (typeof summaryInput.totalItems !== "number" || !Number.isFinite(summaryInput.totalItems)) {
    return null;
  }

  if (!summaryInput.byKind || typeof summaryInput.byKind !== "object" || Array.isArray(summaryInput.byKind)) {
    return null;
  }

  const byKind: Record<string, number> = {};
  for (const [kind, count] of Object.entries(summaryInput.byKind as Record<string, unknown>)) {
    if (typeof count !== "number" || !Number.isFinite(count)) {
      return null;
    }

    byKind[kind] = count;
  }

  let summary: MergeAuditEntry["summary"] = {
    totalItems: summaryInput.totalItems,
    byKind,
  };

  const detailsInput = candidate.details && typeof candidate.details === "object" ? (candidate.details as Record<string, unknown>) : {};
  const entityInput = detailsInput.entityIds && typeof detailsInput.entityIds === "object"
    ? (detailsInput.entityIds as Record<string, unknown>)
    : {};

  const itemIds = Array.isArray(detailsInput.itemIds)
    ? toLimitedIdList(readStringArray(detailsInput.itemIds), maxIdsPerEntry)
    : toLimitedIdList(readStringArray((detailsInput.itemIds as Record<string, unknown> | undefined)?.ids), maxIdsPerEntry);
  const cards = Array.isArray(entityInput.cards)
    ? toLimitedIdList(readStringArray(entityInput.cards), maxIdsPerEntry)
    : toLimitedIdList(readStringArray((entityInput.cards as Record<string, unknown> | undefined)?.ids), maxIdsPerEntry);
  const islands = Array.isArray(entityInput.islands)
    ? toLimitedIdList(readStringArray(entityInput.islands), maxIdsPerEntry)
    : toLimitedIdList(readStringArray((entityInput.islands as Record<string, unknown> | undefined)?.ids), maxIdsPerEntry);
  const evidence = Array.isArray(entityInput.evidence)
    ? toLimitedIdList(readStringArray(entityInput.evidence), maxIdsPerEntry)
    : toLimitedIdList(readStringArray((entityInput.evidence as Record<string, unknown> | undefined)?.ids), maxIdsPerEntry);

  const entityIds: MergeAuditEntityIds = {
    ...(cards ? { cards } : {}),
    ...(islands ? { islands } : {}),
    ...(evidence ? { evidence } : {}),
  };

  const hasDisallowedFields = (() => {
    const check = (value: unknown): boolean => {
      if (!value || typeof value !== "object") {
        return false;
      }

      for (const [key, child] of Object.entries(value as Record<string, unknown>)) {
        if (isDisallowedFieldName(key)) {
          return true;
        }

        if (check(child)) {
          return true;
        }
      }

      return false;
    };

    return check(candidate);
  })();

  if (hasDisallowedFields) {
    summary = addWarning(summary, "stripped_disallowed_fields");
  }

  const sanitized: MergeAuditEntry = {
    id: candidate.id,
    createdAt: candidate.createdAt,
    source: {
      kind: source.kind,
      ...(typeof source.fileName === "string" ? { fileName: source.fileName } : {}),
      ...(typeof source.packId === "string" ? { packId: source.packId } : {}),
    },
    summary,
    details: {
      ...(itemIds ? { itemIds } : {}),
      ...(hasAnyEntityIds(entityIds) ? { entityIds } : {}),
    },
  };

  assertNoDisallowedText(sanitized, "mergeAuditEntry");
  return sanitized;
}

export function createMergeAuditEntry(selectedItems: MergeItem[], source?: MergeAuditSource, createdAt?: string): MergeAuditEntry {
  const byKind: Record<string, number> = {};
  const cardIds: string[] = [];
  const islandIds: string[] = [];
  const evidenceIds: string[] = [];

  for (const item of selectedItems) {
    byKind[item.kind] = (byKind[item.kind] ?? 0) + 1;
    if (item.entityRef.kind === "card") {
      cardIds.push(item.entityRef.id);
    }
    if (item.entityRef.kind === "island") {
      islandIds.push(item.entityRef.id);
    }
    if (item.entityRef.kind === "evidence") {
      evidenceIds.push(item.entityRef.id);
    }
  }

  const timestamp = createdAt ?? new Date().toISOString();

  return sanitizeEntry({
    id: `merge-${timestamp}-${Math.random().toString(16).slice(2, 10)}`,
    createdAt: timestamp,
    source: source ?? { kind: "unknown" },
    summary: {
      totalItems: selectedItems.length,
      byKind,
    },
    details: {
      itemIds: selectedItems.map((item) => item.id),
      entityIds: {
        cards: cardIds,
        islands: islandIds,
        evidence: evidenceIds,
      },
    },
  }, MERGE_AUDIT_DETAILS_LIMIT) as MergeAuditEntry;
}

export function appendMergeAuditEntry<T extends { mergeAuditLog?: MergeAuditEntry[] }>(
  viewState: T,
  entry: MergeAuditEntry,
  options?: MergeAuditAppendOptions,
): T {
  const maxEntries = options?.maxEntries ?? MERGE_AUDIT_LOG_LIMIT;
  const maxIdsPerEntry = options?.maxIdsPerEntry ?? MERGE_AUDIT_DETAILS_LIMIT;
  const current = sanitizeMergeAuditLog(viewState.mergeAuditLog, { maxEntries, maxIdsPerEntry });
  const safeEntry = sanitizeEntry(entry, maxIdsPerEntry);
  if (!safeEntry) {
    return { ...viewState, mergeAuditLog: current };
  }

  const nextEntries = [...current, safeEntry];
  return {
    ...viewState,
    mergeAuditLog: nextEntries.length > maxEntries ? nextEntries.slice(nextEntries.length - maxEntries) : nextEntries,
  };
}

export function appendMergeAuditLog(current: MergeAuditEntry[] | undefined, entry: MergeAuditEntry): MergeAuditEntry[] {
  return appendMergeAuditEntry({ mergeAuditLog: current }, entry).mergeAuditLog ?? [];
}

export function sanitizeMergeAuditLog(value: unknown, options?: MergeAuditAppendOptions): MergeAuditEntry[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const maxEntries = options?.maxEntries ?? MERGE_AUDIT_LOG_LIMIT;
  const maxIdsPerEntry = options?.maxIdsPerEntry ?? MERGE_AUDIT_DETAILS_LIMIT;

  const entries: MergeAuditEntry[] = [];
  for (const item of value) {
    const sanitized = sanitizeEntry(item, maxIdsPerEntry);
    if (!sanitized) {
      continue;
    }

    entries.push(sanitized);
  }

  return entries.length > maxEntries ? entries.slice(entries.length - maxEntries) : entries;
}
