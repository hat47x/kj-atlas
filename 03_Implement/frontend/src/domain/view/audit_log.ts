import type { MergeItem } from "../../diff/merge_items";

export const MERGE_AUDIT_LOG_LIMIT = 50;
export const MERGE_AUDIT_DETAILS_LIMIT = 200;

export type MergeAuditSource = {
  kind: "zip" | "unknown";
  fileName?: string;
  packId?: string;
};

export type MergeAuditEntityIds = {
  cards?: string[];
  islands?: string[];
  evidence?: string[];
};

export type MergeAuditEntry = {
  id: string;
  createdAt: string;
  source: MergeAuditSource;
  summary: {
    totalItems: number;
    byKind: Record<string, number>;
  };
  details: {
    itemIds?: string[];
    entityIds?: MergeAuditEntityIds;
  };
  notes?: string;
};

function toLimitedUnique(values: string[], limit: number): string[] {
  const next: string[] = [];
  const seen = new Set<string>();
  for (const value of values) {
    if (seen.has(value)) {
      continue;
    }
    seen.add(value);
    next.push(value);
    if (next.length >= limit) {
      break;
    }
  }

  return next;
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

  const itemIds = toLimitedUnique(selectedItems.map((item) => item.id), MERGE_AUDIT_DETAILS_LIMIT);
  const cards = toLimitedUnique(cardIds, MERGE_AUDIT_DETAILS_LIMIT);
  const islands = toLimitedUnique(islandIds, MERGE_AUDIT_DETAILS_LIMIT);
  const evidence = toLimitedUnique(evidenceIds, MERGE_AUDIT_DETAILS_LIMIT);

  const timestamp = createdAt ?? new Date().toISOString();

  return {
    id: `merge-${timestamp}-${Math.random().toString(16).slice(2, 10)}`,
    createdAt: timestamp,
    source: source ?? { kind: "unknown" },
    summary: {
      totalItems: selectedItems.length,
      byKind,
    },
    details: {
      itemIds,
      entityIds: {
        ...(cards.length > 0 ? { cards } : {}),
        ...(islands.length > 0 ? { islands } : {}),
        ...(evidence.length > 0 ? { evidence } : {}),
      },
    },
  };
}

export function appendMergeAuditLog(current: MergeAuditEntry[] | undefined, entry: MergeAuditEntry): MergeAuditEntry[] {
  const base = current ?? [];
  const next = [...base, entry];
  if (next.length <= MERGE_AUDIT_LOG_LIMIT) {
    return next;
  }

  return next.slice(next.length - MERGE_AUDIT_LOG_LIMIT);
}

export function sanitizeMergeAuditLog(value: unknown): MergeAuditEntry[] {
  if (!Array.isArray(value)) {
    return [];
  }

  const entries: MergeAuditEntry[] = [];
  for (const item of value) {
    if (!item || typeof item !== "object") {
      continue;
    }

    const candidate = item as Record<string, unknown>;
    if (typeof candidate.id !== "string" || typeof candidate.createdAt !== "string") {
      continue;
    }

    const sourceRaw = candidate.source;
    if (!sourceRaw || typeof sourceRaw !== "object") {
      continue;
    }
    const source = sourceRaw as Record<string, unknown>;
    if (source.kind !== "zip" && source.kind !== "unknown") {
      continue;
    }

    const summaryRaw = candidate.summary;
    if (!summaryRaw || typeof summaryRaw !== "object") {
      continue;
    }
    const summary = summaryRaw as Record<string, unknown>;
    if (typeof summary.totalItems !== "number" || !Number.isFinite(summary.totalItems)) {
      continue;
    }
    if (!summary.byKind || typeof summary.byKind !== "object" || Array.isArray(summary.byKind)) {
      continue;
    }

    const byKind: Record<string, number> = {};
    let byKindValid = true;
    for (const [key, count] of Object.entries(summary.byKind as Record<string, unknown>)) {
      if (typeof count !== "number" || !Number.isFinite(count)) {
        byKindValid = false;
        break;
      }
      byKind[key] = count;
    }
    if (!byKindValid) {
      continue;
    }

    const detailsRaw = candidate.details;
    const details = detailsRaw && typeof detailsRaw === "object" ? (detailsRaw as Record<string, unknown>) : {};
    const itemIds = Array.isArray(details.itemIds)
      ? toLimitedUnique(details.itemIds.filter((entry): entry is string => typeof entry === "string"), MERGE_AUDIT_DETAILS_LIMIT)
      : undefined;

    const entityIdsRaw = details.entityIds;
    const entityIdsRecord = entityIdsRaw && typeof entityIdsRaw === "object" ? (entityIdsRaw as Record<string, unknown>) : {};
    const cards = Array.isArray(entityIdsRecord.cards)
      ? toLimitedUnique(entityIdsRecord.cards.filter((entry): entry is string => typeof entry === "string"), MERGE_AUDIT_DETAILS_LIMIT)
      : undefined;
    const islands = Array.isArray(entityIdsRecord.islands)
      ? toLimitedUnique(entityIdsRecord.islands.filter((entry): entry is string => typeof entry === "string"), MERGE_AUDIT_DETAILS_LIMIT)
      : undefined;
    const evidence = Array.isArray(entityIdsRecord.evidence)
      ? toLimitedUnique(entityIdsRecord.evidence.filter((entry): entry is string => typeof entry === "string"), MERGE_AUDIT_DETAILS_LIMIT)
      : undefined;

    entries.push({
      id: candidate.id,
      createdAt: candidate.createdAt,
      source: {
        kind: source.kind,
        ...(typeof source.fileName === "string" ? { fileName: source.fileName } : {}),
        ...(typeof source.packId === "string" ? { packId: source.packId } : {}),
      },
      summary: {
        totalItems: summary.totalItems,
        byKind,
      },
      details: {
        ...(itemIds && itemIds.length > 0 ? { itemIds } : {}),
        ...((cards && cards.length > 0) || (islands && islands.length > 0) || (evidence && evidence.length > 0)
          ? {
            entityIds: {
              ...(cards && cards.length > 0 ? { cards } : {}),
              ...(islands && islands.length > 0 ? { islands } : {}),
              ...(evidence && evidence.length > 0 ? { evidence } : {}),
            },
          }
          : {}),
      },
      ...(typeof candidate.notes === "string" ? { notes: candidate.notes } : {}),
    });
  }

  if (entries.length <= MERGE_AUDIT_LOG_LIMIT) {
    return entries;
  }

  return entries.slice(entries.length - MERGE_AUDIT_LOG_LIMIT);
}
