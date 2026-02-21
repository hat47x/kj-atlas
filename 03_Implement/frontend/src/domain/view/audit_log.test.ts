import { describe, expect, it } from "vitest";
import {
  appendMergeAuditEntry,
  appendMergeAuditLog,
  createMergeAuditEntry,
  MERGE_AUDIT_DETAILS_LIMIT,
  MERGE_AUDIT_LOG_LIMIT,
  sanitizeMergeAuditLog,
  type MergeAuditEntry,
} from "./audit_log";
import type { MergeItem } from "../../diff/merge_items";

function item(id: string, kind: MergeItem["kind"], entityKind: MergeItem["entityRef"]["kind"], entityId: string): MergeItem {
  return {
    id,
    kind,
    entityRef: { kind: entityKind, id: entityId },
    prerequisites: [],
  };
}

function entry(id: string): MergeAuditEntry {
  return {
    id,
    createdAt: "2026-01-01T00:00:00.000Z",
    source: { kind: "unknown" },
    summary: { totalItems: 1, byKind: { "card.add": 1 } },
    details: { itemIds: { ids: [id] }, entityIds: { cards: { ids: [id] } } },
  };
}

describe("merge audit log", () => {
  it("creates summary counts and id-only details", () => {
    const created = createMergeAuditEntry([
      item("card.field:c1:text", "card.field", "card", "c1"),
      item("evidence.add:e1", "evidence.add", "evidence", "e1"),
      item("card.field:c1:x", "card.field", "card", "c1"),
    ], { kind: "unknown", fileName: "compare.json" }, "2026-01-01T00:00:00.000Z");

    expect(created.summary.totalItems).toBe(3);
    expect(created.summary.byKind["card.field"]).toBe(2);
    expect(created.summary.byKind["evidence.add"]).toBe(1);
    expect(created.details.entityIds?.cards?.ids).toEqual(["c1"]);
    expect(created.details.entityIds?.evidence?.ids).toEqual(["e1"]);
    expect(JSON.stringify(created)).not.toContain("draft");
  });

  it("append caps keep newest 50 entries", () => {
    const entries = [];
    for (let index = 0; index < 60; index += 1) {
      entries.push(entry(`card-${index}`));
    }

    const log = entries.reduce((acc, current) => appendMergeAuditLog(acc, current), [] as MergeAuditEntry[]);
    expect(log).toHaveLength(MERGE_AUDIT_LOG_LIMIT);
    expect(log[0]?.id).toBe("card-10");
    expect(log[49]?.id).toBe("card-59");
  });

  it("id truncation keeps 200 and stores truncatedCount", () => {
    const many = createMergeAuditEntry(
      Array.from({ length: 300 }, (_, index) => item(`card.add:c${index}`, "card.add", "card", `c${index}`)),
      { kind: "unknown" },
    );

    expect(many.details.itemIds?.ids).toHaveLength(MERGE_AUDIT_DETAILS_LIMIT);
    expect(many.details.itemIds?.truncatedCount).toBe(100);
    expect(many.details.entityIds?.cards?.ids).toHaveLength(MERGE_AUDIT_DETAILS_LIMIT);
    expect(many.details.entityIds?.cards?.truncatedCount).toBe(100);
  });

  it("privacy guard strips disallowed text fields and appends warning", () => {
    const sanitized = sanitizeMergeAuditLog([
      {
        id: "x",
        createdAt: "now",
        source: { kind: "unknown", fileName: "safe.json", content: "private" },
        summary: { totalItems: 1, byKind: { "card.add": 1 }, summaryText: "private" },
        details: { itemIds: ["a"], text: "private" },
      },
    ]);

    expect(sanitized).toHaveLength(1);
    expect(JSON.stringify(sanitized[0])).not.toContain("private");
    expect(sanitized[0]?.summary.warnings).toContain("stripped_disallowed_fields");
  });


  it("privacy guard detects similar text-like field names", () => {
    const sanitized = sanitizeMergeAuditLog([
      {
        id: "y",
        createdAt: "now",
        source: { kind: "unknown", fileName: "safe.json", cardText: "private" },
        summary: { totalItems: 1, byKind: { "card.add": 1 } },
        details: { itemIds: ["a"], island_body: "private", entityIds: { cards: ["c1"] } },
      },
    ]);

    expect(sanitized).toHaveLength(1);
    expect(JSON.stringify(sanitized[0])).not.toContain("private");
    expect(sanitized[0]?.summary.warnings).toContain("stripped_disallowed_fields");
    expect(sanitized[0]?.summary.totalItems).toBe(1);
  });

  it("appendMergeAuditEntry updates viewState with sanitized log", () => {
    const next = appendMergeAuditEntry({ mergeAuditLog: [] }, entry("a"));
    expect(next.mergeAuditLog).toHaveLength(1);
    expect(next.mergeAuditLog?.[0]?.details.itemIds?.ids).toEqual(["a"]);
  });
});
