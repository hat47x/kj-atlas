import type { DocumentV1, EvidenceLink } from "../domain/types";
import type { ComputeTaskContext } from "../utils/compute_scheduler";
import { computeDocumentDiff, flattenDocumentDiff } from "./document_diff";
import { computeViewDiff } from "./view_diff";

export type MergeEntityKind = "card" | "island" | "edge" | "evidence" | "view" | "relationSummary";
export type MergeItemKind =
  | "card.add"
  | "card.remove"
  | "card.field"
  | "island.add"
  | "island.remove"
  | "island.field"
  | "edge.add"
  | "edge.remove"
  | "evidence.add"
  | "evidence.remove"
  | "relationSummary.field"
  | "view.field";

export type MergeItemRef = { kind: MergeEntityKind; id: string };

export type MergeItem = {
  id: string;
  kind: MergeItemKind;
  entityRef: MergeItemRef;
  field?: string;
  before?: unknown;
  after?: unknown;
  prerequisites: MergeItemRef[];
};

function toRefSetKey(ref: MergeItemRef): string {
  return `${ref.kind}:${ref.id}`;
}

function uniqueRefs(refs: MergeItemRef[]): MergeItemRef[] {
  const deduped = new Map<string, MergeItemRef>();
  for (const ref of refs) {
    deduped.set(toRefSetKey(ref), ref);
  }
  return [...deduped.values()];
}

function computePrerequisites(baseDoc: DocumentV1, item: MergeItem): MergeItemRef[] {
  if (item.kind === "evidence.add") {
    const link = item.after as EvidenceLink | undefined;
    if (!link) {
      return [];
    }

    const refs: MergeItemRef[] = [];
    for (const cardId of [link.fromCardId, link.toCardId]) {
      if (!baseDoc.cards.some((card) => card.id === cardId)) {
        refs.push({ kind: "card", id: cardId });
      }
    }

    return uniqueRefs(refs);
  }

  if (item.kind === "card.remove") {
    const refs: MergeItemRef[] = [];
    for (const evidenceLink of baseDoc.evidenceLinks ?? []) {
      if (evidenceLink.fromCardId === item.entityRef.id || evidenceLink.toCardId === item.entityRef.id) {
        refs.push({ kind: "evidence", id: evidenceLink.id });
      }
    }

    return uniqueRefs(refs);
  }

  return [];
}

function attachPrerequisites(baseDoc: DocumentV1, items: MergeItem[]): MergeItem[] {
  return items.map((item) => ({ ...item, prerequisites: computePrerequisites(baseDoc, item) }));
}

export function finalizeMergeItems(baseDoc: DocumentV1, documentDiff: MergeItem[], viewDiff: MergeItem[]): MergeItem[] {
  return attachPrerequisites(baseDoc, [...documentDiff, ...viewDiff]);
}

export function buildMergeItems(baseDoc: DocumentV1, incomingDoc: DocumentV1): MergeItem[] {
  const documentDiff = flattenDocumentDiff(computeDocumentDiff(baseDoc, incomingDoc));
  const viewDiff = computeViewDiff(baseDoc, incomingDoc);
  return finalizeMergeItems(baseDoc, documentDiff, viewDiff);
}

export async function buildMergeItemsIncremental(
  baseDoc: DocumentV1,
  incomingDoc: DocumentV1,
  ctx: ComputeTaskContext,
  guardrails: { maxNodes?: number; maxMs?: number } = {}
): Promise<{ items: MergeItem[]; truncated: boolean; notes: string[] }> {
  const maxNodes = Math.max(1, Math.floor(guardrails.maxNodes ?? 5000));
  const maxMs = Math.max(1, Math.floor(guardrails.maxMs ?? 2000));
  const startedAt = Date.now();
  const notes: string[] = [];

  const documentDiff = computeDocumentDiff(baseDoc, incomingDoc);
  const groups: Array<{ label: string; compute: () => MergeItem[] }> = [
    { label: "cards", compute: () => documentDiff.cards },
    { label: "islands", compute: () => documentDiff.islands },
    { label: "edges", compute: () => documentDiff.edges },
    { label: "evidenceLinks", compute: () => documentDiff.evidence },
  ];

  const items: MergeItem[] = [];
  for (let index = 0; index < groups.length; index += 1) {
    if (ctx.isCancelled()) {
      return { items: [], truncated: true, notes: ["Cancelled"] };
    }

    const group = groups[index];
    ctx.reportProgress({ message: `Computing diff: ${group.label}`, completed: index + 1, total: groups.length + 1 });
    items.push(...group.compute());
    if (items.length > maxNodes) {
      notes.push(`Truncated due to node limit (${items.length}/${maxNodes}).`);
      return { items: finalizeMergeItems(baseDoc, items.slice(0, maxNodes), []), truncated: true, notes };
    }
    await ctx.yieldToMainThread();
  }

  const viewDiff = computeViewDiff(baseDoc, incomingDoc);
  const elapsedMs = Date.now() - startedAt;
  if (elapsedMs > maxMs) {
    notes.push(`Truncated due to time limit (${maxMs}ms).`);
  }

  return { items: finalizeMergeItems(baseDoc, items, viewDiff), truncated: notes.length > 0, notes };
}
