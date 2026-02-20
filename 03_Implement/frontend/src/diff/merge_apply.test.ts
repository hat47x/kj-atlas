import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { buildMergeItems } from "./merge_items";
import { evaluateMergeSelection } from "./merge_dependencies";
import { applySelectedMergeItemsAtomic } from "./merge_apply";

function doc(overrides: Partial<DocumentV2>): DocumentV2 {
  return {
    version: 2,
    id: "doc-1",
    createdAt: "2025-01-01T00:00:00.000Z",
    updatedAt: overrides.updatedAt ?? "2025-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    relationSummaries: [],
    evidenceLinks: [],
    ...overrides,
  };
}

describe("selective merge", () => {
  it("auto-includes missing cards for evidence.add", () => {
    const base = doc({});
    const incoming = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }, { id: "c2", text: "B", x: 1, y: 1 }], evidenceLinks: [{ id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" }] });
    const items = buildMergeItems(base, incoming);
    const evidenceItem = items.find((item) => item.kind === "evidence.add");
    expect(evidenceItem).toBeTruthy();

    const selected = new Set([evidenceItem!.id]);
    const evaluated = evaluateMergeSelection(base, base, incoming, base, items, selected, true);

    expect(evaluated.selectedIdsWithPrerequisites.size).toBeGreaterThan(1);
    expect([...evaluated.selectedIdsWithPrerequisites].some((id) => id.includes("card.add:c1"))).toBe(true);
    expect([...evaluated.selectedIdsWithPrerequisites].some((id) => id.includes("card.add:c2"))).toBe(true);
  });

  it("blocks card.remove when dependent evidence.remove is missing", () => {
    const base = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }, { id: "c2", text: "B", x: 1, y: 1 }], evidenceLinks: [{ id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" }] });
    const incoming = doc({ cards: [{ id: "c2", text: "B", x: 1, y: 1 }], evidenceLinks: [] });
    const items = buildMergeItems(base, incoming);
    const removeCard = items.find((item) => item.kind === "card.remove" && item.entityRef.id === "c1");
    const evaluated = evaluateMergeSelection(base, base, incoming, base, items, new Set([removeCard!.id]), false);
    const row = evaluated.evaluations.find((entry) => entry.item.id === removeCard!.id);
    expect(row?.status).toBe("missing_prerequisites");
  });

  it("detects conflict when base changed since snapshot", () => {
    const snapshot = doc({ cards: [{ id: "c1", text: "old", x: 0, y: 0 }] });
    const current = doc({ updatedAt: "2025-01-01T00:00:01.000Z", cards: [{ id: "c1", text: "current", x: 0, y: 0 }] });
    const incoming = doc({ cards: [{ id: "c1", text: "incoming", x: 0, y: 0 }] });
    const items = buildMergeItems(snapshot, incoming);
    const cardField = items.find((item) => item.kind === "card.field");
    const evaluated = evaluateMergeSelection(snapshot, current, incoming, snapshot, items, new Set([cardField!.id]), false);
    const row = evaluated.evaluations.find((entry) => entry.item.id === cardField!.id);
    expect(row?.status).toBe("conflict");
  });

  it("applies selected merge atomically and validates", () => {
    const base = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] });
    const incoming = doc({ cards: [{ id: "c1", text: "A+", x: 0, y: 0 }, { id: "c2", text: "B", x: 1, y: 1 }], evidenceLinks: [{ id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" }] });
    const items = buildMergeItems(base, incoming);
    const selected = items.filter((item) => item.kind === "card.field" || item.kind === "card.add" || item.kind === "evidence.add");
    const result = applySelectedMergeItemsAtomic(base, base, incoming, selected);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.cards.some((card) => card.id === "c2")).toBe(true);
      expect((result.document.evidenceLinks ?? []).some((evidence) => evidence.id === "e1")).toBe(true);
    }
  });


  it("fails merge preflight when incoming document is invalid", () => {
    const base = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] });
    const incoming = {
      ...doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] }),
      cards: [{ id: "c1", text: 42, x: 0, y: 0 }],
    } as unknown as DocumentV2;
    const result = applySelectedMergeItemsAtomic(base, base, incoming, []);
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.reason).toContain("Merge preflight failed");
    }
  });

  it("deduplicates entity upsert ops when selecting multiple field items", () => {
    const base = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] });
    const incoming = doc({ cards: [{ id: "c1", text: "A2", x: 10, y: 20 }] });
    const items = buildMergeItems(base, incoming).filter((item) => item.kind === "card.field" && item.entityRef.id === "c1");
    expect(items.length).toBeGreaterThan(1);

    const result = applySelectedMergeItemsAtomic(base, base, incoming, items);
    expect(result.ok).toBe(true);
    if (result.ok) {
      const card = result.document.cards.find((entry) => entry.id === "c1");
      expect(card?.text).toBe("A2");
      expect(card?.x).toBe(10);
      expect(card?.y).toBe(20);
    }
  });
});
