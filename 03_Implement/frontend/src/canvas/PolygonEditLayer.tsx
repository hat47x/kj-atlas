import { useRef, useState, type PointerEvent } from "react";

import type { Point } from "../domain/types";

type PolygonEditLayerProps = {
  points: Point[];
  onVertexMove: (vertexIndex: number, point: Point) => void;
};

type DragState = {
  pointerId: number;
  vertexIndex: number;
};

const HANDLE_SIZE = 10;

export function PolygonEditLayer({ points, onVertexMove }: PolygonEditLayerProps) {
  const [draggingVertexIndex, setDraggingVertexIndex] = useState<number | null>(null);
  const dragStateRef = useRef<DragState | null>(null);

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>, vertexIndex: number) => {
    event.preventDefault();
    event.stopPropagation();
    event.currentTarget.setPointerCapture(event.pointerId);
    dragStateRef.current = {
      pointerId: event.pointerId,
      vertexIndex,
    };
    setDraggingVertexIndex(vertexIndex);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const dragState = dragStateRef.current;
    if (!dragState || dragState.pointerId !== event.pointerId) {
      return;
    }

    event.preventDefault();
    event.stopPropagation();
    onVertexMove(dragState.vertexIndex, { x: event.clientX, y: event.clientY });
  };

  const clearDrag = (event: PointerEvent<HTMLDivElement>) => {
    const dragState = dragStateRef.current;
    if (!dragState || dragState.pointerId !== event.pointerId) {
      return;
    }

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    event.preventDefault();
    event.stopPropagation();
    dragStateRef.current = null;
    setDraggingVertexIndex(null);
  };

  return (
    <>
      {points.map((point, index) => (
        <div
          key={index}
          role="button"
          aria-label={`Move polygon vertex ${index + 1}`}
          onPointerDown={(event) => {
            handlePointerDown(event, index);
          }}
          onPointerMove={handlePointerMove}
          onPointerUp={clearDrag}
          onPointerCancel={clearDrag}
          style={{
            position: "absolute",
            left: point.x - HANDLE_SIZE / 2,
            top: point.y - HANDLE_SIZE / 2,
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
      ))}
    </>
  );
}
