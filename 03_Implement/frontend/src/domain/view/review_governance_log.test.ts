import { describe, expect, it } from "vitest";
import { normalizeReviewGovernanceLogs } from "./review_governance_log";

describe("review_governance_log", () => {
  it("applies strip-identities redaction", () => {
    const result = normalizeReviewGovernanceLogs({
      mergeAuditLog: [],
      reviewEvents: [{
        id: "review-1",
        target: { kind: "card", id: "c-1" },
        action: "markReviewed",
        createdAt: "2026-03-06T00:00:00.000Z",
        reviewerRef: "user:local:abc",
      }],
      redactionMode: "strip-identities",
    });

    expect(result.reviewEvents).toEqual([{ id: "review-1", target: { kind: "card", id: "c-1" }, action: "markReviewed", createdAt: "2026-03-06T00:00:00.000Z" }]);
  });

  it("drops all review events with strip-all", () => {
    const result = normalizeReviewGovernanceLogs({
      mergeAuditLog: [],
      reviewEvents: [{
        id: "review-1",
        target: { kind: "card", id: "c-1" },
        action: "markReviewed",
        createdAt: "2026-03-06T00:00:00.000Z",
      }],
      redactionMode: "strip-all",
    });

    expect(result.reviewEvents).toBeUndefined();
  });

  it("trims oldest entries deterministically across merge and review logs", () => {
    const result = normalizeReviewGovernanceLogs({
      maxEntries: 2,
      mergeAuditLog: [{
        id: "merge-1",
        createdAt: "2026-03-06T00:00:00.000Z",
        source: { kind: "unknown" },
        summary: { totalItems: 1, byKind: { card: 1 } },
        details: {},
      }],
      reviewEvents: [
        { id: "review-1", target: { kind: "card", id: "c-1" }, action: "markReviewed", createdAt: "2026-03-06T00:00:01.000Z" },
        { id: "review-2", target: { kind: "card", id: "c-2" }, action: "markReviewed", createdAt: "2026-03-06T00:00:02.000Z" },
      ],
    });

    expect(result.mergeAuditLog).toEqual([]);
    expect(result.reviewEvents?.map((entry) => entry.id)).toEqual(["review-1", "review-2"]);
  });

  it("deduplicates same-id entries and keeps the latest timestamp", () => {
    const result = normalizeReviewGovernanceLogs({
      mergeAuditLog: [
        {
          id: "merge-dup",
          createdAt: "2026-03-06T00:00:00.000Z",
          source: { kind: "unknown" },
          summary: { totalItems: 1, byKind: { card: 1 } },
          details: { itemIds: { ids: ["old"] } },
        },
        {
          id: "merge-dup",
          createdAt: "2026-03-06T00:00:03.000Z",
          source: { kind: "unknown" },
          summary: { totalItems: 2, byKind: { card: 2 } },
          details: { itemIds: { ids: ["new"] } },
        },
      ],
      reviewEvents: [
        { id: "review-dup", target: { kind: "card", id: "c-1" }, action: "markReviewed", createdAt: "2026-03-06T00:00:01.000Z" },
        { id: "review-dup", target: { kind: "card", id: "c-2" }, action: "unreview", createdAt: "2026-03-06T00:00:04.000Z" },
      ],
    });

    expect(result.mergeAuditLog).toHaveLength(1);
    expect(result.mergeAuditLog?.[0]?.details.itemIds?.ids).toEqual(["new"]);
    expect(result.reviewEvents).toHaveLength(1);
    expect(result.reviewEvents?.[0]).toMatchObject({ id: "review-dup", action: "unreview", target: { id: "c-2" } });
  });

});
