import type { DocumentV1 } from "../types";
import type { PatchDocument, PatchOp } from "./patch_apply";
import type { PatchLintResult } from "./patch_lint";

export type PatchTransform =
  | { kind: "removeMissingIslandCardRefs"; islandId: string; removedCardIds: string[] }
  | { kind: "dropEdgesWithMissingEndpoints"; removedEdgeIds: string[] }
  | { kind: "pruneMissingRelationGroundings"; sourceSignature: string; removedCardIds: string[]; removedEdgeIds: string[] };

export type FixProposal = {
  fixId: string;
  title: string;
  description: string;
  severity: "safe" | "risky";
  targetIssueCodes: string[];
  affectedOpIds: string[];
  patchTransform: PatchTransform;
};

type SimulatedPostApplyModel = {
  patch: PatchDocument;
  cardIds: Set<string>;
  edgeIds: Set<string>;
};

function parseEntityId(entityKey: string | undefined, prefix: string): string | null {
  if (!entityKey || !entityKey.startsWith(`${prefix}:`)) {
    return null;
  }

  return entityKey.slice(prefix.length + 1);
}

function unique<T>(items: T[]): T[] {
  return [...new Set(items)];
}

function findUpsertIslandOpIds(patch: PatchDocument, islandId: string): string[] {
  return patch.ops.filter((op) => op.kind === "upsert_island" && op.island.id === islandId).map((op) => op.id);
}

function findUpsertEdgeOpIds(patch: PatchDocument, edgeIds: Set<string>): string[] {
  return patch.ops
    .filter((op) => op.kind === "upsert_edge" && edgeIds.has(op.edge.id))
    .map((op) => op.id);
}

function findUpsertRelationSummaryOpIds(patch: PatchDocument, sourceSignature: string): string[] {
  return patch.ops
    .filter((op) => op.kind === "upsert_relation_summary" && op.relationSummary.sourceSignature === sourceSignature)
    .map((op) => op.id);
}

export function proposeFixesAgainstSimulatedPostApply(tempModel: SimulatedPostApplyModel, lintResult: PatchLintResult): FixProposal[] {
  const proposals: FixProposal[] = [];

  const p001ByIsland = new Map<string, Set<string>>();
  for (const issue of lintResult.issues) {
    if (issue.code !== "P001") continue;
    const islandId = parseEntityId(issue.entityKey, "island");
    if (!islandId) continue;
    const existing = p001ByIsland.get(islandId) ?? new Set<string>();
    for (const cardId of issue.relatedIds ?? []) {
      existing.add(cardId);
    }
    p001ByIsland.set(islandId, existing);
  }

  for (const [islandId, removedCardIdsSet] of p001ByIsland) {
    const removedCardIds = [...removedCardIdsSet];
    const affectedOpIds = findUpsertIslandOpIds(tempModel.patch, islandId);
    if (removedCardIds.length === 0 || affectedOpIds.length === 0) continue;

    proposals.push({
      fixId: `fix-p001-${islandId}`,
      title: `Remove missing card refs from island ${islandId}`,
      description: `Remove ${removedCardIds.length} missing card reference(s) from island ${islandId}.`,
      severity: "safe",
      targetIssueCodes: ["P001"],
      affectedOpIds,
      patchTransform: {
        kind: "removeMissingIslandCardRefs",
        islandId,
        removedCardIds,
      },
    });
  }

  const missingEdgeIds = new Set<string>();
  for (const issue of lintResult.issues) {
    if (issue.code !== "P002") continue;
    const edgeId = parseEntityId(issue.entityKey, "edge");
    if (!edgeId) continue;
    missingEdgeIds.add(edgeId);
  }

  if (missingEdgeIds.size > 0) {
    const affectedOpIds = findUpsertEdgeOpIds(tempModel.patch, missingEdgeIds);
    const removedEdgeIdsBuffer: string[] = [];
    for (const op of tempModel.patch.ops) {
      if (op.kind !== "upsert_edge") continue;
      if (!missingEdgeIds.has(op.edge.id)) continue;
      removedEdgeIdsBuffer.push(op.edge.id);
    }
    const removedEdgeIds = unique(removedEdgeIdsBuffer);

    if (affectedOpIds.length > 0 && removedEdgeIds.length > 0) {
      proposals.push({
        fixId: "fix-p002-drop-upsert-edges-with-missing-endpoints",
        title: "Drop upsert_edge ops with missing endpoints",
        description: `Remove ${removedEdgeIds.length} edge upsert op(s) that reference missing card/island endpoints.`,
        severity: "safe",
        targetIssueCodes: ["P002"],
        affectedOpIds,
        patchTransform: {
          kind: "dropEdgesWithMissingEndpoints",
          removedEdgeIds,
        },
      });
    }
  }

  const p005BySummary = new Map<string, { cardIds: Set<string>; edgeIds: Set<string> }>();
  const p005SourceSignatures = new Set<string>();
  for (const issue of lintResult.issues) {
    if (issue.code !== "P005") continue;
    const sourceSignature = parseEntityId(issue.entityKey, "relSummary");
    if (!sourceSignature) continue;
    p005SourceSignatures.add(sourceSignature);
  }

  for (const sourceSignature of p005SourceSignatures) {
    const relationUpsertOp = tempModel.patch.ops.find(
      (op) => op.kind === "upsert_relation_summary" && op.relationSummary.sourceSignature === sourceSignature
    );

    if (!relationUpsertOp || relationUpsertOp.kind !== "upsert_relation_summary") {
      continue;
    }

    const missingCardIds = new Set<string>();
    const missingEdgeIds = new Set<string>();

    for (const cardId of relationUpsertOp.relationSummary.groundingCardIds) {
      if (!tempModel.cardIds.has(cardId)) {
        missingCardIds.add(cardId);
      }
    }

    for (const edgeId of relationUpsertOp.relationSummary.groundingEdgeIds) {
      if (!tempModel.edgeIds.has(edgeId)) {
        missingEdgeIds.add(edgeId);
      }
    }

    for (const historyEntry of relationUpsertOp.relationSummary.history ?? []) {
      for (const cardId of historyEntry.groundingCardIdsSnapshot ?? []) {
        if (!tempModel.cardIds.has(cardId)) {
          missingCardIds.add(cardId);
        }
      }
      for (const edgeId of historyEntry.groundingEdgeIdsSnapshot ?? []) {
        if (!tempModel.edgeIds.has(edgeId)) {
          missingEdgeIds.add(edgeId);
        }
      }
    }

    if (missingCardIds.size === 0 && missingEdgeIds.size === 0) {
      continue;
    }

    p005BySummary.set(sourceSignature, { cardIds: missingCardIds, edgeIds: missingEdgeIds });
  }

  for (const [sourceSignature, removed] of p005BySummary) {
    const removedCardIds = [...removed.cardIds];
    const removedEdgeIds = [...removed.edgeIds];
    const affectedOpIds = findUpsertRelationSummaryOpIds(tempModel.patch, sourceSignature);
    if (affectedOpIds.length === 0 || (removedCardIds.length === 0 && removedEdgeIds.length === 0)) continue;

    proposals.push({
      fixId: `fix-p005-${sourceSignature}`,
      title: `Prune missing grounding ids in relation ${sourceSignature}`,
      description: `Remove missing grounding refs (cards: ${removedCardIds.length}, edges: ${removedEdgeIds.length}) from relation summary ${sourceSignature}.`,
      severity: "safe",
      targetIssueCodes: ["P005"],
      affectedOpIds,
      patchTransform: {
        kind: "pruneMissingRelationGroundings",
        sourceSignature,
        removedCardIds,
        removedEdgeIds,
      },
    });
  }

  return proposals;
}

export function proposeFixes(currentDoc: DocumentV1, patch: PatchDocument, lintResult: PatchLintResult): FixProposal[] {
  const cardIds = new Set(currentDoc.cards.map((card) => card.id));
  const edgeIds = new Set(currentDoc.edges.map((edge) => edge.id));

  for (const op of patch.ops) {
    if (op.kind === "upsert_card") cardIds.add(op.card.id);
    if (op.kind === "delete_card") cardIds.delete(op.cardId);
    if (op.kind === "upsert_edge") edgeIds.add(op.edge.id);
    if (op.kind === "delete_edge") edgeIds.delete(op.edgeId);
  }

  return proposeFixesAgainstSimulatedPostApply({ patch, cardIds, edgeIds }, lintResult);
}

function applyPatchTransform(op: PatchOp, transform: PatchTransform): PatchOp {
  if (transform.kind === "removeMissingIslandCardRefs" && op.kind === "upsert_island" && op.island.id === transform.islandId) {
    return {
      ...op,
      island: {
        ...op.island,
        cardIds: op.island.cardIds.filter((cardId) => !transform.removedCardIds.includes(cardId)),
      },
    };
  }

  if (transform.kind === "pruneMissingRelationGroundings" && op.kind === "upsert_relation_summary" && op.relationSummary.sourceSignature === transform.sourceSignature) {
    return {
      ...op,
      relationSummary: {
        ...op.relationSummary,
        groundingCardIds: op.relationSummary.groundingCardIds.filter((cardId) => !transform.removedCardIds.includes(cardId)),
        groundingEdgeIds: op.relationSummary.groundingEdgeIds.filter((edgeId) => !transform.removedEdgeIds.includes(edgeId)),
        history: (op.relationSummary.history ?? []).map((entry) => ({
          ...entry,
          groundingCardIdsSnapshot: (entry.groundingCardIdsSnapshot ?? []).filter((cardId) => !transform.removedCardIds.includes(cardId)),
          groundingEdgeIdsSnapshot: (entry.groundingEdgeIdsSnapshot ?? []).filter((edgeId) => !transform.removedEdgeIds.includes(edgeId)),
        })),
      },
    };
  }

  return op;
}

export function applyFixesToPatch(originalPatch: PatchDocument, selectedFixIds: string[], proposals: FixProposal[]): PatchDocument {
  const selectedSet = new Set(selectedFixIds);
  const selectedProposals = proposals.filter((proposal) => selectedSet.has(proposal.fixId));

  const dropEdgeIds = new Set<string>();
  const transforms: PatchTransform[] = [];

  for (const proposal of selectedProposals) {
    if (proposal.patchTransform.kind === "dropEdgesWithMissingEndpoints") {
      for (const edgeId of proposal.patchTransform.removedEdgeIds) {
        dropEdgeIds.add(edgeId);
      }
      continue;
    }
    transforms.push(proposal.patchTransform);
  }

  const nextOps = originalPatch.ops
    .filter((op) => !(op.kind === "upsert_edge" && dropEdgeIds.has(op.edge.id)))
    .map((op) => transforms.reduce((currentOp, transform) => applyPatchTransform(currentOp, transform), op));

  return {
    ...originalPatch,
    ops: nextOps,
  };
}
