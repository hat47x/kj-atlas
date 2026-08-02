import { useMemo, useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

import {
  deleteHandDrawnCueAsset,
  saveHandDrawnCueAsset,
  type HandDrawnCueAssetV1,
  type HandDrawnCuePointV1,
} from "../domain/representative_visual_cue_assets";
import type { RepresentativeVisualCue } from "../domain/types";
import { t } from "../i18n/translate";
import { useRepresentativeVisualCueAssetScope } from "./RepresentativeVisualCueAssetScope";

type Props = {
  documentId: string;
  disabled: boolean;
  onAdopt: (cue: RepresentativeVisualCue) => boolean;
};

function clampCoordinate(value: number): number {
  return Math.max(0, Math.min(20, Math.round(value)));
}

function appendDistinctPoint(
  strokes: readonly (readonly HandDrawnCuePointV1[])[],
  point: HandDrawnCuePointV1,
): HandDrawnCuePointV1[][] {
  const next = strokes.map((stroke) => [...stroke]);
  const current = next[next.length - 1];
  if (!current) {
    return [[point]];
  }
  const previous = current[current.length - 1];
  if (previous?.x !== point.x || previous?.y !== point.y) {
    current.push(point);
  }
  return next;
}

export function RepresentativeVisualCueHandDrawnEditor({ documentId, disabled, onAdopt }: Props) {
  const scope = useRepresentativeVisualCueAssetScope();
  const [strokes, setStrokes] = useState<HandDrawnCuePointV1[][]>([]);
  const [cursor, setCursor] = useState<HandDrawnCuePointV1>({ x: 10, y: 10 });
  const [keyboardDrawing, setKeyboardDrawing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const activePointerId = useRef<number | null>(null);

  const asset = useMemo<HandDrawnCueAssetV1 | null>(() => {
    if (strokes.length === 0) {
      return null;
    }
    return {
      version: 1,
      kind: "hand_drawn",
      width: 20,
      height: 20,
      strokes,
    };
  }, [strokes]);

  const pointFromPointer = (event: PointerEvent<SVGSVGElement>): HandDrawnCuePointV1 => {
    const bounds = event.currentTarget.getBoundingClientRect();
    return {
      x: clampCoordinate(((event.clientX - bounds.left) / bounds.width) * 20),
      y: clampCoordinate(((event.clientY - bounds.top) / bounds.height) * 20),
    };
  };

  const handlePointerDown = (event: PointerEvent<SVGSVGElement>) => {
    if (disabled || isSaving) {
      return;
    }
    event.currentTarget.setPointerCapture(event.pointerId);
    activePointerId.current = event.pointerId;
    const point = pointFromPointer(event);
    setCursor(point);
    setKeyboardDrawing(false);
    setStrokes((current) => [...current, [point]]);
  };

  const handlePointerMove = (event: PointerEvent<SVGSVGElement>) => {
    if (activePointerId.current !== event.pointerId) {
      return;
    }
    const point = pointFromPointer(event);
    setCursor(point);
    setStrokes((current) => appendDistinctPoint(current, point));
  };

  const finishPointer = (event: PointerEvent<SVGSVGElement>) => {
    if (activePointerId.current === event.pointerId) {
      activePointerId.current = null;
      if (event.currentTarget.hasPointerCapture(event.pointerId)) {
        event.currentTarget.releasePointerCapture(event.pointerId);
      }
    }
  };

  const handleKeyDown = (event: KeyboardEvent<SVGSVGElement>) => {
    if (disabled || isSaving) {
      return;
    }
    if (event.key === " " || event.key === "Enter") {
      event.preventDefault();
      if (keyboardDrawing) {
        setKeyboardDrawing(false);
      } else {
        setKeyboardDrawing(true);
        setStrokes((current) => [...current, [cursor]]);
      }
      return;
    }
    const delta =
      event.key === "ArrowLeft" ? { x: -1, y: 0 }
      : event.key === "ArrowRight" ? { x: 1, y: 0 }
      : event.key === "ArrowUp" ? { x: 0, y: -1 }
      : event.key === "ArrowDown" ? { x: 0, y: 1 }
      : null;
    if (!delta) {
      return;
    }
    event.preventDefault();
    const next = {
      x: clampCoordinate(cursor.x + delta.x),
      y: clampCoordinate(cursor.y + delta.y),
    };
    setCursor(next);
    if (keyboardDrawing) {
      setStrokes((current) => appendDistinctPoint(current, next));
    }
  };

  const handleSave = async () => {
    if (!asset || disabled || isSaving) {
      return;
    }
    setIsSaving(true);
    setError(null);
    try {
      const imageRef = await saveHandDrawnCueAsset(documentId, asset, scope);
      const adopted = onAdopt({
        kind: "hand_drawn",
        cueId: imageRef,
        imageRef,
        altText: t("side_panel.visual_cue.hand_drawn.default_alt"),
      });
      if (!adopted) {
        await deleteHandDrawnCueAsset(imageRef, scope);
        throw new Error("document rejected the visual cue");
      }
      setStrokes([]);
      setKeyboardDrawing(false);
    } catch {
      setError(t("side_panel.visual_cue.hand_drawn.save_error"));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div
      data-visual-cue-editor="hand-drawn"
      style={{ display: "grid", gap: 8, borderTop: "1px solid #e2e8f0", paddingTop: 8 }}
    >
      <div style={{ fontSize: 12, fontWeight: 700, color: "#334155" }}>
        {t("side_panel.visual_cue.hand_drawn.title")}
      </div>
      <div id="hand-drawn-cue-instructions" style={{ fontSize: 11, lineHeight: 1.5, color: "#475569" }}>
        {t("side_panel.visual_cue.hand_drawn.instructions")}
      </div>
      <svg
        role="application"
        aria-label={t("side_panel.visual_cue.hand_drawn.canvas")}
        aria-describedby="hand-drawn-cue-instructions"
        tabIndex={disabled ? -1 : 0}
        viewBox="0 0 20 20"
        width="120"
        height="120"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={finishPointer}
        onPointerCancel={finishPointer}
        onKeyDown={handleKeyDown}
        style={{
          width: 120,
          height: 120,
          maxWidth: "100%",
          justifySelf: "center",
          border: "1px solid #94a3b8",
          borderRadius: 6,
          backgroundColor: "#ffffff",
          color: "#475569",
          touchAction: "none",
        }}
      >
        {strokes.map((stroke, index) =>
          stroke.length === 1 ? (
            <circle key={index} cx={stroke[0].x} cy={stroke[0].y} r="0.6" fill="currentColor" />
          ) : (
            <polyline
              key={index}
              points={stroke.map((point) => `${point.x},${point.y}`).join(" ")}
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          ),
        )}
        <circle
          cx={cursor.x}
          cy={cursor.y}
          r="0.75"
          fill={keyboardDrawing ? "#0284c7" : "none"}
          stroke="#0284c7"
          strokeWidth="0.4"
          pointerEvents="none"
        />
      </svg>
      <div role="status" style={{ minHeight: 18, fontSize: 11, color: error ? "#b91c1c" : "#475569" }}>
        {error ?? (keyboardDrawing
          ? t("side_panel.visual_cue.hand_drawn.keyboard_drawing")
          : t("side_panel.visual_cue.hand_drawn.keyboard_cursor"))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: 6 }}>
        <button
          type="button"
          disabled={disabled || isSaving || strokes.length === 0}
          onClick={() => {
            setStrokes((current) => current.slice(0, -1));
            setKeyboardDrawing(false);
          }}
        >
          {t("side_panel.visual_cue.hand_drawn.undo_stroke")}
        </button>
        <button
          type="button"
          disabled={disabled || isSaving || strokes.length === 0}
          onClick={() => {
            setStrokes([]);
            setKeyboardDrawing(false);
          }}
        >
          {t("side_panel.visual_cue.hand_drawn.clear")}
        </button>
        <button type="button" disabled={disabled || isSaving || !asset} onClick={() => void handleSave()}>
          {isSaving
            ? t("side_panel.visual_cue.hand_drawn.saving")
            : t("side_panel.visual_cue.hand_drawn.adopt")}
        </button>
      </div>
    </div>
  );
}
