import type { DocumentV1 } from "../types";
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

export const PERSPECTIVE_MODE_VALUES: PerspectiveMode[] = [
  "default",
  "facts",
  "claims",
  "hypotheses",
  "unknown",
  "evidence",
  "contradiction",
  "review",
];

export type PerspectiveState = {
  mode: PerspectiveMode;
  strictFilter: boolean;
  lodEnabled?: boolean;
  evidenceOverlayPrefs?: {
    mode: "supports" | "contradicts" | "both";
    depth: number;
    scope: "all" | "selection";
    dimOthers: boolean;
  };
};

export type PerspectivePreset = {
  id: string;
  name: string;
  perspective: PerspectiveState;
  forceSafeModeOnShare?: boolean;
};

export const DEFAULT_PERSPECTIVE_PRESETS: PerspectivePreset[] = [
  {
    id: "default-explore",
    name: "Explore",
    perspective: { mode: "default", strictFilter: false, evidenceOverlayPrefs: { mode: "supports", depth: 1, scope: "selection", dimOthers: true } },
  },
  {
    id: "default-review",
    name: "Review",
    perspective: { mode: "review", strictFilter: false, evidenceOverlayPrefs: { mode: "supports", depth: 1, scope: "selection", dimOthers: true } },
    forceSafeModeOnShare: true,
  },
  {
    id: "default-summary",
    name: "Summary",
    perspective: { mode: "default", strictFilter: false, lodEnabled: true, evidenceOverlayPrefs: { mode: "supports", depth: 1, scope: "selection", dimOthers: true } },
  },
];

export function isDefaultPerspectivePresetId(presetId: string): boolean {
  return DEFAULT_PERSPECTIVE_PRESETS.some((preset) => preset.id === presetId);
}

function sortPresets(presets: PerspectivePreset[]): PerspectivePreset[] {
  return [...presets].sort((left, right) => {
    const byName = left.name.localeCompare(right.name);
    if (byName !== 0) {
      return byName;
    }

    return left.id.localeCompare(right.id);
  });
}

function normalizePerspectiveState(state: PerspectiveState): PerspectiveState {
  const next: PerspectiveState = {
    mode: state.mode,
    strictFilter: state.strictFilter,
  };

  if (state.lodEnabled !== undefined) {
    next.lodEnabled = state.lodEnabled;
  }

  const prefs = state.evidenceOverlayPrefs;
  next.evidenceOverlayPrefs = {
    mode: prefs?.mode ?? "supports",
    depth: Math.max(1, Math.min(3, Math.floor(prefs?.depth ?? 1))),
    scope: prefs?.scope ?? "selection",
    dimOthers: prefs?.dimOthers ?? true,
  };

  return next;
}

export function mergeWithDefaultPerspectivePresets(presets: PerspectivePreset[]): PerspectivePreset[] {
  const byId = new Map<string, PerspectivePreset>();
  for (const preset of DEFAULT_PERSPECTIVE_PRESETS) {
    byId.set(preset.id, preset);
  }
  for (const preset of presets) {
    byId.set(preset.id, preset);
  }

  return sortPresets([...byId.values()]);
}

export function replacePerspectivePreset(presets: PerspectivePreset[], nextPreset: PerspectivePreset): PerspectivePreset[] {
  const remaining = presets.filter((preset) => preset.id !== nextPreset.id);
  return sortPresets([...remaining, nextPreset]);
}

export function renamePerspectivePreset(presets: PerspectivePreset[], presetId: string, nextName: string): PerspectivePreset[] {
  return sortPresets(
    presets.map((preset) => (preset.id === presetId ? { ...preset, name: nextName } : preset)),
  );
}

export function removePerspectivePreset(presets: PerspectivePreset[], presetId: string): PerspectivePreset[] {
  return sortPresets(presets.filter((preset) => preset.id !== presetId));
}

export function resolveCurrentPerspectivePresetId(
  presets: PerspectivePreset[],
  perspective: PerspectiveState,
): string | null {
  const current = JSON.stringify(normalizePerspectiveState(perspective));
  const matched = presets.find((preset) => JSON.stringify(normalizePerspectiveState(preset.perspective)) === current);
  return matched?.id ?? null;
}

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

function isUnknownClaimType(claimType: DocumentV1["cards"][number]["claimType"]): boolean {
  return claimType === undefined || claimType === "unknown";
}

function getTypeMatchedCardIds(doc: DocumentV1, mode: PerspectiveMode): Set<string> {
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
  doc: DocumentV1,
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
  doc: DocumentV1,
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
