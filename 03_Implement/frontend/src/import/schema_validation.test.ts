import { describe, expect, it } from "vitest";
import { validateDocument, validateView } from "./schema_validation";

describe("schema_validation", () => {
  it("accepts cards as a map and normalizes to array", () => {
    const result = validateDocument({
      version: 1,
      id: "doc-1",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: {
        c1: { text: "A" },
      },
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.cards).toHaveLength(1);
      expect(result.value.cards[0]).toMatchObject({ id: "c1", text: "A", x: 0, y: 0 });
    }
  });

  it("returns structured errors for invalid document", () => {
    const result = validateDocument({ version: 1, id: "doc-1" });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors[0]).toMatchObject({ code: "V001", path: "cards" });
    }
  });

  it("returns card field errors with actionable paths", () => {
    const result = validateDocument({
      version: 1,
      id: "doc-1",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: 10 }],
    });
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors.some((entry) => entry.code === "V002" && entry.path === "cards[0].text")).toBe(true);
    }
  });

  it("fills defaults for missing camera and perspective mode", () => {
    const result = validateView({ viewState: {} });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.camera).toEqual({ panX: 0, panY: 0, zoom: 1 });
      expect(result.value.viewState.perspectiveMode).toBe("default");
      expect(result.value.viewState.collapsedIslandIds).toEqual([]);
      expect(result.value.visibility).toBe("Restricted");
    }
  });

  it("normalizes collapsedIslandIds to string ids", () => {
    const result = validateView({ viewState: { collapsedIslandIds: ["island-a", 123, "island-b"] } });
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.value.viewState.collapsedIslandIds).toEqual(["island-a", "island-b"]);
    }
  });



  it.each(["", "public", null, 1, { value: "Org" }])("rejects non-enum visibility values: %p", (visibility) => {
    const result = validateView({
      visibility,
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors[0]?.message).toContain("metadata.visibility must be");
    }
  });

  it("rejects invalid visibility value", () => {
    const result = validateView({
      visibility: "FriendsOnly",
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
    });

    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.errors[0]?.message).toContain("metadata.visibility must be");
    }
  });
});
