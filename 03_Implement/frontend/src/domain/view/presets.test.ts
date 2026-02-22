import { describe, expect, it } from "vitest";
import { DEFAULT_VIEW_PRESETS, migrateViewPresets, removeViewPreset, renameViewPreset, replaceViewPreset, resolveSummaryAbstractFromPatch } from "./presets";

describe("view preset CRUD", () => {
  it("supports create rename delete", () => {
    const now = "2026-01-01T00:00:00.000Z";
    const created = replaceViewPreset(DEFAULT_VIEW_PRESETS, {
      id: "custom",
      name: "Team",
      viewPatch: { perspectiveMode: "claims", safeMode: true },
      createdAt: now,
      updatedAt: now,
    });
    const renamed = renameViewPreset(created, "custom", "Team Review", "2026-01-02T00:00:00.000Z");
    const removed = removeViewPreset(renamed, "custom");

    expect(created.some((item) => item.id === "custom")).toBe(true);
    expect(renamed.find((item) => item.id === "custom")?.name).toBe("Team Review");
    expect(removed).toEqual(DEFAULT_VIEW_PRESETS);
  });

  it("migrates defaults when missing", () => {
    const migrated = migrateViewPresets([{ ...DEFAULT_VIEW_PRESETS[0], id: "custom-only", name: "Custom" }]);
    expect(migrated.some((item) => item.id === "default-review")).toBe(true);
    expect(migrated.some((item) => item.id === "default-summary")).toBe(true);
  });
});


describe("resolveSummaryAbstractFromPatch", () => {
  it("turns summary off when applying explore-style patch from abstract view", () => {
    const next = resolveSummaryAbstractFromPatch(
      { summaryView: true, abstractMapView: true },
      { summaryView: false, abstractMapView: false },
    );
    expect(next).toEqual({ summaryView: false, abstractMapView: false });
  });

  it("forces summary on when abstract map is enabled", () => {
    const next = resolveSummaryAbstractFromPatch(
      { summaryView: false, abstractMapView: false },
      { abstractMapView: true, summaryView: false },
    );
    expect(next).toEqual({ summaryView: true, abstractMapView: true });
  });
});
