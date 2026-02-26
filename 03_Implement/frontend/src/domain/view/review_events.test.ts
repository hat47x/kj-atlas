import { describe, expect, it, vi } from "vitest";

import { appendReviewEvent, REVIEW_EVENT_LOG_LIMIT, sanitizeReviewEvents } from "./review_events";

describe("review_events", () => {
  it("appends review event with markReviewed action", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-05T00:00:00.000Z"));

    const events = appendReviewEvent([], {
      target: { kind: "summary", id: "summary-1" },
      reviewed: true,
      reviewerRef: "user:local:abc",
      contextLabel: "relation.summary",
    });

    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({
      target: { kind: "summary", id: "summary-1" },
      action: "markReviewed",
      createdAt: "2026-03-05T00:00:00.000Z",
      reviewerRef: "user:local:abc",
      contextLabel: "relation.summary",
    });
    vi.useRealTimers();
  });

  it("trims oldest events when exceeding max", () => {
    const events = [
      {
        id: "event-1",
        target: { kind: "island" as const, id: "i-1" },
        action: "markReviewed" as const,
        createdAt: "2026-01-01T00:00:00.000Z",
      },
    ];

    const next = appendReviewEvent(events, {
      target: { kind: "island", id: "i-2" },
      reviewed: false,
      createdAt: "2026-01-02T00:00:00.000Z",
    }, { maxEvents: 1 });

    expect(next).toHaveLength(1);
    expect(next[0].target.id).toBe("i-2");
    expect(next[0].action).toBe("unreview");
  });

  it("sanitizes imported review events and drops invalid entries", () => {
    const events = sanitizeReviewEvents([
      {
        id: "event-valid",
        target: { kind: "card", id: "c-1" },
        action: "markReviewed",
        createdAt: "2026-01-01T00:00:00.000Z",
        reviewerRef: "user:local:abc",
        contextLabel: "card.text",
      },
      {
        id: "event-invalid-kind",
        target: { kind: "invalid", id: "c-2" },
        action: "markReviewed",
        createdAt: "2026-01-01T00:00:00.000Z",
      },
      {
        id: "event-invalid-action",
        target: { kind: "card", id: "c-3" },
        action: "approve",
        createdAt: "2026-01-01T00:00:00.000Z",
      },
    ]);

    expect(events).toEqual([
      {
        id: "event-valid",
        target: { kind: "card", id: "c-1" },
        action: "markReviewed",
        createdAt: "2026-01-01T00:00:00.000Z",
        reviewerRef: "user:local:abc",
        contextLabel: "card.text",
      },
    ]);
  });

  it("enforces default max event limit", () => {
    const many = Array.from({ length: REVIEW_EVENT_LOG_LIMIT + 2 }, (_, index) => ({
      id: `event-${index + 1}`,
      target: { kind: "summary" as const, id: `s-${index + 1}` },
      action: "markReviewed" as const,
      createdAt: `2026-01-01T00:00:${String(index).padStart(2, "0")}.000Z`,
    }));

    const sanitized = sanitizeReviewEvents(many);
    expect(sanitized).toHaveLength(REVIEW_EVENT_LOG_LIMIT);
    expect(sanitized[0]?.id).toBe("event-3");
  });
});
