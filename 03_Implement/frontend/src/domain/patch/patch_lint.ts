import type { DocumentV1, Edge, EvidenceLink, Island, RelationSummary } from "../types";
import type { PatchDocument, PatchOp } from "./patch_apply";

export type PatchLintSeverity = "error" | "warn" | "info";

export type PatchLintIssue = {
  severity: PatchLintSeverity;
  code: string;
  message: string;
  opId?: string;
  entityKey?: string;
  relatedIds?: string[];
};

export type PatchLintResult = {
  issues: PatchLintIssue[];
};

type EntityMaps = {
  cards: Map<string, true>;
  islands: Map<string, Island>;
  edges: Map<string, Edge>;
  relationSummaries: Map<string, RelationSummary>;
  evidenceLinks: Map<string, EvidenceLink>;
};

function buildCurrentSignature(doc: DocumentV1): string {
  return `${doc.id}:${doc.updatedAt}`;
}

function applyPatchToMaps(currentDoc: DocumentV1, patch: PatchDocument): {
  maps: EntityMaps;
  lastOpByEntityKey: Map<string, string>;
  deleteCardOpById: Map<string, string>;
  deleteIslandOpById: Map<string, string>;
  deleteEdgeOpById: Map<string, string>;
} {
  const maps: EntityMaps = {
    cards: new Map(currentDoc.cards.map((card) => [card.id, true])),
    islands: new Map(currentDoc.islands.map((island) => [island.id, island])),
    edges: new Map(currentDoc.edges.map((edge) => [edge.id, edge])),
    relationSummaries: new Map((currentDoc.relationSummaries ?? []).map((summary) => [summary.sourceSignature, summary])),
    evidenceLinks: new Map((currentDoc.evidenceLinks ?? []).map((link) => [link.id, link])),
  };

  const lastOpByEntityKey = new Map<string, string>();
  const deleteCardOpById = new Map<string, string>();
  const deleteIslandOpById = new Map<string, string>();
  const deleteEdgeOpById = new Map<string, string>();

  for (const op of patch.ops) {
    switch (op.kind) {
      case "upsert_card":
        maps.cards.set(op.card.id, true);
        lastOpByEntityKey.set(`card:${op.card.id}`, op.id);
        break;
      case "delete_card":
        maps.cards.delete(op.cardId);
        lastOpByEntityKey.set(`card:${op.cardId}`, op.id);
        deleteCardOpById.set(op.cardId, op.id);
        break;
      case "upsert_island":
        maps.islands.set(op.island.id, op.island);
        lastOpByEntityKey.set(`island:${op.island.id}`, op.id);
        break;
      case "delete_island":
        maps.islands.delete(op.islandId);
        lastOpByEntityKey.set(`island:${op.islandId}`, op.id);
        deleteIslandOpById.set(op.islandId, op.id);
        break;
      case "upsert_edge":
        maps.edges.set(op.edge.id, op.edge);
        lastOpByEntityKey.set(`edge:${op.edge.id}`, op.id);
        break;
      case "delete_edge":
        maps.edges.delete(op.edgeId);
        lastOpByEntityKey.set(`edge:${op.edgeId}`, op.id);
        deleteEdgeOpById.set(op.edgeId, op.id);
        break;
      case "upsert_relation_summary":
        maps.relationSummaries.set(op.relationSummary.sourceSignature, op.relationSummary);
        lastOpByEntityKey.set(`relSummary:${op.relationSummary.sourceSignature}`, op.id);
        break;
      case "delete_relation_summary":
        maps.relationSummaries.delete(op.sourceSignature);
        lastOpByEntityKey.set(`relSummary:${op.sourceSignature}`, op.id);
        break;
      case "upsert_evidence_link":
        maps.evidenceLinks.set(op.evidenceLink.id, op.evidenceLink);
        lastOpByEntityKey.set(`evidenceLink:${op.evidenceLink.id}`, op.id);
        break;
      case "delete_evidence_link":
        maps.evidenceLinks.delete(op.evidenceLinkId);
        lastOpByEntityKey.set(`evidenceLink:${op.evidenceLinkId}`, op.id);
        break;
    }
  }

  return { maps, lastOpByEntityKey, deleteCardOpById, deleteIslandOpById, deleteEdgeOpById };
}

function findUpsertEntityKey(op: PatchOp): string | null {
  switch (op.kind) {
    case "upsert_card":
      return `card:${op.card.id}`;
    case "upsert_island":
      return `island:${op.island.id}`;
    case "upsert_edge":
      return `edge:${op.edge.id}`;
    case "upsert_relation_summary":
      return `relSummary:${op.relationSummary.sourceSignature}`;
    case "upsert_evidence_link":
      return `evidenceLink:${op.evidenceLink.id}`;
    default:
      return null;
  }
}

export function lintPatchAgainstCurrentDoc(currentDoc: DocumentV1, patch: PatchDocument): PatchLintResult {
  const issues: PatchLintIssue[] = [];

  const opIdCounts = new Map<string, number>();
  for (const op of patch.ops) {
    opIdCounts.set(op.id, (opIdCounts.get(op.id) ?? 0) + 1);
  }
  for (const [opId, count] of opIdCounts) {
    if (count > 1) {
      issues.push({
        severity: "error",
        code: "P007",
        message: `Duplicate opId detected: ${opId}`,
        opId,
      });
    }
  }

  const upsertOpIdsByEntityKey = new Map<string, string[]>();
  for (const op of patch.ops) {
    const entityKey = findUpsertEntityKey(op);
    if (!entityKey) continue;
    const existing = upsertOpIdsByEntityKey.get(entityKey) ?? [];
    upsertOpIdsByEntityKey.set(entityKey, [...existing, op.id]);
  }
  for (const [entityKey, opIds] of upsertOpIdsByEntityKey) {
    if (opIds.length > 1) {
      issues.push({
        severity: "warn",
        code: "P008",
        message: `Duplicate upserts detected for ${entityKey}; later op wins.`,
        opId: opIds[opIds.length - 1],
        entityKey,
        relatedIds: opIds,
      });
    }
  }

  if (patch.baseDocSignature && patch.baseDocSignature !== buildCurrentSignature(currentDoc)) {
    issues.push({
      severity: "warn",
      code: "P006",
      message: `Patch base signature mismatch (patch=${patch.baseDocSignature}, current=${buildCurrentSignature(currentDoc)}).`,
    });
  }

  const { maps, lastOpByEntityKey, deleteCardOpById, deleteIslandOpById, deleteEdgeOpById } = applyPatchToMaps(currentDoc, patch);

  for (const island of maps.islands.values()) {
    const missingCardIds = island.cardIds.filter((cardId) => !maps.cards.has(cardId));
    if (missingCardIds.length === 0) continue;

    issues.push({
      severity: "error",
      code: "P001",
      message: `Island ${island.id} references missing card(s): ${missingCardIds.join(", ")}`,
      opId: lastOpByEntityKey.get(`island:${island.id}`),
      entityKey: `island:${island.id}`,
      relatedIds: missingCardIds,
    });
  }

  for (const edge of maps.edges.values()) {
    const fromKind = edge.fromKind ?? "card";
    const toKind = edge.toKind ?? "card";
    const missing: string[] = [];
    let missingDeleteOpId: string | undefined;

    const fromMissing = fromKind === "card" ? !maps.cards.has(edge.fromId) : !maps.islands.has(edge.fromId);
    if (fromMissing) {
      missing.push(edge.fromId);
      missingDeleteOpId = fromKind === "card" ? deleteCardOpById.get(edge.fromId) : deleteIslandOpById.get(edge.fromId);
    }

    const toMissing = toKind === "card" ? !maps.cards.has(edge.toId) : !maps.islands.has(edge.toId);
    if (toMissing) {
      missing.push(edge.toId);
      if (!missingDeleteOpId) {
        missingDeleteOpId = toKind === "card" ? deleteCardOpById.get(edge.toId) : deleteIslandOpById.get(edge.toId);
      }
    }

    if (missing.length === 0) continue;

    issues.push({
      severity: "error",
      code: "P002",
      message: `Edge ${edge.id} references missing endpoint(s): ${missing.join(", ")}`,
      opId: missingDeleteOpId ?? lastOpByEntityKey.get(`edge:${edge.id}`),
      entityKey: `edge:${edge.id}`,
      relatedIds: missing,
    });
  }

  for (const op of patch.ops) {
    if (op.kind !== "delete_card") continue;

    const referencingIslandIds: string[] = [];
    for (const island of maps.islands.values()) {
      if (island.cardIds.includes(op.cardId)) {
        referencingIslandIds.push(island.id);
      }
    }

    const referencingRelationIds: string[] = [];
    for (const summary of maps.relationSummaries.values()) {
      const historyHasCard = (summary.history ?? []).some((entry) => entry.groundingCardIdsSnapshot?.includes(op.cardId));
      if (summary.groundingCardIds.includes(op.cardId) || historyHasCard) {
        referencingRelationIds.push(summary.sourceSignature);
      }
    }

    const relatedIds = [...referencingIslandIds.map((id) => `island:${id}`), ...referencingRelationIds.map((id) => `relSummary:${id}`)];

    if (relatedIds.length > 0) {
      issues.push({
        severity: "warn",
        code: "P003",
        message: `Deleting card ${op.cardId} leaves dangling references.`,
        opId: op.id,
        entityKey: `card:${op.cardId}`,
        relatedIds,
      });
    }
  }

  for (const evidenceLink of maps.evidenceLinks.values()) {
    const missing: string[] = [];
    if (!maps.cards.has(evidenceLink.fromCardId)) {
      missing.push(evidenceLink.fromCardId);
    }
    if (!maps.cards.has(evidenceLink.toCardId)) {
      missing.push(evidenceLink.toCardId);
    }

    if (missing.length === 0) {
      continue;
    }

    const opId =
      lastOpByEntityKey.get(`evidenceLink:${evidenceLink.id}`) ??
      deleteCardOpById.get(missing[0] ?? "");

    issues.push({
      severity: "error",
      code: "P009",
      message: `EvidenceLink ${evidenceLink.id} references missing cardId(s): ${missing.join(", ")}`,
      opId,
      entityKey: `evidenceLink:${evidenceLink.id}`,
      relatedIds: missing,
    });
  }

  for (const op of patch.ops) {
    if (op.kind !== "delete_island") continue;

    const referencingEdges = [...maps.edges.values()].filter((edge) => {
      const fromKind = edge.fromKind ?? "card";
      const toKind = edge.toKind ?? "card";
      return (fromKind === "island" && edge.fromId === op.islandId) || (toKind === "island" && edge.toId === op.islandId);
    });

    if (referencingEdges.length > 0) {
      issues.push({
        severity: "warn",
        code: "P004",
        message: `Deleting island ${op.islandId} is referenced by edge endpoint(s).`,
        opId: op.id,
        entityKey: `island:${op.islandId}`,
        relatedIds: referencingEdges.map((edge) => edge.id),
      });
    }
  }

  for (const summary of maps.relationSummaries.values()) {
    const missingCardIds = summary.groundingCardIds.filter((cardId) => !maps.cards.has(cardId));
    const missingEdgeIds = summary.groundingEdgeIds.filter((edgeId) => !maps.edges.has(edgeId));

    const missingHistoryCardIds = (summary.history ?? [])
      .flatMap((entry) => entry.groundingCardIdsSnapshot ?? [])
      .filter((cardId) => !maps.cards.has(cardId));
    const missingHistoryEdgeIds = (summary.history ?? [])
      .flatMap((entry) => entry.groundingEdgeIdsSnapshot ?? [])
      .filter((edgeId) => !maps.edges.has(edgeId));

    const relatedIds = [...missingCardIds, ...missingEdgeIds, ...missingHistoryCardIds, ...missingHistoryEdgeIds];
    if (relatedIds.length === 0) continue;

    const opId =
      lastOpByEntityKey.get(`relSummary:${summary.sourceSignature}`) ??
      deleteCardOpById.get(missingCardIds[0] ?? missingHistoryCardIds[0] ?? "") ??
      deleteEdgeOpById.get(missingEdgeIds[0] ?? missingHistoryEdgeIds[0] ?? "");

    issues.push({
      severity: "warn",
      code: "P005",
      message: `RelationSummary ${summary.sourceSignature} references missing grounding card/edge ids.`,
      opId,
      entityKey: `relSummary:${summary.sourceSignature}`,
      relatedIds,
    });
  }

  return { issues };
}
