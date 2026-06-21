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

  it("accepts supported card hold states and rejects unknown values", () => {
    expect(validateDocumentV2Strict({
      ...validDocument,
      cards: [{ ...validDocument.cards[0], holdState: "shelved" }],
    }).ok).toBe(true);

    const invalid = validateDocumentV2Strict({
      ...validDocument,
      cards: [{ ...validDocument.cards[0], holdState: "resolved" }],
    });
    expect(invalid.ok).toBe(false);
    if (invalid.ok) return;
    expect(invalid.errors).toContain("cards[0].holdState: must be 'held' | 'pending' | 'shelved' when provided");
  });

  it("rejects unknown root fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      unknownField: true,
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("document: unknown field 'unknownField'");
  });

  it("accepts polygon geometry", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
              { x: 100, y: 100 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("keeps shape compatibility for rect and polygon islands", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i_rect",
          cardIds: ["c1"],
          shape: {
            kind: "rect",
          },
        },
        {
          id: "i_polygon",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
              { x: 100, y: 100 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("accepts legacy polygon geometry payload", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            polygon: {
              points: [
                { x: 0, y: 0 },
                { x: 100, y: 0 },
                { x: 100, y: 100 },
              ],
            },
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("rejects polygon shape with fewer than 3 points", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("islands[0].shape.points: must contain at least 3 points for polygon");
  });

  it("rejects self-intersecting polygon shape", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 120, y: 120 },
              { x: 120, y: 0 },
              { x: 0, y: 120 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("islands[0].shape.points: polygon must not self-intersect");
  });


  it("accepts merge suggestion decisions", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      mergeSuggestionDecisions: [
        {
          id: "decision-1",
          groupId: "heuristic-a-b",
          decision: "defer",
          decidedAt: now,
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("rejects merge suggestion decisions with invalid status", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      mergeSuggestionDecisions: [
        {
          id: "decision-1",
          groupId: "heuristic-a-b",
          decision: "approved",
          decidedAt: now,
          cardIds: ["c1", "c2"],
          mergedTextDraft: "A",
          editedText: "A",
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain(
      "mergeSuggestionDecisions[0].decision: must be 'accept' | 'partial' | 'reject' | 'defer'"
    );
  });

  it("accepts A1 contract-only DocumentV2 fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "crit-1",
          targetRef: "island:i1",
          critiqueType: "feels_off",
          createdAt: now,
          iteration: 1,
          comment: "境界が分かりにくい",
        },
      ],
      reproposalDiffs: [
        {
          schemaVersion: "1.0.0",
          proposalId: "proposal-1",
          basedOnIteration: 1,
          traceKey: "trace:crit-1",
          rationale: "カード追加の取り消しに必要な前後差分を保持する",
          diffOps: [
            {
              opId: "op-add-c2",
              opType: "add",
              targetRef: "card:c2",
              before: null,
              after: { id: "c2", text: "B", x: 10, y: 20 },
            },
          ],
        },
      ],
      reviewAttribution: {
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: now,
        reviewerRef: "reviewer:opaque-1",
        auditRecordedAt: now,
        overridePolicy: "human_dual_control_only",
      },
      deterministicTieBreak: {
        schemaVersion: "1.0.0",
        order: [
          "padding_compliance",
          "self_intersection_avoidance",
          "minimum_area_delta",
          "minimum_vertex_count",
        ],
      },
    });

    expect(result.ok).toBe(true);
  });

  it("rejects irreversible reproposal diffs", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      reproposalDiffs: [
        {
          schemaVersion: "1.0.0",
          proposalId: "proposal-1",
          basedOnIteration: 1,
          traceKey: "trace:crit-1",
          diffOps: [
            {
              opId: "op-empty",
              opType: "move",
              targetRef: "card:c1",
              before: null,
              after: null,
            },
          ],
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("reproposalDiffs[0].diffOps[0]: before and after must not both be null");
  });

  it("rejects review attribution with email-like reviewer refs", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      reviewAttribution: {
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: now,
        reviewerRef: "reviewer@example.com",
        auditRecordedAt: now,
        overridePolicy: "human_dual_control_only",
      },
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("reviewAttribution.reviewerRef: must not contain email-like identifiers");
  });

  it("rejects reordered deterministic tie-break fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      deterministicTieBreak: {
        schemaVersion: "1.0.0",
        order: [
          "self_intersection_avoidance",
          "padding_compliance",
          "minimum_area_delta",
          "minimum_vertex_count",
        ],
      },
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("deterministicTieBreak.order[0]: must be 'padding_compliance'");
  });

});
