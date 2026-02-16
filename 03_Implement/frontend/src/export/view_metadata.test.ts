import { afterEach, describe, expect, it, vi } from "vitest";

import { buildExportViewMetadata } from "./view_metadata";

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
});
