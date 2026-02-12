import { memo } from "react";
import type { CSSProperties, KeyboardEvent } from "react";

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
  isSelected: boolean;
  onSelect: (islandId: string) => void;
  isPickingEdgeTarget?: boolean;
  zIndex?: number;
};

type EdgeHitbox = {
  key: string;
  style: CSSProperties;
};

const EDGE_HITBOXES: EdgeHitbox[] = [
  {
    key: "top",
    style: {
      left: 0,
      top: 0,
      width: "100%",
      height: 8,
    },
  },
  {
    key: "right",
    style: {
      right: 0,
      top: 0,
      width: 8,
      height: "100%",
    },
  },
  {
    key: "bottom",
    style: {
      left: 0,
      bottom: 0,
      width: "100%",
      height: 8,
    },
  },
  {
    key: "left",
    style: {
      left: 0,
      top: 0,
      width: 8,
      height: "100%",
    },
  },
];

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

function handleTitleKeyDown(event: KeyboardEvent<HTMLDivElement>, onSelect: () => void) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    onSelect();
  }
}

function IslandViewComponent({
  island,
  cards,
  isSelected,
  onSelect,
  isPickingEdgeTarget = false,
  zIndex = 0,
}: IslandViewProps) {
  const bounds = getIslandBounds(island, cards);
  const hasCritique = typeof island.critique === "string" && island.critique.trim().length > 0;
  const islandBackgroundImage = island.imageUrl
    ? `url("${encodeURI(island.imageUrl)}")`
    : null;

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
        borderRadius: 12,
        boxSizing: "border-box",
        overflow: "hidden",
        zIndex,
        isolation: "isolate",
      }}
    >
      {EDGE_HITBOXES.map((edgeHitbox) => (
        <button
          key={edgeHitbox.key}
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            if (!isPickingEdgeTarget) onSelect(island.id);
          }}
          style={{
            pointerEvents: isPickingEdgeTarget ? "none" : "auto",
            position: "absolute",
            ...edgeHitbox.style,
            border: "none",
            backgroundColor: "transparent",
            padding: 0,
            cursor: isPickingEdgeTarget ? "default" : "pointer",
            zIndex: 2,
          }}
          aria-label={`Select island ${island.id}`}
        />
      ))}
      {islandBackgroundImage ? (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: islandBackgroundImage,
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            opacity: 0.15,
            zIndex: 0,
          }}
        />
      ) : null}
      <div
        style={{
          position: "absolute",
          inset: 0,
          border: isSelected ? "2px solid #0284c7" : "2px solid #0ea5e9",
          borderRadius: 12,
          backgroundColor: isSelected ? "rgba(14, 165, 233, 0.12)" : "rgba(14, 165, 233, 0.05)",
          boxSizing: "border-box",
          zIndex: 1,
        }}
      />
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
        role="button"
        tabIndex={isPickingEdgeTarget ? -1 : 0}
        onClick={(event) => {
          event.stopPropagation();
          if (!isPickingEdgeTarget) onSelect(island.id);
        }}
        onKeyDown={(event) => {
          handleTitleKeyDown(event, () => {
            if (!isPickingEdgeTarget) onSelect(island.id);
          });
        }}
        style={{
          pointerEvents: isPickingEdgeTarget ? "none" : "auto",
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
          zIndex: 3,
          cursor: isPickingEdgeTarget ? "default" : "pointer",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        {island.title && island.title.length > 0 ? island.title : "Island"}
        {hasCritique ? (
          <span
            aria-label="Island has critique note"
            title="Island has critique note"
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#f59e0b",
            }}
          />
        ) : null}
      </div>
    </div>
  );
}

export const IslandView = memo(IslandViewComponent);
