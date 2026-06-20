import { useRef, useState, type KeyboardEvent, type PointerEvent } from "react";

import type { Point } from "../domain/types";
import { t } from "../i18n/translate";

type PolygonEditLayerProps = {
  points: Point[];
  onVertexDragStart?: (vertexIndex: number) => void;
  onVertexDragMove?: (vertexIndex: number, point: Point) => void;
  onVertexDragCommit: (vertexIndex: number, point: Point) => void;
  onVertexDragCancel?: (vertexIndex: number) => void;
  onVertexNudge?: (vertexIndex: number, screenDelta: Point) => void;
  onVertexRemove: (vertexIndex: number) => void;
};

type DragState = {
  pointerId: number;
  vertexIndex: number;
};

const HANDLE_SIZE = 10;
const KEYBOARD_NUDGE_STEP = 8;
const KEYBOARD_NUDGE_LARGE_STEP = 32;

export function PolygonEditLayer({
  points,
  onVertexDragStart,
  onVertexDragMove,
  onVertexDragCommit,
  onVertexDragCancel,
  onVertexNudge,
  onVertexRemove,
}: PolygonEditLayerProps) {
  const [draggingVertexIndex, setDraggingVertexIndex] = useState<number | null>(null);
  const [dragPreviewPoint, setDragPreviewPoint] = useState<Point | null>(null);
  const dragStateRef = useRef<DragState | null>(null);
  const dragPreviewPointRef = useRef<Point | null>(null);

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>, vertexIndex: number) => {
    if (event.altKey) {
      event.preventDefault();
      event.stopPropagation();
      onVertexRemove(vertexIndex);
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);
    dragStateRef.current = {
      pointerId: event.pointerId,
      vertexIndex,
    };
    const startPoint = points[vertexIndex] ?? null;
    setDraggingVertexIndex(vertexIndex);
    setDragPreviewPoint(startPoint);
    dragPreviewPointRef.current = startPoint;
    onVertexDragStart?.(vertexIndex);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const dragState = dragStateRef.current;
    if (!dragState || dragState.pointerId !== event.pointerId) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    const nextPoint = { x: event.clientX, y: event.clientY };
    setDragPreviewPoint(nextPoint);
    dragPreviewPointRef.current = nextPoint;
    onVertexDragMove?.(dragState.vertexIndex, nextPoint);
  };

  const clearDrag = (event: PointerEvent<HTMLDivElement>, canceled: boolean) => {
    const dragState = dragStateRef.current;
    if (!dragState || dragState.pointerId !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    event.preventDefault();
    event.stopPropagation();
    const commitPoint = dragPreviewPointRef.current;
    dragStateRef.current = null;
    dragPreviewPointRef.current = null;
    setDraggingVertexIndex(null);
    setDragPreviewPoint(null);

    if (canceled) {
      onVertexDragCancel?.(dragState.vertexIndex);
      return;
    }

    if (commitPoint) {
      onVertexDragCommit(dragState.vertexIndex, commitPoint);
    }
  };

  const getDisplayPoint = (point: Point, index: number): Point => {
    if (index === draggingVertexIndex && dragPreviewPoint) {
      return dragPreviewPoint;
    }

    return point;
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>, vertexIndex: number) => {
    if (event.key === "Delete" || event.key === "Backspace") {
      event.preventDefault();
      event.stopPropagation();
      onVertexRemove(vertexIndex);
      return;
    }

    const step = event.shiftKey ? KEYBOARD_NUDGE_LARGE_STEP : KEYBOARD_NUDGE_STEP;
    const deltaByKey: Record<string, Point> = {
      ArrowLeft: { x: -step, y: 0 },
      ArrowRight: { x: step, y: 0 },
      ArrowUp: { x: 0, y: -step },
      ArrowDown: { x: 0, y: step },
    };
    const delta = deltaByKey[event.key];
    if (!delta) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    onVertexNudge?.(vertexIndex, delta);
  };

  const minX = Math.min(...points.map((point) => point.x)) - HANDLE_SIZE;
  const minY = Math.min(...points.map((point) => point.y)) - HANDLE_SIZE;
  const maxX = Math.max(...points.map((point) => point.x)) + HANDLE_SIZE;
  const maxY = Math.max(...points.map((point) => point.y)) + HANDLE_SIZE;

  return (
    <div
      style={{
        position: "absolute",
        left: minX,
        top: minY,
        width: Math.max(HANDLE_SIZE, maxX - minX),
        height: Math.max(HANDLE_SIZE, maxY - minY),
        pointerEvents: "auto",
        zIndex: 10000,
      }}
    >
      {points.map((point, index) => {
        const displayPoint = getDisplayPoint(point, index);

        return (
          <div
            key={index}
            role="button"
            tabIndex={0}
            aria-label={t("canvas.polygon.vertex_handle", { index: index + 1 })}
            aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Shift+ArrowLeft Shift+ArrowRight Shift+ArrowUp Shift+ArrowDown Delete Backspace"
            title={t("canvas.polygon.vertex_handle_help")}
            onPointerDown={(event) => {
              handlePointerDown(event, index);
            }}
            onPointerMove={handlePointerMove}
            onPointerUp={(event) => {
              clearDrag(event, false);
            }}
            onPointerCancel={(event) => {
              clearDrag(event, true);
            }}
            onKeyDown={(event) => {
              handleKeyDown(event, index);
            }}
            style={{
              position: "absolute",
              left: displayPoint.x - minX - HANDLE_SIZE / 2,
              top: displayPoint.y - minY - HANDLE_SIZE / 2,
              width: HANDLE_SIZE,
              height: HANDLE_SIZE,
              borderRadius: HANDLE_SIZE / 2,
              border: "1px solid #1d4ed8",
              backgroundColor: draggingVertexIndex === index ? "#2563eb" : "#93c5fd",
              boxShadow: "0 0 0 1px #ffffff",
              cursor: draggingVertexIndex === index ? "grabbing" : "grab",
              pointerEvents: "auto",
              zIndex: 1000,
            }}
          />
        );
      })}
    </div>
  );
}
