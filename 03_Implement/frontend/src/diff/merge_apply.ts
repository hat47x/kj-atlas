import { applyPatchWithResolutionsDetailed } from "../domain/patch/patch_apply";
import { lintPatchAgainstCurrentDoc } from "../domain/patch/patch_lint";
import type { PatchDocument, PatchOp } from "../domain/patch/patch_apply";
import type { DocumentV2 } from "../domain/types";
import { validateDocument } from "../import/schema_validation";
import type { MergeItem } from "./merge_items";
import { createMergeAuditEntry, type MergeAuditEntry, type MergeAuditSource } from "../domain/view/audit_log";

function sortById<T extends { id: string }>(values: T[]): T[] {
  return [...values].sort((left, right) => left.id.localeCompare(right.id));
}

function buildOpList(baseDoc: DocumentV2, incomingDoc: DocumentV2, selectedItems: MergeItem[]): PatchOp[] {
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

export function buildSelectedPatchFromItems(baseDoc: DocumentV2, incomingDoc: DocumentV2, selectedItems: MergeItem[]): PatchDocument {
  return {
    kind: "kj-atlas-patch",
    version: 1,
    baseDocSignature: `${baseDoc.id}:${baseDoc.updatedAt}`,
    ops: buildOpList(baseDoc, incomingDoc, selectedItems),
  };
}


export function buildMergeAuditEntry(selectedItems: MergeItem[], source?: MergeAuditSource): MergeAuditEntry {
  return createMergeAuditEntry(selectedItems, source);
}

export function applySelectedMergeItemsAtomic(currentDoc: DocumentV2, baseDoc: DocumentV2, incomingDoc: DocumentV2, selectedItems: MergeItem[]): { ok: true; document: DocumentV2 } | { ok: false; reason: string } {
  const preflightDocs = [
    { label: "current", value: currentDoc },
    { label: "base", value: baseDoc },
    { label: "incoming", value: incomingDoc },
  ] as const;

  for (const entry of preflightDocs) {
    const validation = validateDocument(entry.value, { evidenceEndpointSeverity: "error" });
    if (!validation.ok) {
      const formatted = validation.errors.map((error) => `[${error.code}] ${error.path}: ${error.message}`).join("\n");
      return { ok: false, reason: `Merge preflight failed (${entry.label} document):\n${formatted}` };
    }
  }
  const patch = buildSelectedPatchFromItems(baseDoc, incomingDoc, selectedItems);
  const lint = lintPatchAgainstCurrentDoc(currentDoc, patch);
  if (lint.issues.some((issue) => issue.severity === "error")) {
    return { ok: false, reason: lint.issues.map((issue) => issue.message).join("\n") };
  }

  const applied = applyPatchWithResolutionsDetailed(currentDoc, patch, {}, undefined, new Set(patch.ops.map((op) => op.id)));
  const nextDoc: DocumentV2 = {
    ...applied.document,
    readingOrder: selectedItems.some((item) => item.kind === "view.field" && item.field === "readingOrder") ? (incomingDoc.readingOrder ?? []) : applied.document.readingOrder,
  };

  return { ok: true, document: nextDoc };
}
