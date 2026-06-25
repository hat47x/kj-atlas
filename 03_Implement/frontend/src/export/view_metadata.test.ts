import { afterEach, describe, expect, it, vi } from "vitest";

import { buildExportViewMetadata, validateImportViewMetadata } from "./view_metadata";

describe("view metadata export", () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it("builds metadata with viewport mode", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-01T12:34:56.000Z"));

    const metadata = buildExportViewMetadata({
      doc: { id: "doc-123", title: "Sample" },
      camera: { panX: 100, panY: 200, zoom: 1.5 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: true,
        maxDepth: 2,
        focusIslandId: "island-1",
        showReadingOrder: true,
        editReadingOrder: false,
        readingNavEnabled: true,
        readingIndex: 2,
        readingMode: "islands+cards",
        reviewedOnly: true,
      },
      exportMode: "viewport",
      bounds: { x: 10, y: 20, w: 300, h: 400 },
    });

    expect(metadata).toEqual({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      visibility: "Restricted",
      camera: { panX: 100, panY: 200, zoom: 1.5 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: true,
        maxDepth: 2,
        focusIslandId: "island-1",
        showReadingOrder: true,
        editReadingOrder: false,
        readingNavEnabled: true,
        readingIndex: 2,
        readingMode: "islands+cards",
        reviewedOnly: true,
        perspective: {
          mode: "default",
          strictFilter: false,
        },
      },
      export: {
        mode: "viewport",
        bounds: { x: 10, y: 20, w: 300, h: 400 },
      },
      notes: "",
    });
  });

  it("uses unknown signature when document is missing", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-03-01T12:34:56.000Z"));

    const metadata = buildExportViewMetadata({
      doc: null,
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: true,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      exportMode: "bounds",
      padding: 64,
    });

    expect(metadata.docSignature).toBe("unknown");
    expect(metadata.export).toEqual({ mode: "bounds", padding: 64 });
    expect(metadata.viewState.editReadingOrder).toBeUndefined();
    expect(metadata.viewState.perspective).toEqual({ mode: "default", strictFilter: false });
  });

  it("uses provided generatedAt when specified", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-456", title: "Sample" },
      camera: { panX: 1, panY: 2, zoom: 3 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: true,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: true,
      },
      exportMode: "viewport",
      generatedAt: "2026-03-02T00:00:00.000Z",
    });

    expect(metadata.generatedAt).toBe("2026-03-02T00:00:00.000Z");
  });


  it("falls back to Restricted visibility for legacy metadata", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-legacy",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.visibility).toBe("Restricted");
    }
  });

  it("rejects invalid visibility value", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      visibility: "FriendsOnly",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
    });

    expect(result).toEqual({ ok: false, error: 'metadata.visibility must be "Public" | "Unlisted" | "Org" | "Restricted" when present' });
  });

  it("validates import metadata successfully", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-123", title: "Sample" },
      camera: { panX: 1, panY: 2, zoom: 1.5 },
      viewState: {
        summaryView: true,
        abstractMapView: true,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: true,
      },
      exportMode: "viewport",
    });

    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });




  it("persists collapsedIslandIds when present", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-123", title: "Sample" },
      camera: { panX: 1, panY: 2, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        hierarchyLevel: "overview",
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        collapsedIslandIds: ["island-b", "island-a"],
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.collapsedIslandIds).toEqual(["island-a", "island-b"]);
    expect(metadata.viewState.hierarchyLevel).toBe("overview");
    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });

  it("rejects invalid hierarchyLevel", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        hierarchyLevel: "deep",
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: 'viewState.hierarchyLevel must be "overview" | "mid" | "detail" when present' });
  });

  it("rejects invalid collapsedIslandIds", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        collapsedIslandIds: ["island-1", 2],
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: "viewState.collapsedIslandIds[1] must be a string" });
  });

  it("persists and validates safeMode when present", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-789", title: "Sample" },
      camera: { panX: 3, panY: 4, zoom: 1.2 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: true,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        safeMode: true,
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.safeMode).toBe(true);

    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });

  it("rejects invalid safeMode type", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        safeMode: "yes",
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: "viewState.safeMode must be a boolean when present" });
  });

  it("rejects invalid reading mode", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        readingMode: "all",
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: 'viewState.readingMode must be "islands" | "islands+cards" when present' });
  });

  it("rejects invalid maxDepth", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: -1,
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: 'viewState.maxDepth must be "all" or a number >= 0' });
  });

  it("rejects invalid focusIslandId", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: 123,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: "viewState.focusIslandId must be a string or null" });
  });
  it("persists lod view state fields", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-lod", title: "LOD" },
      camera: { panX: 0, panY: 0, zoom: 0.4 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        lodEnabled: true,
        lodThresholds: { close: 1, mid: 0.5 },
        lodLevelOverride: null,
        lodShowLoneWolvesWhenFar: true,
        resolvedLodLevel: "far",
        evidenceOverlayEnabled: true,
        evidenceOverlayMode: "both",
        evidenceOverlayDepth: 2,
        evidenceOverlayScope: "selection",
        evidenceOverlayDimOthers: true,
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.lodEnabled).toBe(true);
    expect(metadata.viewState.lodThresholds).toEqual({ close: 1, mid: 0.5 });
    expect(metadata.viewState.evidenceOverlayMode).toBe("both");

    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });

  it("exports sorted perspective presets", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-persp", title: "Perspective" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        perspectiveMode: "claims",
        perspectiveStrictFilter: true,
        perspectivePresets: [
          { id: "b", name: "Beta", perspective: { mode: "claims", strictFilter: true } },
          { id: "a-2", name: "Alpha", perspective: { mode: "facts", strictFilter: false } },
          { id: "a-1", name: "Alpha", perspective: { mode: "default", strictFilter: false } },
        ],
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.perspective).toEqual({ mode: "claims", strictFilter: true });
    expect(metadata.viewState.perspectivePresets?.map((preset) => `${preset.name}:${preset.id}`)).toEqual([
      "Alpha:a-1",
      "Alpha:a-2",
      "Beta:b",
    ]);
  });

  it("preserves perspective presets on export/import roundtrip", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-presets", title: "Presets" },
      camera: { panX: 10, panY: 20, zoom: 1.2 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        perspectiveMode: "review",
        perspectiveStrictFilter: false,
        perspectivePresets: [
          { id: "default-review", name: "Review", perspective: { mode: "review", strictFilter: false }, forceSafeModeOnShare: true },
          { id: "custom-1", name: "Custom", perspective: { mode: "claims", strictFilter: true } },
        ],
      },
      exportMode: "viewport",
    });

    const validated = validateImportViewMetadata(metadata);
    expect(validated.ok).toBe(true);
    if (validated.ok) {
      expect(validated.metadata.viewState.perspectivePresets).toEqual(metadata.viewState.perspectivePresets);
    }
  });


  it("keeps backward compatibility for old view.json without perspective fields", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-legacy",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: true,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result.ok).toBe(true);
  });

  it("accepts modern perspective payloads for backward-compatible import", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        perspective: {
          mode: "unsupported-mode",
          strictFilter: true,
          evidenceOverlayPrefs: { mode: "both", depth: 9, scope: "all", dimOthers: false },
        },
        perspectivePresets: [
          {
            id: "preset-1",
            name: "My preset",
            perspective: { mode: "legacy-mode", strictFilter: false },
          },
        ],
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result.ok).toBe(true);
  });

  it("rejects invalid evidence overlay depth", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        evidenceOverlayDepth: 5,
      },
      export: { mode: "viewport" },
      notes: "",
    });

    expect(result).toEqual({ ok: false, error: "viewState.evidenceOverlayDepth must be a number within 1..3 when present" });
  });


  it("includes mergeAuditLog in export/import roundtrip", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-audit", title: "Audit" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      exportMode: "viewport",
      mergeAuditLog: [
        {
          id: "merge-1",
          createdAt: "2026-01-01T00:00:00.000Z",
          source: { kind: "unknown", fileName: "compare.json" },
          summary: { totalItems: 1, byKind: { "card.add": 1 } },
          details: { itemIds: { ids: ["card.add:c1"] }, entityIds: { cards: { ids: ["c1"] } } },
        },
      ],
    });

    expect(metadata.mergeAuditLog).toHaveLength(1);
    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.mergeAuditLog).toHaveLength(1);
      expect(result.metadata.mergeAuditLog?.[0]?.details.itemIds?.ids).toEqual(["card.add:c1"]);
    }
  });

  it("accepts legacy mergeAuditLog array-id format", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-legacy-audit",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      mergeAuditLog: [
        {
          id: "legacy-1",
          createdAt: "2026-01-01T00:00:00.000Z",
          source: { kind: "unknown" },
          summary: { totalItems: 1, byKind: { "card.add": 1 } },
          details: { itemIds: ["card.add:c1"], entityIds: { cards: ["c1"] } },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.mergeAuditLog?.[0]?.details.itemIds?.ids).toEqual(["card.add:c1"]);
    }
  });


  it("includes reviewEvents in export/import roundtrip", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-review", title: "Review" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      exportMode: "viewport",
      reviewEvents: [
        {
          id: "review-1",
          target: { kind: "summary", id: "summary-1" },
          action: "markReviewed",
          createdAt: "2026-03-01T00:00:00.000Z",
          contextLabel: "relation.summary",
        },
      ],
    });

    expect(metadata.reviewEvents).toHaveLength(1);
    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.reviewEvents).toHaveLength(1);
      expect(result.metadata.reviewEvents?.[0]?.target).toEqual({ kind: "summary", id: "summary-1" });
    }
  });

  it("strips reviewerRef when review redaction mode is strip-identities", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-review", title: "Review" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      exportMode: "viewport",
      reviewRedactionMode: "strip-identities",
      reviewEvents: [
        {
          id: "review-1",
          target: { kind: "summary", id: "summary-1" },
          action: "markReviewed",
          createdAt: "2026-03-01T00:00:00.000Z",
          reviewerRef: "user:local:abc",
        },
      ],
    });

    expect(metadata.reviewEvents?.[0]).toEqual({
      id: "review-1",
      target: { kind: "summary", id: "summary-1" },
      action: "markReviewed",
      createdAt: "2026-03-01T00:00:00.000Z",
    });
  });

  it("removes reviewEvents when review redaction mode is strip-all", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-review", title: "Review" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      exportMode: "viewport",
      reviewRedactionMode: "strip-all",
      reviewEvents: [
        {
          id: "review-1",
          target: { kind: "summary", id: "summary-1" },
          action: "markReviewed",
          createdAt: "2026-03-01T00:00:00.000Z",
        },
      ],
    });

    expect(metadata.reviewEvents).toBeUndefined();
  });

  it("sanitizes invalid reviewEvents entries on import", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-review-events",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      reviewEvents: [
        {
          id: "review-valid",
          target: { kind: "island", id: "island-1" },
          action: "unreview",
          createdAt: "2026-03-01T00:00:00.000Z",
        },
        {
          id: "review-invalid",
          target: { kind: "island", id: "island-2" },
          action: "approve",
          createdAt: "2026-03-01T00:00:00.000Z",
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.reviewEvents).toHaveLength(1);
      expect(result.metadata.reviewEvents?.[0]?.id).toBe("review-valid");
    }
  });

  it("rejects non-array reviewEvents payload", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-review-events-invalid",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
      reviewEvents: "invalid",
    });

    expect(result).toEqual({ ok: false, error: "metadata.reviewEvents must be an array when present" });
  });

  it("keeps backward compatibility when mergeAuditLog is missing", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-no-audit",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
      },
      export: { mode: "viewport" },
    });

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.metadata.mergeAuditLog).toBeUndefined();
    }
  });


});

it("preserves presets and activePresetId across export/import validation", () => {
  const metadata = buildExportViewMetadata({
    doc: { id: "doc-321", title: "Preset" },
    camera: { panX: 1, panY: 2, zoom: 1 },
    viewState: {
      summaryView: false,
      abstractMapView: false,
      hideSourceCards: false,
      maxDepth: "all",
      focusIslandId: null,
      showReadingOrder: false,
      presets: [
        {
          id: "preset-1",
          name: "Review",
          viewPatch: { perspectiveMode: "review", safeMode: true },
          createdAt: "2026-01-01T00:00:00.000Z",
          updatedAt: "2026-01-01T00:00:00.000Z",
        },
      ],
      activePresetId: "preset-1",
    },
    exportMode: "viewport",
  });

  const result = validateImportViewMetadata(metadata);
  expect(result.ok).toBe(true);
  if (result.ok) {
    expect(result.metadata.viewState.presets?.[0].id).toBe("preset-1");
    expect(result.metadata.viewState.activePresetId).toBe("preset-1");
  }
});

  it("persists and validates locale in view metadata", () => {
    const metadata = buildExportViewMetadata({
      doc: { id: "doc-locale", title: "Locale" },
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: false,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: "all",
        focusIslandId: null,
        showReadingOrder: false,
        locale: "en",
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.locale).toBe("en");
    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });

  it("rejects unsupported locale in view metadata", () => {
    const result = validateImportViewMetadata({
      version: "1",
      generatedAt: "2026-03-01T12:34:56.000Z",
      docSignature: "doc-123",
      camera: { panX: 0, panY: 0, zoom: 1 },
      viewState: {
        summaryView: true,
        abstractMapView: false,
        hideSourceCards: false,
        maxDepth: 1,
        focusIslandId: null,
        showReadingOrder: false,
        locale: "fr",
      },
      export: { mode: "viewport" },
    });

    expect(result).toEqual({ ok: false, error: "viewState.locale must be a supported locale when present" });
  });
