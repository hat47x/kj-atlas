import type { Card, DocumentV2, Edge, EvidenceLink, Island, RelationSummary } from "../domain/types";

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

function stableSerialize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableSerialize(item)).join(",")}]`;
  const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b));
  return `{${entries.map(([key, entry]) => `${JSON.stringify(key)}:${stableSerialize(entry)}`).join(",")}}`;
}

function changedFields<T extends object>(before: T, after: T): string[] {
  const keys = new Set([...Object.keys(before), ...Object.keys(after)]);
  return [...keys].filter((key) => stableSerialize((before as Record<string, unknown>)[key]) !== stableSerialize((after as Record<string, unknown>)[key]));
}

function byId<T extends { id: string }>(items: T[]): Map<string, T> {
  return new Map(items.map((item) => [item.id, item]));
}

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

function computePrerequisites(baseDoc: DocumentV2, item: MergeItem): MergeItemRef[] {
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

function attachPrerequisites(baseDoc: DocumentV2, items: MergeItem[]): MergeItem[] {
  return items.map((item) => ({ ...item, prerequisites: computePrerequisites(baseDoc, item) }));
}

function buildEntityItems<T extends { id: string }>(scope: string, baseMap: Map<string, T>, incomingMap: Map<string, T>, entityKind: MergeEntityKind, addKind: MergeItemKind, removeKind: MergeItemKind, fieldKind?: MergeItemKind): MergeItem[] {
  const result: MergeItem[] = [];
  const allIds = new Set([...baseMap.keys(), ...incomingMap.keys()]);

  for (const id of [...allIds].sort((a, b) => a.localeCompare(b))) {
    const before = baseMap.get(id);
    const after = incomingMap.get(id);

    if (!before && after) {
      result.push({ id: `${addKind}:${id}`, kind: addKind, entityRef: { kind: entityKind, id }, after, prerequisites: [] });
      continue;
    }
    if (before && !after) {
      result.push({ id: `${removeKind}:${id}`, kind: removeKind, entityRef: { kind: entityKind, id }, before, prerequisites: [] });
      continue;
    }
    if (!before || !after || !fieldKind) continue;

    for (const field of changedFields(before, after)) {
      result.push({
        id: `${scope}.field:${id}:${field}`,
        kind: fieldKind,
        entityRef: { kind: entityKind, id },
        field,
        before: (before as Record<string, unknown>)[field],
        after: (after as Record<string, unknown>)[field],
        prerequisites: [],
      });
    }
  }

  return result;
}

function relationSummaryBySignature(items: RelationSummary[]): Map<string, RelationSummary> {
  return new Map(items.map((item) => [item.sourceSignature, item]));
}

export function buildMergeItems(baseDoc: DocumentV2, incomingDoc: DocumentV2): MergeItem[] {
  const cardItems = buildEntityItems("card", byId(baseDoc.cards), byId(incomingDoc.cards), "card", "card.add", "card.remove", "card.field");
  const islandItems = buildEntityItems("island", byId(baseDoc.islands), byId(incomingDoc.islands), "island", "island.add", "island.remove", "island.field");
  const edgeItems = buildEntityItems("edge", byId(baseDoc.edges), byId(incomingDoc.edges), "edge", "edge.add", "edge.remove");
  const evidenceItems = buildEntityItems("evidence", byId(baseDoc.evidenceLinks ?? []), byId(incomingDoc.evidenceLinks ?? []), "evidence", "evidence.add", "evidence.remove");

  const relationItems = buildEntityItems(
    "relationSummary",
    relationSummaryBySignature(baseDoc.relationSummaries ?? []),
    relationSummaryBySignature(incomingDoc.relationSummaries ?? []),
    "relationSummary",
    "relationSummary.field",
    "relationSummary.field",
    "relationSummary.field"
  );

  const readingOrderBefore = baseDoc.readingOrder ?? [];
  const readingOrderAfter = incomingDoc.readingOrder ?? [];
  const viewItems: MergeItem[] =
    stableSerialize(readingOrderBefore) === stableSerialize(readingOrderAfter)
      ? []
      : [{ id: "view.field:readingOrder", kind: "view.field", entityRef: { kind: "view", id: "document" }, field: "readingOrder", before: readingOrderBefore, after: readingOrderAfter, prerequisites: [] }];

  return attachPrerequisites(baseDoc, [...cardItems, ...islandItems, ...edgeItems, ...evidenceItems, ...relationItems, ...viewItems]);
}
