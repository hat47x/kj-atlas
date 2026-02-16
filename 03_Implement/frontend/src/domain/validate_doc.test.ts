import { describe, expect, it } from "vitest";

import { validateDocumentV2Strict } from "./validate_doc";

describe("validateDocumentV2Strict", () => {
  const now = new Date().toISOString();

  const validDocument = {
    version: 2,
    id: "doc_v2",
    createdAt: now,
    updatedAt: now,
    transform: {
      panX: 0,
      panY: 0,
      zoom: 1,
    },
    cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
    edges: [],
    islands: [],
  };

  it("accepts valid DocumentV2", () => {
    const result = validateDocumentV2Strict(validDocument);
    expect(result.ok).toBe(true);
  });

  it("rejects unknown root fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      unknownField: true,
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      return;
    }

    expect(result.errors).toContain("document: unknown field 'unknownField'");
  });

  it("rejects v1 payload", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      version: 1,
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      return;
    }

    expect(result.errors).toContain("document.version: must be the number 2 (DocumentV2 only)");
  });
});
