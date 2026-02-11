import { useState } from "react";

import { CanvasShell } from "./canvas/CanvasShell";
import type { DocumentV1 } from "./domain/types";
import { Shell } from "./ui/Shell";

function createInitialDocument(): DocumentV1 {
  const now = new Date().toISOString();

  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Phase 1 Canvas Sample",
    createdAt: now,
    updatedAt: now,
    transform: {
      panX: 0,
      panY: 0,
      zoom: 1,
    },
    cards: [
      {
        id: "card_1",
        text: "ユーザー課題を集める",
        x: 80,
        y: 60,
      },
      {
        id: "card_2",
        text: "観察メモをカード化する",
        x: 380,
        y: 180,
      },
      {
        id: "card_3",
        text: "似ている内容を近くに置く",
        x: 220,
        y: 360,
      },
    ],
    edges: [],
  };
}

export default function App() {
  const [document, setDocument] = useState<DocumentV1>(() => createInitialDocument());

  const handleCardMove = (cardId: string, deltaWorldX: number, deltaWorldY: number) => {
    if (deltaWorldX === 0 && deltaWorldY === 0) {
      return;
    }

    setDocument((prev) => ({
      ...prev,
      cards: prev.cards.map((card) =>
        card.id === cardId
          ? {
              ...card,
              x: card.x + deltaWorldX,
              y: card.y + deltaWorldY,
            }
          : card
      ),
    }));
  };

  return (
    <Shell title="kj-atlas Canvas MVP">
      <CanvasShell document={document} onCardMove={handleCardMove} />
    </Shell>
  );
}
