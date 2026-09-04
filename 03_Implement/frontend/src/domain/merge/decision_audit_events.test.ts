import { describe, expect, it } from "vitest";

import {
  appendMergeDecisionAuditEvent,
  createMergeDecisionAuditEvent,
  MERGE_DECISION_AUDIT_EVENT_LIMIT,
} from "./decision_audit_events";

describe("decision_audit_events", () => {
  it("候補全体と部分採用したカード集合を正規化して監査記録へ残す", () => {
    const event = createMergeDecisionAuditEvent({
      eventId: "evt-1",
      groupId: "g-1",
      decision: "partial",
      decidedAt: "2026-03-15T00:00:00.000Z",
      cardIds: ["c-3", "c-2", "c-1", "c-2"],
      selectedCardIds: ["c-2", "c-1", "c-2"],
      snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      decisionReason: "Reviewed by operator",
    });

    expect(event).toEqual({
      eventId: "evt-1",
      groupId: "g-1",
      decision: "partial",
      decidedAt: "2026-03-15T00:00:00.000Z",
      decidedBy: "human",
      cardIds: ["c-1", "c-2", "c-3"],
      selectedCardIds: ["c-1", "c-2"],
      snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      decisionReason: "Reviewed by operator",
    });
  });

  it("keeps append-only recent audit events up to limit", () => {
    const events = Array.from({ length: MERGE_DECISION_AUDIT_EVENT_LIMIT + 1 }, (_, index) =>
      createMergeDecisionAuditEvent({
        eventId: `evt-${index + 1}`,
        groupId: "g-1",
        decision: "accept",
        decidedAt: `2026-03-15T00:${String(index).padStart(2, "0")}:00.000Z`,
        cardIds: ["c-1", "c-2"],
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      })
    );

    const appended = events.reduce(
      (current, event) => appendMergeDecisionAuditEvent(current, event),
      [] as ReturnType<typeof createMergeDecisionAuditEvent>[]
    );

    expect(appended).toHaveLength(MERGE_DECISION_AUDIT_EVENT_LIMIT);
    expect(appended[0]?.eventId).toBe("evt-2");
    expect(appended[appended.length - 1]?.eventId).toBe(`evt-${MERGE_DECISION_AUDIT_EVENT_LIMIT + 1}`);
  });
});
