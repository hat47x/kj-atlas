import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent } from "react";

import { ApiError, getDocument, putDocument, suggestLayout, suggestMerges } from "./api/client";
import { CanvasShell } from "./canvas/CanvasShell";
import { IslandView } from "./canvas/IslandView";
import { alignSelectedCards, distributeSelectedCards, snapValueToGrid } from "./domain/layout_ops";
import type { AlignDirection, DistributeDirection } from "./domain/layout_ops";
import type { Document, DocumentV2, Island } from "./domain/types";
import { validateAndUpgradeImportedDocument } from "./domain/validate";
import { useHotkeys } from "./hooks/useHotkeys";
import { Shell } from "./ui/Shell";
import { SidePanel } from "./ui/SidePanel";
import { SuggestionPanel } from "./ui/SuggestionPanel";
import { SearchBar } from "./ui/SearchBar";
import { MergeSuggestionsPanel } from "./ui/MergeSuggestionsPanel";
import type { SuggestionMoveDiff } from "./canvas/SuggestionDiffLayer";
import { loadRecentDocumentIds, pushRecentDocumentId } from "./storage/recent";

const DEFAULT_DOCUMENT_ID = "doc_phase1_canvas";
const HISTORY_LIMIT = 50;
const GRID_SNAP_SIZE = 10;
const SUGGESTION_MOVE_THRESHOLD = 1;

type DocumentHistory = {
  past: DocumentV2[];
  present: DocumentV2;
  future: DocumentV2[];
};

type MergeSuggestionDraft = {
  groupId: string;
  cardIds: string[];
  mergedTextDraft: string;
  rationale?: string;
  editedText: string;
  isEdited: boolean;
};

type EdgeEndpointKind = "card" | "island";

type EdgeConnectSource = {
  id: string;
  kind: EdgeEndpointKind;
};

type FocusTarget = {
  focusIslandId?: string;
};

type ViewMaxDepth = number | "all";

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
    readingOrder: [],
  };
}

function createNewDocument(docId: string): DocumentV2 {
  const now = new Date().toISOString();

  return {
    version: 2,
    id: docId,
    title: "Untitled",
    createdAt: now,
    updatedAt: now,
    transform: {
      panX: 0,
      panY: 0,
      zoom: 1,
    },
    cards: [
      {
        id: crypto.randomUUID(),
        text: "新しいカード",
        x: 120,
        y: 120,
      },
    ],
    edges: [],
    islands: [],
  };
}

function duplicateDocumentWithNewId(sourceDocument: DocumentV2): DocumentV2 {
  const now = new Date().toISOString();

  return {
    ...cloneDocument(sourceDocument),
    id: crypto.randomUUID(),
    createdAt: now,
    updatedAt: now,
  };
}

function toDocumentV2(document: Document): DocumentV2 {
  if (document.version === 2) {
    return {
      ...document,
      readingOrder: document.readingOrder ?? [],
    };
  }

  return {
    ...document,
    version: 2,
    islands: [],
    readingOrder: [],
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

function markSuggestedFieldsUnreviewed(document: DocumentV2, baseDocument: DocumentV2): DocumentV2 {
  const baseCardsById = new Map(baseDocument.cards.map((card) => [card.id, card]));
  const baseIslandsById = new Map(baseDocument.islands.map((island) => [island.id, island]));

  return {
    ...document,
    cards: document.cards.map((card) => ({
      ...card,
      textReviewed:
        !baseCardsById.has(card.id) || baseCardsById.get(card.id)?.text !== card.text
          ? false
          : baseCardsById.get(card.id)?.textReviewed,
    })),
    islands: document.islands.map((island) => ({
      ...island,
      titleReviewed:
        !baseIslandsById.has(island.id) || baseIslandsById.get(island.id)?.title !== island.title
          ? false
          : baseIslandsById.get(island.id)?.titleReviewed,
      imageReviewed:
        !baseIslandsById.has(island.id) || baseIslandsById.get(island.id)?.imageUrl !== island.imageUrl
          ? false
          : baseIslandsById.get(island.id)?.imageReviewed,
      summaryReviewed:
        !baseIslandsById.has(island.id) || baseIslandsById.get(island.id)?.summaryText !== island.summaryText
          ? false
          : baseIslandsById.get(island.id)?.summaryReviewed,
    })),
  };
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
    collapsed: false,
    title: `Island ${existingIslands.length + 1}`,
  };
}


function collectCollapsedIslandIds(islands: Island[]): Set<string> {
  const islandsByParentId = new Map<string, Island[]>();

  for (const island of islands) {
    if (!island.parentIslandId) {
      continue;
    }

    const siblings = islandsByParentId.get(island.parentIslandId) ?? [];
    siblings.push(island);
    islandsByParentId.set(island.parentIslandId, siblings);
  }

  const hiddenIslandIds = new Set<string>();
  const stack = islands.filter((island) => island.collapsed === true);

  while (stack.length > 0) {
    const current = stack.pop();
    if (!current || hiddenIslandIds.has(current.id)) {
      continue;
    }

    hiddenIslandIds.add(current.id);

    const children = islandsByParentId.get(current.id) ?? [];
    for (const child of children) {
      stack.push(child);
    }
  }

  return hiddenIslandIds;
}

function getIslandDepth(island: Island, islandsById: Map<string, Island>): number {
  let depth = 0;
  let cursor = island;
  const visited = new Set<string>([island.id]);

  while (cursor.parentIslandId) {
    const parent = islandsById.get(cursor.parentIslandId);
    if (!parent || visited.has(parent.id)) {
      break;
    }

    depth += 1;
    cursor = parent;
    visited.add(parent.id);
  }

  return depth;
}

function getIslandDepthMap(islands: Island[]): Map<string, number> {
  const islandsById = new Map(islands.map((island) => [island.id, island]));
  return new Map(islands.map((island) => [island.id, getIslandDepth(island, islandsById)]));
}

function getCardMinDepthMap(document: DocumentV2, islandDepthById: Map<string, number>): Map<string, number> {
  const cardDepthById = new Map<string, number>();

  for (const island of document.islands) {
    const islandDepth = islandDepthById.get(island.id) ?? 0;
    for (const cardId of island.cardIds) {
      const currentDepth = cardDepthById.get(cardId);
      if (currentDepth === undefined || islandDepth < currentDepth) {
        cardDepthById.set(cardId, islandDepth);
      }
    }
  }

  for (const card of document.cards) {
    if (cardDepthById.has(card.id)) {
      continue;
    }

    // Lone-wolf cards (not contained in any island) are treated as depth=0.
    cardDepthById.set(card.id, 0);
  }

  return cardDepthById;
}

export default function App() {
  const [history, setHistory] = useState<DocumentHistory | null>(null);
  const [selectedCardIds, setSelectedCardIds] = useState<string[]>([]);
  const [selectedIslandId, setSelectedIslandId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isReloadingDocument, setIsReloadingDocument] = useState(false);
  const [isDirty, setIsDirty] = useState(false);
  const [docEtag, setDocEtag] = useState<string | null>(null);
  const [hasSaveConflict, setHasSaveConflict] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string>("");
  const [activeDocumentId, setActiveDocumentId] = useState(DEFAULT_DOCUMENT_ID);
  const [recentDocumentIds, setRecentDocumentIds] = useState<string[]>(() => loadRecentDocumentIds());
  const [selectedRecentDocumentId, setSelectedRecentDocumentId] = useState("");
  const [suggestionInstruction, setSuggestionInstruction] = useState("");
  const [suggestedDocument, setSuggestedDocument] = useState<DocumentV2 | null>(null);
  const [suggestionId, setSuggestionId] = useState<string | null>(null);
  const [suggestionNotes, setSuggestionNotes] = useState<string | null>(null);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [isSuggesting, setIsSuggesting] = useState(false);
  const [isSuggestionPreviewEnabled, setIsSuggestionPreviewEnabled] = useState(true);
  const [isAnnotateOverlayEnabled, setIsAnnotateOverlayEnabled] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0);
  const [hideNonMatches, setHideNonMatches] = useState(false);
  const [hideSourceCards, setHideSourceCards] = useState(false);
  const [showCanonicalOnlyEdges, setShowCanonicalOnlyEdges] = useState(false);
  const [focusCardId, setFocusCardId] = useState<string | null>(null);
  const [focusTarget, setFocusTarget] = useState<FocusTarget>({});
  const [focusWorldPoint, setFocusWorldPoint] = useState<{ x: number; y: number } | null>(null);
  const [focusRequestSeq, setFocusRequestSeq] = useState(0);
  const [peekIslandId, setPeekIslandId] = useState<string | undefined>(undefined);
  const [isGridSnapEnabled, setIsGridSnapEnabled] = useState(false);
  const [mergeSuggestionInstruction, setMergeSuggestionInstruction] = useState("");
  const [mergeSuggestions, setMergeSuggestions] = useState<MergeSuggestionDraft[]>([]);
  const [mergeSuggestionError, setMergeSuggestionError] = useState<string | null>(null);
  const [isSuggestingMerges, setIsSuggestingMerges] = useState(false);
  const [isPickingEdgeTarget, setIsPickingEdgeTarget] = useState(false);
  const [connectEdgeType, setConnectEdgeType] = useState<"related" | "negate">("related");
  const [maxDepth, setMaxDepth] = useState<ViewMaxDepth>("all");

  const document = history?.present ?? null;
  const isPreviewingSuggestion = Boolean(suggestedDocument) && isSuggestionPreviewEnabled;
  const visibleDocument = isPreviewingSuggestion && suggestedDocument ? suggestedDocument : document;
  const focusedVisibleDocument = visibleDocument;
  const suggestionMoveDiffs = useMemo(() => {
    if (!document || !suggestedDocument || !isPreviewingSuggestion) {
      return [] as SuggestionMoveDiff[];
    }

    const baseCardsById = new Map(document.cards.map((card) => [card.id, card]));

    return suggestedDocument.cards
      .map((card) => {
        const baseCard = baseCardsById.get(card.id);
        if (!baseCard) {
          return null;
        }

        const deltaX = card.x - baseCard.x;
        const deltaY = card.y - baseCard.y;

        if (Math.hypot(deltaX, deltaY) <= SUGGESTION_MOVE_THRESHOLD) {
          return null;
        }

        return {
          cardId: card.id,
          fromX: baseCard.x,
          fromY: baseCard.y,
          toX: card.x,
          toY: card.y,
        } satisfies SuggestionMoveDiff;
      })
      .filter((diff): diff is SuggestionMoveDiff => diff !== null);
  }, [document, isPreviewingSuggestion, suggestedDocument]);
  const normalizedSearchQuery = searchQuery.trim().toLowerCase();
  const matchedCardIds = useMemo(() => {
    if (!focusedVisibleDocument || normalizedSearchQuery.length === 0) {
      return [] as string[];
    }

    return focusedVisibleDocument.cards
      .filter((card) => card.text.toLowerCase().includes(normalizedSearchQuery))
      .map((card) => card.id);
  }, [focusedVisibleDocument, normalizedSearchQuery]);
  const matchedCardIdSet = useMemo(() => new Set(matchedCardIds), [matchedCardIds]);
  const activeMatchIndex = matchedCardIds.length > 0 ? ((currentMatchIndex % matchedCardIds.length) + matchedCardIds.length) % matchedCardIds.length : 0;
  const activeMatchedCardId = matchedCardIds.length > 0 ? matchedCardIds[activeMatchIndex] : null;
  const collapsedIslandIdSet = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Set<string>();
    }

    return collectCollapsedIslandIds(focusedVisibleDocument.islands);
  }, [focusedVisibleDocument]);
  const islandDepthById = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Map<string, number>();
    }

    return getIslandDepthMap(focusedVisibleDocument.islands);
  }, [focusedVisibleDocument]);
  const cardMinDepthById = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Map<string, number>();
    }

    return getCardMinDepthMap(focusedVisibleDocument, islandDepthById);
  }, [focusedVisibleDocument, islandDepthById]);
  const depthHiddenIslandIdSet = useMemo(() => {
    if (!focusedVisibleDocument || maxDepth === "all") {
      return new Set<string>();
    }

    return new Set(
      focusedVisibleDocument.islands
        .filter((island) => (islandDepthById.get(island.id) ?? 0) > maxDepth)
        .map((island) => island.id)
    );
  }, [focusedVisibleDocument, islandDepthById, maxDepth]);
  const hiddenCardIdSet = useMemo(() => {
    const collapsedHiddenCardIds = new Set<string>();
    const depthHiddenCardIds = new Set<string>();
    const searchHiddenCardIds = new Set<string>();

    if (focusedVisibleDocument) {
      // 1) collapseで隠れるカード
      for (const island of focusedVisibleDocument.islands) {
        if (!collapsedIslandIdSet.has(island.id)) {
          continue;
        }
        for (const cardId of island.cardIds) {
          collapsedHiddenCardIds.add(cardId);
        }
      }

      // 2) depth制限で隠れるカード
      if (maxDepth !== "all") {
        for (const card of focusedVisibleDocument.cards) {
          if ((cardMinDepthById.get(card.id) ?? 0) > maxDepth) {
            depthHiddenCardIds.add(card.id);
          }
        }
      }
    }

    // 3) 検索非一致を隠す
    if (hideNonMatches && normalizedSearchQuery.length > 0 && focusedVisibleDocument) {
      for (const card of focusedVisibleDocument.cards) {
        if (!matchedCardIdSet.has(card.id)) {
          searchHiddenCardIds.add(card.id);
        }
      }
    }

    // 4) peek中の島のカードは collapse 隠しから除外
    if (peekIslandId && focusedVisibleDocument) {
      const peekIsland = focusedVisibleDocument.islands.find((island) => island.id === peekIslandId);
      if (peekIsland) {
        for (const cardId of peekIsland.cardIds) {
          collapsedHiddenCardIds.delete(cardId);
        }
      }
    }

    // merge
    const hiddenCardIds = new Set<string>(collapsedHiddenCardIds);
    for (const cardId of depthHiddenCardIds) hiddenCardIds.add(cardId);
    for (const cardId of searchHiddenCardIds) hiddenCardIds.add(cardId);

    return hiddenCardIds;
  }, [
    cardMinDepthById,
    collapsedIslandIdSet,
    focusedVisibleDocument,
    hideNonMatches,
    matchedCardIdSet,
    maxDepth,
    normalizedSearchQuery,
    peekIslandId,
  ]);

  const canUndo = (history?.past.length ?? 0) > 0;
  const canRedo = (history?.future.length ?? 0) > 0;
  const pendingCardDragSnapshotRef = useRef<DocumentV2 | null>(null);
  const suppressNextTransformPersistRef = useRef(false);
  const importInputRef = useRef<HTMLInputElement | null>(null);
  const cardsById = useMemo(() => new Map((document?.cards ?? []).map((card) => [card.id, card])), [document]);

  const rememberRecentDocumentId = useCallback((docId: string) => {
    setRecentDocumentIds(pushRecentDocumentId(docId));
  }, []);

  const loadDocument = useCallback(
    async (docId: string, options?: { allowCreateOnNotFound?: boolean; isReload?: boolean }) => {
      const allowCreateOnNotFound = options?.allowCreateOnNotFound ?? false;
      const isReload = options?.isReload ?? false;
      if (isReload) {
        setIsReloadingDocument(true);
      }
      setIsLoading(true);
      setStatusMessage(isReload ? "Reloading document..." : "Loading document...");

      try {
        const loaded = await getDocument(docId);
        const loadedDocument = toDocumentV2(loaded.document);

        setHistory({
          past: [],
          present: cloneDocument(loadedDocument),
          future: [],
        });
        setActiveDocumentId(loadedDocument.id);
        rememberRecentDocumentId(loadedDocument.id);
        setSelectedRecentDocumentId(loadedDocument.id);
        setDocEtag(loaded.etag ?? null);
        setSelectedCardIds([]);
        setSelectedIslandId(null);
        setIsDirty(false);
        setHasSaveConflict(false);
        setSuggestedDocument(null);
        setSuggestionId(null);
        setSuggestionNotes(null);
        setSuggestionError(null);
        pendingCardDragSnapshotRef.current = null;
        setStatusMessage("Document loaded");
      } catch (error) {
        if (allowCreateOnNotFound && error instanceof ApiError && error.status === 404) {
          const defaultDocument = createDefaultDocument(docId);

          try {
            const saved = await putDocument(docId, defaultDocument);
            const savedDocument = toDocumentV2(saved.document);

            setHistory({
              past: [],
              present: cloneDocument(savedDocument),
              future: [],
            });
            setActiveDocumentId(savedDocument.id);
            rememberRecentDocumentId(savedDocument.id);
            setSelectedRecentDocumentId(savedDocument.id);
            setDocEtag(saved.etag ?? null);
            setSelectedCardIds([]);
            setSelectedIslandId(null);
            setIsDirty(false);
            setHasSaveConflict(false);
            setSuggestedDocument(null);
            setSuggestionId(null);
            setSuggestionNotes(null);
            setSuggestionError(null);
            pendingCardDragSnapshotRef.current = null;
            setStatusMessage("Created a new document");
          } catch (saveError) {
            setStatusMessage(saveError instanceof Error ? saveError.message : "Failed to create document");
          }
        } else {
          if (error instanceof ApiError && error.status === 404) {
            setStatusMessage(`Document ${docId} was not found`);
          } else {
            setStatusMessage(error instanceof Error ? error.message : "Failed to load document");
          }
        }
      } finally {
        setIsLoading(false);
        if (isReload) {
          setIsReloadingDocument(false);
        }
      }
    },
    []
  );

  useEffect(() => {
    let isCancelled = false;

    const loadForMount = async () => {
      if (isCancelled) {
        return;
      }

      await loadDocument(DEFAULT_DOCUMENT_ID, { allowCreateOnNotFound: true });
    };

    void loadForMount();

    return () => {
      isCancelled = true;
    };
  }, [loadDocument]);

  const applyDocumentChange = useCallback(
    (
      nextDocument: DocumentV2,
      nextStatusMessage?: string,
      options?: {
        preserveSuggestionPreview?: boolean;
      }
    ) => {
      pendingCardDragSnapshotRef.current = null;

      setHistory((previousHistory) => {
        if (!previousHistory) {
          return previousHistory;
        }

        return pushHistorySnapshot(previousHistory, nextDocument);
      });
      setIsDirty(true);
      if (!options?.preserveSuggestionPreview) {
        setSuggestedDocument(null);
        setSuggestionId(null);
        setSuggestionNotes(null);
        setSuggestionError(null);
        setIsAnnotateOverlayEnabled(false);
      }
      setMergeSuggestions([]);
      setMergeSuggestionError(null);
      setHasSaveConflict(false);
      if (nextStatusMessage) {
        setStatusMessage(nextStatusMessage);
      }
    },
    []
  );


  useEffect(() => {
    if (matchedCardIds.length === 0) {
      if (currentMatchIndex !== 0) {
        setCurrentMatchIndex(0);
      }
      return;
    }

    if (currentMatchIndex >= matchedCardIds.length) {
      setCurrentMatchIndex(0);
    }
  }, [currentMatchIndex, matchedCardIds]);

  const requestCanvasFocus = useCallback((cardId: string) => {
    setFocusCardId(cardId);
    setFocusRequestSeq((previousSeq) => previousSeq + 1);
  }, []);

  const handleSearchNext = useCallback(() => {
    if (matchedCardIds.length === 0) {
      return;
    }

    const nextIndex = (activeMatchIndex + 1) % matchedCardIds.length;
    const nextCardId = matchedCardIds[nextIndex];
    setCurrentMatchIndex(nextIndex);
    requestCanvasFocus(nextCardId);
  }, [activeMatchIndex, matchedCardIds, requestCanvasFocus]);

  const handleSearchPrev = useCallback(() => {
    if (matchedCardIds.length === 0) {
      return;
    }

    const prevIndex = (activeMatchIndex - 1 + matchedCardIds.length) % matchedCardIds.length;
    const prevCardId = matchedCardIds[prevIndex];
    setCurrentMatchIndex(prevIndex);
    requestCanvasFocus(prevCardId);
  }, [activeMatchIndex, matchedCardIds, requestCanvasFocus]);

  const handleTransformChange = useCallback(
    (nextTransform: DocumentV2["transform"]) => {
      if (!document || isPreviewingSuggestion) {
        return;
      }

      if (suppressNextTransformPersistRef.current) {
        suppressNextTransformPersistRef.current = false;
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
    [document, isPreviewingSuggestion]
  );

  const handleCardMove = useCallback(
    (cardId: string, deltaWorldX: number, deltaWorldY: number) => {
      if (!document || isPreviewingSuggestion || (deltaWorldX === 0 && deltaWorldY === 0)) {
        return;
      }

      const nextCards = document.cards.map((card) => {
        if (card.id !== cardId) {
          return card;
        }

        const nextX = card.x + deltaWorldX;
        const nextY = card.y + deltaWorldY;

        return {
          ...card,
          x: isGridSnapEnabled ? snapValueToGrid(nextX, { gridSize: GRID_SNAP_SIZE }) : nextX,
          y: isGridSnapEnabled ? snapValueToGrid(nextY, { gridSize: GRID_SNAP_SIZE }) : nextY,
        };
      });

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
    [document, isGridSnapEnabled, isPreviewingSuggestion]
  );

  const applyLayoutOperation = useCallback(
    (operationName: string, operation: (cards: DocumentV2["cards"]) => DocumentV2["cards"]) => {
      if (!document || isPreviewingSuggestion) {
        return;
      }

      const nextCards = operation(document.cards);
      if (nextCards === document.cards) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          cards: nextCards,
        },
        operationName
      );
    },
    [applyDocumentChange, document, isPreviewingSuggestion]
  );

  const handleAlign = useCallback(
    (direction: AlignDirection) => {
      applyLayoutOperation(`Aligned ${direction}`, (cards) => alignSelectedCards(cards, selectedCardIds, direction, {}));
    },
    [applyLayoutOperation, selectedCardIds]
  );

  const handleDistribute = useCallback(
    (direction: DistributeDirection) => {
      const status = direction === "horizontal" ? "Distributed horizontally" : "Distributed vertically";
      applyLayoutOperation(status, (cards) => distributeSelectedCards(cards, selectedCardIds, direction, {}));
    },
    [applyLayoutOperation, selectedCardIds]
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
      const saved = await putDocument(document.id, withUpdatedTimestamp(document), docEtag ?? undefined);
      const savedDocument = toDocumentV2(saved.document);
      pendingCardDragSnapshotRef.current = null;
      setHistory({
        past: [],
        present: cloneDocument(savedDocument),
        future: [],
      });
      setActiveDocumentId(savedDocument.id);
      rememberRecentDocumentId(savedDocument.id);
      setSelectedRecentDocumentId(savedDocument.id);
      setDocEtag(saved.etag ?? null);
      setIsDirty(false);
      setHasSaveConflict(false);
      setStatusMessage("Saved");
    } catch (error) {
      if (error instanceof ApiError && error.status === 409) {
        setHasSaveConflict(true);
        setStatusMessage("This document has been updated elsewhere. Please reload or export your changes.");
        return;
      }

      setStatusMessage(error instanceof Error ? error.message : "Failed to save document");
    } finally {
      setIsSaving(false);
    }
  };

  const handleNewDocument = useCallback(() => {
    const newDocId = crypto.randomUUID();
    const newDocument = createNewDocument(newDocId);

    pendingCardDragSnapshotRef.current = null;
    setHistory({
      past: [],
      present: cloneDocument(newDocument),
      future: [],
    });
    setActiveDocumentId(newDocId);
    setSelectedRecentDocumentId("");
    setDocEtag(null);
    setSelectedCardIds([]);
    setSelectedIslandId(null);
    setIsDirty(true);
    setHasSaveConflict(false);
    setSuggestedDocument(null);
    setSuggestionId(null);
    setSuggestionNotes(null);
    setSuggestionError(null);
    setStatusMessage("Created a new local document");
  }, []);

  const handleDuplicateDocument = useCallback(() => {
    if (!document) {
      return;
    }

    const duplicated = duplicateDocumentWithNewId(document);

    pendingCardDragSnapshotRef.current = null;
    setHistory({
      past: [],
      present: cloneDocument(duplicated),
      future: [],
    });
    setActiveDocumentId(duplicated.id);
    setSelectedRecentDocumentId("");
    setDocEtag(null);
    setSelectedCardIds([]);
    setSelectedIslandId(null);
    setIsDirty(true);
    setHasSaveConflict(false);
    setSuggestedDocument(null);
    setSuggestionId(null);
    setSuggestionNotes(null);
    setSuggestionError(null);
    setStatusMessage("Duplicated the current document");
  }, [document]);

  const handleOpenRecent = useCallback(() => {
    if (!selectedRecentDocumentId || selectedRecentDocumentId === activeDocumentId) {
      return;
    }

    void loadDocument(selectedRecentDocumentId);
  }, [activeDocumentId, loadDocument, selectedRecentDocumentId]);

  const handleSuggestLayout = useCallback(async () => {
    if (!document || isSuggesting) {
      return;
    }

    setIsSuggesting(true);
    setSuggestionError(null);
    setStatusMessage("Requesting draft suggestion...");

    try {
      const result = await suggestLayout(document, suggestionInstruction.trim() || undefined);
      setSuggestionId(result.suggestionId);
      setSuggestedDocument(markSuggestedFieldsUnreviewed(cloneDocument(result.suggestedDoc), document));
      setSuggestionNotes(result.notes ?? null);
      setSuggestionError(null);
      setIsSuggestionPreviewEnabled(true);
      setIsAnnotateOverlayEnabled(false);
      setStatusMessage("Draft suggestion ready for preview");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to get suggestion";
      setSuggestionError(message);
      setStatusMessage(message);
      setSuggestedDocument(null);
      setSuggestionId(null);
      setSuggestionNotes(null);
    } finally {
      setIsSuggesting(false);
    }
  }, [document, isSuggesting, suggestionInstruction]);

  const handleApplySuggestion = useCallback(() => {
    if (!document || !suggestedDocument) {
      return;
    }

    applyDocumentChange(cloneDocument(suggestedDocument), "Applied draft suggestion");
  }, [applyDocumentChange, document, suggestedDocument]);

  const handleDiscardSuggestion = useCallback(() => {
    setSuggestedDocument(null);
    setSuggestionId(null);
    setSuggestionNotes(null);
    setSuggestionError(null);
    setIsSuggestionPreviewEnabled(true);
    setIsAnnotateOverlayEnabled(false);
    setStatusMessage("Discarded draft suggestion");
  }, []);

  const handleSuggestMerges = useCallback(async () => {
    if (!document || isSuggestingMerges) {
      return;
    }

    setIsSuggestingMerges(true);
    setMergeSuggestionError(null);
    setStatusMessage("Requesting merge suggestions...");

    try {
      const result = await suggestMerges(document, mergeSuggestionInstruction.trim() || undefined);
      setMergeSuggestions(
        result.suggestions.map((suggestion) => ({
          ...suggestion,
          editedText: suggestion.mergedTextDraft,
          isEdited: false,
        }))
      );
      setMergeSuggestionError(null);
      setStatusMessage("Merge suggestions ready");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to get merge suggestions";
      setMergeSuggestionError(message);
      setMergeSuggestions([]);
      setStatusMessage(message);
    } finally {
      setIsSuggestingMerges(false);
    }
  }, [document, isSuggestingMerges, mergeSuggestionInstruction]);

  const handleMergeSuggestionTextChange = useCallback((groupId: string, value: string) => {
    setMergeSuggestions((previousSuggestions) =>
      previousSuggestions.map((suggestion) =>
        suggestion.groupId === groupId
          ? {
              ...suggestion,
              editedText: value,
              isEdited: value !== suggestion.mergedTextDraft,
            }
          : suggestion
      )
    );
  }, []);

  const handleDismissMergeSuggestion = useCallback((groupId: string) => {
    setMergeSuggestions((previousSuggestions) => previousSuggestions.filter((suggestion) => suggestion.groupId !== groupId));
  }, []);

  const handleApplyMergeSuggestion = useCallback(
    (groupId: string) => {
      if (!document) {
        return;
      }

      const suggestion = mergeSuggestions.find((item) => item.groupId === groupId);
      if (!suggestion) {
        return;
      }

      const cardsToMerge = document.cards.filter((card) => suggestion.cardIds.includes(card.id));
      if (cardsToMerge.length < 2) {
        setMergeSuggestionError("Merge suggestion is no longer applicable.");
        return;
      }

      const mergedCardIds = new Set(cardsToMerge.map((card) => card.id));
      const averageX = cardsToMerge.reduce((sum, card) => sum + card.x, 0) / cardsToMerge.length;
      const averageY = cardsToMerge.reduce((sum, card) => sum + card.y, 0) / cardsToMerge.length;
      const newCardId = crypto.randomUUID();

      const nextDocument: DocumentV2 = {
        ...document,
        cards: [
          ...document.cards.filter((card) => !mergedCardIds.has(card.id)),
          {
            id: newCardId,
            text: suggestion.editedText,
            x: averageX,
            y: averageY,
            critique: "",
            textReviewed: suggestion.isEdited,
          },
        ],
        edges: document.edges.filter((edge) => !mergedCardIds.has(edge.fromId) && !mergedCardIds.has(edge.toId)),
        islands: document.islands.map((island) => {
          const hasMergedCard = island.cardIds.some((cardId) => mergedCardIds.has(cardId));
          if (!hasMergedCard) {
            return island;
          }

          const preservedIds = island.cardIds.filter((cardId) => !mergedCardIds.has(cardId));
          return {
            ...island,
            cardIds: [...preservedIds, newCardId],
          };
        }),
      };

      applyDocumentChange(nextDocument, "Applied merge suggestion");
      setMergeSuggestions((previousSuggestions) => previousSuggestions.filter((item) => item.groupId !== groupId));
      setSelectedCardIds((previousCardIds) =>
        previousCardIds.filter((cardId) => !mergedCardIds.has(cardId)).concat(newCardId)
      );
    },
    [applyDocumentChange, document, mergeSuggestions]
  );

  const handleExport = useCallback(() => {
    if (!document) {
      return;
    }

    const blob = new Blob([JSON.stringify(document, null, 2)], { type: "application/json" });
    const objectUrl = URL.createObjectURL(blob);
    const downloadLink = window.document.createElement("a");

    downloadLink.href = objectUrl;
    downloadLink.download = `kj-atlas-doc-${document.id}.json`;
    window.document.body.appendChild(downloadLink);
    downloadLink.click();
    downloadLink.remove();

    URL.revokeObjectURL(objectUrl);
    setStatusMessage("Exported document as JSON");
  }, [document]);

  const handleImportFileChange = useCallback(
    async (event: ChangeEvent<HTMLInputElement>) => {
      const selectedFile = event.target.files?.[0];
      event.target.value = "";

      if (!selectedFile) {
        return;
      }

      try {
        const rawText = await selectedFile.text();
        const parsedJson: unknown = JSON.parse(rawText);
        const validateResult = validateAndUpgradeImportedDocument(parsedJson);

        if (!validateResult.ok) {
          setStatusMessage(validateResult.error);
          return;
        }

        pendingCardDragSnapshotRef.current = null;
        setHistory({
          past: [],
          present: cloneDocument(validateResult.document),
          future: [],
        });
        setActiveDocumentId(validateResult.document.id);
        setSelectedRecentDocumentId("");
        setDocEtag(null);
        setSelectedCardIds([]);
        setSelectedIslandId(null);
        setIsDirty(true);
        setHasSaveConflict(false);
        setSuggestedDocument(null);
        setSuggestionId(null);
        setSuggestionNotes(null);
        setSuggestionError(null);
        setStatusMessage("Imported document");
      } catch (error) {
        if (error instanceof SyntaxError) {
          setStatusMessage("Failed to parse JSON file");
          return;
        }

        setStatusMessage(error instanceof Error ? error.message : "Failed to import document");
      }
    },
    []
  );

  const handleImportClick = useCallback(() => {
    importInputRef.current?.click();
  }, []);

  const handleCardSelect = useCallback((cardId: string, isShiftPressed: boolean) => {
    if (isPickingEdgeTarget) {
      if (!document) {
        return;
      }

      const source =
        selectedIslandId && selectedCardIds.length === 0
          ? { id: selectedIslandId, kind: "island" as const }
          : !selectedIslandId && selectedCardIds.length === 1
            ? { id: selectedCardIds[0], kind: "card" as const }
            : null;

      if (!source || (source.id === cardId && source.kind === "card")) {
        return;
      }

      const edgeWithKinds = {
        id: crypto.randomUUID(),
        fromId: source.id,
        toId: cardId,
        fromKind: source.kind,
        toKind: "card",
        type: connectEdgeType,
      } as DocumentV2["edges"][number];

      applyDocumentChange(
        {
          ...document,
          edges: [...document.edges, edgeWithKinds],
        },
        `Connected ${source.kind} → card`
      );
      setIsPickingEdgeTarget(false);
      return;
    }

    if (isPreviewingSuggestion && !isAnnotateOverlayEnabled) {
      return;
    }

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
    if (isPreviewingSuggestion && isAnnotateOverlayEnabled) {
      setSelectedIslandId(null);
    }
  }, [
    applyDocumentChange,
    connectEdgeType,
    document,
    isAnnotateOverlayEnabled,
    isPickingEdgeTarget,
    isPreviewingSuggestion,
    selectedCardIds,
    selectedIslandId,
  ]);

  const handleCanvasBackgroundClick = useCallback(() => {
    if (isPickingEdgeTarget) {
      return;
    }

    setSelectedCardIds((previousSelectedCardIds) => {
      if (previousSelectedCardIds.length === 0) {
        return previousSelectedCardIds;
      }

      return [];
    });
    setSelectedIslandId(null);
  }, [isPickingEdgeTarget]);

  const handleClearSelection = useCallback(() => {
    if (isPickingEdgeTarget) {
      setIsPickingEdgeTarget(false);
      setStatusMessage("Canceled connect");
      return;
    }

    setSelectedCardIds((previousSelectedCardIds) => {
      if (previousSelectedCardIds.length === 0) {
        return previousSelectedCardIds;
      }

      return [];
    });
    setSelectedIslandId(null);
  }, [isPickingEdgeTarget]);

  const handleMarqueeSelect = useCallback((cardIds: string[], isShiftPressed: boolean) => {
    if (isPickingEdgeTarget) {
      return;
    }

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
  }, [isPickingEdgeTarget]);

  const canCreateIsland = selectedCardIds.length > 0;
  const edgeConnectSource = useMemo<EdgeConnectSource | null>(() => {
    if (selectedIslandId && selectedCardIds.length === 0) {
      return { id: selectedIslandId, kind: "island" };
    }

    if (!selectedIslandId && selectedCardIds.length === 1) {
      return { id: selectedCardIds[0], kind: "card" };
    }

    return null;
  }, [selectedCardIds, selectedIslandId]);
  const canStartConnect = edgeConnectSource !== null;

  const handleStartConnect = useCallback(() => {
    if (!edgeConnectSource) {
      return;
    }

    setIsPickingEdgeTarget(true);
    setStatusMessage("Select a target card or island");
  }, [edgeConnectSource]);

  const handleCancelConnect = useCallback(() => {
    if (!isPickingEdgeTarget) {
      return;
    }

    setIsPickingEdgeTarget(false);
    setStatusMessage("Canceled connect");
  }, [isPickingEdgeTarget]);

  const handleConnectToTarget = useCallback(
    (target: EdgeConnectSource) => {
      if (!document || !isPickingEdgeTarget || !edgeConnectSource) {
        return;
      }

      if (edgeConnectSource.id === target.id && edgeConnectSource.kind === target.kind) {
        return;
      }

      const edgeWithKinds = {
        id: crypto.randomUUID(),
        fromId: edgeConnectSource.id,
        toId: target.id,
        fromKind: edgeConnectSource.kind,
        toKind: target.kind,
        type: connectEdgeType,
      } as DocumentV2["edges"][number];

      applyDocumentChange(
        {
          ...document,
          edges: [...document.edges, edgeWithKinds],
        },
        `Connected ${edgeConnectSource.kind} → ${target.kind}`
      );
      setIsPickingEdgeTarget(false);
    },
    [applyDocumentChange, connectEdgeType, document, isPickingEdgeTarget, selectedCardIds, selectedIslandId]
  );

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

      const nextTitle = rawTitle.length > 0 ? rawTitle : undefined;
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
          titleReviewed: true,
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

  const handleIslandSummaryTextChange = useCallback(
    (islandId: string, rawSummaryText: string) => {
      if (!document) {
        return;
      }

      const nextSummaryText = rawSummaryText.length > 0 ? rawSummaryText : undefined;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.summaryText ?? undefined) === nextSummaryText && island.summaryReviewed === true) {
          return island;
        }

        return {
          ...island,
          summaryText: nextSummaryText,
          summaryReviewed: true,
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
        "Updated island summary"
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
          imageReviewed: true,
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

  const handleCardCritiqueChange = useCallback(
    (cardId: string, rawCritique: string) => {
      if (!document) {
        return;
      }

      const nextCritique = rawCritique.length > 0 ? rawCritique : undefined;
      const nextCards = document.cards.map((card) => {
        if (card.id !== cardId) {
          return card;
        }

        if ((card.critique ?? undefined) === nextCritique) {
          return card;
        }

        return {
          ...card,
          critique: nextCritique,
        };
      });

      const hasChanges = nextCards.some((card, index) => card !== document.cards[index]);
      if (!hasChanges) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          cards: nextCards,
        },
        "Updated card critique",
        { preserveSuggestionPreview: true }
      );
    },
    [applyDocumentChange, document]
  );

  const handleCardCritiqueTagsChange = useCallback(
    (cardId: string, nextTags: string[]) => {
      if (!document) {
        return;
      }

      const normalizedNextTags = nextTags.length > 0 ? [...nextTags] : undefined;
      const nextCards = document.cards.map((card) => {
        if (card.id !== cardId) {
          return card;
        }

        const currentTags = card.critiqueTags ?? [];
        const tagsChanged =
          currentTags.length !== nextTags.length || currentTags.some((tag, index) => tag !== nextTags[index]);
        if (!tagsChanged) {
          return card;
        }

        return {
          ...card,
          critiqueTags: normalizedNextTags,
        };
      });

      const hasChanges = nextCards.some((card, index) => card !== document.cards[index]);
      if (!hasChanges) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          cards: nextCards,
        },
        "Updated card critique tags",
        { preserveSuggestionPreview: true }
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandCritiqueChange = useCallback(
    (islandId: string, rawCritique: string) => {
      if (!document) {
        return;
      }

      const nextCritique = rawCritique.length > 0 ? rawCritique : undefined;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.critique ?? undefined) === nextCritique) {
          return island;
        }

        return {
          ...island,
          critique: nextCritique,
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
        "Updated island critique",
        { preserveSuggestionPreview: true }
      );
    },
    [applyDocumentChange, document]
  );


  const handleIslandCritiqueTagsChange = useCallback(
    (islandId: string, nextTags: string[]) => {
      if (!document) {
        return;
      }

      const normalizedNextTags = nextTags.length > 0 ? [...nextTags] : undefined;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        const currentTags = island.critiqueTags ?? [];
        const tagsChanged =
          currentTags.length !== nextTags.length || currentTags.some((tag, index) => tag !== nextTags[index]);
        if (!tagsChanged) {
          return island;
        }

        return {
          ...island,
          critiqueTags: normalizedNextTags,
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
        "Updated island critique tags",
        { preserveSuggestionPreview: true }
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandTitleReviewedChange = useCallback(
    (islandId: string, reviewed: boolean) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.titleReviewed ?? false) === reviewed) {
          return island;
        }

        return {
          ...island,
          titleReviewed: reviewed,
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
        "Updated island title reviewed state"
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandSummaryReviewedChange = useCallback(
    (islandId: string, reviewed: boolean) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.summaryReviewed ?? false) === reviewed) {
          return island;
        }

        return {
          ...island,
          summaryReviewed: reviewed,
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
        "Updated island summary reviewed state"
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandImageReviewedChange = useCallback(
    (islandId: string, reviewed: boolean) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        if ((island.imageReviewed ?? false) === reviewed) {
          return island;
        }

        return {
          ...island,
          imageReviewed: reviewed,
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
        "Updated island image reviewed state"
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandCollapsedChange = useCallback(
    (islandId: string, collapsed: boolean) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId) {
          return island;
        }

        const currentCollapsed = island.collapsed === true;
        if (currentCollapsed === collapsed) {
          return island;
        }

        return {
          ...island,
          collapsed,
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
        collapsed ? "Collapsed island" : "Expanded island"
      );
    },
    [applyDocumentChange, document]
  );

  useEffect(() => {
    if (!peekIslandId || !focusedVisibleDocument) {
      return;
    }

    const hasPeekTarget = focusedVisibleDocument.islands.some((island) => island.id === peekIslandId);
    if (!hasPeekTarget) {
      setPeekIslandId(undefined);
    }
  }, [focusedVisibleDocument, peekIslandId]);

  useEffect(() => {
    if (!peekIslandId) {
      return;
    }

    const clearPeek = () => {
      setPeekIslandId(undefined);
    };

    window.addEventListener("mouseup", clearPeek);
    return () => {
      window.removeEventListener("mouseup", clearPeek);
    };
  }, [peekIslandId]);

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

  const uniqueIslands = useMemo(() => {
    const normalizedIslands = (focusedVisibleDocument?.islands ?? []).map((island) => ({
      ...island,
      collapsed: island.collapsed === true,
      cardIds: Array.from(new Set(island.cardIds)),
    }));
    const islandsById = new Map(normalizedIslands.map((island) => [island.id, island]));

    return normalizedIslands
      .map((island, index) => ({
        island,
        index,
        depth: getIslandDepth(island, islandsById),
      }))
      .sort((left, right) => {
        if (left.depth !== right.depth) {
          return left.depth - right.depth;
        }

        return left.index - right.index;
      })
      .map((entry) => entry.island);
  }, [focusedVisibleDocument?.islands]);

  const maxAvailableDepth = useMemo(() => {
    if (islandDepthById.size === 0) {
      return 0;
    }

    return Math.max(...islandDepthById.values());
  }, [islandDepthById]);

  useEffect(() => {
    if (maxDepth === "all") {
      return;
    }

    if (maxDepth > maxAvailableDepth) {
      setMaxDepth(maxAvailableDepth);
    }
  }, [maxAvailableDepth, maxDepth]);

  const visibleIslands = useMemo(() => {
    return uniqueIslands.filter((island) => {
      if (depthHiddenIslandIdSet.has(island.id)) {
        return false;
      }

      return !island.parentIslandId || !collapsedIslandIdSet.has(island.parentIslandId);
    });
  }, [collapsedIslandIdSet, depthHiddenIslandIdSet, uniqueIslands]);

  const visibleIslandIdSet = useMemo(() => new Set(visibleIslands.map((island) => island.id)), [visibleIslands]);

  useEffect(() => {
    if (uniqueIslands.length === 0) {
      setSelectedIslandId(null);
      return;
    }

    if (selectedIslandId && !uniqueIslands.some((island) => island.id === selectedIslandId)) {
      setSelectedIslandId(null);
    }
  }, [selectedIslandId, uniqueIslands]);

  useEffect(() => {
    if (!selectedIslandId) {
      return;
    }

    if (!visibleIslandIdSet.has(selectedIslandId)) {
      setSelectedIslandId(null);
    }
  }, [selectedIslandId, visibleIslandIdSet]);

  useEffect(() => {
    if (!focusTarget.focusIslandId) {
      return;
    }

    if (!visibleIslandIdSet.has(focusTarget.focusIslandId)) {
      setFocusTarget({});
      setFocusWorldPoint(null);
    }
  }, [focusTarget.focusIslandId, visibleIslandIdSet]);

  useEffect(() => {
    setFocusTarget({});
    setFocusWorldPoint(null);
  }, [document?.id]);

  const selectedIsland = useMemo(() => {
    if (!document || !selectedIslandId) {
      return null;
    }

    return document.islands.find((island) => island.id === selectedIslandId) ?? null;
  }, [document, selectedIslandId]);
  const selectedCard = useMemo(() => {
    if (!document || selectedCardIds.length !== 1) {
      return null;
    }

    return document.cards.find((card) => card.id === selectedCardIds[0]) ?? null;
  }, [document?.cards, selectedCardIds]);

  const handleIslandSelect = useCallback((islandId: string) => {
    if (isPickingEdgeTarget) {
      handleConnectToTarget({ id: islandId, kind: "island" });
      return;
    }

    if (isPreviewingSuggestion && !isAnnotateOverlayEnabled) {
      return;
    }

    setSelectedIslandId(islandId);
    if (isPreviewingSuggestion && isAnnotateOverlayEnabled) {
      setSelectedCardIds([]);
    }
  }, [handleConnectToTarget, isAnnotateOverlayEnabled, isPickingEdgeTarget, isPreviewingSuggestion]);

  const handleFocusIsland = useCallback(() => {
    if (!selectedIsland || !document) {
      return;
    }

    const focusedCards = document.cards.filter((card) => selectedIsland.cardIds.includes(card.id));
    const nextFocusWorldPoint =
      focusedCards.length === 0
        ? null
        : {
            x:
              (Math.min(...focusedCards.map((card) => card.x)) +
                Math.max(...focusedCards.map((card) => card.x + 220))) /
              2,
            y:
              (Math.min(...focusedCards.map((card) => card.y)) +
                Math.max(...focusedCards.map((card) => card.y + 80))) /
              2,
          };

    setFocusTarget({ focusIslandId: selectedIsland.id });
    setFocusWorldPoint(nextFocusWorldPoint);
    suppressNextTransformPersistRef.current = true;
    setFocusRequestSeq((previousSeq) => previousSeq + 1);
  }, [document, selectedIsland]);

  const handleClearFocus = useCallback(() => {
    setFocusTarget({});
    setFocusWorldPoint(null);
  }, []);

  const islandViews = useMemo(() => {
    if (!focusedVisibleDocument) {
      return null;
    }

  return uniqueIslands
    .filter((island) => !island.parentIslandId || !collapsedIslandIdSet.has(island.parentIslandId))
    .map((island, index) => (
      <IslandView
        key={island.id}
        island={island}
        cards={focusedVisibleDocument.cards}
        isSelected={selectedIslandId === island.id}
        isPeeking={peekIslandId === island.id}
        zIndex={index}
        onSelect={handleIslandSelect}
        onToggleCollapsed={handleIslandCollapsedChange}
        onPeekStart={(islandId) => {
          setPeekIslandId(islandId);
        }}
        onPeekEnd={() => {
          setPeekIslandId(undefined);
        }}
        isPickingEdgeTarget={isPickingEdgeTarget}
      />
    ));
  }, [
    collapsedIslandIdSet,
    focusedVisibleDocument,
    handleIslandCollapsedChange,
    handleIslandSelect,
    isPickingEdgeTarget,
    peekIslandId,
    selectedIslandId,
    uniqueIslands,
  ]);

  const readingOrderItems = useMemo(() => {
    if (!document) {
      return [] as Array<{ id: string; label: string }>;
    }

    return (document.readingOrder ?? []).map((entryId) => {
      const island = document.islands.find((item) => item.id === entryId);
      if (island) {
        const label = island.title?.trim() ? island.title.trim() : `Island ${island.id}`;
        return { id: entryId, label };
      }

      const card = document.cards.find((item) => item.id === entryId);
      if (card) {
        const snippet = card.text.trim().slice(0, 40);
        return { id: entryId, label: snippet.length > 0 ? snippet : `Card ${card.id}` };
      }

      return { id: entryId, label: "(missing)" };
    });
  }, [document]);

  const handleAddSelectedItemToReadingOrder = useCallback(() => {
    if (!document) {
      return;
    }

    const targetId = selectedIsland?.id ?? selectedCard?.id;
    if (!targetId) {
      return;
    }

    applyDocumentChange(
      {
        ...document,
        readingOrder: [...(document.readingOrder ?? []), targetId],
      },
      "Added item to reading order"
    );
  }, [applyDocumentChange, document, selectedCard?.id, selectedIsland?.id]);

  const handleMoveReadingOrderItem = useCallback(
    (index: number, direction: -1 | 1) => {
      if (!document) {
        return;
      }

      const readingOrder = [...(document.readingOrder ?? [])];
      const nextIndex = index + direction;
      if (index < 0 || index >= readingOrder.length || nextIndex < 0 || nextIndex >= readingOrder.length) {
        return;
      }

      const [entry] = readingOrder.splice(index, 1);
      readingOrder.splice(nextIndex, 0, entry);

      applyDocumentChange(
        {
          ...document,
          readingOrder,
        },
        "Reordered reading order"
      );
    },
    [applyDocumentChange, document]
  );

  const handleRemoveReadingOrderItem = useCallback(
    (index: number) => {
      if (!document) {
        return;
      }

      const readingOrder = [...(document.readingOrder ?? [])];
      if (index < 0 || index >= readingOrder.length) {
        return;
      }

      readingOrder.splice(index, 1);
      applyDocumentChange(
        {
          ...document,
          readingOrder,
        },
        "Removed item from reading order"
      );
    },
    [applyDocumentChange, document]
  );

  const handleAddSelectedCardsToIsland = useCallback(() => {
    if (!document || !selectedIsland || selectedCardIds.length === 0) {
      return;
    }

    const mergedCardIds = Array.from(new Set([...selectedIsland.cardIds, ...selectedCardIds]));
    if (
      mergedCardIds.length === selectedIsland.cardIds.length &&
      mergedCardIds.every((cardId, index) => cardId === selectedIsland.cardIds[index])
    ) {
      return;
    }

    applyDocumentChange(
      {
        ...document,
        islands: document.islands.map((island) =>
          island.id === selectedIsland.id ? { ...island, cardIds: mergedCardIds } : island
        ),
      },
      "Added selected cards to island"
    );
  }, [applyDocumentChange, document, selectedCardIds, selectedIsland]);

  const handleRemoveSelectedCardsFromIsland = useCallback(() => {
    if (!document || !selectedIsland || selectedCardIds.length === 0) {
      return;
    }

    const selectedCardIdSet = new Set(selectedCardIds);
    const nextCardIds = selectedIsland.cardIds.filter((cardId) => !selectedCardIdSet.has(cardId));

    if (nextCardIds.length === selectedIsland.cardIds.length) {
      return;
    }

    applyDocumentChange(
      {
        ...document,
        islands: document.islands.map((island) =>
          island.id === selectedIsland.id ? { ...island, cardIds: nextCardIds } : island
        ),
      },
      "Removed selected cards from island"
    );
  }, [applyDocumentChange, document, selectedCardIds, selectedIsland]);

  const handleDeleteSelectedIsland = useCallback(() => {
    if (!document || !selectedIsland) {
      return;
    }

    const nextIslands = document.islands.filter((island) => island.id !== selectedIsland.id);
    applyDocumentChange(
      {
        ...document,
        islands: nextIslands,
        readingOrder: (document.readingOrder ?? []).filter((id) => id !== selectedIsland.id),
      },
      "Deleted island"
    );
    setSelectedIslandId(null);
  }, [applyDocumentChange, document, selectedIsland]);

  const headerCenter = (
    <SearchBar
      query={searchQuery}
      totalMatches={matchedCardIds.length}
      currentMatchIndex={activeMatchIndex}
      hideNonMatches={hideNonMatches}
      onQueryChange={(nextQuery) => {
        setSearchQuery(nextQuery);
        setCurrentMatchIndex(0);
      }}
      onPrev={handleSearchPrev}
      onNext={handleSearchNext}
      onHideNonMatchesChange={setHideNonMatches}
    />
  );

  const handleDeleteSelection = useCallback(() => {
    if (!document || isPreviewingSuggestion) {
      return;
    }

    if (selectedCardIds.length > 0) {
      const selectedCardIdSet = new Set(selectedCardIds);
      const nextCards = document.cards.filter((card) => !selectedCardIdSet.has(card.id));

      if (nextCards.length === document.cards.length) {
        return;
      }

      const nextEdges = document.edges.filter(
        (edge) => !selectedCardIdSet.has(edge.fromId) && !selectedCardIdSet.has(edge.toId)
      );
      const nextIslands = document.islands
        .map((island) => ({
          ...island,
          cardIds: island.cardIds.filter((cardId) => !selectedCardIdSet.has(cardId)),
        }))
        .filter((island) => island.cardIds.length > 0);

      applyDocumentChange(
        {
          ...document,
          cards: nextCards,
          edges: nextEdges,
          islands: nextIslands,
          readingOrder: (document.readingOrder ?? []).filter((entryId) => {
            if (selectedCardIdSet.has(entryId)) {
              return false;
            }

            return nextCards.some((card) => card.id === entryId) || nextIslands.some((island) => island.id === entryId);
          }),
        },
        "Deleted selected cards"
      );
      setSelectedCardIds([]);
      setSelectedIslandId((previousSelectedIslandId) =>
        previousSelectedIslandId && nextIslands.some((island) => island.id === previousSelectedIslandId)
          ? previousSelectedIslandId
          : null
      );
      return;
    }

    if (!selectedIslandId) {
      return;
    }

    const nextIslands = document.islands.filter((island) => island.id !== selectedIslandId);
    if (nextIslands.length === document.islands.length) {
      return;
    }

    applyDocumentChange(
      {
        ...document,
        islands: nextIslands,
        readingOrder: (document.readingOrder ?? []).filter((id) => id !== selectedIslandId),
      },
      "Deleted selected island"
    );
    setSelectedIslandId(null);
  }, [applyDocumentChange, document, isPreviewingSuggestion, selectedCardIds, selectedIslandId]);

  const handleNudgeSelection = useCallback(
    (dx: number, dy: number) => {
      if (!document || isPreviewingSuggestion || selectedCardIds.length === 0) {
        return;
      }

      const selectedCardIdSet = new Set(selectedCardIds);
      const nextCards = document.cards.map((card) =>
        selectedCardIdSet.has(card.id)
          ? {
              ...card,
              x: card.x + dx,
              y: card.y + dy,
            }
          : card
      );

      applyDocumentChange(
        {
          ...document,
          cards: nextCards,
        },
        "Nudged selected cards"
      );
    },
    [applyDocumentChange, document, isPreviewingSuggestion, selectedCardIds]
  );

  useHotkeys({
    onClearSelection: handleClearSelection,
    onDeleteSelection: handleDeleteSelection,
    onNudge: handleNudgeSelection,
  });

  const headerRight = (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      <button
        type="button"
        onClick={handleNewDocument}
        disabled={isLoading || isSaving}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || isSaving ? "not-allowed" : "pointer",
        }}
      >
        New
      </button>
      <button
        type="button"
        onClick={handleDuplicateDocument}
        disabled={isLoading || isSaving || !document}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || isSaving || !document ? "not-allowed" : "pointer",
        }}
      >
        Duplicate
      </button>
      <select
        value={selectedRecentDocumentId}
        onChange={(event) => {
          setSelectedRecentDocumentId(event.target.value);
        }}
        disabled={isLoading || recentDocumentIds.length === 0}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 500,
          minWidth: 180,
        }}
      >
        <option value="">Recent documents</option>
        {recentDocumentIds.map((docId) => (
          <option key={docId} value={docId}>
            {docId}
          </option>
        ))}
      </select>
      <button
        type="button"
        onClick={handleOpenRecent}
        disabled={isLoading || !selectedRecentDocumentId || selectedRecentDocumentId === activeDocumentId}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor:
            isLoading || !selectedRecentDocumentId || selectedRecentDocumentId === activeDocumentId
              ? "not-allowed"
              : "pointer",
        }}
      >
        Open
      </button>
      <button
        type="button"
        onClick={() => {
          void handleSuggestLayout();
        }}
        disabled={isLoading || !document || isSuggesting}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || !document || isSuggesting ? "not-allowed" : "pointer",
        }}
      >
        {isSuggesting ? "Suggesting..." : "Suggest layout"}
      </button>
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
        onClick={handleImportClick}
        disabled={isLoading}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading ? "not-allowed" : "pointer",
        }}
      >
        Import
      </button>
      <button
        type="button"
        onClick={handleExport}
        disabled={isLoading || !document}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "6px 12px",
          fontWeight: 600,
          cursor: isLoading || !document ? "not-allowed" : "pointer",
        }}
      >
        Export
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
    <Shell
      title="kj-atlas Canvas MVP"
      subtitle={`Document: ${activeDocumentId}`}
      headerCenter={headerCenter}
      headerRight={headerRight}
      hasUnsavedChanges={isDirty}
      saveConflictMessage={
        hasSaveConflict
          ? "This document has been updated elsewhere. Please reload or export your changes."
          : undefined
      }
      onReloadAfterConflict={() => {
        void loadDocument(activeDocumentId, { isReload: true });
      }}
      onExportAfterConflict={handleExport}
      isReloadingAfterConflict={isReloadingDocument}
      sidePanel={
        <SidePanel
          selectedCard={selectedCard}
          topContent={
            <>
              <MergeSuggestionsPanel
                instruction={mergeSuggestionInstruction}
                onInstructionChange={setMergeSuggestionInstruction}
                onSuggest={() => {
                  void handleSuggestMerges();
                }}
                isSuggesting={isSuggestingMerges}
                errorMessage={mergeSuggestionError}
                suggestions={mergeSuggestions}
                cardsById={cardsById}
                onMergedTextChange={handleMergeSuggestionTextChange}
                onApply={handleApplyMergeSuggestion}
                onDismiss={handleDismissMergeSuggestion}
              />
              <SuggestionPanel
                instruction={suggestionInstruction}
                onInstructionChange={setSuggestionInstruction}
                onSuggest={() => {
                  void handleSuggestLayout();
                }}
                onResuggest={() => {
                  void handleSuggestLayout();
                }}
                onApply={handleApplySuggestion}
                onDiscard={handleDiscardSuggestion}
                hasSuggestion={Boolean(suggestedDocument && suggestionId)}
                isPreviewEnabled={isSuggestionPreviewEnabled}
                onPreviewToggle={setIsSuggestionPreviewEnabled}
                isAnnotateOverlayEnabled={isAnnotateOverlayEnabled}
                onAnnotateOverlayToggle={setIsAnnotateOverlayEnabled}
                isSuggesting={isSuggesting}
                errorMessage={suggestionError}
                notes={suggestionNotes}
              />
            </>
          }
          selectedIsland={selectedIsland}
          selectedCardCount={selectedCardIds.length}
          onCardCritiqueChange={(value) => {
            if (!selectedCard) {
              return;
            }

            handleCardCritiqueChange(selectedCard.id, value);
          }}
          onCardCritiqueTagsChange={(value) => {
            if (!selectedCard) {
              return;
            }

            handleCardCritiqueTagsChange(selectedCard.id, value);
          }}
          onTitleChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandTitleChange(selectedIsland.id, value);
          }}
          onTitleReviewedChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandTitleReviewedChange(selectedIsland.id, value);
          }}
          onSummaryTextChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandSummaryTextChange(selectedIsland.id, value);
          }}
          onSummaryReviewedChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandSummaryReviewedChange(selectedIsland.id, value);
          }}
          onImageUrlChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandImageUrlChange(selectedIsland.id, value);
          }}
          onImageReviewedChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandImageReviewedChange(selectedIsland.id, value);
          }}
          onIslandCollapsedChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandCollapsedChange(selectedIsland.id, value);
          }}
          onIslandCritiqueChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandCritiqueChange(selectedIsland.id, value);
          }}
          onIslandCritiqueTagsChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandCritiqueTagsChange(selectedIsland.id, value);
          }}
          onAddSelectedCards={handleAddSelectedCardsToIsland}
          onRemoveSelectedCards={handleRemoveSelectedCardsFromIsland}
          onDeleteIsland={handleDeleteSelectedIsland}
          isFocusActive={Boolean(focusTarget.focusIslandId)}
          onFocusIsland={handleFocusIsland}
          onClearFocus={handleClearFocus}
          isGridSnapEnabled={isGridSnapEnabled}
          onGridSnapToggle={setIsGridSnapEnabled}
          maxDepth={maxDepth}
          maxAvailableDepth={maxAvailableDepth}
          onMaxDepthChange={setMaxDepth}
          hideSourceCards={hideSourceCards}
          onHideSourceCardsChange={setHideSourceCards}
          showCanonicalOnlyEdges={showCanonicalOnlyEdges}
          onShowCanonicalOnlyEdgesChange={setShowCanonicalOnlyEdges}
          onAlignLeft={() => {
            handleAlign("left");
          }}
          onAlignRight={() => {
            handleAlign("right");
          }}
          onAlignTop={() => {
            handleAlign("top");
          }}
          onAlignBottom={() => {
            handleAlign("bottom");
          }}
          onDistributeHorizontally={() => {
            handleDistribute("horizontal");
          }}
          onDistributeVertically={() => {
            handleDistribute("vertical");
          }}
          canStartConnect={canStartConnect}
          isPickingEdgeTarget={isPickingEdgeTarget}
          connectEdgeType={connectEdgeType}
          onConnectEdgeTypeChange={setConnectEdgeType}
          onStartConnect={handleStartConnect}
          onCancelConnect={handleCancelConnect}
          readingOrderItems={readingOrderItems}
          canAddSelectedItemToReadingOrder={Boolean(selectedIsland || selectedCard)}
          onAddSelectedItemToReadingOrder={handleAddSelectedItemToReadingOrder}
          onMoveReadingOrderItem={handleMoveReadingOrderItem}
          onRemoveReadingOrderItem={handleRemoveReadingOrderItem}
        />
      }
    >
      <input
        ref={importInputRef}
        type="file"
        accept="application/json,.json"
        onChange={(event) => {
          void handleImportFileChange(event);
        }}
        style={{ display: "none" }}
      />
      {isLoading || !focusedVisibleDocument ? (
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
            document={focusedVisibleDocument}
            onCardMove={handleCardMove}
            onTransformChange={handleTransformChange}
            selectedCardIds={selectedCardIds}
            onCardSelect={handleCardSelect}
            onCanvasBackgroundClick={handleCanvasBackgroundClick}
            onMarqueeSelect={handleMarqueeSelect}
            searchQuery={normalizedSearchQuery}
            matchedCardIds={matchedCardIdSet}
            activeMatchedCardId={activeMatchedCardId}
            hiddenCardIds={hiddenCardIdSet}
            hideSourceCards={hideSourceCards}
            showCanonicalOnlyEdges={showCanonicalOnlyEdges}
            focusCardId={focusCardId}
            focusWorldPoint={focusWorldPoint}
            focusRequestSeq={focusRequestSeq}
            isPickingEdgeTarget={isPickingEdgeTarget}
            suggestionMoveDiffs={suggestionMoveDiffs}
          >
            {islandViews}
          </CanvasShell>
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
