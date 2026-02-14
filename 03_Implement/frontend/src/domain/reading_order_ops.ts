export type ReadingOrderDropPosition = "before" | "after";

export function appendReadingOrderEntry(
  readingOrder: string[],
  entryId: string,
  visibleEntryIdSet: Set<string>
): string[] {
  if (!visibleEntryIdSet.has(entryId) || readingOrder.includes(entryId)) {
    return readingOrder;
  }

  return [...readingOrder, entryId];
}

export function removeReadingOrderEntry(readingOrder: string[], entryId: string): string[] {
  const nextOrder = readingOrder.filter((id) => id !== entryId);
  return nextOrder.length === readingOrder.length ? readingOrder : nextOrder;
}

export function moveReadingOrderEntry(
  readingOrder: string[],
  entryId: string,
  targetEntryId: string,
  position: ReadingOrderDropPosition
): string[] {
  if (entryId === targetEntryId) {
    return readingOrder;
  }

  const sourceIndex = readingOrder.indexOf(entryId);
  const targetIndex = readingOrder.indexOf(targetEntryId);
  if (sourceIndex < 0 || targetIndex < 0) {
    return readingOrder;
  }

  const nextOrder = [...readingOrder];
  nextOrder.splice(sourceIndex, 1);

  const adjustedTargetIndex = sourceIndex < targetIndex ? targetIndex - 1 : targetIndex;
  const insertIndex = position === "before" ? adjustedTargetIndex : adjustedTargetIndex + 1;
  nextOrder.splice(insertIndex, 0, entryId);

  return nextOrder;
}
