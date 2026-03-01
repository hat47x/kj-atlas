import { useRef, useState, type PointerEvent } from "react";

import type { Point } from "../domain/types";

type PolygonEditLayerProps = {
  points: Point[];
  onVertexDragStart?: (vertexIndex: number) => void;
  onVertexDragMove?: (vertexIndex: number, point: Point) => void;
  onVertexDragCommit: (vertexIndex: number, point: Point) => void;
  onVertexDragCancel?: (vertexIndex: number) => void;
  onVertexRemove: (vertexIndex: number) => void;
};

type DragState = {
  pointerId: number;
  vertexIndex: number;
};

const HANDLE_SIZE = 10;

export function PolygonEditLayer({
  points,
  onVertexDragStart,
  onVertexDragMove,
  onVertexDragCommit,
  onVertexDragCancel,
  onVertexRemove,
}: PolygonEditLayerProps) {
  const [draggingVertexIndex, setDraggingVertexIndex] = useState<number | null>(null);
  const [dragPreviewPoint, setDragPreviewPoint] = useState<Point | null>(null);
  const dragStateRef = useRef<DragState | null>(null);

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
    setDraggingVertexIndex(vertexIndex);
    setDragPreviewPoint(points[vertexIndex] ?? null);
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
    const commitPoint = dragPreviewPoint;
    dragStateRef.current = null;
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

  return (
    <>
      {points.map((point, index) => {
        const displayPoint = getDisplayPoint(point, index);

        return (
          <div
            key={index}
            role="button"
            aria-label={`Move polygon vertex ${index + 1}`}
            title="Drag to move / Alt+Click to remove"
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
            style={{
              position: "absolute",
              left: displayPoint.x - HANDLE_SIZE / 2,
              top: displayPoint.y - HANDLE_SIZE / 2,
              width: HANDLE_SIZE,
              height: HANDLE_SIZE,
              borderRadius: HANDLE_SIZE / 2,
              border: "1px solid #1d4ed8",
              backgroundColor: draggingVertexIndex === index ? "#2563eb" : "#93c5fd",
              boxShadow: "0 0 0 1px #ffffff",
              cursor: draggingVertexIndex === index ? "grabbing" : "grab",
              zIndex: 1000,
            }}
          />
        );
      })}
    </>
  );
}
