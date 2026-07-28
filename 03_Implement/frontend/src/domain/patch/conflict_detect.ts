import type { Card, DocumentV1, Edge, EvidenceLink, Island, RelationSummary } from "../types";
import { stableSerialize } from "../../utils/stable_serialize";
import type { PatchDocument, PatchOp, PatchOpKind } from "./patch_apply";

export type ConflictItem = {
  opId: string;
  kind: PatchOpKind;
  entityKey: string;
  baseValue: Card | Island | Edge | RelationSummary | EvidenceLink | null;
  yourValue: Card | Island | Edge | RelationSummary | EvidenceLink | null;
  theirValue: Card | Island | Edge | RelationSummary | EvidenceLink | null;
  reason: string;
};

export type ConflictReport = {
  conflicts: ConflictItem[];
  nonConflictingOpIds: string[];
};

function getPatchOpEntityKey(op: PatchOp): string {
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
    case "upsert_evidence_link":
      return `evidenceLink:${op.evidenceLink.id}`;
    case "delete_evidence_link":
      return `evidenceLink:${op.evidenceLinkId}`;
  }
}

function isEqual(left: unknown, right: unknown): boolean {
  return stableSerialize(left) === stableSerialize(right);
}

function getDocEntityByOp(doc: DocumentV1, op: PatchOp): Card | Island | Edge | RelationSummary | EvidenceLink | null {
  switch (op.kind) {
    case "upsert_card":
    case "delete_card":
      return doc.cards.find((card) => card.id === (op.kind === "upsert_card" ? op.card.id : op.cardId)) ?? null;
    case "upsert_island":
    case "delete_island":
      return doc.islands.find((island) => island.id === (op.kind === "upsert_island" ? op.island.id : op.islandId)) ?? null;
    case "upsert_edge":
    case "delete_edge":
      return doc.edges.find((edge) => edge.id === (op.kind === "upsert_edge" ? op.edge.id : op.edgeId)) ?? null;
    case "upsert_relation_summary":
    case "delete_relation_summary": {
      const signature = op.kind === "upsert_relation_summary" ? op.relationSummary.sourceSignature : op.sourceSignature;
      return (doc.relationSummaries ?? []).find((summary) => summary.sourceSignature === signature) ?? null;
    }
    case "upsert_evidence_link":
    case "delete_evidence_link": {
      const evidenceLinkId = op.kind === "upsert_evidence_link" ? op.evidenceLink.id : op.evidenceLinkId;
      return (doc.evidenceLinks ?? []).find((link) => link.id === evidenceLinkId) ?? null;
    }
  }
}

function getTheirValue(op: PatchOp): Card | Island | Edge | RelationSummary | EvidenceLink | null {
  switch (op.kind) {
    case "upsert_card":
      return op.card;
    case "delete_card":
      return null;
    case "upsert_island":
      return op.island;
    case "delete_island":
      return null;
    case "upsert_edge":
      return op.edge;
    case "delete_edge":
      return null;
    case "upsert_relation_summary":
      return op.relationSummary;
    case "delete_relation_summary":
      return null;
    case "upsert_evidence_link":
      return op.evidenceLink;
    case "delete_evidence_link":
      return null;
  }
}

function buildReason(baseChanged: boolean, yourValue: unknown, theirValue: unknown): string {
  if (!baseChanged) {
    return "both modified";
  }

  if (yourValue === null && theirValue !== null) {
    return "delete vs update";
  }

  if (yourValue !== null && theirValue === null) {
    return "update vs delete";
  }

  return "both modified";
}

export function detectPatchConflicts(baselineDoc: DocumentV1, currentDoc: DocumentV1, patch: PatchDocument): ConflictReport {
  const conflicts: ConflictItem[] = [];
  const nonConflictingOpIds: string[] = [];

  for (const op of patch.ops) {
    const entityKey = getPatchOpEntityKey(op);
    const baseValue = getDocEntityByOp(baselineDoc, op);
    const yourValue = getDocEntityByOp(currentDoc, op);
    const theirValue = getTheirValue(op);

    const baseToYourChanged = !isEqual(baseValue, yourValue);
    const baseToTheirChanged = !isEqual(baseValue, theirValue);
    const yourAndTheirUnequal = !isEqual(yourValue, theirValue);

    if (baseToYourChanged && baseToTheirChanged && yourAndTheirUnequal) {
      conflicts.push({
        opId: op.id,
        kind: op.kind,
        entityKey,
        baseValue,
        yourValue,
        theirValue,
        reason: buildReason(baseToYourChanged, yourValue, theirValue),
      });
      continue;
    }

    nonConflictingOpIds.push(op.id);
  }

  return {
    conflicts,
    nonConflictingOpIds,
  };
}
