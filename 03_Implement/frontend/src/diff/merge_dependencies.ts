import type { DocumentV1 } from "../domain/types";
import { getPatchOpEntityKey } from "../domain/patch/patch_apply";
import { detectPatchConflicts } from "../domain/patch/conflict_detect";
import type { MergeItem, MergeItemRef } from "./merge_items";
import { buildSelectedPatchFromItems } from "./merge_apply";

export type MergeItemStatus = "ok" | "missing_prerequisites" | "conflict";

export type MergeItemEvaluation = {
  item: MergeItem;
  status: MergeItemStatus;
  missingPrerequisites: MergeItemRef[];
  conflict: boolean;
};

function toRefSetKey(ref: MergeItemRef): string {
  return `${ref.kind}:${ref.id}`;
}

function selectedRefKeys(selectedItems: MergeItem[]): Set<string> {
  return new Set(selectedItems.map((item) => toRefSetKey(item.entityRef)));
}

function collectMissingPrerequisites(item: MergeItem, selectedRefKeySet: Set<string>): MergeItemRef[] {
  return item.prerequisites.filter((prerequisite) => !selectedRefKeySet.has(toRefSetKey(prerequisite)));
}

export function evaluateMergeSelection(
  baseDoc: DocumentV1,
  currentDoc: DocumentV1,
  incomingDoc: DocumentV1,
  snapshotDoc: DocumentV1,
  items: MergeItem[],
  selectedIds: Set<string>,
  autoIncludePrerequisites: boolean
): { evaluations: MergeItemEvaluation[]; selectedIdsWithPrerequisites: Set<string> } {
  const selectedItems = items.filter((item) => selectedIds.has(item.id));

  const selectedIdsWithPrerequisites = new Set(selectedIds);
  if (autoIncludePrerequisites) {
    for (const selectedItem of selectedItems) {
      for (const prerequisite of selectedItem.prerequisites) {
        const prerequisiteItem = items.find((candidate) => {
          return candidate.entityRef.kind === prerequisite.kind && candidate.entityRef.id === prerequisite.id && (candidate.kind === "card.add" || candidate.kind === "evidence.remove");
        });
        if (prerequisiteItem) {
          selectedIdsWithPrerequisites.add(prerequisiteItem.id);
        }
      }
    }
  }

  const selectedItemsWithPrerequisites = items.filter((item) => selectedIdsWithPrerequisites.has(item.id));
  const selectedRefKeySet = selectedRefKeys(selectedItemsWithPrerequisites);
  const candidatePatch = buildSelectedPatchFromItems(baseDoc, incomingDoc, selectedItemsWithPrerequisites);
  const conflictOpIds = new Set(detectPatchConflicts(snapshotDoc, currentDoc, candidatePatch).conflicts.map((conflict) => conflict.opId));

  const evaluations = items.map((item) => {
    const missingPrerequisites = selectedIdsWithPrerequisites.has(item.id) ? collectMissingPrerequisites(item, selectedRefKeySet) : [];
    const patchEntityKeyPrefix = item.entityRef.kind === "relationSummary" ? "relSummary" : item.entityRef.kind;
    const opId = candidatePatch.ops.find((op) => getPatchOpEntityKey(op) === `${patchEntityKeyPrefix}:${item.entityRef.id}`)?.id;
    const conflict = Boolean(opId && conflictOpIds.has(opId));
    const status: MergeItemStatus = conflict ? "conflict" : missingPrerequisites.length > 0 ? "missing_prerequisites" : "ok";
    return { item, status, missingPrerequisites, conflict };
  });

  return { evaluations, selectedIdsWithPrerequisites };
}
