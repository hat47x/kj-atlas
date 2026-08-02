import { describe, expect, it } from "vitest";
import { deflateSync } from "node:zlib";

import {
  collectPortableVisualCueImageRefs,
  encodeUserImageCuePng,
  HAND_DRAWN_CUE_ASSET_MAX_BYTES,
  parseRepresentativeVisualCueAssetBundle,
  parseHandDrawnCueAsset,
  parseUserImageCueAsset,
  serializeHandDrawnCueAsset,
  stripPortableVisualCues,
  visualCueAssetScopeKey,
} from "./representative_visual_cue_assets";
import type { DocumentV1 } from "./types";

function crc32(bytes: Uint8Array): number {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pngChunk(type: string, data: Uint8Array): Uint8Array {
  const result = new Uint8Array(12 + data.byteLength);
  const view = new DataView(result.buffer);
  view.setUint32(0, data.byteLength);
  result.set(new TextEncoder().encode(type), 4);
  result.set(data, 8);
  view.setUint32(8 + data.byteLength, crc32(result.subarray(4, 8 + data.byteLength)));
  return result;
}

function buildPng(width = 48, height = 48): Uint8Array {
  const signature = Uint8Array.from([137, 80, 78, 71, 13, 10, 26, 10]);
  const header = new Uint8Array(13);
  const headerView = new DataView(header.buffer);
  headerView.setUint32(0, width);
  headerView.setUint32(4, height);
  header.set([8, 6, 0, 0, 0], 8);
  const scanlines = new Uint8Array(height * (1 + width * 4));
  const compressed = new Uint8Array(deflateSync(scanlines));
  const chunks = [
    pngChunk("IHDR", header),
    pngChunk("IDAT", compressed),
    pngChunk("IEND", new Uint8Array()),
  ];
  const result = new Uint8Array(signature.byteLength + chunks.reduce((sum, chunk) => sum + chunk.byteLength, 0));
  let offset = 0;
  for (const part of [signature, ...chunks]) {
    result.set(part, offset);
    offset += part.byteLength;
  }
  return result;
}

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
  const validUserImage = {
    version: 1,
    kind: "user_image",
    width: 48,
    height: 48,
    mimeType: "image/png",
    base64: encodeUserImageCuePng(buildPng()),
  } as const;

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

  it("strictly validates a bounded, canonical 48x48 PNG crop", () => {
    expect(parseUserImageCueAsset(validUserImage)).toEqual(validUserImage);
  });

  it.each([
    { ...validUserImage, width: 47 },
    { ...validUserImage, future: true },
    { ...validUserImage, base64: `${validUserImage.base64}\n` },
    { ...validUserImage, base64: encodeUserImageCuePng(buildPng(47, 48)) },
    {
      ...validUserImage,
      base64: encodeUserImageCuePng(Uint8Array.from([
        ...buildPng().slice(0, -1),
        buildPng().at(-1)! ^ 1,
      ])),
    },
  ])("rejects malformed, non-canonical, wrong-size, or corrupted image crops", (value) => {
    expect(() => parseUserImageCueAsset(value)).toThrow();
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

  it("strictly binds an asset bundle to the document's exact local references and cue kinds", () => {
    const bundle = parseRepresentativeVisualCueAssetBundle({
      version: "1",
      documentId: documentWithCue.id,
      assets: [{ imageRef, asset: valid }],
    }, documentWithCue);

    expect(bundle.assets).toEqual([{ imageRef, asset: valid }]);
    expect(collectPortableVisualCueImageRefs(documentWithCue)).toEqual([imageRef]);

    const userImageDocument: DocumentV1 = {
      ...documentWithCue,
      islands: [{
        ...documentWithCue.islands[0],
        representativeCue: {
          kind: "user_image",
          cueId: imageRef,
          imageRef,
          altText: "crop",
        },
      }],
    };
    expect(parseRepresentativeVisualCueAssetBundle({
      version: "1",
      documentId: userImageDocument.id,
      assets: [{ imageRef, asset: validUserImage }],
    }, userImageDocument).assets[0].asset.kind).toBe("user_image");
    expect(() => parseRepresentativeVisualCueAssetBundle({
      version: "1",
      documentId: userImageDocument.id,
      assets: [{ imageRef, asset: valid }],
    }, userImageDocument)).toThrow(/kind does not match/);
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
    expect(() => parseRepresentativeVisualCueAssetBundle(bundle, documentWithCue)).toThrow();
  });

  it("removes local asset metadata without changing presets or the source document", () => {
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
        {
          id: "island-3",
          cardIds: [],
          representativeCue: {
            kind: "user_image",
            cueId: "visual-cue:00000000-0000-4000-8000-000000000003",
            imageRef: "visual-cue:00000000-0000-4000-8000-000000000003",
            altText: "crop",
          },
        },
      ],
    };

    const stripped = stripPortableVisualCues(presetDocument);
    expect(stripped.islands[0].representativeCue).toBeUndefined();
    expect(stripped.islands[1].representativeCue).toEqual(presetDocument.islands[1].representativeCue);
    expect(stripped.islands[2].representativeCue).toBeUndefined();
    expect(presetDocument.islands[0].representativeCue?.kind).toBe("hand_drawn");
  });
});
