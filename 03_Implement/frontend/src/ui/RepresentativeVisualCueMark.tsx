import { useEffect, useState } from "react";

import {
  loadHandDrawnCueAsset,
  type HandDrawnCueAssetV1,
  visualCueAssetScopeKey,
} from "../domain/representative_visual_cue_assets";
import { isRepresentativeVisualCuePresetId } from "../domain/representative_visual_cue_presets";
import type { RepresentativeVisualCue } from "../domain/types";
import { useRepresentativeVisualCueAssetScope } from "./RepresentativeVisualCueAssetScope";

type RepresentativeVisualCueMarkProps = {
  cue: RepresentativeVisualCue;
  size?: number;
};

export function RepresentativeVisualCueMark({ cue, size = 20 }: RepresentativeVisualCueMarkProps) {
  const scope = useRepresentativeVisualCueAssetScope();
  const scopeKey = visualCueAssetScopeKey(scope);
  const [loadedHandDrawnAsset, setLoadedHandDrawnAsset] = useState<{
    imageRef: string;
    scopeKey: string;
    asset: HandDrawnCueAssetV1;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadedHandDrawnAsset(null);
    if (cue.kind !== "hand_drawn" || !cue.imageRef) {
      return () => {
        cancelled = true;
      };
    }
    void loadHandDrawnCueAsset(cue.imageRef, scope)
      .then((asset) => {
        if (!cancelled && asset) {
          setLoadedHandDrawnAsset({
            imageRef: cue.imageRef!,
            scopeKey,
            asset,
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadedHandDrawnAsset(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [cue.imageRef, cue.kind, scopeKey]);

  const isPreset = cue.kind === "preset_svg" && isRepresentativeVisualCuePresetId(cue.cueId);
  const handDrawnAsset =
    cue.kind === "hand_drawn"
    && cue.imageRef
    && loadedHandDrawnAsset?.imageRef === cue.imageRef
    && loadedHandDrawnAsset.scopeKey === scopeKey
      ? loadedHandDrawnAsset.asset
      : null;
  if (!isPreset && !handDrawnAsset) {
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
      {isPreset && cue.cueId === "shape-circle" ? <circle cx="10" cy="10" r="6" /> : null}
      {isPreset && cue.cueId === "shape-triangle" ? <path d="M10 3.5 16.5 16H3.5Z" /> : null}
      {isPreset && cue.cueId === "shape-diamond" ? <path d="m10 3 7 7-7 7-7-7Z" /> : null}
      {isPreset && cue.cueId === "shape-parallel-lines" ? (
        <>
          <path d="M4 6h12" />
          <path d="M4 10h12" />
          <path d="M4 14h12" />
        </>
      ) : null}
      {handDrawnAsset?.strokes.map((stroke, index) =>
        stroke.length === 1 ? (
          <circle key={index} cx={stroke[0].x} cy={stroke[0].y} r="0.6" fill="currentColor" />
        ) : (
          <polyline
            key={index}
            points={stroke.map((point) => `${point.x},${point.y}`).join(" ")}
            fill="none"
          />
        ),
      )}
    </svg>
  );
}
