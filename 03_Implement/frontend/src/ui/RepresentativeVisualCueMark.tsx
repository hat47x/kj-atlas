import { useEffect, useState } from "react";

import {
  loadRepresentativeVisualCueAsset,
  type RepresentativeVisualCueAssetV1,
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
  const [loadedPortableAsset, setLoadedPortableAsset] = useState<{
    imageRef: string;
    scopeKey: string;
    asset: RepresentativeVisualCueAssetV1;
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoadedPortableAsset(null);
    if ((cue.kind !== "hand_drawn" && cue.kind !== "user_image") || !cue.imageRef) {
      return () => {
        cancelled = true;
      };
    }
    void loadRepresentativeVisualCueAsset(cue.imageRef, scope)
      .then((asset) => {
        if (!cancelled && asset?.kind === cue.kind) {
          setLoadedPortableAsset({
            imageRef: cue.imageRef!,
            scopeKey,
            asset,
          });
        }
      })
      .catch(() => {
        if (!cancelled) {
          setLoadedPortableAsset(null);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [cue.imageRef, cue.kind, scopeKey]);

  const isPreset = cue.kind === "preset_svg" && isRepresentativeVisualCuePresetId(cue.cueId);
  const portableAsset =
    (cue.kind === "hand_drawn" || cue.kind === "user_image")
    && cue.imageRef
    && loadedPortableAsset?.imageRef === cue.imageRef
    && loadedPortableAsset.scopeKey === scopeKey
    && loadedPortableAsset.asset.kind === cue.kind
      ? loadedPortableAsset.asset
      : null;
  if (!isPreset && !portableAsset) {
    return null;
  }

  if (portableAsset?.kind === "user_image") {
    return (
      <img
        aria-hidden="true"
        data-representative-visual-cue={cue.cueId}
        width={size}
        height={size}
        src={`data:image/png;base64,${portableAsset.base64}`}
        alt=""
        style={{
          display: "block",
          flex: "0 0 auto",
          width: size,
          height: size,
          borderRadius: 2,
          objectFit: "cover",
          filter: "saturate(0.75)",
        }}
      />
    );
  }

  const handDrawnAsset = portableAsset?.kind === "hand_drawn" ? portableAsset : null;
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
