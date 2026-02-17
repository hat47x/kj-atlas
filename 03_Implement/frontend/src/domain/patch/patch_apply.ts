import type { Card, DocumentV2, Edge, Island, PatchApplyStats, PatchConflictMeta, RelationSummary } from "../types";
import { detectPatchConflicts } from "./conflict_detect";
import type { PatchLintResult } from "./patch_lint";

export type PatchOpKind =
  | "upsert_card"
  | "delete_card"
  | "upsert_island"
  | "delete_island"
  | "upsert_edge"
  | "delete_edge"
  | "upsert_relation_summary"
  | "delete_relation_summary";

export type PatchOp =
  | { id: string; kind: "upsert_card"; card: Card }
  | { id: string; kind: "delete_card"; cardId: string }
  | { id: string; kind: "upsert_island"; island: Island }
  | { id: string; kind: "delete_island"; islandId: string }
  | { id: string; kind: "upsert_edge"; edge: Edge }
  | { id: string; kind: "delete_edge"; edgeId: string }
  | { id: string; kind: "upsert_relation_summary"; relationSummary: RelationSummary }
  | { id: string; kind: "delete_relation_summary"; sourceSignature: string };

export type PatchDocument = {
  kind: "kj-atlas-patch";
  version: 1;
  baseDocSignature?: string;
  ops: PatchOp[];
};

export type PatchResolution = "yours" | "theirs" | "skip";

export type ApplyResultMeta = {
  appliedOpIds: string[];
  stats: PatchApplyStats;
  conflictMeta?: PatchConflictMeta;
  patchTitle?: string;
  baseDocSignature?: string;
  note?: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function parseCard(value: unknown): Card | null {
  if (!isRecord(value) || typeof value.id !== "string" || typeof value.text !== "string" || !isFiniteNumber(value.x) || !isFiniteNumber(value.y)) {
    return null;
  }

  if (value.canonicalId !== undefined && typeof value.canonicalId !== "string") return null;
  if (value.sources !== undefined && !isStringArray(value.sources)) return null;
  if (value.critique !== undefined && typeof value.critique !== "string") return null;
  if (value.critiqueTags !== undefined && !isStringArray(value.critiqueTags)) return null;
  if (value.textReviewed !== undefined && typeof value.textReviewed !== "boolean") return null;

  return value as Card;
}

function parseEdge(value: unknown): Edge | null {
  if (!isRecord(value) || typeof value.id !== "string" || typeof value.fromId !== "string" || typeof value.toId !== "string") {
    return null;
  }

  if (value.type !== "related" && value.type !== "negate") return null;
  if (value.fromKind !== undefined && value.fromKind !== "card" && value.fromKind !== "island") return null;
  if (value.toKind !== undefined && value.toKind !== "card" && value.toKind !== "island") return null;

  return value as Edge;
}

function parseIsland(value: unknown): Island | null {
  if (!isRecord(value) || typeof value.id !== "string" || !isStringArray(value.cardIds)) {
    return null;
  }

  if (value.parentIslandId !== undefined && typeof value.parentIslandId !== "string") return null;
  if (value.collapsed !== undefined && typeof value.collapsed !== "boolean") return null;
  if (value.title !== undefined && typeof value.title !== "string") return null;
  if (value.titleReviewed !== undefined && typeof value.titleReviewed !== "boolean") return null;
  if (value.summaryText !== undefined && typeof value.summaryText !== "string") return null;
  if (value.summaryReviewed !== undefined && typeof value.summaryReviewed !== "boolean") return null;
  if (value.summaryGrounding !== undefined && !isStringArray(value.summaryGrounding)) return null;
  if (value.imageUrl !== undefined && typeof value.imageUrl !== "string") return null;
  if (value.imageReviewed !== undefined && typeof value.imageReviewed !== "boolean") return null;
  if (value.critique !== undefined && typeof value.critique !== "string") return null;
  if (value.critiqueTags !== undefined && !isStringArray(value.critiqueTags)) return null;
  if (value.shapeStale !== undefined && typeof value.shapeStale !== "boolean") return null;

  return value as Island;
}

function parseRelationSummary(value: unknown): RelationSummary | null {
  if (
    !isRecord(value) ||
    typeof value.id !== "string" ||
    typeof value.createdAt !== "string" ||
    typeof value.islandAId !== "string" ||
    typeof value.islandBId !== "string" ||
    (value.relationType !== "related" && value.relationType !== "negate" && value.relationType !== "unknown") ||
    typeof value.derived !== "boolean" ||
    typeof value.text !== "string" ||
    typeof value.reviewed !== "boolean" ||
    !isStringArray(value.groundingCardIds) ||
    !isStringArray(value.groundingEdgeIds) ||
    typeof value.sourceSignature !== "string"
  ) {
    return null;
  }

  if (value.warnings !== undefined && !isStringArray(value.warnings)) return null;

  return value as RelationSummary;
}

export function parsePatchDocument(value: unknown): PatchDocument | null {
  if (!isRecord(value) || value.kind !== "kj-atlas-patch" || value.version !== 1 || !Array.isArray(value.ops)) {
    return null;
  }

  const ops: PatchOp[] = [];

  for (const item of value.ops) {
    if (!isRecord(item) || typeof item.id !== "string" || typeof item.kind !== "string") {
      return null;
    }

    if (item.kind === "upsert_card") {
      const card = parseCard(item.card);
      if (!card) return null;
      ops.push({ id: item.id, kind: item.kind, card });
      continue;
    }

    if (item.kind === "delete_card" && typeof item.cardId === "string") {
      ops.push({ id: item.id, kind: item.kind, cardId: item.cardId });
      continue;
    }

    if (item.kind === "upsert_island") {
      const island = parseIsland(item.island);
      if (!island) return null;
      ops.push({ id: item.id, kind: item.kind, island });
      continue;
    }

    if (item.kind === "delete_island" && typeof item.islandId === "string") {
      ops.push({ id: item.id, kind: item.kind, islandId: item.islandId });
      continue;
    }

    if (item.kind === "upsert_edge") {
      const edge = parseEdge(item.edge);
      if (!edge) return null;
      ops.push({ id: item.id, kind: item.kind, edge });
      continue;
    }

    if (item.kind === "delete_edge" && typeof item.edgeId === "string") {
      ops.push({ id: item.id, kind: item.kind, edgeId: item.edgeId });
      continue;
    }

    if (item.kind === "upsert_relation_summary") {
      const relationSummary = parseRelationSummary(item.relationSummary);
      if (!relationSummary) return null;
      ops.push({ id: item.id, kind: item.kind, relationSummary });
      continue;
    }

    if (item.kind === "delete_relation_summary" && typeof item.sourceSignature === "string") {
      ops.push({ id: item.id, kind: item.kind, sourceSignature: item.sourceSignature });
      continue;
    }

    return null;
  }

  return {
    kind: "kj-atlas-patch",
    version: 1,
    baseDocSignature: typeof value.baseDocSignature === "string" ? value.baseDocSignature : undefined,
    ops,
  };
}

export function shouldBlockPatchApplyByLint(lintResult: PatchLintResult | null): boolean {
  if (!lintResult) {
    return false;
  }

  return lintResult.issues.some((issue) => issue.severity === "error");
}

export function getPatchOpEntityKey(op: PatchOp): string {
  switch (op.kind) {
    case "upsert_card":
      return `card:${op.card.id}`;
    case "delete_card":
      return `card:${op.cardId}`;
    case "upsert_island":
      return `island:${op.island.id}`;
    case "delete_island":
      return `island:${op.islandId}`;
    case "upsert_edge":
      return `edge:${op.edge.id}`;
    case "delete_edge":
      return `edge:${op.edgeId}`;
    case "upsert_relation_summary":
      return `relSummary:${op.relationSummary.sourceSignature}`;
    case "delete_relation_summary":
      return `relSummary:${op.sourceSignature}`;
  }
}

function upsertById<T extends { id: string }>(items: T[], value: T): T[] {
  const index = items.findIndex((item) => item.id === value.id);
  if (index < 0) {
    return [...items, value];
  }

  const next = [...items];
  next[index] = value;
  return next;
}

function applyPatchOp(currentDoc: DocumentV2, op: PatchOp): DocumentV2 {
  switch (op.kind) {
    case "upsert_card":
      return { ...currentDoc, cards: upsertById(currentDoc.cards, op.card) };
    case "delete_card":
      return { ...currentDoc, cards: currentDoc.cards.filter((card) => card.id !== op.cardId) };
    case "upsert_island":
      return { ...currentDoc, islands: upsertById(currentDoc.islands, op.island) };
    case "delete_island":
      return { ...currentDoc, islands: currentDoc.islands.filter((island) => island.id !== op.islandId) };
    case "upsert_edge":
      return { ...currentDoc, edges: upsertById(currentDoc.edges, op.edge) };
    case "delete_edge":
      return { ...currentDoc, edges: currentDoc.edges.filter((edge) => edge.id !== op.edgeId) };
    case "upsert_relation_summary": {
      const existing = currentDoc.relationSummaries ?? [];
      const index = existing.findIndex((summary) => summary.sourceSignature === op.relationSummary.sourceSignature);
      if (index < 0) {
        return { ...currentDoc, relationSummaries: [...existing, op.relationSummary] };
      }

      const next = [...existing];
      next[index] = op.relationSummary;
      return { ...currentDoc, relationSummaries: next };
    }
    case "delete_relation_summary":
      return {
        ...currentDoc,
        relationSummaries: (currentDoc.relationSummaries ?? []).filter((summary) => summary.sourceSignature !== op.sourceSignature),
      };
  }
}

export function applyPatchWithResolutions(
  currentDoc: DocumentV2,
  patch: PatchDocument,
  resolutions: Record<string, PatchResolution>,
  baselineDoc?: DocumentV2,
  selectedOpIds?: Set<string>
): DocumentV2 {
  return applyPatchWithResolutionsDetailed(currentDoc, patch, resolutions, baselineDoc, selectedOpIds).document;
}

function createEmptyApplyStats(): PatchApplyStats {
  return {
    upsertCards: 0,
    deleteCards: 0,
    upsertIslands: 0,
    deleteIslands: 0,
    upsertEdges: 0,
    deleteEdges: 0,
    upsertRelationSummaries: 0,
    deleteRelationSummaries: 0,
  };
}

function incrementApplyStats(stats: PatchApplyStats, kind: PatchOpKind): void {
  switch (kind) {
    case "upsert_card":
      stats.upsertCards += 1;
      break;
    case "delete_card":
      stats.deleteCards += 1;
      break;
    case "upsert_island":
      stats.upsertIslands += 1;
      break;
    case "delete_island":
      stats.deleteIslands += 1;
      break;
    case "upsert_edge":
      stats.upsertEdges += 1;
      break;
    case "delete_edge":
      stats.deleteEdges += 1;
      break;
    case "upsert_relation_summary":
      stats.upsertRelationSummaries += 1;
      break;
    case "delete_relation_summary":
      stats.deleteRelationSummaries += 1;
      break;
  }
}

export function applyPatchWithResolutionsDetailed(
  currentDoc: DocumentV2,
  patch: PatchDocument,
  resolutions: Record<string, PatchResolution>,
  baselineDoc?: DocumentV2,
  selectedOpIds?: Set<string>
): { document: DocumentV2; meta: ApplyResultMeta } {
  const conflictReport = baselineDoc ? detectPatchConflicts(baselineDoc, currentDoc, patch) : null;
  const conflictOpIdSet = new Set(conflictReport ? conflictReport.conflicts.map((item) => item.opId) : []);

  let nextDoc = currentDoc;
  const appliedOpIds: string[] = [];
  const stats = createEmptyApplyStats();
  const chosenConflictCounts: PatchConflictMeta = {
    totalConflicts: conflictReport?.conflicts.length ?? 0,
    chosenYours: 0,
    chosenTheirs: 0,
    chosenSkip: 0,
  };

  for (const op of patch.ops) {
    if (selectedOpIds && !selectedOpIds.has(op.id)) {
      continue;
    }

    if (conflictOpIdSet.has(op.id)) {
      const resolution = resolutions[op.id] ?? "skip";
      if (resolution === "theirs") {
        chosenConflictCounts.chosenTheirs += 1;
        nextDoc = applyPatchOp(nextDoc, op);
        appliedOpIds.push(op.id);
        incrementApplyStats(stats, op.kind);
        continue;
      }
      if (resolution === "yours") {
        chosenConflictCounts.chosenYours += 1;
      } else {
        chosenConflictCounts.chosenSkip += 1;
      }
      continue;
    }

    nextDoc = applyPatchOp(nextDoc, op);
    appliedOpIds.push(op.id);
    incrementApplyStats(stats, op.kind);
  }

  return {
    document: nextDoc,
    meta: {
      appliedOpIds,
      stats,
      conflictMeta: conflictReport ? chosenConflictCounts : undefined,
    },
  };
}
