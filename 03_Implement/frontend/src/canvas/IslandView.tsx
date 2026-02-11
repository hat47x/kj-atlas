import type { Card, Island } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const ISLAND_PADDING = 24;
const ISLAND_HEADER_HEIGHT = 24;
const ISLAND_TITLE_MARGIN_LEFT = 10;
const ISLAND_TITLE_MARGIN_TOP = 6;

type IslandViewProps = {
  island: Island;
  cards: Card[];
};

function getIslandBounds(island: Island, cards: Card[]) {
  const islandCards = cards.filter((card) => island.cardIds.includes(card.id));
  if (islandCards.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  islandCards.forEach((card) => {
    minX = Math.min(minX, card.x);
    minY = Math.min(minY, card.y);
    maxX = Math.max(maxX, card.x + CARD_WIDTH);
    maxY = Math.max(maxY, card.y + CARD_MIN_HEIGHT);
  });

  return {
    left: minX - ISLAND_PADDING,
    top: minY - ISLAND_PADDING,
    width: maxX - minX + ISLAND_PADDING * 2,
    height: maxY - minY + ISLAND_PADDING * 2,
  };
}

export function IslandView({ island, cards }: IslandViewProps) {
  const bounds = getIslandBounds(island, cards);

  if (!bounds) {
    return null;
  }

  return (
    <div
      style={{
        pointerEvents: "none",
        position: "absolute",
        left: bounds.left,
        top: bounds.top,
        width: bounds.width,
        height: bounds.height,
        border: "2px solid #0ea5e9",
        borderRadius: 12,
        backgroundColor: "rgba(14, 165, 233, 0.05)",
        boxSizing: "border-box",
        overflow: "hidden",
        zIndex: -1,
        isolation: "isolate",
      }}
    >
      {island.imageUrl ? (
        <img
          src={island.imageUrl}
          alt=""
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            objectFit: "cover",
            opacity: 0.18,
            zIndex: 0,
          }}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: "100%",
          height: ISLAND_HEADER_HEIGHT,
          borderBottom: "1px solid #bae6fd",
          backgroundColor: "rgba(240, 249, 255, 0.9)",
          zIndex: 1,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: ISLAND_TITLE_MARGIN_LEFT,
          top: ISLAND_TITLE_MARGIN_TOP,
          fontSize: 12,
          fontWeight: 700,
          color: "#0c4a6e",
          backgroundColor: "#f0f9ff",
          padding: "2px 6px",
          borderRadius: 6,
          border: "1px solid #bae6fd",
          zIndex: 1,
        }}
      >
        {island.title && island.title.length > 0 ? island.title : "Island"}
      </div>
    </div>
  );
}
