import { describe, expect, it } from "vitest";

import {
  collectHandDrawnCueImageRefs,
  HAND_DRAWN_CUE_ASSET_MAX_BYTES,
  parseHandDrawnCueAssetBundle,
  parseHandDrawnCueAsset,
  serializeHandDrawnCueAsset,
  stripHandDrawnVisualCues,
  visualCueAssetScopeKey,
} from "./representative_visual_cue_assets";
import type { DocumentV1 } from "./types";

describe("representative visual cue assets", () => {
  const valid = {
    version: 1,
    kind: "hand_drawn",
    width: 20,
    height: 20,
    strokes: [[{ x: 1, y: 2 }, { x: 10, y: 12 }]],
  } as const;
  const imageRef = "visual-cue:00000000-0000-4000-8000-000000000001";
  const documentWithCue: DocumentV1 = {
    version: 1,
    id: "doc-cue",
    createdAt: "2026-08-02T00:00:00.000Z",
    updatedAt: "2026-08-02T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [
      {
        id: "island-1",
        cardIds: [],
        representativeCue: {
          kind: "hand_drawn",
          cueId: imageRef,
          imageRef,
          altText: "mark",
        },
      },
    ],
  };

  it("strictly validates and serializes a bounded hand-drawn vector asset", () => {
    expect(parseHandDrawnCueAsset(valid)).toEqual(valid);
    expect(JSON.parse(serializeHandDrawnCueAsset(valid))).toEqual(valid);
    expect(new TextEncoder().encode(serializeHandDrawnCueAsset(valid)).byteLength).toBeLessThanOrEqual(
      HAND_DRAWN_CUE_ASSET_MAX_BYTES,
    );
  });

  it("rejects a coordinate payload over the 4KB storage budget", () => {
    const points = Array.from({ length: 250 }, (_, index) => ({
      x: index % 21,
      y: Math.floor(index / 21) % 21,
    }));
    expect(() =>
      parseHandDrawnCueAsset({
        ...valid,
        strokes: [points, points],
      }),
    ).toThrow("exceeds 4KB");
  });

  it.each([
    { ...valid, future: true },
    { ...valid, version: 2 },
    { ...valid, strokes: [] },
    { ...valid, strokes: [[{ x: -1, y: 2 }]] },
    { ...valid, strokes: [[{ x: 1.5, y: 2 }]] },
    { ...valid, strokes: [[{ x: 1, y: 2, pressure: 1 }]] },
  ])("rejects malformed or unknown asset data", (value) => {
    expect(() => parseHandDrawnCueAsset(value)).toThrow();
  });

  it("uses a closed local scope and separates tenant/principal storage", () => {
    const local = visualCueAssetScopeKey();
    const tenantA = visualCueAssetScopeKey({
      deployment: "https://atlas.example.test",
      tenantId: "tenant-a",
      principalId: "user-1",
    });
    const tenantB = visualCueAssetScopeKey({
      deployment: "https://atlas.example.test",
      tenantId: "tenant-b",
      principalId: "user-1",
    });

    expect(local).toBe("kj-atlas/local-scope/v1/");
    expect(tenantA).not.toBe(tenantB);
    expect(() =>
      visualCueAssetScopeKey({
        deployment: "https://atlas.example.test",
        tenantId: " tenant-a",
        principalId: "user-1",
      }),
    ).toThrow();
  });

  it("strictly binds an asset bundle to the document's exact hand-drawn references", () => {
    const bundle = parseHandDrawnCueAssetBundle({
      version: "1",
      documentId: documentWithCue.id,
      assets: [{ imageRef, asset: valid }],
    }, documentWithCue);

    expect(bundle.assets).toEqual([{ imageRef, asset: valid }]);
    expect(collectHandDrawnCueImageRefs(documentWithCue)).toEqual([imageRef]);
  });

  it.each([
    {
      version: "1",
      documentId: "other-document",
      assets: [{ imageRef, asset: valid }],
    },
    {
      version: "1",
      documentId: documentWithCue.id,
      assets: [],
    },
    {
      version: "1",
      documentId: documentWithCue.id,
      assets: [{ imageRef: "visual-cue:00000000-0000-4000-8000-000000000099", asset: valid }],
    },
    {
      version: "1",
      documentId: documentWithCue.id,
      assets: [{ imageRef, asset: valid }, { imageRef, asset: valid }],
    },
    {
      version: "1",
      documentId: documentWithCue.id,
      assets: [{ imageRef, asset: valid, extra: true }],
    },
  ])("rejects a forged, incomplete, duplicate, or unknown asset bundle", (bundle) => {
    expect(() => parseHandDrawnCueAssetBundle(bundle, documentWithCue)).toThrow();
  });

  it("removes hand-drawn metadata without changing other cues or the source document", () => {
    const presetDocument: DocumentV1 = {
      ...documentWithCue,
      islands: [
        ...documentWithCue.islands,
        {
          id: "island-2",
          cardIds: [],
          representativeCue: {
            kind: "preset_svg",
            cueId: "shape-circle",
            altText: "circle",
          },
        },
      ],
    };

    const stripped = stripHandDrawnVisualCues(presetDocument);
    expect(stripped.islands[0].representativeCue).toBeUndefined();
    expect(stripped.islands[1].representativeCue).toEqual(presetDocument.islands[1].representativeCue);
    expect(presetDocument.islands[0].representativeCue?.kind).toBe("hand_drawn");
  });
});
