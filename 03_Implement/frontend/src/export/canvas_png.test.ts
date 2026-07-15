import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { computeVisibleBounds } from "../domain/geometry/bounds";
import type { DocumentV1 } from "../domain/types";
import { exportCanvasToPngBlob, exportSvgToPngBlob } from "./canvas_png";

class MockImage {
  onload: null | (() => void) = null;
  onerror: null | (() => void) = null;

  set src(_value: string) {
    setTimeout(() => {
      this.onload?.();
    }, 0);
  }
}

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc_png",
    title: "PNG",
    createdAt: "2026-02-15T00:00:00.000Z",
    updatedAt: "2026-02-15T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Card one", x: 100, y: 100 },
      { id: "c2", text: "Card two", x: 360, y: 140 },
      { id: "c3", text: "Source card", x: 620, y: 180, canonicalId: "c2" },
    ],
    edges: [
      { id: "e1", fromId: "c1", toId: "c2", type: "related" },
      { id: "e2", fromId: "c2", toId: "c3", type: "negate" },
      { id: "e3", fromId: "c1", toId: "c3", type: "related" },
    ],
    islands: [
      { id: "i1", title: "Island One", summaryText: "Summary", cardIds: ["c1", "c2"] },
      { id: "i2", title: "Island Two", cardIds: ["c3"] },
    ],
  };
}

describe("canvas_png export", () => {
  beforeEach(() => {
    vi.restoreAllMocks();

    const mockCanvas = {
      width: 0,
      height: 0,
      getContext: vi.fn(() => ({ drawImage: vi.fn() })),
      toBlob: vi.fn((callback: (blob: Blob | null) => void) => {
        callback(new Blob([Uint8Array.from([137, 80, 78, 71])], { type: "image/png" }));
      }),
    };

    vi.stubGlobal("Image", MockImage as unknown as typeof Image);
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:mock"),
      revokeObjectURL: vi.fn(),
    });
    vi.stubGlobal("document", {
      createElement: vi.fn(() => mockCanvas),
    });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("exports png blob at 1x", async () => {
    const blob = await exportSvgToPngBlob({
      svg: '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"></svg>',
      width: 100,
      height: 50,
      scale: 1,
    });

    expect(blob.type).toBe("image/png");
    const header = new Uint8Array(await blob.arrayBuffer());
    expect(Array.from(header)).toEqual([137, 80, 78, 71]);
  });

  it("applies 2x scale to canvas dimensions", async () => {
    const canvas = document.createElement("canvas") as {
      width: number;
      height: number;
    };

    await exportSvgToPngBlob({
      svg: '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50"></svg>',
      width: 100,
      height: 50,
      scale: 2,
    });

    expect(canvas.width).toBe(200);
    expect(canvas.height).toBe(100);
  });

  it("exports png via svg pipeline helper", async () => {
    const doc = buildDoc();
    const viewState = {
      visibleIslandIds: new Set(["i1", "i2"]),
      hiddenCardIds: new Set<string>(),
      hideSourceCards: false,
      summaryView: false,
      abstractMapView: false,
    };
    const area = computeVisibleBounds(doc, viewState);
    expect(area).not.toBeNull();

    const blob = await exportCanvasToPngBlob({
      doc,
      viewState,
      camera: { panX: 0, panY: 0, zoom: 1, viewportWidth: 1280, viewportHeight: 720 },
      area: area!,
      scale: 2,
    });

    expect(blob.type).toBe("image/png");
    const header = new Uint8Array(await blob.arrayBuffer());
    expect(Array.from(header)).toEqual([137, 80, 78, 71]);
  });

  it("exports normal and abstract map views via helper without mutating document", async () => {
    const doc = buildDoc();
    const before = JSON.stringify(doc);

    const normalViewState = {
      visibleIslandIds: new Set(["i1", "i2"]),
      hiddenCardIds: new Set<string>(),
      hideSourceCards: false,
      summaryView: false,
      abstractMapView: false,
    };
    const abstractMapViewState = {
      visibleIslandIds: new Set(["i1", "i2"]),
      hiddenCardIds: new Set(["c1", "c2", "c3"]),
      hideSourceCards: true,
      summaryView: true,
      abstractMapView: true,
    };

    const normalBounds = computeVisibleBounds(doc, normalViewState);
    const abstractBounds = computeVisibleBounds(doc, abstractMapViewState);

    expect(normalBounds).not.toBeNull();
    expect(abstractBounds).not.toBeNull();

    const normalPng = await exportCanvasToPngBlob({
      doc,
      viewState: normalViewState,
      camera: { panX: 0, panY: 0, zoom: 1, viewportWidth: 1280, viewportHeight: 720 },
      area: normalBounds!,
      scale: 1,
    });
    const abstractPng = await exportCanvasToPngBlob({
      doc,
      viewState: abstractMapViewState,
      camera: { panX: 0, panY: 0, zoom: 1, viewportWidth: 1280, viewportHeight: 720 },
      area: abstractBounds!,
      scale: 2,
    });

    expect(normalPng.type).toBe("image/png");
    expect(abstractPng.type).toBe("image/png");
    expect(JSON.stringify(doc)).toBe(before);
  });
});
