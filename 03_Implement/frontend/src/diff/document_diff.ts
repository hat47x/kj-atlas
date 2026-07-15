import type { DocumentV1, RelationSummary } from "../domain/types";
import type { MergeEntityKind, MergeItem, MergeItemKind } from "./merge_items";

function stableSerialize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableSerialize(item)).join(",")}]`;
  const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b));
  return `{${entries.map(([key, entry]) => `${JSON.stringify(key)}:${stableSerialize(entry)}`).join(",")}}`;
}

function changedFields<T extends object>(before: T, after: T): string[] {
  const keys = new Set([...Object.keys(before), ...Object.keys(after)]);
  return [...keys]
    .filter((key) => stableSerialize((before as Record<string, unknown>)[key]) !== stableSerialize((after as Record<string, unknown>)[key]))
    .sort((a, b) => a.localeCompare(b));
}

function byId<T extends { id: string }>(items: T[]): Map<string, T> {
  return new Map(items.map((item) => [item.id, item]));
}

function relationSummaryBySignature(items: RelationSummary[]): Map<string, RelationSummary> {
  return new Map(items.map((item) => [item.sourceSignature, item]));
}

function buildEntityItems<T extends { id: string }>(
  scope: string,
  baseMap: Map<string, T>,
  incomingMap: Map<string, T>,
  entityKind: MergeEntityKind,
  addKind: MergeItemKind,
  removeKind: MergeItemKind,
  fieldKind?: MergeItemKind,
): MergeItem[] {
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

export function computeDocumentDiff(baseDoc: DocumentV1, incomingDoc: DocumentV1): {
  cards: MergeItem[];
  islands: MergeItem[];
  edges: MergeItem[];
  evidence: MergeItem[];
} {
  return {
    cards: buildEntityItems("card", byId(baseDoc.cards), byId(incomingDoc.cards), "card", "card.add", "card.remove", "card.field"),
    islands: buildEntityItems("island", byId(baseDoc.islands), byId(incomingDoc.islands), "island", "island.add", "island.remove", "island.field"),
    edges: buildEntityItems("edge", byId(baseDoc.edges), byId(incomingDoc.edges), "edge", "edge.add", "edge.remove"),
    evidence: [
      ...buildEntityItems("evidence", byId(baseDoc.evidenceLinks ?? []), byId(incomingDoc.evidenceLinks ?? []), "evidence", "evidence.add", "evidence.remove"),
      ...buildEntityItems(
        "relationSummary",
        relationSummaryBySignature(baseDoc.relationSummaries ?? []),
        relationSummaryBySignature(incomingDoc.relationSummaries ?? []),
        "relationSummary",
        "relationSummary.field",
        "relationSummary.field",
        "relationSummary.field",
      ),
    ],
  };
}

export function flattenDocumentDiff(diff: ReturnType<typeof computeDocumentDiff>): MergeItem[] {
  return [...diff.cards, ...diff.islands, ...diff.edges, ...diff.evidence];
}
