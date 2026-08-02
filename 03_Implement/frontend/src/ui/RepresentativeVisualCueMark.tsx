import { isRepresentativeVisualCuePresetId } from "../domain/representative_visual_cue_presets";
import type { RepresentativeVisualCue } from "../domain/types";

type RepresentativeVisualCueMarkProps = {
  cue: RepresentativeVisualCue;
  size?: number;
};

export function RepresentativeVisualCueMark({ cue, size = 20 }: RepresentativeVisualCueMarkProps) {
  if (cue.kind !== "preset_svg" || !isRepresentativeVisualCuePresetId(cue.cueId)) {
    return null;
  }

  return (
    <svg
      aria-hidden="true"
      data-representative-visual-cue={cue.cueId}
      focusable="false"
      width={size}
      height={size}
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      style={{ display: "block", flex: "0 0 auto", color: "#64748b" }}
    >
      {cue.cueId === "shape-circle" ? <circle cx="10" cy="10" r="6" /> : null}
      {cue.cueId === "shape-triangle" ? <path d="M10 3.5 16.5 16H3.5Z" /> : null}
      {cue.cueId === "shape-diamond" ? <path d="m10 3 7 7-7 7-7-7Z" /> : null}
      {cue.cueId === "shape-parallel-lines" ? (
        <>
          <path d="M4 6h12" />
          <path d="M4 10h12" />
          <path d="M4 14h12" />
        </>
      ) : null}
    </svg>
  );
}
