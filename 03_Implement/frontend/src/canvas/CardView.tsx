import type { Card } from "../domain/types";

type CardViewProps = {
  card: Card;
};

export function CardView({ card }: CardViewProps) {
  return (
    <div
      style={{
        position: "absolute",
        left: card.x,
        top: card.y,
        width: 220,
        minHeight: 80,
        padding: 12,
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        backgroundColor: "#ffffff",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.08)",
        color: "#0f172a",
        lineHeight: 1.4,
        whiteSpace: "pre-wrap",
      }}
    >
      {card.text}
    </div>
  );
}
