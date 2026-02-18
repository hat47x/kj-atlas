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
      },
      exportMode: "viewport",
    });

    expect(metadata.viewState.lodEnabled).toBe(true);
    expect(metadata.viewState.lodThresholds).toEqual({ close: 1, mid: 0.5 });

    const result = validateImportViewMetadata(metadata);
    expect(result.ok).toBe(true);
  });

});
