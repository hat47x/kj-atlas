import { describe, expect, it } from "vitest";
import { appendMergeAuditLog, createMergeAuditEntry, MERGE_AUDIT_DETAILS_LIMIT, MERGE_AUDIT_LOG_LIMIT, sanitizeMergeAuditLog } from "./audit_log";
import type { MergeItem } from "../../diff/merge_items";

function item(id: string, kind: MergeItem["kind"], entityKind: MergeItem["entityRef"]["kind"], entityId: string): MergeItem {
  return {
    id,
    kind,
    entityRef: { kind: entityKind, id: entityId },
    prerequisites: [],
  };
}

describe("merge audit log", () => {
  it("creates summary counts and id-only details", () => {
    const entry = createMergeAuditEntry([
      item("card.field:c1:text", "card.field", "card", "c1"),
      item("evidence.add:e1", "evidence.add", "evidence", "e1"),
      item("card.field:c1:x", "card.field", "card", "c1"),
    ], { kind: "unknown", fileName: "compare.json" }, "2026-01-01T00:00:00.000Z");

    expect(entry.summary.totalItems).toBe(3);
    expect(entry.summary.byKind["card.field"]).toBe(2);
    expect(entry.summary.byKind["evidence.add"]).toBe(1);
    expect(entry.details.entityIds?.cards).toEqual(["c1"]);
    expect(entry.details.entityIds?.evidence).toEqual(["e1"]);
    expect(JSON.stringify(entry)).not.toContain("draft");
  });

  it("enforces caps", () => {
    const entries = [];
    for (let index = 0; index < MERGE_AUDIT_LOG_LIMIT + 5; index += 1) {
      entries.push(createMergeAuditEntry([item(`card.add:c${index}`, "card.add", "card", `c${index}`)], { kind: "unknown" }));
    }

    const log = entries.reduce((acc, entry) => appendMergeAuditLog(acc, entry), [] as ReturnType<typeof sanitizeMergeAuditLog>);
    expect(log).toHaveLength(MERGE_AUDIT_LOG_LIMIT);

    const many = createMergeAuditEntry(
      Array.from({ length: MERGE_AUDIT_DETAILS_LIMIT + 10 }, (_, index) => item(`card.add:c${index}`, "card.add", "card", `c${index}`)),
      { kind: "unknown" }
    );
    expect(many.details.itemIds?.length).toBe(MERGE_AUDIT_DETAILS_LIMIT);
    expect(many.details.entityIds?.cards?.length).toBe(MERGE_AUDIT_DETAILS_LIMIT);
  });

  it("sanitizes invalid entries and truncates list", () => {
    const raw = [
      { id: "x", createdAt: "now", source: { kind: "unknown" }, summary: { totalItems: 1, byKind: { "card.add": 1 } }, details: { itemIds: ["a"] } },
      { invalid: true },
    ];
    const sanitized = sanitizeMergeAuditLog(raw);
    expect(sanitized).toHaveLength(1);
    expect(sanitized[0]?.id).toBe("x");
  });
});
