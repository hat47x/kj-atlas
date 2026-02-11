import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiError, getDocument, putDocument } from "./api/client";
import { CanvasShell } from "./canvas/CanvasShell";
import { IslandView } from "./canvas/IslandView";
import type { Document, DocumentV2, Island } from "./domain/types";
import { Shell } from "./ui/Shell";

const DOCUMENT_ID = "doc_phase1_canvas";
const HISTORY_LIMIT = 50;

type DocumentHistory = {
  past: DocumentV2[];
  present: DocumentV2;
  future: DocumentV2[];
};

function createDefaultDocument(docId: string): DocumentV2 {
  const now = new Date().toISOString();

  return {
    version: 2,
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
    islands: [],
  };
}

function toDocumentV2(document: Document): DocumentV2 {
  if (document.version === 2) {
    return document;
  }

  return {
    ...document,
    version: 2,
    islands: [],
  };
}

function withUpdatedTimestamp(document: DocumentV2): DocumentV2 {
  return {
    ...document,
    updatedAt: new Date().toISOString(),
  };
}

function cloneDocument(document: DocumentV2): DocumentV2 {
  return structuredClone(document);
}

function pushHistorySnapshot(history: DocumentHistory, nextDocument: DocumentV2): DocumentHistory {
  const nextPast = [...history.past, cloneDocument(history.present)];
  const trimmedPast = nextPast.length > HISTORY_LIMIT ? nextPast.slice(nextPast.length - HISTORY_LIMIT) : nextPast;

  return {
    past: trimmedPast,
    present: cloneDocument(nextDocument),
    future: [],
  };
}

function createIslandFromSelection(selectedCardIds: string[], existingIslands: Island[]): Island {
  return {
    id: crypto.randomUUID(),
    cardIds: selectedCardIds,
    title: `Island ${existingIslands.length + 1}`,
  };
}

export default function App() {
  const [history, setHistory] = useState<DocumentHistory | null>(null);
  const [selectedCardIds, setSelectedCardIds] = useState<string[]>([]);
  const [selectedIslandId, setSelectedIslandId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>("");

  const document = history?.present ?? null;
  const canUndo = (history?.past.length ?? 0) > 0;
  const canRedo = (history?.future.length ?? 0) > 0;
  const pendingCardDragSnapshotRef = useRef<DocumentV2 | null>(null);

  useEffect(() => {
    let isCancelled = false;

    const loadDocument = async () => {
      setIsLoading(true);
      setStatusMessage("Loading document...");

      try {
        const loadedDocument = toDocumentV2(await getDocument(DOCUMENT_ID));
        if (!isCancelled) {
          setHistory({
            past: [],
            present: cloneDocument(loadedDocument),
            future: [],
          });
          setSelectedCardIds([]);
          setSelectedIslandId(null);
          setIsDirty(false);
          pendingCardDragSnapshotRef.current = null;
          setStatusMessage("Document loaded");
        }
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) {
          const defaultDocument = createDefaultDocument(DOCUMENT_ID);

          try {
            const savedDocument = toDocumentV2(await putDocument(DOCUMENT_ID, defaultDocument));
            if (!isCancelled) {
              setHistory({
                past: [],
                present: cloneDocument(savedDocument),
                future: [],
              });
              setSelectedCardIds([]);
              setSelectedIslandId(null);
              setIsDirty(false);
              pendingCardDragSnapshotRef.current = null;
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

  const applyDocumentChange = useCallback((nextDocument: DocumentV2, nextStatusMessage?: string) => {
    pendingCardDragSnapshotRef.current = null;

    setHistory((previousHistory) => {
      if (!previousHistory) {
        return previousHistory;
      }

      return pushHistorySnapshot(previousHistory, nextDocument);
    });
    setIsDirty(true);
    if (nextStatusMessage) {
      setStatusMessage(nextStatusMessage);
    }
  }, []);

  const handleTransformChange = useCallback(
    (nextTransform: DocumentV2["transform"]) => {
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
      setHistory((previousHistory) => {
        if (!previousHistory) {
          return previousHistory;
        }

        return {
          ...previousHistory,
          present: {
            ...previousHistory.present,
            transform: nextTransform,
          },
        };
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

      if (!pendingCardDragSnapshotRef.current) {
        pendingCardDragSnapshotRef.current = cloneDocument(document);
      }

      setIsDirty(true);
      setHistory((previousHistory) => {
        if (!previousHistory) {
          return previousHistory;
        }

        return {
          ...previousHistory,
          present: {
            ...previousHistory.present,
            cards: nextCards,
          },
        };
      });
    },
    [document]
  );


  useEffect(() => {
    const commitCardDragSnapshot = () => {
      const dragSnapshot = pendingCardDragSnapshotRef.current;
      pendingCardDragSnapshotRef.current = null;

      if (!dragSnapshot) {
        return;
      }

      setHistory((previousHistory) => {
        if (!previousHistory) {
          return previousHistory;
        }

        const nextPast = [...previousHistory.past, dragSnapshot];
        const trimmedPast =
          nextPast.length > HISTORY_LIMIT ? nextPast.slice(nextPast.length - HISTORY_LIMIT) : nextPast;

        return {
          past: trimmedPast,
          present: cloneDocument(previousHistory.present),
          future: [],
        };
      });
      setStatusMessage("Moved card");
    };

    window.addEventListener("pointerup", commitCardDragSnapshot);
    window.addEventListener("pointercancel", commitCardDragSnapshot);

    return () => {
      window.removeEventListener("pointerup", commitCardDragSnapshot);
      window.removeEventListener("pointercancel", commitCardDragSnapshot);
    };
  }, []);

  const handleSave = async () => {
    if (!document || isSaving || !isDirty) {
      return;
    }

    setIsSaving(true);
    setStatusMessage("Saving...");

    try {
      const savedDocument = toDocumentV2(await putDocument(document.id, withUpdatedTimestamp(document)));
      pendingCardDragSnapshotRef.current = null;
      setHistory({
        past: [],
        present: cloneDocument(savedDocument),
        future: [],
      });
      setIsDirty(false);
      setStatusMessage("Saved");
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Failed to save document");
    } finally {
      setIsSaving(false);
    }
  };

  const handleCardSelect = useCallback((cardId: string, isShiftPressed: boolean) => {
    setSelectedCardIds((previousSelectedCardIds) => {
      if (isShiftPressed) {
        const isAlreadySelected = previousSelectedCardIds.includes(cardId);
        if (isAlreadySelected) {
          return previousSelectedCardIds.filter((selectedCardId) => selectedCardId !== cardId);
        }

        return [...previousSelectedCardIds, cardId];
      }

      if (previousSelectedCardIds.length === 1 && previousSelectedCardIds[0] === cardId) {
        return previousSelectedCardIds;
      }

      return [cardId];
    });
  }, []);

  const handleCanvasBackgroundClick = useCallback(() => {
    setSelectedCardIds((previousSelectedCardIds) => {
      if (previousSelectedCardIds.length === 0) {
        return previousSelectedCardIds;
      }

      return [];
    });
  }, []);

  const handleMarqueeSelect = useCallback((cardIds: string[], isShiftPressed: boolean) => {
    setSelectedCardIds((previousSelectedCardIds) => {
      const uniqueCardIds = Array.from(new Set(cardIds));

      if (isShiftPressed) {
        return Array.from(new Set([...previousSelectedCardIds, ...uniqueCardIds]));
      }

      if (
        previousSelectedCardIds.length === uniqueCardIds.length &&
        previousSelectedCardIds.every((id, index) => id === uniqueCardIds[index])
      ) {
        return previousSelectedCardIds;
      }

      return uniqueCardIds;
    });
  }, []);

  const canCreateIsland = selectedCardIds.length > 0;

  const handleCreateIsland = useCallback(() => {
    if (!document || selectedCardIds.length === 0) {
      return;
    }

    const uniqueSelectedCardIds = Array.from(new Set(selectedCardIds));

    const newIsland = createIslandFromSelection(uniqueSelectedCardIds, document.islands);

    applyDocumentChange({
      ...document,
      islands: [...document.islands, newIsland],
    });
    setSelectedIslandId(newIsland.id);
    setStatusMessage(`Created island from ${selectedCardIds.length} selected card(s)`);
  }, [applyDocumentChange, document, selectedCardIds]);

  const handleIslandTitleChange = useCallback(
    (islandId: string, rawTitle: string) => {
      if (!document) {
        return;
      }

      const nextTitle = rawTitle.trim().length > 0 ? rawTitle : undefined;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.title ?? undefined) === nextTitle) {
          return island;
        }

        return {
          ...island,
          title: nextTitle,
        };
      });

      const hasChanges = nextIslands.some((island, index) => island !== document.islands[index]);
      if (!hasChanges) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          islands: nextIslands,
        },
        "Updated island title"
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandImageUrlChange = useCallback(
    (islandId: string, rawImageUrl: string) => {
      if (!document) {
        return;
      }

      const nextImageUrl = rawImageUrl.length > 0 ? rawImageUrl : undefined;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.imageUrl ?? undefined) === nextImageUrl) {
          return island;
        }

        return {
          ...island,
          imageUrl: nextImageUrl,
        };
      });

      const hasChanges = nextIslands.some((island, index) => island !== document.islands[index]);
      if (!hasChanges) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          islands: nextIslands,
        },
        "Updated island image URL"
      );
    },
    [applyDocumentChange, document]
  );

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const usesShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "g";
      if (!usesShortcut || !canCreateIsland) {
        return;
      }

      event.preventDefault();
      handleCreateIsland();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [canCreateIsland, handleCreateIsland]);

  const handleUndo = useCallback(() => {
    pendingCardDragSnapshotRef.current = null;

    setHistory((previousHistory) => {
      if (!previousHistory || previousHistory.past.length === 0) {
        return previousHistory;
      }

      const previousDocument = previousHistory.past[previousHistory.past.length - 1];
      return {
        past: previousHistory.past.slice(0, -1),
        present: cloneDocument(previousDocument),
        future: [cloneDocument(previousHistory.present), ...previousHistory.future],
      };
    });
    setIsDirty(true);
    setStatusMessage("Undo");
  }, []);

  const handleRedo = useCallback(() => {
    pendingCardDragSnapshotRef.current = null;

    setHistory((previousHistory) => {
      if (!previousHistory || previousHistory.future.length === 0) {
        return previousHistory;
      }

      const [nextDocument, ...remainingFuture] = previousHistory.future;
      const nextPast = [...previousHistory.past, cloneDocument(previousHistory.present)];
      const trimmedPast =
        nextPast.length > HISTORY_LIMIT ? nextPast.slice(nextPast.length - HISTORY_LIMIT) : nextPast;

      return {
        past: trimmedPast,
        present: cloneDocument(nextDocument),
        future: remainingFuture,
      };
    });
    setIsDirty(true);
    setStatusMessage("Redo");
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isModifierPressed = event.metaKey || event.ctrlKey;
      if (!isModifierPressed) {
        return;
      }

      const lowerKey = event.key.toLowerCase();

      const wantsUndo = lowerKey === "z" && !event.shiftKey;
      if (wantsUndo && canUndo) {
        event.preventDefault();
        handleUndo();
        return;
      }

      const wantsRedo = lowerKey === "y" || (lowerKey === "z" && event.shiftKey);
      if (wantsRedo && canRedo) {
        event.preventDefault();
        handleRedo();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [canRedo, canUndo, handleRedo, handleUndo]);

  const uniqueIslands = useMemo(
    () =>
      (document?.islands ?? []).map((island) => ({
        ...island,
        cardIds: Array.from(new Set(island.cardIds)),
      })),
    [document]
  );

  useEffect(() => {
    if (uniqueIslands.length === 0) {
      setSelectedIslandId(null);
      return;
    }

    if (!selectedIslandId || !uniqueIslands.some((island) => island.id === selectedIslandId)) {
      setSelectedIslandId(uniqueIslands[0].id);
    }
  }, [selectedIslandId, uniqueIslands]);

  const selectedIsland = useMemo(
    () => uniqueIslands.find((island) => island.id === selectedIslandId) ?? null,
    [selectedIslandId, uniqueIslands]
  );

  const headerRight = (
    <div style={{ display: "flex", gap: 8 }}>
      <button
        type="button"
        onClick={handleUndo}
        disabled={isLoading || !document || !canUndo}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || !document || !canUndo ? "not-allowed" : "pointer",
        }}
      >
        Undo
      </button>
      <button
        type="button"
        onClick={handleRedo}
        disabled={isLoading || !document || !canRedo}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || !document || !canRedo ? "not-allowed" : "pointer",
        }}
      >
        Redo
      </button>
      <button
        type="button"
        onClick={handleCreateIsland}
        disabled={isLoading || !document || !canCreateIsland}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || !document || !canCreateIsland ? "not-allowed" : "pointer",
        }}
      >
        Create Island
      </button>
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
    </div>
  );

  return (
    <Shell title="kj-atlas Canvas MVP" headerRight={headerRight} hasUnsavedChanges={isDirty}>
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
        <>
          <CanvasShell
            document={document}
            onCardMove={handleCardMove}
            onTransformChange={handleTransformChange}
            selectedCardIds={selectedCardIds}
            onCardSelect={handleCardSelect}
            onCanvasBackgroundClick={handleCanvasBackgroundClick}
            onMarqueeSelect={handleMarqueeSelect}
          >
            {uniqueIslands.map((island) => (
              <IslandView key={island.id} island={island} cards={document.cards} />
            ))}
          </CanvasShell>
          <div
            style={{
              position: "absolute",
              top: 16,
              right: 16,
              width: 280,
              border: "1px solid #cbd5e1",
              borderRadius: 8,
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              padding: 12,
              boxShadow: "0 6px 18px rgba(15, 23, 42, 0.12)",
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, marginBottom: 8, color: "#334155" }}>
              Island Image
            </div>
            {uniqueIslands.length === 0 ? (
              <div style={{ fontSize: 12, color: "#64748b" }}>Create an island to attach an image.</div>
            ) : (
              <>
                <select
                  value={selectedIslandId ?? ""}
                  onChange={(event) => {
                    setSelectedIslandId(event.target.value);
                  }}
                  style={{
                    width: "100%",
                    marginBottom: 8,
                    border: "1px solid #cbd5e1",
                    borderRadius: 6,
                    padding: "6px 8px",
                  }}
                >
                  {uniqueIslands.map((island) => (
                    <option key={island.id} value={island.id}>
                      {island.title && island.title.length > 0 ? island.title : "Island"}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder="Island title"
                  value={selectedIsland?.title ?? ""}
                  onChange={(event) => {
                    if (!selectedIsland) {
                      return;
                    }

                    handleIslandTitleChange(selectedIsland.id, event.target.value);
                  }}
                  style={{
                    width: "100%",
                    border: "1px solid #cbd5e1",
                    borderRadius: 6,
                    padding: "6px 8px",
                    boxSizing: "border-box",
                    marginBottom: 8,
                  }}
                />
                <input
                  type="url"
                  placeholder="https://example.com/image.jpg"
                  value={selectedIsland?.imageUrl ?? ""}
                  onChange={(event) => {
                    if (!selectedIsland) {
                      return;
                    }

                    handleIslandImageUrlChange(selectedIsland.id, event.target.value);
                  }}
                  style={{
                    width: "100%",
                    border: "1px solid #cbd5e1",
                    borderRadius: 6,
                    padding: "6px 8px",
                    boxSizing: "border-box",
                    marginBottom: 8,
                  }}
                />
                <div
                  style={{
                    height: 120,
                    borderRadius: 6,
                    border: "1px solid #e2e8f0",
                    overflow: "hidden",
                    backgroundColor: "#f8fafc",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#94a3b8",
                    fontSize: 12,
                  }}
                >
                  {selectedIsland?.imageUrl ? (
                    <img
                      src={selectedIsland.imageUrl}
                      alt="Island preview"
                      style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    />
                  ) : (
                    "No image"
                  )}
                </div>
              </>
            )}
          </div>
        </>
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
