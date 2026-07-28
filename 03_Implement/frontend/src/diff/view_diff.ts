import { stableSerialize } from "../utils/stable_serialize";
import type { MergeItem } from "./merge_items";

export type DiffViewSnapshot = {
  readingOrder?: string[];
};

export function computeViewDiff(baseView: DiffViewSnapshot, incomingView: DiffViewSnapshot): MergeItem[] {
  const readingOrderBefore = baseView.readingOrder ?? [];
  const readingOrderAfter = incomingView.readingOrder ?? [];
  if (stableSerialize(readingOrderBefore) === stableSerialize(readingOrderAfter)) {
    return [];
  }

  return [{ id: "view.field:readingOrder", kind: "view.field", entityRef: { kind: "view", id: "document" }, field: "readingOrder", before: readingOrderBefore, after: readingOrderAfter, prerequisites: [] }];
}
