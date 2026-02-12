import { memo } from "react";

export type SuggestionMoveDiff = {
  cardId: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
};

type SuggestionDiffLayerProps = {
  diffs: SuggestionMoveDiff[];
  cardWidth: number;
  cardHeight: number;
};

function SuggestionDiffLayerComponent({ diffs, cardWidth, cardHeight }: SuggestionDiffLayerProps) {
  if (diffs.length === 0) {
    return null;
  }

  return (
    <div
      aria-hidden="true"
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
      }}
    >
      {diffs.map((diff) => (
        <div
          key={diff.cardId}
          style={{
            position: "absolute",
            left: diff.fromX,
            top: diff.fromY,
            width: cardWidth,
            minHeight: cardHeight,
            borderRadius: 8,
            border: "2px dashed rgba(245, 158, 11, 0.85)",
            backgroundColor: "rgba(245, 158, 11, 0.08)",
            boxSizing: "border-box",
          }}
        />
      ))}
    </div>
  );
}

export const SuggestionDiffLayer = memo(SuggestionDiffLayerComponent);
