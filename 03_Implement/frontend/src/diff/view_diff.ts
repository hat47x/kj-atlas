import type { MergeItem } from "./merge_items";

export type DiffViewSnapshot = {
  readingOrder?: string[];
};

function stableSerialize(value: unknown): string {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => stableSerialize(item)).join(",")}]`;
  const entries = Object.entries(value).sort(([a], [b]) => a.localeCompare(b));
  return `{${entries.map(([key, entry]) => `${JSON.stringify(key)}:${stableSerialize(entry)}`).join(",")}}`;
}

export function computeViewDiff(baseView: DiffViewSnapshot, incomingView: DiffViewSnapshot): MergeItem[] {
  const readingOrderBefore = baseView.readingOrder ?? [];
  const readingOrderAfter = incomingView.readingOrder ?? [];
  if (stableSerialize(readingOrderBefore) === stableSerialize(readingOrderAfter)) {
    return [];
  }

  return [{ id: "view.field:readingOrder", kind: "view.field", entityRef: { kind: "view", id: "document" }, field: "readingOrder", before: readingOrderBefore, after: readingOrderAfter, prerequisites: [] }];
}
