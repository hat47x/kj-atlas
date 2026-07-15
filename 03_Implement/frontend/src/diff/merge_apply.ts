import { applyPatchWithResolutionsDetailed } from "../domain/patch/patch_apply";
import { lintPatchAgainstCurrentDoc } from "../domain/patch/patch_lint";
import type { PatchDocument, PatchOp } from "../domain/patch/patch_apply";
import type { DocumentV1 } from "../domain/types";
import { validateDocument } from "../import/schema_validation";
import type { MergeItem, MergeItemRef } from "./merge_items";
import { createMergeAuditEntry, type MergeAuditEntry, type MergeAuditSource } from "../domain/view/audit_log";
import { detectPatchConflicts } from "../domain/patch/conflict_detect";

const MERGE_SELECTED_ITEMS_SOFT_LIMIT = 200;
const MERGE_SELECTED_ITEMS_HARD_LIMIT = 1000;

type MergeDiagnostic = {
  code: string;
  message: string;
};

export type MergePreflightResult =
  | {
      ok: true;
      patchOrPlan: PatchDocument;
      warnings: MergeDiagnostic[];
      selectedItems: MergeItem[];
    }
  | {
      ok: false;
      errors: MergeDiagnostic[];
    };

export type MergeTransactionResult = { ok: true; document: DocumentV1; warnings: MergeDiagnostic[] } | { ok: false; errors: MergeDiagnostic[] };

function sortById<T extends { id: string }>(values: T[]): T[] {
  return [...values].sort((left, right) => left.id.localeCompare(right.id));
}

function makeSyntheticItem(kind: "card.add" | "evidence.remove", id: string): MergeItem {
  return {
    id: `auto:${kind}:${id}`,
    kind,
    entityRef: { kind: kind === "card.add" ? "card" : "evidence", id },
    prerequisites: [],
  };
}

function toRefKey(ref: MergeItemRef): string {
  return `${ref.kind}:${ref.id}`;
}

function selectWithAutoPrerequisites(baseDoc: DocumentV1, incomingDoc: DocumentV1, selectedItems: MergeItem[]): { selectedItems: MergeItem[]; warnings: MergeDiagnostic[]; errors: MergeDiagnostic[] } {
  const warnings: MergeDiagnostic[] = [];
  const errors: MergeDiagnostic[] = [];
  const selectedMap = new Map(selectedItems.map((item) => [item.id, item]));
  const selectedRefKeys = new Set(selectedItems.map((item) => toRefKey(item.entityRef)));

  for (const item of selectedItems) {
    if (item.kind === "evidence.add") {
      const link = (incomingDoc.evidenceLinks ?? []).find((entry) => entry.id === item.entityRef.id);
      if (!link) {
        errors.push({ code: "M001", message: `Selected evidence.add ${item.entityRef.id} does not exist in incoming document.` });
        continue;
      }

      for (const cardId of [link.fromCardId, link.toCardId]) {
        if (selectedRefKeys.has(`card:${cardId}`) || baseDoc.cards.some((card) => card.id === cardId)) {
          continue;
        }

        const incomingCard = incomingDoc.cards.find((card) => card.id === cardId);
        if (!incomingCard) {
          errors.push({ code: "M002", message: `evidence.add ${item.entityRef.id} depends on missing card ${cardId}.` });
          continue;
        }

        const synthetic = makeSyntheticItem("card.add", cardId);
        if (!selectedMap.has(synthetic.id)) {
          selectedMap.set(synthetic.id, synthetic);
          selectedRefKeys.add(`card:${cardId}`);
          warnings.push({ code: "M101", message: `Auto-included prerequisite card.add ${cardId} for evidence.add ${item.entityRef.id}.` });
        }
      }
    }

    if (item.kind === "card.remove") {
      const dependentEvidence = (baseDoc.evidenceLinks ?? []).filter((link) => link.fromCardId === item.entityRef.id || link.toCardId === item.entityRef.id);
      for (const link of dependentEvidence) {
        const evidenceRefKey = `evidence:${link.id}`;
        if (selectedRefKeys.has(evidenceRefKey)) {
          continue;
        }

        const incomingHasLink = (incomingDoc.evidenceLinks ?? []).some((incomingLink) => incomingLink.id === link.id);
        if (incomingHasLink) {
          errors.push({
            code: "M003",
            message: `card.remove ${item.entityRef.id} requires dependent evidence.remove ${link.id} (still present in incoming document).`,
          });
          continue;
        }

        const synthetic = makeSyntheticItem("evidence.remove", link.id);
        if (!selectedMap.has(synthetic.id)) {
          selectedMap.set(synthetic.id, synthetic);
          selectedRefKeys.add(evidenceRefKey);
          warnings.push({ code: "M102", message: `Auto-included evidence.remove ${link.id} for card.remove ${item.entityRef.id}.` });
        }
      }
    }
  }

  return { selectedItems: [...selectedMap.values()], warnings, errors };
}

function buildOpList(incomingDoc: DocumentV1, selectedItems: MergeItem[]): PatchOp[] {
  const selectedCardUpserts = new Set<string>();
  const selectedCardDeletes = new Set<string>();
  const selectedIslandUpserts = new Set<string>();
  const selectedIslandDeletes = new Set<string>();
  const selectedEdgeUpserts = new Set<string>();
  const selectedEdgeDeletes = new Set<string>();
  const selectedEvidenceUpserts = new Set<string>();
  const selectedEvidenceDeletes = new Set<string>();
  const selectedRelationUpserts = new Set<string>();
  const selectedRelationDeletes = new Set<string>();

  for (const item of selectedItems) {
    switch (item.kind) {
      case "card.add":
      case "card.field":
        selectedCardUpserts.add(item.entityRef.id);
        break;
      case "card.remove":
        selectedCardDeletes.add(item.entityRef.id);
        break;
      case "island.add":
      case "island.field":
        selectedIslandUpserts.add(item.entityRef.id);
        break;
      case "island.remove":
        selectedIslandDeletes.add(item.entityRef.id);
        break;
      case "edge.add":
        selectedEdgeUpserts.add(item.entityRef.id);
        break;
      case "edge.remove":
        selectedEdgeDeletes.add(item.entityRef.id);
        break;
      case "evidence.add":
        selectedEvidenceUpserts.add(item.entityRef.id);
        break;
      case "evidence.remove":
        selectedEvidenceDeletes.add(item.entityRef.id);
        break;
      case "relationSummary.field": {
        const existsIncoming = (incomingDoc.relationSummaries ?? []).some((summary) => summary.sourceSignature === item.entityRef.id);
        if (existsIncoming) {
          selectedRelationUpserts.add(item.entityRef.id);
        } else {
          selectedRelationDeletes.add(item.entityRef.id);
        }
        break;
      }
      case "view.field":
        break;
    }
  }

  const ops: PatchOp[] = [];

  for (const cardId of [...selectedCardUpserts].sort((a, b) => a.localeCompare(b))) {
    const card = incomingDoc.cards.find((entry) => entry.id === cardId);
    if (card) {
      ops.push({ id: `merge:upsert_card:${cardId}`, kind: "upsert_card", card });
    }
  }

  for (const cardId of [...selectedCardDeletes].sort((a, b) => a.localeCompare(b))) {
    ops.push({ id: `merge:delete_card:${cardId}`, kind: "delete_card", cardId });
  }

  for (const islandId of [...selectedIslandUpserts].sort((a, b) => a.localeCompare(b))) {
    const island = incomingDoc.islands.find((entry) => entry.id === islandId);
    if (island) {
      ops.push({ id: `merge:upsert_island:${islandId}`, kind: "upsert_island", island });
    }
  }

  for (const islandId of [...selectedIslandDeletes].sort((a, b) => a.localeCompare(b))) {
    ops.push({ id: `merge:delete_island:${islandId}`, kind: "delete_island", islandId });
  }

  for (const edgeId of [...selectedEdgeUpserts].sort((a, b) => a.localeCompare(b))) {
    const edge = incomingDoc.edges.find((entry) => entry.id === edgeId);
    if (edge) {
      ops.push({ id: `merge:upsert_edge:${edgeId}`, kind: "upsert_edge", edge });
    }
  }

  for (const edgeId of [...selectedEdgeDeletes].sort((a, b) => a.localeCompare(b))) {
    ops.push({ id: `merge:delete_edge:${edgeId}`, kind: "delete_edge", edgeId });
  }

  for (const evidenceId of [...selectedEvidenceUpserts].sort((a, b) => a.localeCompare(b))) {
    const evidenceLink = (incomingDoc.evidenceLinks ?? []).find((entry) => entry.id === evidenceId);
    if (evidenceLink) {
      ops.push({ id: `merge:upsert_evidence_link:${evidenceId}`, kind: "upsert_evidence_link", evidenceLink });
    }
  }

  for (const evidenceId of [...selectedEvidenceDeletes].sort((a, b) => a.localeCompare(b))) {
    ops.push({ id: `merge:delete_evidence_link:${evidenceId}`, kind: "delete_evidence_link", evidenceLinkId: evidenceId });
  }

  for (const sourceSignature of [...selectedRelationUpserts].sort((a, b) => a.localeCompare(b))) {
    const relationSummary = (incomingDoc.relationSummaries ?? []).find((entry) => entry.sourceSignature === sourceSignature);
    if (relationSummary) {
      ops.push({ id: `merge:upsert_relation_summary:${sourceSignature}`, kind: "upsert_relation_summary", relationSummary });
    }
  }

  for (const sourceSignature of [...selectedRelationDeletes].sort((a, b) => a.localeCompare(b))) {
    ops.push({ id: `merge:delete_relation_summary:${sourceSignature}`, kind: "delete_relation_summary", sourceSignature });
  }

  return sortById(ops);
}

export function buildSelectedPatchFromItems(baseDoc: DocumentV1, incomingDoc: DocumentV1, selectedItems: MergeItem[]): PatchDocument {
  return {
    kind: "kj-atlas-patch",
    version: 1,
    baseDocSignature: `${baseDoc.id}:${baseDoc.updatedAt}`,
    ops: buildOpList(incomingDoc, selectedItems),
  };
}

export function preflightMerge(baseDoc: DocumentV1, selectedItems: MergeItem[], incomingDoc: DocumentV1): MergePreflightResult {
  const preflightDocs = [
    { label: "base", value: baseDoc },
    { label: "incoming", value: incomingDoc },
  ] as const;

  const errors: MergeDiagnostic[] = [];
  for (const entry of preflightDocs) {
    const validation = validateDocument(entry.value, { evidenceEndpointSeverity: "error" });
    if (!validation.ok) {
      errors.push(
        ...validation.errors.map((error) => ({
          code: `SCHEMA:${entry.label}`,
          message: `[${error.code}] ${error.path}: ${error.message}`,
        }))
      );
    }
  }

  if (selectedItems.length > MERGE_SELECTED_ITEMS_HARD_LIMIT) {
    errors.push({ code: "M004", message: `Selected merge items (${selectedItems.length}) exceed hard limit (${MERGE_SELECTED_ITEMS_HARD_LIMIT}).` });
  }

  if (errors.length > 0) {
    return { ok: false, errors };
  }

  const prereqPlan = selectWithAutoPrerequisites(baseDoc, incomingDoc, selectedItems);
  if (prereqPlan.errors.length > 0) {
    return { ok: false, errors: prereqPlan.errors };
  }

  const patch = buildSelectedPatchFromItems(baseDoc, incomingDoc, prereqPlan.selectedItems);
  const lint = lintPatchAgainstCurrentDoc(baseDoc, patch);
  const lintErrors = lint.issues.filter((issue) => issue.severity === "error").map((issue) => ({ code: issue.code, message: issue.message }));
  if (lintErrors.length > 0) {
    return { ok: false, errors: lintErrors };
  }

  const warnings: MergeDiagnostic[] = [...prereqPlan.warnings, ...lint.issues.filter((issue) => issue.severity !== "error").map((issue) => ({ code: issue.code, message: issue.message }))];
  if (selectedItems.length > MERGE_SELECTED_ITEMS_SOFT_LIMIT) {
    warnings.push({ code: "M103", message: `Large merge selection (${selectedItems.length} items). Review carefully before applying.` });
  }

  return { ok: true, patchOrPlan: patch, warnings, selectedItems: prereqPlan.selectedItems };
}

export function buildMergeAuditEntry(selectedItems: MergeItem[], source?: MergeAuditSource): MergeAuditEntry {
  return createMergeAuditEntry(selectedItems, source);
}

export function applyMergeTransaction(
  currentDoc: DocumentV1,
  snapshotDoc: DocumentV1,
  baseDoc: DocumentV1,
  incomingDoc: DocumentV1,
  selectedItems: MergeItem[],
  options?: { allowWarnings?: boolean }
): MergeTransactionResult {
  const preflight = preflightMerge(baseDoc, selectedItems, incomingDoc);
  if (!preflight.ok) {
    return { ok: false, errors: preflight.errors };
  }

  if (preflight.warnings.length > 0 && !options?.allowWarnings) {
    return { ok: false, errors: [{ code: "M105", message: "Merge preflight has warnings. Explicit confirmation required." }, ...preflight.warnings] };
  }

  const conflicts = detectPatchConflicts(snapshotDoc, currentDoc, preflight.patchOrPlan);
  if (conflicts.conflicts.length > 0) {
    return {
      ok: false,
      errors: conflicts.conflicts.map((conflict) => ({ code: "M006", message: `Conflict on ${conflict.entityKey}: ${conflict.reason}` })),
    };
  }

  const currentLint = lintPatchAgainstCurrentDoc(currentDoc, preflight.patchOrPlan);
  const currentLintErrors = currentLint.issues
    .filter((issue) => issue.severity === "error")
    .map((issue) => ({ code: `CUR:${issue.code}`, message: issue.message }));
  if (currentLintErrors.length > 0) {
    return { ok: false, errors: currentLintErrors };
  }

  const applied = applyPatchWithResolutionsDetailed(currentDoc, preflight.patchOrPlan, {}, undefined, new Set(preflight.patchOrPlan.ops.map((op) => op.id)));
  const nextDoc: DocumentV1 = {
    ...applied.document,
    readingOrder: preflight.selectedItems.some((item) => item.kind === "view.field" && item.field === "readingOrder") ? (incomingDoc.readingOrder ?? []) : applied.document.readingOrder,
  };

  const postValidation = validateDocument(nextDoc, { evidenceEndpointSeverity: "error" });
  if (!postValidation.ok) {
    return {
      ok: false,
      errors: postValidation.errors.map((error) => ({ code: `POST:${error.code}`, message: `${error.path}: ${error.message}` })),
    };
  }

  return { ok: true, document: nextDoc, warnings: preflight.warnings };
}

export function applySelectedMergeItemsAtomic(currentDoc: DocumentV1, baseDoc: DocumentV1, incomingDoc: DocumentV1, selectedItems: MergeItem[]): { ok: true; document: DocumentV1 } | { ok: false; reason: string } {
  const result = applyMergeTransaction(currentDoc, baseDoc, baseDoc, incomingDoc, selectedItems, { allowWarnings: true });
  if (!result.ok) {
    return { ok: false, reason: result.errors.map((error) => `[${error.code}] ${error.message}`).join("\n") };
  }

  return { ok: true, document: result.document };
}
