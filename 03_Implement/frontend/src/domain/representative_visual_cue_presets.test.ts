import { describe, expect, it } from "vitest";

import {
  createRepresentativeVisualCuePreset,
  isRepresentativeVisualCuePresetId,
  REPRESENTATIVE_VISUAL_CUE_PRESETS,
} from "./representative_visual_cue_presets";

describe("representative visual cue presets", () => {
  it("keeps a small, unique, offline-only basic-shape catalog", () => {
    expect(REPRESENTATIVE_VISUAL_CUE_PRESETS).toHaveLength(4);
    expect(new Set(REPRESENTATIVE_VISUAL_CUE_PRESETS.map((preset) => preset.cueId)).size).toBe(
      REPRESENTATIVE_VISUAL_CUE_PRESETS.length,
    );
    expect(REPRESENTATIVE_VISUAL_CUE_PRESETS.every((preset) => preset.cueId.startsWith("shape-"))).toBe(true);
  });

  it("creates a preset reference without external or binary data", () => {
    expect(createRepresentativeVisualCuePreset("shape-circle", "Circle")).toEqual({
      kind: "preset_svg",
      cueId: "shape-circle",
      altText: "Circle",
    });
    expect(isRepresentativeVisualCuePresetId("shape-circle")).toBe(true);
    expect(isRepresentativeVisualCuePresetId("https://example.test/cue.svg")).toBe(false);
  });
});
