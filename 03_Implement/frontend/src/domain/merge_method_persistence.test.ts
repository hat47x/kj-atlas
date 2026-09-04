import { describe, expect, it } from "vitest";

import { validateImportedDocument } from "./validate";
import { validateDocumentV1Strict } from "./validate_doc";

const baseDocument = {
  version: 1,
  id: "doc-merge-method",
  createdAt: "2026-09-04T00:00:00.000Z",
  updatedAt: "2026-09-04T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [],
  edges: [],
  islands: [],
};

function decision(mergeMethod?: unknown) {
  return {
    id: "d1",
    groupId: "g1",
    decision: "accept",
    decidedAt: "2026-09-04T00:01:00.000Z",
    cardIds: ["c1", "c2"],
    mergedTextDraft: "統合案",
    editedText: "統合案",
    ...(mergeMethod === undefined ? {} : { mergeMethod }),
  };
}

describe("mergeMethod persisted decision compatibility", () => {
  it.each(["near_duplicate", "kernel_fusion"] as const)("strictly accepts and preserves %s", (mergeMethod) => {
    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision(mergeMethod)] };
    const strict = validateDocumentV1Strict(raw);
    expect(strict.ok).toBe(true);
    const normalized = validateImportedDocument(raw);
    expect(normalized.ok).toBe(true);
    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBe(mergeMethod);
  });

  it("keeps legacy decisions without guessing a method", () => {
    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision()] };
    const strict = validateDocumentV1Strict(raw);
    expect(strict.ok).toBe(true);
    const normalized = validateImportedDocument(raw);
    expect(normalized.ok).toBe(true);
    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBeUndefined();
  });

  it("rejects unknown methods strictly and drops them in lenient normalization", () => {
    const raw = { ...baseDocument, mergeSuggestionDecisions: [decision("unknown_method")] };
    const strict = validateDocumentV1Strict(raw);
    expect(strict.ok).toBe(false);
    const normalized = validateImportedDocument(raw);
    expect(normalized.ok).toBe(true);
    if (normalized.ok) expect(normalized.document.mergeSuggestionDecisions?.[0]?.mergeMethod).toBeUndefined();
  });
});
