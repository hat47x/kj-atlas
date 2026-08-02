import type { RepresentativeVisualCue } from "./types";

export const REPRESENTATIVE_VISUAL_CUE_PRESETS = [
  { cueId: "shape-circle", labelKey: "side_panel.visual_cue.preset.circle" },
  { cueId: "shape-triangle", labelKey: "side_panel.visual_cue.preset.triangle" },
  { cueId: "shape-diamond", labelKey: "side_panel.visual_cue.preset.diamond" },
  { cueId: "shape-parallel-lines", labelKey: "side_panel.visual_cue.preset.parallel_lines" },
] as const;

export type RepresentativeVisualCuePresetId = (typeof REPRESENTATIVE_VISUAL_CUE_PRESETS)[number]["cueId"];

const presetIds = new Set<string>(REPRESENTATIVE_VISUAL_CUE_PRESETS.map((preset) => preset.cueId));

export function isRepresentativeVisualCuePresetId(value: string): value is RepresentativeVisualCuePresetId {
  return presetIds.has(value);
}

export function createRepresentativeVisualCuePreset(
  cueId: RepresentativeVisualCuePresetId,
  altText: string,
): RepresentativeVisualCue {
  return {
    kind: "preset_svg",
    cueId,
    altText,
  };
}
