import { describe, expect, it } from "vitest";

import {
  HAND_DRAWN_CUE_ASSET_MAX_BYTES,
  parseHandDrawnCueAsset,
  serializeHandDrawnCueAsset,
  visualCueAssetScopeKey,
} from "./representative_visual_cue_assets";

describe("representative visual cue assets", () => {
  const valid = {
    version: 1,
    kind: "hand_drawn",
    width: 20,
    height: 20,
    strokes: [[{ x: 1, y: 2 }, { x: 10, y: 12 }]],
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
});
