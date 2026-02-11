import { useCallback, useEffect, useState } from "react";

import { ApiError, getDocument, putDocument } from "./api/client";
import { CanvasShell } from "./canvas/CanvasShell";
import type { DocumentV1 } from "./domain/types";
import { Shell } from "./ui/Shell";

const DOCUMENT_ID = "doc_phase1_canvas";

function createDefaultDocument(docId: string): DocumentV1 {
  const now = new Date().toISOString();

  return {
    version: 1,
    id: docId,
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

function withUpdatedTimestamp(document: DocumentV1): DocumentV1 {
  return {
    ...document,
    updatedAt: new Date().toISOString(),
  };
}

export default function App() {
  const [document, setDocument] = useState<DocumentV1 | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>("");

  useEffect(() => {
    let isCancelled = false;

    const loadDocument = async () => {
      setIsLoading(true);
      setStatusMessage("Loading document...");

      try {
        const loadedDocument = await getDocument(DOCUMENT_ID);
        if (!isCancelled) {
          setDocument(loadedDocument);
          setIsDirty(false);
          setStatusMessage("Document loaded");
        }
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          const defaultDocument = createDefaultDocument(DOCUMENT_ID);

          try {
            const savedDocument = await putDocument(DOCUMENT_ID, defaultDocument);
            if (!isCancelled) {
              setDocument(savedDocument);
              setIsDirty(false);
              setStatusMessage("Created a new document");
            }
          } catch (saveError) {
            if (!isCancelled) {
              setStatusMessage(
                saveError instanceof Error ? saveError.message : "Failed to create document"
              );
            }
          }
        } else if (!isCancelled) {
          setStatusMessage(error instanceof Error ? error.message : "Failed to load document");
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadDocument();

    return () => {
      isCancelled = true;
    };
  }, []);

  const handleTransformChange = useCallback(
    (nextTransform: DocumentV1["transform"]) => {
      if (!document) {
        return;
      }

      const current = document.transform;
      if (
        current.panX === nextTransform.panX &&
        current.panY === nextTransform.panY &&
        current.zoom === nextTransform.zoom
      ) {
        return;
      }

      setIsDirty(true);
      setDocument({
        ...document,
        transform: nextTransform,
      });
    },
    [document]
  );

  const handleCardMove = useCallback(
    (cardId: string, deltaWorldX: number, deltaWorldY: number) => {
      if (!document || (deltaWorldX === 0 && deltaWorldY === 0)) {
        return;
      }

      const nextCards = document.cards.map((card) =>
        card.id === cardId
          ? {
              ...card,
              x: card.x + deltaWorldX,
              y: card.y + deltaWorldY,
            }
          : card
      );

      const didMove = nextCards.some((card, index) => card !== document.cards[index]);
      if (!didMove) {
        return;
      }

      setIsDirty(true);
      setDocument({
        ...document,
        cards: nextCards,
      });
    },
    [document]
  );

  const handleSave = async () => {
    if (!document || isSaving || !isDirty) {
      return;
    }

    setIsSaving(true);
    setStatusMessage("Saving...");

    try {
      const savedDocument = await putDocument(document.id, withUpdatedTimestamp(document));
      setDocument(savedDocument);
      setIsDirty(false);
      setStatusMessage("Saved");
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Failed to save document");
    } finally {
      setIsSaving(false);
    }
  };

  const saveButton = (
    <button
      type="button"
      onClick={() => {
        void handleSave();
      }}
      disabled={isLoading || !document || isSaving || !isDirty}
      style={{
        border: "1px solid #cbd5e1",
        backgroundColor: isSaving ? "#f8fafc" : "#ffffff",
        color: "#0f172a",
        borderRadius: 6,
        padding: "6px 12px",
        fontWeight: 600,
        cursor: isLoading || !document || isSaving || !isDirty ? "not-allowed" : "pointer",
      }}
    >
      {isSaving ? "Saving..." : "Save"}
    </button>
  );

  return (
    <Shell title="kj-atlas Canvas MVP" headerRight={saveButton} hasUnsavedChanges={isDirty}>
      {isLoading || !document ? (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            height: "100%",
            color: "#334155",
          }}
        >
          Loading canvas...
        </div>
      ) : (
        <CanvasShell
          document={document}
          onCardMove={handleCardMove}
          onTransformChange={handleTransformChange}
        />
      )}
      <div
        style={{
          position: "absolute",
          right: 16,
          bottom: 16,
          backgroundColor: "rgba(15, 23, 42, 0.85)",
          color: "#f8fafc",
          padding: "6px 10px",
          borderRadius: 6,
          fontSize: 12,
        }}
      >
        {statusMessage}
      </div>
    </Shell>
  );
}
