import type { DocumentV2 } from "../types";
import { buildEvidenceAdjacency, getEvidenceNeighborhood, type EvidenceOverlayMode } from "./evidence_overlay";

export type PerspectiveMode =
  | "default"
  | "facts"
  | "claims"
  | "hypotheses"
  | "unknown"
  | "evidence"
  | "contradiction"
  | "review";

export type PerspectiveViewState = {
  perspectiveMode: PerspectiveMode;
  perspectiveStrictFilter?: boolean;
};

export type PerspectiveSelection = {
  selectedCardId: string | null;
};

export type PerspectiveRendering = {
  visibleCardIds: Set<string> | null;
  dimCardIds: Set<string>;
  highlightCardIds: Set<string>;
  overlay: {
    evidenceEnabled?: boolean;
    contradictionEnabled?: boolean;
    mode?: "supports" | "contradicts" | "both";
    scope?: "selection" | "all";
  };
  notes: string[];
};

function sortIds(ids: Iterable<string>): string[] {
  return [...ids].sort((left, right) => left.localeCompare(right));
}

function isUnknownClaimType(claimType: DocumentV2["cards"][number]["claimType"]): boolean {
  return claimType === undefined || claimType === "unknown";
}

function getTypeMatchedCardIds(doc: DocumentV2, mode: PerspectiveMode): Set<string> {
  if (mode === "facts") {
    return new Set(sortIds(doc.cards.filter((card) => card.claimType === "fact").map((card) => card.id)));
  }

  if (mode === "claims") {
    return new Set(sortIds(doc.cards.filter((card) => card.claimType === "claim").map((card) => card.id)));
  }

  if (mode === "hypotheses") {
    return new Set(sortIds(doc.cards.filter((card) => card.claimType === "hypothesis").map((card) => card.id)));
  }

  return new Set(sortIds(doc.cards.filter((card) => isUnknownClaimType(card.claimType)).map((card) => card.id)));
}

function getEvidenceMatchedCardIds(
  doc: DocumentV2,
  selectedCardId: string | null,
  mode: EvidenceOverlayMode,
): { matchingCardIds: Set<string>; notes: string[]; scope: "selection" | "all" } {
  const notes: string[] = [];
  const scope: "selection" | "all" = selectedCardId ? "selection" : "all";

  if (!selectedCardId) {
    notes.push("Select a card to explore neighborhood.");
    return {
      matchingCardIds: new Set(sortIds(doc.cards.map((card) => card.id))),
      notes,
      scope,
    };
  }

  const adjacency = buildEvidenceAdjacency(doc);
  const neighborhood = getEvidenceNeighborhood(selectedCardId, adjacency, mode, 1);
  return {
    matchingCardIds: new Set(sortIds(neighborhood.nodes)),
    notes,
    scope,
  };
}

export function computePerspectiveRendering(
  doc: DocumentV2,
  viewState: PerspectiveViewState,
  selection: PerspectiveSelection,
): PerspectiveRendering {
  const cardIds = sortIds(doc.cards.map((card) => card.id));
  const allCardIdSet = new Set(cardIds);
  const highlightCardIds = new Set<string>();
  const notes: string[] = [];

  if (viewState.perspectiveMode === "default") {
    return {
      visibleCardIds: null,
      dimCardIds: new Set<string>(),
      highlightCardIds,
      overlay: {},
      notes,
    };
  }

  let matchingCardIds = new Set<string>();
  let overlay: PerspectiveRendering["overlay"] = {};

  if (
    viewState.perspectiveMode === "facts"
    || viewState.perspectiveMode === "claims"
    || viewState.perspectiveMode === "hypotheses"
    || viewState.perspectiveMode === "unknown"
  ) {
    matchingCardIds = getTypeMatchedCardIds(doc, viewState.perspectiveMode);
  } else if (viewState.perspectiveMode === "evidence" || viewState.perspectiveMode === "contradiction") {
    const evidenceMode: EvidenceOverlayMode = viewState.perspectiveMode === "evidence" ? "supports" : "contradicts";
    const evidenceResult = getEvidenceMatchedCardIds(doc, selection.selectedCardId, evidenceMode);
    matchingCardIds = evidenceResult.matchingCardIds;
    notes.push(...evidenceResult.notes);
    overlay = {
      evidenceEnabled: true,
      contradictionEnabled: viewState.perspectiveMode === "contradiction",
      mode: evidenceMode,
      scope: evidenceResult.scope,
    };
  } else if (viewState.perspectiveMode === "review") {
    matchingCardIds = new Set(cardIds);
    for (const card of doc.cards) {
      if (isUnknownClaimType(card.claimType)) {
        highlightCardIds.add(card.id);
      }
    }
    for (const island of doc.islands) {
      if (island.summaryReviewed === false) {
        for (const cardId of island.cardIds) {
          if (allCardIdSet.has(cardId)) {
            highlightCardIds.add(cardId);
          }
        }
      }
    }
    notes.push("Review mode highlights unreviewed summaries and unknown claim types.");
  }

  if (selection.selectedCardId && allCardIdSet.has(selection.selectedCardId)) {
    matchingCardIds.add(selection.selectedCardId);
  }

  const perspectiveStrictFilter = viewState.perspectiveStrictFilter ?? false;
  if (perspectiveStrictFilter && viewState.perspectiveMode !== "review") {
    return {
      visibleCardIds: new Set(sortIds(matchingCardIds)),
      dimCardIds: new Set<string>(),
      highlightCardIds: new Set(sortIds(highlightCardIds)),
      overlay,
      notes,
    };
  }

  if (viewState.perspectiveMode === "review") {
    return {
      visibleCardIds: null,
      dimCardIds: new Set<string>(),
      highlightCardIds: new Set(sortIds(highlightCardIds)),
      overlay,
      notes,
    };
  }

  return {
    visibleCardIds: null,
    dimCardIds: new Set(cardIds.filter((cardId) => !matchingCardIds.has(cardId))),
    highlightCardIds: new Set(sortIds(highlightCardIds)),
    overlay,
    notes,
  };
}
