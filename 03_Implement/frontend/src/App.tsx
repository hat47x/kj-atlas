import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { ChangeEvent } from "react";

import {
  ApiError,
  checkNarrative,
  generateNarrative,
  getDocument,
  putDocument,
  suggestIslandSummary,
  summarizeIslandRelation,
  suggestLayout,
  suggestMerges,
  type NarrativeIssue,
  type NarrativeIssueReference,
} from "./api/client";
import { CanvasShell } from "./canvas/CanvasShell";
import type { AggregatedEdgeMeta, CameraTransformRequest, CanvasCamera, FocusReference } from "./canvas/CanvasShell";
import { IslandView } from "./canvas/IslandView";
import { getEdgesToRender } from "./domain/edge_aggregate";
import { alignSelectedCards, distributeSelectedCards, snapValueToGrid } from "./domain/layout_ops";
import type { AlignDirection, DistributeDirection } from "./domain/layout_ops";
import { applyCanonicalization } from "./domain/canonical_ops";
import { appendReadingOrderEntry, moveReadingOrderEntry, removeReadingOrderEntry } from "./domain/reading_order_ops";
import { computeConvexHull } from "./domain/geometry/convex_hull";
import { padPolygonFromCentroid } from "./domain/geometry/polygon_pad";
import { buildVersionTokenForCardIds, isPolygonShapeStale } from "./domain/geometry/polygon_stale";
import { isTemporaryRevealEligible } from "./domain/visibility";
import { updateIslandSummaryWithHistory } from "./domain/summary_history_ops";
import { createRepresentativeMerge } from "./domain/representative_merge";
import { isSourceCard, Document, DocumentV2, Island, Narrative, type Point, type RelationSummary } from "./domain/types";
import { validateAndUpgradeImportedDocument } from "./domain/validate";
import { validateDocumentV2Strict } from "./domain/validate_doc";
import { buildReadingOrderSnippets } from "./domain/snippet";
import { useHotkeys } from "./hooks/useHotkeys";
import { Shell } from "./ui/Shell";
import { SidePanel } from "./ui/SidePanel";
import { SuggestionPanel } from "./ui/SuggestionPanel";
import { SearchBar } from "./ui/SearchBar";
import { ViewControlsPanel } from "./ui/ViewControlsPanel";
import { MergeSuggestionsPanel } from "./ui/MergeSuggestionsPanel";
import { NarrativesPanel } from "./ui/NarrativesPanel";
import type { IslandRelationEdgeSelection } from "./domain/island_relation_explain";
import {
  buildRelationSummarySourceSignature,
  buildSummarizeIslandRelationPayload,
  getRelationSummaryBySourceSignature,
  upsertRelationSummaryWithHistory,
} from "./domain/relation_summary_ops";
import type { SuggestionMoveDiff } from "./canvas/SuggestionDiffLayer";
import { loadRecentDocumentIds, pushRecentDocumentId } from "./storage/recent";
import { buildAbstractMapExport, exportAbstractMapHTML, exportAbstractMapMarkdown } from "./export/abstract_map_export";
import { downloadBlobFile, exportCanvasToPngBlob, readBlobAsDataUrl, type PngExportScale } from "./export/canvas_png";
import { exportCanvasToSVG } from "./export/canvas_svg";
import { downloadTextFile } from "./export/narrative_export";
import { buildExportViewMetadata, validateImportViewMetadata } from "./export/view_metadata";
import { computeVisibleBounds, getCardWorldBounds, getIslandWorldBounds } from "./domain/geometry/bounds";
import { diffDocuments } from "./domain/diff/doc_diff";
import {
  DEFAULT_LOD_THRESHOLDS,
  getLODLevel,
  isEffectivelyCollapsed,
  type LODLevel,
  type LODThresholds,
} from "./domain/view/lod";
import {
  applyIslandLodZoom,
  enforceMinZoomForBounds,
  fitToBounds,
  FOCUS_LOD_EPSILON,
  popFocusHistory,
  pushFocusHistory,
  type FocusSnapshot,
} from "./domain/view/focus";
import { buildReadingList, clampReadingIndex, type ReadingItem, type ReadingMode } from "./domain/view/reading_path";
import { buildReadingOutlineMd } from "./domain/view/reading_outline";
import { DiffPanel } from "./ui/DiffPanel";
import { SharePanel } from "./ui/SharePanel";
import { applyPatchWithResolutionsDetailed, getPatchOpEntityKey, parsePatchDocument, shouldBlockPatchApplyByLint, type PatchDocument, type PatchResolution } from "./domain/patch/patch_apply";
import { buildPatchForExport } from "./domain/patch/patch_generate";
import { verifyPatchFingerprint } from "./domain/patch/patch_fingerprint";
import type { TrustLabel } from "./domain/patch/patch_types";
import { detectPatchConflicts, type ConflictItem } from "./domain/patch/conflict_detect";
import { buildPatchSummary, formatPatchSummaryMarkdown } from "./domain/patch/patch_summary";
import { appendPatchApplyLog, formatPatchApplyLogEntryMarkdown } from "./domain/patch/patch_apply_log";
import { lintPatchAgainstCurrentDoc, type PatchLintIssue } from "./domain/patch/patch_lint";
import { applyFixesToPatch, proposeFixes, type FixProposal } from "./domain/patch/patch_fix";

const DEFAULT_DOCUMENT_ID = "doc_phase1_canvas";
const HISTORY_LIMIT = 50;
const GRID_SNAP_SIZE = 10;
const SUGGESTION_MOVE_THRESHOLD = 1;
const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
const POLYGON_PADDING = 16;

const SVG_VISIBLE_BOUNDS_PADDING = 64;

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

type PendingImportedDocument = {
  fileName: string;
  document: DocumentV2;
};

type PendingPatchImport = {
  fileName: string;
  originalPatch: PatchDocument;
  patch: PatchDocument;
};

type PatchPreviewItem = {
  opId: string;
  kind: string;
  entityKey: string;
  checked: boolean;
  canToggle: boolean;
  conflict: boolean;
  lintIssueCount: number;
  lintErrorCount: number;
  lintIssueCodes: string[];
  reason?: string;
  baseSnippet?: string;
  yourSnippet?: string;
  theirSnippet?: string;
  resolution?: PatchResolution;
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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function unwrapComparisonPayload(value: unknown): unknown {
  if (!isRecord(value)) {
    return value;
  }

  if ("document" in value) {
    return value.document;
  }

  if ("snapshot" in value && isRecord(value.snapshot) && "document" in value.snapshot) {
    return value.snapshot.document;
  }

  return value;
}

function parseComparisonRelationSummaries(value: unknown): DocumentV2["relationSummaries"] {
  if (!Array.isArray(value)) {
    return [];
  }

  const relationSummaries: NonNullable<DocumentV2["relationSummaries"]> = [];

  for (const entry of value) {
    if (!isRecord(entry) || typeof entry.id !== "string") {
      continue;
    }

    relationSummaries.push({
      id: entry.id,
      createdAt: typeof entry.createdAt === "string" ? entry.createdAt : new Date().toISOString(),
      islandAId: typeof entry.islandAId === "string" ? entry.islandAId : "",
      islandBId: typeof entry.islandBId === "string" ? entry.islandBId : "",
      relationType:
        entry.relationType === "related" || entry.relationType === "negate" || entry.relationType === "unknown"
          ? entry.relationType
          : "unknown",
      derived: typeof entry.derived === "boolean" ? entry.derived : false,
      text: typeof entry.text === "string" ? entry.text : "",
      reviewed: typeof entry.reviewed === "boolean" ? entry.reviewed : false,
      groundingCardIds:
        Array.isArray(entry.groundingCardIds) && entry.groundingCardIds.every((item) => typeof item === "string")
          ? entry.groundingCardIds
          : [],
      groundingEdgeIds:
        Array.isArray(entry.groundingEdgeIds) && entry.groundingEdgeIds.every((item) => typeof item === "string")
          ? entry.groundingEdgeIds
          : [],
      warnings: Array.isArray(entry.warnings) ? entry.warnings.filter((item): item is string => typeof item === "string") : undefined,
      sourceSignature: typeof entry.sourceSignature === "string" ? entry.sourceSignature : entry.id,
    });
  }

  return relationSummaries;
}

function extractComparisonDocument(value: unknown): DocumentV2 | null {
  const payload = unwrapComparisonPayload(value);
  const validated = validateAndUpgradeImportedDocument(payload);
  if (!validated.ok) {
    return null;
  }

  if (!isRecord(payload)) {
    return validated.document;
  }

  const islandPatchById = new Map<string, { summaryText?: string; summaryReviewed?: boolean }>();
  if (Array.isArray(payload.islands)) {
    for (const island of payload.islands) {
      if (!isRecord(island) || typeof island.id !== "string") {
        continue;
      }

      const patch: { summaryText?: string; summaryReviewed?: boolean } = {};
      if (typeof island.summaryText === "string") {
        patch.summaryText = island.summaryText;
      }
      if (typeof island.summaryReviewed === "boolean") {
        patch.summaryReviewed = island.summaryReviewed;
      }
      islandPatchById.set(island.id, patch);
    }
  }

  return {
    ...validated.document,
    islands: validated.document.islands.map((island) => ({
      ...island,
      ...(islandPatchById.get(island.id) ?? {}),
    })),
    readingOrder:
      Array.isArray(payload.readingOrder) && payload.readingOrder.every((entryId) => typeof entryId === "string")
        ? payload.readingOrder
        : validated.document.readingOrder ?? [],
    relationSummaries: parseComparisonRelationSummaries(payload.relationSummaries),
  };
}



function clipSnippet(value: string | undefined, maxLength = 80): string {
  const text = (value ?? "").trim();
  if (text.length <= maxLength) {
    return text;
  }

  return `${text.slice(0, maxLength)}…`;
}

function formatPatchEntitySnippet(value: unknown): string {
  if (!value || typeof value !== "object") {
    return "(none)";
  }

  if ("text" in value && "x" in value && "y" in value) {
    const card = value as { text?: string; x?: number; y?: number };
    return `text:${clipSnippet(card.text)} @(${String(card.x ?? "?")}, ${String(card.y ?? "?")})`;
  }

  if ("cardIds" in value && ("title" in value || "summaryText" in value)) {
    const island = value as { title?: string; summaryText?: string; cardIds?: string[] };
    return `title:${clipSnippet(island.title)} / summary:${clipSnippet(island.summaryText)} / members:${island.cardIds?.length ?? 0}`;
  }

  if ("fromId" in value && "toId" in value && "type" in value) {
    const edge = value as { fromId?: string; toId?: string; type?: string };
    return `${edge.fromId ?? "?"} -> ${edge.toId ?? "?"} (${edge.type ?? "?"})`;
  }

  if ("sourceSignature" in value && "text" in value && "reviewed" in value) {
    const summary = value as { text?: string; reviewed?: boolean; sourceSignature?: string };
    return `${summary.sourceSignature ?? "?"} / ${clipSnippet(summary.text)} / reviewed:${String(summary.reviewed)}`;
  }

  return clipSnippet(JSON.stringify(value));
}

function buildPatchPreviewItems(
  patch: PatchDocument,
  selectedOpIdSet: Set<string>,
  conflictByOpId: Map<string, ConflictItem>,
  resolutions: Record<string, PatchResolution>,
  lintIssuesByOpId: Map<string, PatchLintIssue[]>
): PatchPreviewItem[] {
  return patch.ops.map((op) => {
    const conflict = conflictByOpId.get(op.id);
    const lintIssues = lintIssuesByOpId.get(op.id) ?? [];

    return {
      opId: op.id,
      kind: op.kind,
      entityKey: getPatchOpEntityKey(op),
      checked: selectedOpIdSet.has(op.id),
      canToggle: !conflict,
      conflict: Boolean(conflict),
      lintIssueCount: lintIssues.length,
      lintErrorCount: lintIssues.filter((item) => item.severity === "error").length,
      lintIssueCodes: lintIssues.map((item) => item.code),
      reason: conflict?.reason,
      baseSnippet: conflict ? formatPatchEntitySnippet(conflict.baseValue) : undefined,
      yourSnippet: conflict ? formatPatchEntitySnippet(conflict.yourValue) : undefined,
      theirSnippet: conflict ? formatPatchEntitySnippet(conflict.theirValue) : undefined,
      resolution: conflict ? resolutions[op.id] : undefined,
    };
  });
}

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
    narratives: [],
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
    narratives: [],
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
      narratives: document.narratives ?? [],
    };
  }

  return {
    ...document,
    version: 2,
    islands: [],
    readingOrder: [],
    narratives: [],
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



function buildIslandPolygonFromCards(document: DocumentV2, island: Island): Point[] {
  const memberCards = document.cards.filter((card) => island.cardIds.includes(card.id));
  if (memberCards.length === 0) {
    return [];
  }

  const points: Point[] = [];
  for (const card of memberCards) {
    const right = card.x + CARD_WIDTH;
    const bottom = card.y + CARD_HEIGHT;
    points.push(
      { x: card.x, y: card.y },
      { x: right, y: card.y },
      { x: right, y: bottom },
      { x: card.x, y: bottom }
    );
  }

  const hull = computeConvexHull(points);
  if (hull.length < 3) {
    return [];
  }

  return padPolygonFromCentroid(hull, POLYGON_PADDING);
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

function areIdSetsEqual(a: Set<string>, b: Set<string>): boolean {
  if (a.size !== b.size) {
    return false;
  }

  for (const value of a) {
    if (!b.has(value)) {
      return false;
    }
  }

  return true;
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

function collectFocusedIslandIds(islands: Island[], focusIslandId: string): Set<string> {
  const islandsByParentId = new Map<string, Island[]>();

  for (const island of islands) {
    if (!island.parentIslandId) {
      continue;
    }

    const children = islandsByParentId.get(island.parentIslandId) ?? [];
    children.push(island);
    islandsByParentId.set(island.parentIslandId, children);
  }

  const focusedIslandIds = new Set<string>();
  const stack = [focusIslandId];

  while (stack.length > 0) {
    const islandId = stack.pop();
    if (!islandId || focusedIslandIds.has(islandId)) {
      continue;
    }

    focusedIslandIds.add(islandId);

    const children = islandsByParentId.get(islandId) ?? [];
    for (const child of children) {
      stack.push(child.id);
    }
  }

  return focusedIslandIds;
}

function applyFocusScope(document: DocumentV2, focusTarget: FocusTarget): DocumentV2 {
  if (!focusTarget.focusIslandId) {
    return document;
  }

  const hasFocusIsland = document.islands.some((island) => island.id === focusTarget.focusIslandId);
  if (!hasFocusIsland) {
    return document;
  }

  const focusedIslandIds = collectFocusedIslandIds(document.islands, focusTarget.focusIslandId);
  const focusedIslands = document.islands.filter((island) => focusedIslandIds.has(island.id));
  const focusedCardIdSet = new Set<string>();

  for (const island of focusedIslands) {
    for (const cardId of island.cardIds) {
      focusedCardIdSet.add(cardId);
    }
  }

  return {
    ...document,
    cards: document.cards.filter((card) => focusedCardIdSet.has(card.id)),
    edges: document.edges.filter(
      (edge) => focusedCardIdSet.has(edge.fromId) && focusedCardIdSet.has(edge.toId)
    ),
    islands: focusedIslands,
    readingOrder: (document.readingOrder ?? []).filter(
      (entryId) => focusedCardIdSet.has(entryId) || focusedIslandIds.has(entryId)
    ),
  };
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
  const [hideSourceCards, setHideSourceCards] = useState(true);
  const [hideMergedOriginals, setHideMergedOriginals] = useState(false);
  const [summaryView, setSummaryView] = useState(false);
  const [abstractMapView, setAbstractMapView] = useState(false);
  const [lodEnabled, setLodEnabled] = useState(false);
  const [lodThresholds, setLodThresholds] = useState<LODThresholds>(DEFAULT_LOD_THRESHOLDS);
  const [lodLevelOverride, setLodLevelOverride] = useState<LODLevel | null>(null);
  const [lodShowLoneWolvesWhenFar, setLodShowLoneWolvesWhenFar] = useState(true);
  const [safeMode, setSafeMode] = useState(true);
  const [showLabelBounds, setShowLabelBounds] = useState(false);
  const [includeUnreviewedDraftsInExport, setIncludeUnreviewedDraftsInExport] = useState(false);
  const [revealedSourceCardIds, setRevealedSourceCardIds] = useState<Set<string>>(new Set());
  const [showCanonicalOnlyEdges, setShowCanonicalOnlyEdges] = useState(false);
  const [showReadingOrder, setShowReadingOrder] = useState(false);
  const [isReadingOrderEditMode, setIsReadingOrderEditMode] = useState(false);
  const [readingNavEnabled, setReadingNavEnabled] = useState(false);
  const [readingIndex, setReadingIndex] = useState(0);
  const [readingMode, setReadingMode] = useState<ReadingMode>("islands");
  const [reviewedOnly, setReviewedOnly] = useState(false);
  const [outlineIncludeCardTexts, setOutlineIncludeCardTexts] = useState(false);
  const [outlineIncludeRelationSummaries, setOutlineIncludeRelationSummaries] = useState(true);
  const [outlineIncludeUnreviewed, setOutlineIncludeUnreviewed] = useState(false);
  const [pngExportScale, setPngExportScale] = useState<PngExportScale>(1);
  const [focusCardId, setFocusCardId] = useState<string | null>(null);
  const [focusTarget, setFocusTarget] = useState<FocusTarget>({});
  const [focusWorldPoint, setFocusWorldPoint] = useState<{ x: number; y: number } | null>(null);
  const [focusRequestSeq, setFocusRequestSeq] = useState(0);
  const [focusHistory, setFocusHistory] = useState<FocusSnapshot[]>([]);
  const [flashReference, setFlashReference] = useState<FocusReference | null>(null);
  const [flashRequestSeq, setFlashRequestSeq] = useState(0);
  const [narrativeText, setNarrativeText] = useState("");
  const [narrativeIssues, setNarrativeIssues] = useState<NarrativeIssue[]>([]);
  const [narrativeCheckError, setNarrativeCheckError] = useState<string | null>(null);
  const [isCheckingNarrative, setIsCheckingNarrative] = useState(false);
  const [isGeneratingNarrative, setIsGeneratingNarrative] = useState(false);
  const [narrativeGenerationError, setNarrativeGenerationError] = useState<string | null>(null);
  const [peekIslandId, setPeekIslandId] = useState<string | undefined>(undefined);
  const [summaryRevealIslandIds, setSummaryRevealIslandIds] = useState<Set<string>>(new Set());
  const [collapsedIslandIds, setCollapsedIslandIds] = useState<Set<string>>(new Set());
  const [temporaryRevealCardIds, setTemporaryRevealCardIds] = useState<Set<string>>(new Set());
  const [groundingVisibilityMessage, setGroundingVisibilityMessage] = useState<string | null>(null);
  const [isGridSnapEnabled, setIsGridSnapEnabled] = useState(false);
  const [isPolygonVertexEditEnabled, setIsPolygonVertexEditEnabled] = useState(false);
  const [mergeSuggestionInstruction, setMergeSuggestionInstruction] = useState("");
  const [mergeSuggestions, setMergeSuggestions] = useState<MergeSuggestionDraft[]>([]);
  const [mergeSuggestionError, setMergeSuggestionError] = useState<string | null>(null);
  const [isSuggestingMerges, setIsSuggestingMerges] = useState(false);
  const [isSuggestingIslandSummary, setIsSuggestingIslandSummary] = useState(false);
  const [islandSummarySuggestionWarningsByIslandId, setIslandSummarySuggestionWarningsByIslandId] = useState<Record<string, string[]>>({});
  const [isPickingEdgeTarget, setIsPickingEdgeTarget] = useState(false);
  const [connectEdgeType, setConnectEdgeType] = useState<"related" | "negate">("related");
  const [maxDepth, setMaxDepth] = useState<ViewMaxDepth>("all");
  const [isViewControlsOpen, setIsViewControlsOpen] = useState(false);
  const [isSharePanelOpen, setIsSharePanelOpen] = useState(false);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [visibleAggregatedEdges, setVisibleAggregatedEdges] = useState<AggregatedEdgeMeta[]>([]);
  const [isGeneratingRelationSummary, setIsGeneratingRelationSummary] = useState(false);
  const [comparisonDocument, setComparisonDocument] = useState<DocumentV2 | null>(null);
  const [comparisonFileName, setComparisonFileName] = useState<string | null>(null);
  const [pendingImportedDocument, setPendingImportedDocument] = useState<PendingImportedDocument | null>(null);
  const [importDocumentError, setImportDocumentError] = useState<string | null>(null);
  const [pendingPatchImport, setPendingPatchImport] = useState<PendingPatchImport | null>(null);
  const [patchImportError, setPatchImportError] = useState<string | null>(null);
  const [patchBaselineDoc, setPatchBaselineDoc] = useState<DocumentV2 | null>(null);
  const [patchBaselineFileName, setPatchBaselineFileName] = useState<string | null>(null);
  const [patchSelectedOpIdSet, setPatchSelectedOpIdSet] = useState<Set<string>>(new Set());
  const [patchResolutionsByOpId, setPatchResolutionsByOpId] = useState<Record<string, PatchResolution>>({});
  const [patchTrustLabel, setPatchTrustLabel] = useState<TrustLabel>("unknown");
  const [patchFingerprintStatus, setPatchFingerprintStatus] = useState<{ status: string; expected?: string; actual?: string } | null>(null);
  const [patchExportAuthor, setPatchExportAuthor] = useState("");
  const [patchExportAuthorNote, setPatchExportAuthorNote] = useState("");
  const [selectedFixProposalIdSet, setSelectedFixProposalIdSet] = useState<Set<string>>(new Set());

  const [canvasCamera, setCanvasCamera] = useState<CanvasCamera | null>(null);
  const [cameraTransformRequest, setCameraTransformRequest] = useState<CameraTransformRequest | null>(null);
  const collapsedStateDocIdRef = useRef<string | null>(null);

  const document = history?.present ?? null;
  const generatedNarratives = useMemo(() => document?.narratives ?? [], [document]);
  const isPreviewingSuggestion = Boolean(suggestedDocument) && isSuggestionPreviewEnabled;
  const visibleDocument = isPreviewingSuggestion && suggestedDocument ? suggestedDocument : document;
  const diffResult = useMemo(() => {
    if (!document || !comparisonDocument) {
      return null;
    }

    return diffDocuments(document, comparisonDocument);
  }, [comparisonDocument, document]);
  const currentCardIdSet = useMemo(() => new Set((document?.cards ?? []).map((card) => card.id)), [document?.cards]);
  const currentIslandIdSet = useMemo(() => new Set((document?.islands ?? []).map((island) => island.id)), [document?.islands]);
  const patchConflictReport = useMemo(() => {
    if (!document || !pendingPatchImport || !patchBaselineDoc) {
      return null;
    }

    return detectPatchConflicts(patchBaselineDoc, document, pendingPatchImport.patch);
  }, [document, patchBaselineDoc, pendingPatchImport]);
  const patchConflictByOpId = useMemo(() => {
    return new Map((patchConflictReport?.conflicts ?? []).map((item) => [item.opId, item]));
  }, [patchConflictReport]);
  const patchLintResult = useMemo(() => {
    if (!document || !pendingPatchImport) {
      return null;
    }

    return lintPatchAgainstCurrentDoc(document, pendingPatchImport.patch);
  }, [document, pendingPatchImport]);
  const patchFixProposals = useMemo(() => {
    if (!document || !pendingPatchImport || !patchLintResult) {
      return [] as FixProposal[];
    }

    return proposeFixes(document, pendingPatchImport.patch, patchLintResult);
  }, [document, patchLintResult, pendingPatchImport]);

  const patchLintIssuesByOpId = useMemo(() => {
    const next = new Map<string, PatchLintIssue[]>();
    for (const issue of patchLintResult?.issues ?? []) {
      if (!issue.opId) {
        continue;
      }

      const existing = next.get(issue.opId) ?? [];
      next.set(issue.opId, [...existing, issue]);
    }

    return next;
  }, [patchLintResult]);
  const patchPreviewItems = useMemo(() => {
    if (!pendingPatchImport) {
      return [] as PatchPreviewItem[];
    }

    return buildPatchPreviewItems(pendingPatchImport.patch, patchSelectedOpIdSet, patchConflictByOpId, patchResolutionsByOpId, patchLintIssuesByOpId);
  }, [patchConflictByOpId, patchLintIssuesByOpId, patchResolutionsByOpId, patchSelectedOpIdSet, pendingPatchImport]);
  const patchConflictWarning = useMemo(() => {
    if (!pendingPatchImport) {
      return null;
    }

    if (!patchBaselineDoc) {
      return "No baseline loaded. Conflict detection is disabled (H4 behavior).";
    }

    if (!patchConflictReport || patchConflictReport.conflicts.length === 0) {
      return null;
    }

    return `${patchConflictReport.conflicts.length} conflict(s) detected. Default resolution is Skip. Choose resolution to apply.`;
  }, [patchBaselineDoc, patchConflictReport, pendingPatchImport]);
  const patchBaselineSignatureMatch = useMemo(() => {
    if (!document || !patchBaselineDoc) {
      return undefined;
    }

    return patchBaselineDoc.id === document.id;
  }, [document, patchBaselineDoc]);
  const patchSummary = useMemo(() => {
    if (!pendingPatchImport) {
      return null;
    }

    return buildPatchSummary(pendingPatchImport.patch, patchConflictReport ?? undefined, patchBaselineSignatureMatch);
  }, [patchBaselineSignatureMatch, patchConflictReport, pendingPatchImport]);
  useEffect(() => {
    setSelectedFixProposalIdSet((previousSet) => {
      const nextIds = new Set(patchFixProposals.map((proposal) => proposal.fixId));
      return new Set([...previousSet].filter((id) => nextIds.has(id)));
    });
  }, [patchFixProposals]);

  const hasPatchSelection = patchSelectedOpIdSet.size > 0;
  const canApplyPatch = Boolean(document && pendingPatchImport && hasPatchSelection) && !shouldBlockPatchApplyByLint(patchLintResult);
  const focusedVisibleDocument = useMemo(() => {
    if (!visibleDocument) {
      return visibleDocument;
    }

    return applyFocusScope(visibleDocument, focusTarget);
  }, [focusTarget, visibleDocument]);

  useEffect(() => {
    setFocusHistory([]);
  }, [document?.id]);

  const temporaryRevealIslandIds = useMemo(() => {
    if (!document || temporaryRevealCardIds.size === 0) {
      return new Set<string>();
    }

    const revealedIslandIds = new Set<string>();
    for (const island of document.islands) {
      if (island.cardIds.some((cardId) => temporaryRevealCardIds.has(cardId))) {
        revealedIslandIds.add(island.id);
      }
    }

    return revealedIslandIds;
  }, [document, temporaryRevealCardIds]);
  const mergedRevealCardIds = useMemo(
    () => new Set([...revealedSourceCardIds, ...temporaryRevealCardIds]),
    [revealedSourceCardIds, temporaryRevealCardIds]
  );
  const suggestionMoveDiffs = useMemo(() => {
    if (!document || !suggestedDocument || !isPreviewingSuggestion) {
      return [] as SuggestionMoveDiff[];
    }

    const scopedBaseDocument = applyFocusScope(document, focusTarget);
    const scopedSuggestedDocument = applyFocusScope(suggestedDocument, focusTarget);
    const scopedBaseCardIds = new Set(scopedBaseDocument.cards.map((card) => card.id));

    const baseCardsById = new Map(scopedBaseDocument.cards.map((card) => [card.id, card]));

    return scopedSuggestedDocument.cards
      .filter((card) => scopedBaseCardIds.has(card.id))
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
  }, [document, focusTarget, isPreviewingSuggestion, suggestedDocument]);
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
  const collapseLodLevel = useMemo(() => {
    if (!lodEnabled) {
      return null;
    }

    const zoom = canvasCamera?.zoom ?? 1;
    return getLODLevel(zoom, { lodThresholds, lodLevelOverride }).level;
  }, [canvasCamera?.zoom, lodEnabled, lodLevelOverride, lodThresholds]);
  const collapsedIslandIdSet = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Set<string>();
    }

    const islandsByParentId = new Map<string, Island[]>();
    for (const island of focusedVisibleDocument.islands) {
      if (!island.parentIslandId) {
        continue;
      }

      const siblings = islandsByParentId.get(island.parentIslandId) ?? [];
      siblings.push(island);
      islandsByParentId.set(island.parentIslandId, siblings);
    }

    const hiddenIslandIds = new Set<string>();
    const stack = focusedVisibleDocument.islands.filter((island) => collapsedIslandIds.has(island.id));

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
  }, [collapsedIslandIds, focusedVisibleDocument]);
  const effectiveCollapsedIslandIdSet = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Set<string>();
    }

    const collapsedIds = summaryView
      ? new Set(focusedVisibleDocument.islands.map((island) => island.id))
      : new Set(
          focusedVisibleDocument.islands
            .filter((island) => isEffectivelyCollapsed(collapsedIslandIdSet.has(island.id), lodEnabled, collapseLodLevel))
            .map((island) => island.id)
        );

    for (const islandId of temporaryRevealIslandIds) {
      collapsedIds.delete(islandId);
    }
    for (const islandId of summaryRevealIslandIds) {
      collapsedIds.delete(islandId);
    }

    if (peekIslandId) {
      collapsedIds.delete(peekIslandId);
    }

    return collapsedIds;
  }, [collapseLodLevel, collapsedIslandIdSet, focusedVisibleDocument, lodEnabled, peekIslandId, summaryRevealIslandIds, summaryView, temporaryRevealIslandIds]);
  const islandDepthById = useMemo(() => {
    if (!visibleDocument) {
      return new Map<string, number>();
    }

    return getIslandDepthMap(visibleDocument.islands);
  }, [visibleDocument]);
  const cardMinDepthById = useMemo(() => {
    if (!visibleDocument) {
      return new Map<string, number>();
    }

    return getCardMinDepthMap(visibleDocument, islandDepthById);
  }, [visibleDocument, islandDepthById]);
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
    const summaryHiddenCardIds = new Set<string>();
    const searchHiddenCardIds = new Set<string>();
    const mergedHiddenCardIds = new Set<string>();

    if (focusedVisibleDocument) {
      // 1) collapseで隠れるカード
      for (const island of focusedVisibleDocument.islands) {
        if (!effectiveCollapsedIslandIdSet.has(island.id)) {
          continue;
        }
        for (const cardId of island.cardIds) {
          collapsedHiddenCardIds.add(cardId);
        }
      }

      if (summaryView && !focusTarget.focusIslandId) {
        for (const island of focusedVisibleDocument.islands) {
          const canRevealMembers =
            summaryRevealIslandIds.has(island.id) || temporaryRevealIslandIds.has(island.id) || peekIslandId === island.id;
          if (canRevealMembers) {
            continue;
          }

          for (const cardId of island.cardIds) {
            summaryHiddenCardIds.add(cardId);
          }
        }
      }

      if (abstractMapView) {
        for (const island of focusedVisibleDocument.islands) {
          const canRevealMembers =
            summaryRevealIslandIds.has(island.id) || temporaryRevealIslandIds.has(island.id) || peekIslandId === island.id;
          if (canRevealMembers) {
            continue;
          }

          for (const cardId of island.cardIds) {
            summaryHiddenCardIds.add(cardId);
          }
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

    if (hideMergedOriginals && focusedVisibleDocument) {
      for (const card of focusedVisibleDocument.cards) {
        if (typeof card.mergedIntoCardId === "string" && card.mergedIntoCardId.length > 0) {
          mergedHiddenCardIds.add(card.id);
        }
      }
    }

    // merge
    const hiddenCardIds = new Set<string>(collapsedHiddenCardIds);
    for (const cardId of depthHiddenCardIds) hiddenCardIds.add(cardId);
    for (const cardId of summaryHiddenCardIds) hiddenCardIds.add(cardId);
    for (const cardId of searchHiddenCardIds) hiddenCardIds.add(cardId);
    for (const cardId of mergedHiddenCardIds) hiddenCardIds.add(cardId);
    for (const cardId of temporaryRevealCardIds) {
      if (!depthHiddenCardIds.has(cardId)) {
        hiddenCardIds.delete(cardId);
      }
    }

    return hiddenCardIds;
  }, [
    cardMinDepthById,
    effectiveCollapsedIslandIdSet,
    focusTarget.focusIslandId,
    focusedVisibleDocument,
    hideNonMatches,
    hideMergedOriginals,
    matchedCardIdSet,
    maxDepth,
    normalizedSearchQuery,
    peekIslandId,
    summaryRevealIslandIds,
    summaryView,
    abstractMapView,
    temporaryRevealCardIds,
    temporaryRevealIslandIds,
  ]);

  const visibleCardIdSet = useMemo(() => {
    if (!focusedVisibleDocument) {
      return new Set<string>();
    }

    return new Set(
      focusedVisibleDocument.cards
        .map((card) => card.id)
        .filter((cardId) => !hiddenCardIdSet.has(cardId))
    );
  }, [focusedVisibleDocument, hiddenCardIdSet]);

  const canUndo = (history?.past.length ?? 0) > 0;
  const canRedo = (history?.future.length ?? 0) > 0;
  const pendingCardDragSnapshotRef = useRef<DocumentV2 | null>(null);
  const suppressNextTransformPersistRef = useRef(false);
  const importInputRef = useRef<HTMLInputElement | null>(null);
  const compareImportInputRef = useRef<HTMLInputElement | null>(null);
  const cardsById = useMemo(() => new Map((document?.cards ?? []).map((card) => [card.id, card])), [document]);
  const selectedAggregatedEdge = useMemo(() => {
    if (!selectedEdgeId) {
      return null;
    }

    return visibleAggregatedEdges.find((edge) => edge.id === selectedEdgeId) ?? null;
  }, [selectedEdgeId, visibleAggregatedEdges]);

  const selectedIslandRelationEdge = useMemo<IslandRelationEdgeSelection | null>(() => {
    if (!selectedAggregatedEdge || selectedAggregatedEdge.fromKind !== "island" || selectedAggregatedEdge.toKind !== "island") {
      return null;
    }

    if (selectedAggregatedEdge.isDerivedIslandEdge) {
      return {
        edgeId: selectedAggregatedEdge.id,
        fromIslandId: selectedAggregatedEdge.fromId,
        toIslandId: selectedAggregatedEdge.toId,
        type: selectedAggregatedEdge.type,
        isDerived: true,
        contributingEdgeIds: selectedAggregatedEdge.contributingEdgeIds ?? [],
        contributingCardIds: selectedAggregatedEdge.contributingCardIds ?? [],
      };
    }

    const sourceEdgeId = selectedAggregatedEdge.sources[0]?.sourceEdgeId ?? selectedAggregatedEdge.id;

    return {
      edgeId: sourceEdgeId,
      fromIslandId: selectedAggregatedEdge.fromId,
      toIslandId: selectedAggregatedEdge.toId,
      type: selectedAggregatedEdge.type,
      isDerived: false,
    };
  }, [selectedAggregatedEdge]);


  const selectedRelationSummary = useMemo<RelationSummary | null>(() => {
    if (!document || !selectedIslandRelationEdge) {
      return null;
    }

    const sourceSignature = buildRelationSummarySourceSignature(selectedIslandRelationEdge);
    return getRelationSummaryBySourceSignature(document, sourceSignature);
  }, [document, selectedIslandRelationEdge]);

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

  const requestCameraTransform = useCallback((nextTransform: { panX: number; panY: number; zoom: number }) => {
    suppressNextTransformPersistRef.current = true;
    setCameraTransformRequest((previousRequest) => ({
      panX: nextTransform.panX,
      panY: nextTransform.panY,
      zoom: nextTransform.zoom,
      requestSeq: (previousRequest?.requestSeq ?? 0) + 1,
    }));
  }, []);

  const pushCurrentFocusSnapshot = useCallback(() => {
    if (!canvasCamera) {
      return;
    }

    const currentSnapshot: FocusSnapshot = {
      camera: {
        panX: canvasCamera.panX,
        panY: canvasCamera.panY,
        zoom: canvasCamera.zoom,
      },
      viewState: {
        focusIslandId: focusTarget.focusIslandId,
        maxDepth,
      },
    };

    setFocusHistory((previousHistory) => pushFocusHistory(previousHistory, currentSnapshot));
  }, [canvasCamera, focusTarget.focusIslandId, maxDepth]);

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

  const handleSuggestIslandSummary = useCallback(async () => {
    if (!document || !selectedIslandId || isSuggestingIslandSummary) {
      return;
    }

    const targetIsland = document.islands.find((island) => island.id === selectedIslandId);
    if (!targetIsland) {
      return;
    }

    setIsSuggestingIslandSummary(true);
    setStatusMessage("Requesting island summary suggestion...");

    try {
      const result = await suggestIslandSummary(document, targetIsland.id);
      const nextDocument = updateIslandSummaryWithHistory(
        document,
        targetIsland.id,
        {
          summaryText: result.summaryText,
          summaryReviewed: false,
          summaryGrounding: result.groundingIds,
        },
        {
          changeKind: "ai",
        }
      );

      applyDocumentChange(nextDocument, "Suggested island summary");
      setIslandSummarySuggestionWarningsByIslandId((previousWarnings) => ({
        ...previousWarnings,
        [targetIsland.id]: result.warnings ?? [],
      }));
      setStatusMessage("Island summary suggestion ready (unreviewed)");
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Failed to suggest island summary";
      setStatusMessage(message);
    } finally {
      setIsSuggestingIslandSummary(false);
    }
  }, [applyDocumentChange, document, isSuggestingIslandSummary, selectedIslandId]);

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

      const cardsToCanonicalize = document.cards.filter((card) => suggestion.cardIds.includes(card.id));
      if (cardsToCanonicalize.length < 2) {
        setMergeSuggestionError("Merge suggestion is no longer applicable.");
        return;
      }
      let canonicalizedResult: ReturnType<typeof applyCanonicalization>;
      try {
        canonicalizedResult = applyCanonicalization(document, {
          sourceCardIds: suggestion.cardIds,
          mergedText: suggestion.editedText,
          canonicalIdFactory: () => crypto.randomUUID(),
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to adopt canonical suggestion.";
        setMergeSuggestionError(message);
        return;
      }

      applyDocumentChange(canonicalizedResult.document, "Adopted merge suggestion as canonical");
      setMergeSuggestions((previousSuggestions) => previousSuggestions.filter((item) => item.groupId !== groupId));
      setSelectedCardIds([canonicalizedResult.canonicalId]);
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

      setIsSharePanelOpen(true);

      try {
        const rawText = await selectedFile.text();
        const parsedJson: unknown = JSON.parse(rawText);
        const validation = validateDocumentV2Strict(parsedJson);

        if (!validation.ok) {
          const details = validation.errors.slice(0, 6).map((error) => `- ${error}`).join("\n");
          const suffix = validation.errors.length > 6 ? `\n- ...and ${validation.errors.length - 6} more` : "";
          setPendingImportedDocument(null);
          setImportDocumentError(`Document validation failed:\n${details}${suffix}`);
          setStatusMessage("Failed to load document JSON");
          return;
        }

        setPendingImportedDocument({
          fileName: selectedFile.name,
          document: validation.document,
        });
        setImportDocumentError(null);
        setStatusMessage("Document validated. Review summary, then click Replace current document.");
      } catch (error) {
        setPendingImportedDocument(null);

        if (error instanceof SyntaxError) {
          setImportDocumentError("Document validation failed:\n- invalid JSON syntax");
          setStatusMessage("Failed to parse document JSON file");
          return;
        }

        const message = error instanceof Error ? error.message : "Unknown error";
        setImportDocumentError(`Document validation failed:\n- ${message}`);
        setStatusMessage("Failed to load document JSON");
      }
    },
    []
  );

  const handleImportClick = useCallback(() => {
    importInputRef.current?.click();
  }, []);

  const handleLoadComparisonDocumentClick = useCallback(() => {
    compareImportInputRef.current?.click();
  }, []);

  const handleComparisonFileChange = useCallback(async (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    try {
      const rawText = await selectedFile.text();
      const parsedJson: unknown = JSON.parse(rawText);
      const parsedDocument = extractComparisonDocument(parsedJson);

      if (!parsedDocument) {
        setStatusMessage("Failed to load comparison file: expected a valid document JSON");
        return;
      }

      setComparisonDocument(parsedDocument);
      setComparisonFileName(selectedFile.name);
      setStatusMessage("Loaded comparison document (view-only)");
    } catch (error) {
      if (error instanceof SyntaxError) {
        setStatusMessage("Failed to parse comparison JSON file");
        return;
      }

      setStatusMessage(error instanceof Error ? error.message : "Failed to load comparison document");
    }
  }, []);

  const handleLoadViewMetadataFile = useCallback(
    async (selectedFile: File) => {
      if (!document) {
        setStatusMessage("No document loaded");
        return;
      }

      try {
        const rawText = await selectedFile.text();
        const parsedJson: unknown = JSON.parse(rawText);
        const validateResult = validateImportViewMetadata(parsedJson);

        if (!validateResult.ok) {
          setStatusMessage(`Failed to load view metadata: ${validateResult.error}`);
          return;
        }

        const metadata = validateResult.metadata;
        const hasFocusIsland =
          metadata.viewState.focusIslandId === null
            ? false
            : document.islands.some((island) => island.id === metadata.viewState.focusIslandId);

        setSummaryView(metadata.viewState.summaryView || metadata.viewState.abstractMapView);
        setAbstractMapView(metadata.viewState.abstractMapView);
        setHideSourceCards(metadata.viewState.hideSourceCards);
        setMaxDepth(metadata.viewState.maxDepth);
        setShowReadingOrder(metadata.viewState.showReadingOrder);
        setReadingNavEnabled(metadata.viewState.readingNavEnabled ?? false);
        setReadingMode(metadata.viewState.readingMode ?? "islands");
        setReviewedOnly(metadata.viewState.reviewedOnly ?? false);
        setReadingIndex(metadata.viewState.readingIndex ?? 0);
        setSafeMode(metadata.viewState.safeMode ?? true);
        setLodEnabled(metadata.viewState.lodEnabled ?? false);
        setLodThresholds(metadata.viewState.lodThresholds ?? DEFAULT_LOD_THRESHOLDS);
        setLodLevelOverride(metadata.viewState.lodLevelOverride ?? null);
        setLodShowLoneWolvesWhenFar(metadata.viewState.lodShowLoneWolvesWhenFar ?? true);
        setIncludeUnreviewedDraftsInExport(false);
        setIsReadingOrderEditMode(false);
        setRevealedSourceCardIds(new Set());
        setFocusCardId(null);
        setFocusWorldPoint(null);
        suppressNextTransformPersistRef.current = true;
        setCameraTransformRequest((previousRequest) => ({
          panX: metadata.camera.panX,
          panY: metadata.camera.panY,
          zoom: metadata.camera.zoom,
          requestSeq: (previousRequest?.requestSeq ?? 0) + 1,
        }));

        if (metadata.viewState.focusIslandId && !hasFocusIsland) {
          setFocusTarget({});
          setStatusMessage(`Loaded view metadata; focus island not found (${metadata.viewState.focusIslandId}). Focus was cleared.`);
          return;
        }

        setFocusTarget(metadata.viewState.focusIslandId ? { focusIslandId: metadata.viewState.focusIslandId } : {});
        setStatusMessage("Loaded view metadata");
      } catch (error) {
        if (error instanceof SyntaxError) {
          setStatusMessage("Failed to load view metadata: invalid JSON");
          return;
        }

        const message = error instanceof Error ? error.message : "Unknown error";
        setStatusMessage(`Failed to load view metadata: ${message}`);
      }
    },
    [document]
  );

  const handleLoadDocumentFile = useCallback(async (selectedFile: File) => {
    try {
      const rawText = await selectedFile.text();
      const parsedJson: unknown = JSON.parse(rawText);
      const validation = validateDocumentV2Strict(parsedJson);

      if (!validation.ok) {
        const details = validation.errors.slice(0, 6).map((error) => `- ${error}`).join("\n");
        const suffix = validation.errors.length > 6 ? `\n- ...and ${validation.errors.length - 6} more` : "";
        setPendingImportedDocument(null);
        setImportDocumentError(`Document validation failed:\n${details}${suffix}`);
        setStatusMessage("Failed to load document JSON");
        return;
      }

      setPendingImportedDocument({
        fileName: selectedFile.name,
        document: validation.document,
      });
      setImportDocumentError(null);
      setStatusMessage("Document validated. Review summary, then click Replace current document.");
    } catch (error) {
      setPendingImportedDocument(null);

      if (error instanceof SyntaxError) {
        setImportDocumentError("Document validation failed:\n- invalid JSON syntax");
        setStatusMessage("Failed to parse document JSON file");
        return;
      }

      const message = error instanceof Error ? error.message : "Unknown error";
      setImportDocumentError(`Document validation failed:\n- ${message}`);
      setStatusMessage("Failed to load document JSON");
    }
  }, []);

  const handleLoadPatchFile = useCallback(async (selectedFile: File) => {
    try {
      const rawText = await selectedFile.text();
      const parsedJson: unknown = JSON.parse(rawText);
      const parsedPatch = parsePatchDocument(parsedJson);

      if (!parsedPatch) {
        setPendingPatchImport(null);
        setPatchFingerprintStatus(null);
        setPatchTrustLabel("unknown");
        setPatchImportError("Patch validation failed:\n- invalid patch schema");
        setStatusMessage("Failed to load patch JSON");
        return;
      }

      const fingerprintVerification = await verifyPatchFingerprint(parsedPatch);
      if (!parsedPatch.patchFingerprint) {
        setPatchFingerprintStatus({ status: "No fingerprint (Unknown)" });
        setPatchTrustLabel("unknown");
      } else if (fingerprintVerification.ok) {
        setPatchFingerprintStatus({
          status: "Fingerprint OK",
          expected: fingerprintVerification.expected,
          actual: fingerprintVerification.actual,
        });
        setPatchTrustLabel("unknown");
      } else {
        setPatchFingerprintStatus({
          status: "Fingerprint mismatch (Untrusted)",
          expected: fingerprintVerification.expected,
          actual: fingerprintVerification.actual,
        });
        setPatchTrustLabel("untrusted");
      }

      setPendingPatchImport({
        fileName: selectedFile.name,
        originalPatch: parsedPatch,
        patch: parsedPatch,
      });
      setPatchSelectedOpIdSet(new Set(parsedPatch.ops.map((op) => op.id)));
      const nextResolutions: Record<string, PatchResolution> = {};
      for (const op of parsedPatch.ops) {
        nextResolutions[op.id] = "skip";
      }
      setPatchResolutionsByOpId(nextResolutions);
      setPatchImportError(null);
      setSelectedFixProposalIdSet(new Set());
      setStatusMessage("Patch loaded");
    } catch (error) {
      setPendingPatchImport(null);
      setPatchFingerprintStatus(null);
      setPatchTrustLabel("unknown");
      if (error instanceof SyntaxError) {
        setPatchImportError("Patch validation failed:\n- invalid JSON syntax");
      } else {
        const message = error instanceof Error ? error.message : "Unknown error";
        setPatchImportError(`Patch validation failed:\n- ${message}`);
      }
      setStatusMessage("Failed to load patch JSON");
    }
  }, []);

  const handleLoadPatchBaselineFile = useCallback(async (selectedFile: File) => {
    try {
      const rawText = await selectedFile.text();
      const parsedJson: unknown = JSON.parse(rawText);
      const validation = validateDocumentV2Strict(parsedJson);

      if (!validation.ok) {
        setPatchBaselineDoc(null);
        setPatchBaselineFileName(null);
        setStatusMessage("Failed to load baseline document JSON");
        return;
      }

      setPatchBaselineDoc(validation.document);
      setPatchBaselineFileName(selectedFile.name);
      setStatusMessage("Loaded baseline for patch conflict detection");
    } catch {
      setPatchBaselineDoc(null);
      setPatchBaselineFileName(null);
      setStatusMessage("Failed to load baseline document JSON");
    }
  }, []);

  const handleFixProposalCheckedChange = useCallback((fixId: string, checked: boolean) => {
    setSelectedFixProposalIdSet((previousSet) => {
      const next = new Set(previousSet);
      if (checked) {
        next.add(fixId);
      } else {
        next.delete(fixId);
      }
      return next;
    });
  }, []);

  const handleApplySelectedPatchFixes = useCallback(() => {
    if (!pendingPatchImport || selectedFixProposalIdSet.size === 0) {
      setStatusMessage("No fix selected");
      return;
    }

    const nextPatch = applyFixesToPatch(pendingPatchImport.patch, [...selectedFixProposalIdSet], patchFixProposals);
    setPendingPatchImport({
      ...pendingPatchImport,
      patch: nextPatch,
    });

    setPatchSelectedOpIdSet((previousSet) => {
      const nextOpIds = new Set(nextPatch.ops.map((op) => op.id));
      return new Set([...previousSet].filter((opId) => nextOpIds.has(opId)));
    });

    setPatchResolutionsByOpId((previousMap) => {
      const nextMap: Record<string, PatchResolution> = {};
      for (const op of nextPatch.ops) {
        nextMap[op.id] = previousMap[op.id] ?? "skip";
      }
      return nextMap;
    });

    setStatusMessage("Patch updated; re-running lint…");
  }, [patchFixProposals, pendingPatchImport, selectedFixProposalIdSet]);

  const handleExportPatchFile = useCallback(async () => {
    if (!pendingPatchImport) {
      setStatusMessage("No patch loaded");
      return;
    }

    const exportedPatch = await buildPatchForExport(pendingPatchImport.patch, {
      author: patchExportAuthor,
      authorNote: patchExportAuthorNote,
      sourceApp: "kj-atlas",
    });

    downloadTextFile(`${pendingPatchImport.fileName.replace(/\.json$/i, "")}.export.json`, "application/json", `${JSON.stringify(exportedPatch, null, 2)}\n`);
    setStatusMessage("Exported patch with fingerprint");
  }, [patchExportAuthor, patchExportAuthorNote, pendingPatchImport]);

  const handleResetPatchToOriginal = useCallback(() => {
    if (!pendingPatchImport) {
      return;
    }

    const originalPatch = pendingPatchImport.originalPatch;
    setPendingPatchImport({
      ...pendingPatchImport,
      patch: originalPatch,
    });
    setPatchSelectedOpIdSet(new Set(originalPatch.ops.map((op) => op.id)));

    const nextResolutions: Record<string, PatchResolution> = {};
    for (const op of originalPatch.ops) {
      nextResolutions[op.id] = "skip";
    }
    setPatchResolutionsByOpId(nextResolutions);
    setStatusMessage("Patch reset to original");
  }, [pendingPatchImport]);

  const handleApplyPatch = useCallback(() => {
    if (!document || !pendingPatchImport) {
      setStatusMessage("No patch loaded");
      return;
    }

    if (shouldBlockPatchApplyByLint(patchLintResult)) {
      setStatusMessage("Resolve lint errors first");
      return;
    }

    const applyResult = applyPatchWithResolutionsDetailed(
      document,
      pendingPatchImport.patch,
      patchResolutionsByOpId,
      patchBaselineDoc ?? undefined,
      patchSelectedOpIdSet
    );

    const nextDocument = appendPatchApplyLog(applyResult.document, pendingPatchImport.patch, {
      ...applyResult.meta,
      patchTitle: pendingPatchImport.fileName,
      baseDocSignature: patchBaselineDoc ? `${patchBaselineDoc.id}:${patchBaselineDoc.updatedAt}` : undefined,
    });

    applyDocumentChange(nextDocument, "Applied patch");
  }, [applyDocumentChange, document, patchBaselineDoc, patchLintResult, patchResolutionsByOpId, patchSelectedOpIdSet, pendingPatchImport]);


  const handleCopyPatchApplyLogEntry = useCallback(async (entryId: string) => {
    const entry = document?.patchApplyLog?.find((item) => item.id === entryId);
    if (!entry) {
      setStatusMessage("Patch apply log entry not found");
      return;
    }

    try {
      await navigator.clipboard.writeText(formatPatchApplyLogEntryMarkdown(entry));
      setStatusMessage("Copied patch apply log entry (Markdown)");
    } catch {
      setStatusMessage("Failed to copy patch apply log entry");
    }
  }, [document]);

  const handleCopyPatchSummary = useCallback(async () => {
    if (!patchSummary) {
      setStatusMessage("No patch summary available");
      return;
    }

    try {
      await navigator.clipboard.writeText(formatPatchSummaryMarkdown(patchSummary));
      setStatusMessage("Copied patch summary (Markdown)");
    } catch {
      setStatusMessage("Failed to copy patch summary");
    }
  }, [patchSummary]);

  const handleReplaceCurrentDocument = useCallback(() => {
    if (!pendingImportedDocument) {
      setStatusMessage("No validated document is pending replacement");
      return;
    }

    pendingCardDragSnapshotRef.current = null;
    setHistory({
      past: [],
      present: cloneDocument(pendingImportedDocument.document),
      future: [],
    });
    setActiveDocumentId(pendingImportedDocument.document.id);
    setSelectedRecentDocumentId("");
    setDocEtag(null);
    setSelectedCardIds([]);
    setSelectedIslandId(null);
    setSelectedEdgeId(null);
    setIsPickingEdgeTarget(false);
    setFocusCardId(null);
    setFocusTarget({});
    setFocusWorldPoint(null);
    setPeekIslandId(undefined);
    setFlashReference(null);
    setTemporaryRevealCardIds(new Set());
    setSummaryRevealIslandIds(new Set());
    setRevealedSourceCardIds(new Set());
    setComparisonDocument(null);
    setComparisonFileName(null);
    setGroundingVisibilityMessage(null);
    setIsDirty(true);
    setHasSaveConflict(false);
    setSuggestedDocument(null);
    setSuggestionId(null);
    setSuggestionNotes(null);
    setSuggestionError(null);
    setPendingImportedDocument(null);
    setImportDocumentError(null);
    setStatusMessage("Replaced current document");
  }, [pendingImportedDocument]);

  const handleEdgeSelect = useCallback((edgeId: string) => {
    setSelectedEdgeId(edgeId);
    setSelectedCardIds([]);
    setSelectedIslandId(null);
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

    if (document && isReadingOrderEditMode && isShiftPressed) {
      const nextReadingOrder = appendReadingOrderEntry(document.readingOrder ?? [], cardId, visibleCardIdSet);
      if (nextReadingOrder !== (document.readingOrder ?? [])) {
        applyDocumentChange(
          {
            ...document,
            readingOrder: nextReadingOrder,
          },
          "Added card to reading order"
        );
        return;
      }
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
    setSelectedEdgeId(null);
  }, [
    applyDocumentChange,
    connectEdgeType,
    document,
    isAnnotateOverlayEnabled,
    isPickingEdgeTarget,
    isPreviewingSuggestion,
    isReadingOrderEditMode,
    selectedCardIds,
    selectedIslandId,
    visibleCardIdSet,
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
    setSelectedEdgeId(null);
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
    setSelectedEdgeId(null);
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
    setSelectedEdgeId(null);
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

  const handleCreateRepresentativeCard = useCallback(() => {
    if (!document || selectedCardIds.length < 2) {
      return;
    }

    const selectedCards = document.cards.filter((card) => selectedCardIds.includes(card.id));
    const representativeText = window.prompt("Enter representative card text", selectedCards[0]?.text ?? "");
    if (representativeText === null) {
      return;
    }

    const shouldRewire = window.confirm(
      "Rewire island membership and card edges to the representative card?"
    );

    const mergeResult = createRepresentativeMerge(document, selectedCardIds, representativeText, {
      rewireMembershipAndEdges: shouldRewire,
    });

    if (!mergeResult) {
      setStatusMessage("Representative card text is required");
      return;
    }

    applyDocumentChange(mergeResult.nextDocument, "Created representative card");
    setSelectedIslandId(null);
    setSelectedEdgeId(null);
    setSelectedCardIds([mergeResult.representativeCardId]);
    setStatusMessage(
      `Created representative card from ${mergeResult.mergedCardCount} originals${
        shouldRewire ? " (rewired)" : ""
      }`
    );
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
      const nextDocument = updateIslandSummaryWithHistory(
        document,
        islandId,
        {
          summaryText: nextSummaryText,
          summaryReviewed: true,
        },
        {
          changeKind: "manual",
        }
      );

      if (nextDocument === document) {
        return;
      }

      applyDocumentChange(nextDocument, "Updated island summary");
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

  const handleRestoreIslandSummaryVersion = useCallback(
    (islandId: string, historyEntryId: string) => {
      if (!document) {
        return;
      }

      const island = document.islands.find((item) => item.id === islandId);
      const historyEntry = island?.summaryHistory?.find((entry) => entry.id === historyEntryId);
      if (!island || !historyEntry) {
        return;
      }

      const restoredSummaryText = historyEntry.toText ?? undefined;
      const nextDocument = updateIslandSummaryWithHistory(
        document,
        islandId,
        {
          summaryText: restoredSummaryText,
          summaryReviewed: historyEntry.toReviewed ?? false,
        },
        {
          changeKind: "manual",
          note: `rollback:${historyEntry.id}`,
          forceHistoryEntry: true,
        }
      );

      if (nextDocument === document) {
        return;
      }

      applyDocumentChange(nextDocument, "Restored island summary version");
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

  const handleGenerateIslandPolygon = useCallback(
    (islandId: string) => {
      if (!document) {
        return;
      }

      const targetIsland = document.islands.find((island) => island.id === islandId);
      if (!targetIsland) {
        return;
      }

      const polygonPoints = buildIslandPolygonFromCards(document, targetIsland);
      const generatedFrom = {
        cardIds: [...targetIsland.cardIds],
        versionToken: buildVersionTokenForCardIds(document.cards, targetIsland.cardIds, CARD_WIDTH, CARD_HEIGHT),
      };
      const nextShape =
        polygonPoints.length < 3
          ? {
              kind: "rect" as const,
              generatedFrom,
            }
          : {
              kind: "polygon" as const,
              points: polygonPoints,
              generatedFrom,
            };

      const currentShape = targetIsland.shape;
      const generatedFromUnchanged =
        (currentShape?.generatedFrom?.versionToken ?? null) === generatedFrom.versionToken &&
        ((currentShape?.generatedFrom?.cardIds?.length ?? 0) === generatedFrom.cardIds.length &&
          generatedFrom.cardIds.every((cardId, index) => currentShape?.generatedFrom?.cardIds?.[index] === cardId));
      const shapeUnchanged =
        currentShape?.kind === nextShape.kind &&
        (nextShape.kind === "rect" ||
          ((currentShape?.kind === "polygon" ? currentShape.points.length : 0) === nextShape.points.length &&
            nextShape.points.every((point, index) => {
              const currentPoint = currentShape?.kind === "polygon" ? currentShape.points[index] : undefined;
              return currentPoint ? currentPoint.x === point.x && currentPoint.y === point.y : false;
            }))) &&
        generatedFromUnchanged;

      if (shapeUnchanged) {
        setStatusMessage(
          nextShape.kind === "rect"
            ? "Polygon generation fell back to rect (not enough unique corners)"
            : "Polygon already up to date"
        );
        return;
      }

      applyDocumentChange(
        {
          ...document,
          islands: document.islands.map((island) =>
            island.id === islandId
              ? {
                  ...island,
                  shape: nextShape,
                }
              : island
          ),
        },
        nextShape.kind === "rect" ? "Fell back to rect island shape" : "Generated polygon island shape"
      );

      setStatusMessage(
        nextShape.kind === "rect"
          ? "Polygon generation fell back to rect (not enough unique corners)"
          : "Generated polygon from member cards"
      );
    },
    [applyDocumentChange, document]
  );

  const handlePolygonVertexMove = useCallback(
    (islandId: string, vertexIndex: number, point: Point) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId || island.shape?.kind !== "polygon") {
          return island;
        }

        if (vertexIndex < 0 || vertexIndex >= island.shape.points.length) {
          return island;
        }

        const currentPoint = island.shape.points[vertexIndex];
        if (currentPoint.x === point.x && currentPoint.y === point.y) {
          return island;
        }

        const nextPoints = island.shape.points.map((targetPoint, index) =>
          index === vertexIndex ? { ...point } : targetPoint
        );

        return {
          ...island,
          shape: {
            ...island.shape,
            points: nextPoints,
          },
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
        "Moved polygon vertex"
      );
    },
    [applyDocumentChange, document]
  );

  const handlePolygonVertexAdd = useCallback(
    (islandId: string, segmentStartIndex: number, point: Point) => {
      if (!document) {
        return;
      }

      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId || island.shape?.kind !== "polygon") {
          return island;
        }

        if (segmentStartIndex < 0 || segmentStartIndex >= island.shape.points.length) {
          return island;
        }

        const nextPoints = [...island.shape.points];
        nextPoints.splice(segmentStartIndex + 1, 0, { ...point });

        return {
          ...island,
          shape: {
            ...island.shape,
            points: nextPoints,
          },
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
        "Added polygon vertex"
      );
    },
    [applyDocumentChange, document]
  );

  const handlePolygonVertexRemove = useCallback(
    (islandId: string, vertexIndex: number) => {
      if (!document) {
        return;
      }

      let blockedByMinimum = false;
      const nextIslands = document.islands.map((island) => {
        if (island.id !== islandId || island.shape?.kind !== "polygon") {
          return island;
        }

        if (vertexIndex < 0 || vertexIndex >= island.shape.points.length) {
          return island;
        }

        if (island.shape.points.length <= 3) {
          blockedByMinimum = true;
          return island;
        }

        return {
          ...island,
          shape: {
            ...island.shape,
            points: island.shape.points.filter((_, index) => index !== vertexIndex),
          },
        };
      });

      if (blockedByMinimum) {
        setStatusMessage("Polygon needs at least 3 points");
        return;
      }

      const hasChanges = nextIslands.some((island, index) => island !== document.islands[index]);
      if (!hasChanges) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          islands: nextIslands,
        },
        "Removed polygon vertex"
      );
    },
    [applyDocumentChange, document]
  );

  const handleIslandCollapsedChange = useCallback(
    (islandId: string, collapsed: boolean) => {
      setCollapsedIslandIds((previous) => {
        const alreadyCollapsed = previous.has(islandId);
        if (alreadyCollapsed === collapsed) {
          return previous;
        }

        const next = new Set(previous);
        if (collapsed) {
          next.add(islandId);
        } else {
          next.delete(islandId);
        }

        return next;
      });
      setStatusMessage(collapsed ? "Collapsed island" : "Expanded island");
    },
    []
  );

  const handleCollapseAllIslands = useCallback(() => {
    if (!document) {
      return;
    }

    setCollapsedIslandIds(new Set(document.islands.map((island) => island.id)));
    setStatusMessage("Collapsed all islands");
  }, [document]);

  const handleExpandAllIslands = useCallback(() => {
    setCollapsedIslandIds(new Set());
    setStatusMessage("Expanded all islands");
  }, []);

  useEffect(() => {
    if (!document) {
      collapsedStateDocIdRef.current = null;
      setCollapsedIslandIds(new Set());
      return;
    }

    const isDocumentChanged = collapsedStateDocIdRef.current !== document.id;
    collapsedStateDocIdRef.current = document.id;

    setCollapsedIslandIds((previous) => {
      const validIslandIds = new Set(document.islands.map((island) => island.id));

      if (isDocumentChanged) {
        const fallbackCollapsedIds = collectCollapsedIslandIds(document.islands);
        const seeded = new Set<string>();
        for (const islandId of fallbackCollapsedIds) {
          if (validIslandIds.has(islandId)) {
            seeded.add(islandId);
          }
        }

        return seeded;
      }

      const next = new Set<string>();
      for (const islandId of previous) {
        if (validIslandIds.has(islandId)) {
          next.add(islandId);
        }
      }

      return areIdSetsEqual(previous, next) ? previous : next;
    });
  }, [document]);

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

      return !island.parentIslandId || !effectiveCollapsedIslandIdSet.has(island.parentIslandId);
    });
  }, [depthHiddenIslandIdSet, effectiveCollapsedIslandIdSet, uniqueIslands]);

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

  useEffect(() => {
    setRevealedSourceCardIds(new Set());
  }, [document?.id]);

  useEffect(() => {
    if (!summaryView) {
      setSummaryRevealIslandIds(new Set());
      return;
    }

    if (!focusedVisibleDocument) {
      return;
    }

    const visibleIslands = new Set(focusedVisibleDocument.islands.map((island) => island.id));
    setSummaryRevealIslandIds((previousIds) => {
      const nextIds = new Set(Array.from(previousIds).filter((islandId) => visibleIslands.has(islandId)));
      const isUnchanged =
        nextIds.size === previousIds.size &&
        Array.from(nextIds).every((islandId) => previousIds.has(islandId));
      if (isUnchanged) {
        return previousIds;
      }
      return nextIds;
    });
  }, [abstractMapView, focusedVisibleDocument, summaryView]);

  const selectedIsland = useMemo(() => {
    if (!document || !selectedIslandId) {
      return null;
    }

    return document.islands.find((island) => island.id === selectedIslandId) ?? null;
  }, [document, selectedIslandId]);

  useEffect(() => {
    if (selectedIsland?.shape?.kind === "polygon") {
      return;
    }

    setIsPolygonVertexEditEnabled(false);
  }, [selectedIsland]);

  const stalePolygonIslandIdSet = useMemo(() => {
    if (!document) {
      return new Set<string>();
    }

    return new Set(
      document.islands
        .filter((island) => isPolygonShapeStale(island, document.cards, CARD_WIDTH, CARD_HEIGHT))
        .map((island) => island.id)
    );
  }, [document]);

  const selectedCard = useMemo(() => {
    if (!document || selectedCardIds.length !== 1) {
      return null;
    }

    return document.cards.find((card) => card.id === selectedCardIds[0]) ?? null;
  }, [document?.cards, selectedCardIds]);

  const sourceCardsForSelectedCanonical = useMemo(() => {
    if (!document || !selectedCard || selectedCard.canonicalId || (selectedCard.sources ?? []).length === 0) {
      return [] as DocumentV2["cards"];
    }

    const cardsById = new Map(document.cards.map((card) => [card.id, card]));
    return (selectedCard.sources ?? [])
      .map((sourceId) => cardsById.get(sourceId))
      .filter((card): card is DocumentV2["cards"][number] => card !== undefined);
  }, [document, selectedCard]);

  const summaryGroundingItems = useMemo<Array<{ id: string; text: string; kind: "canonical" | "source" }>>(() => {
    if (!selectedIsland || !selectedIsland.summaryGrounding || selectedIsland.summaryGrounding.length === 0) {
      return [] as Array<{ id: string; text: string; kind: "canonical" | "source" }>;
    }

    return selectedIsland.summaryGrounding
      .map((groundingCardId) => cardsById.get(groundingCardId))
      .filter((card): card is DocumentV2["cards"][number] => card !== undefined)
      .map((card) => ({
        id: card.id,
        text: card.text,
        kind: isSourceCard(card) ? "source" : "canonical",
      }));
  }, [cardsById, selectedIsland]);

  const handleSourceCardInspect = useCallback((sourceCardId: string) => {
    requestCanvasFocus(sourceCardId);
    setRevealedSourceCardIds((previousIds) => {
      if (previousIds.has(sourceCardId)) {
        return previousIds;
      }

      const nextIds = new Set(previousIds);
      nextIds.add(sourceCardId);
      return nextIds;
    });
  }, [requestCanvasFocus]);

  useEffect(() => {
    setTemporaryRevealCardIds(new Set());
  }, [document?.id]);

  useEffect(() => {
    if (!groundingVisibilityMessage) {
      return;
    }

    const timeoutId = window.setTimeout(() => {
      setGroundingVisibilityMessage(null);
    }, 2500);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [groundingVisibilityMessage]);

  const revealCardsTemporarily = useCallback((cardIds: string[]) => {
    if (cardIds.length === 0) {
      return;
    }

    setTemporaryRevealCardIds((previousIds) => {
      const nextIds = new Set(previousIds);
      for (const cardId of cardIds) {
        nextIds.add(cardId);
      }
      if (nextIds.size === previousIds.size) {
        return previousIds;
      }
      return nextIds;
    });
  }, []);

  const clearTemporaryReveal = useCallback(() => {
    setTemporaryRevealCardIds((previousIds) => (previousIds.size === 0 ? previousIds : new Set()));
  }, []);

  const handleSummaryGroundingCardInspect = useCallback((cardId: string) => {
    if (!document) {
      return;
    }

    const hasTargetCard = document.cards.some((card) => card.id === cardId);
    if (!hasTargetCard) {
      setStatusMessage(`Item not found: card:${cardId}`);
      return;
    }

    const isInFocusScope = focusedVisibleDocument?.cards.some((card) => card.id === cardId) ?? false;
    const isWithinDepth = maxDepth === "all" || (cardMinDepthById.get(cardId) ?? 0) <= maxDepth;
    if (!isTemporaryRevealEligible({ isInFocusScope, isWithinDepth })) {
      setGroundingVisibilityMessage("This card is hidden by Focus/Depth view controls.");
      return;
    }

    requestCanvasFocus(cardId);
    revealCardsTemporarily([cardId]);
  }, [cardMinDepthById, document, focusedVisibleDocument?.cards, maxDepth, requestCanvasFocus, revealCardsTemporarily]);

  const handleShowAllSummaryGrounding = useCallback(() => {
    if (!selectedIsland?.summaryGrounding || selectedIsland.summaryGrounding.length === 0) {
      return;
    }

    revealCardsTemporarily(selectedIsland.summaryGrounding);
    const firstEligibleCardId = selectedIsland.summaryGrounding.find((cardId) => {
      const isInFocusScope = focusedVisibleDocument?.cards.some((card) => card.id === cardId) ?? false;
      const isWithinDepth = maxDepth === "all" || (cardMinDepthById.get(cardId) ?? 0) <= maxDepth;
      return isTemporaryRevealEligible({ isInFocusScope, isWithinDepth });
    });

    if (firstEligibleCardId) {
      requestCanvasFocus(firstEligibleCardId);
    }
  }, [cardMinDepthById, focusedVisibleDocument?.cards, maxDepth, requestCanvasFocus, revealCardsTemporarily, selectedIsland]);

  const handleRevealSelectedEdgeSources = useCallback(() => {
    if (!selectedAggregatedEdge) {
      return;
    }

    if (selectedAggregatedEdge.isDerivedIslandEdge) {
      revealCardsTemporarily(selectedAggregatedEdge.contributingCardIds ?? []);
      return;
    }

    const sourceCardIds = new Set<string>();
    for (const source of selectedAggregatedEdge.sources) {
      sourceCardIds.add(source.sourceFromCardId);
      if (source.sourceToKind === "card") {
        sourceCardIds.add(source.sourceToId);
      }
    }

    setRevealedSourceCardIds(sourceCardIds);
  }, [revealCardsTemporarily, selectedAggregatedEdge]);

  const handleInspectSelectedEdgeCard = useCallback((cardId: string) => {
    handleSummaryGroundingCardInspect(cardId);
  }, [handleSummaryGroundingCardInspect]);

  const handleGenerateRelationSummary = useCallback(async () => {
    if (!document || !selectedIslandRelationEdge || isGeneratingRelationSummary) {
      return;
    }

    setIsGeneratingRelationSummary(true);
    setStatusMessage("Requesting AI relation summary draft...");

    try {
      const payload = buildSummarizeIslandRelationPayload(document, selectedIslandRelationEdge);
      const result = await summarizeIslandRelation(payload);
      const sourceSignature = buildRelationSummarySourceSignature(selectedIslandRelationEdge);
      const nextDocument = upsertRelationSummaryWithHistory(document, {
        sourceSignature,
        islandAId: selectedIslandRelationEdge.fromIslandId,
        islandBId: selectedIslandRelationEdge.toIslandId,
        relationType: selectedIslandRelationEdge.type,
        derived: selectedIslandRelationEdge.isDerived,
        newText: result.text,
        newWarnings: result.warnings,
        newGroundingCardIds: result.groundingCardIds,
        newGroundingEdgeIds: result.groundingEdgeIds,
        changeKind: "ai",
      });

      applyDocumentChange(nextDocument, "Generated relation summary draft (unreviewed)");
    } catch (error) {
      setStatusMessage(error instanceof Error ? error.message : "Failed to summarize relation");
    } finally {
      setIsGeneratingRelationSummary(false);
    }
  }, [applyDocumentChange, document, isGeneratingRelationSummary, selectedIslandRelationEdge]);

  const handleRelationSummaryCommit = useCallback(
    (value: string) => {
      if (!document || !selectedRelationSummary) {
        return;
      }

      const nextDocument = upsertRelationSummaryWithHistory(document, {
        sourceSignature: selectedRelationSummary.sourceSignature,
        islandAId: selectedRelationSummary.islandAId,
        islandBId: selectedRelationSummary.islandBId,
        relationType: selectedRelationSummary.relationType,
        derived: selectedRelationSummary.derived,
        newText: value,
        newWarnings: selectedRelationSummary.warnings,
        newGroundingCardIds: selectedRelationSummary.groundingCardIds,
        newGroundingEdgeIds: selectedRelationSummary.groundingEdgeIds,
        changeKind: "manual",
      });
      if (nextDocument === document) {
        return;
      }

      applyDocumentChange(nextDocument, "Updated relation summary");
    },
    [applyDocumentChange, document, selectedRelationSummary]
  );

  const handleRelationSummaryReviewedChange = useCallback(
    (reviewed: boolean) => {
      if (!document || !selectedRelationSummary) {
        return;
      }

      const nextDocument = upsertRelationSummaryWithHistory(document, {
        sourceSignature: selectedRelationSummary.sourceSignature,
        islandAId: selectedRelationSummary.islandAId,
        islandBId: selectedRelationSummary.islandBId,
        relationType: selectedRelationSummary.relationType,
        derived: selectedRelationSummary.derived,
        newText: selectedRelationSummary.text,
        newWarnings: selectedRelationSummary.warnings,
        newGroundingCardIds: selectedRelationSummary.groundingCardIds,
        newGroundingEdgeIds: selectedRelationSummary.groundingEdgeIds,
        changeKind: "manual",
        newReviewed: reviewed,
      });
      if (nextDocument === document) {
        return;
      }

      applyDocumentChange(nextDocument, "Updated relation summary reviewed state");
    },
    [applyDocumentChange, document, selectedRelationSummary]
  );

  const handleRestoreRelationSummaryHistoryEntry = useCallback(
    (historyEntryId: string) => {
      if (!document || !selectedRelationSummary) {
        return;
      }

      const entry = selectedRelationSummary.history?.find((item) => item.id === historyEntryId);
      if (!entry || !entry.toText || entry.toText.trim().length === 0) {
        setStatusMessage("Cannot restore empty relation summary history entry");
        return;
      }

      const nextDocument = upsertRelationSummaryWithHistory(document, {
        sourceSignature: selectedRelationSummary.sourceSignature,
        islandAId: selectedRelationSummary.islandAId,
        islandBId: selectedRelationSummary.islandBId,
        relationType: selectedRelationSummary.relationType,
        derived: selectedRelationSummary.derived,
        newText: entry.toText,
        newWarnings: entry.warningsSnapshot ?? selectedRelationSummary.warnings,
        newGroundingCardIds: entry.groundingCardIdsSnapshot ?? selectedRelationSummary.groundingCardIds,
        newGroundingEdgeIds: entry.groundingEdgeIdsSnapshot ?? selectedRelationSummary.groundingEdgeIds,
        changeKind: "rollback",
        note: `restore:${entry.id}`,
        newReviewed: entry.toReviewed ?? selectedRelationSummary.reviewed,
      });
      if (nextDocument === document) {
        return;
      }

      applyDocumentChange(nextDocument, "Restored relation summary history entry");
    },
    [applyDocumentChange, document, selectedRelationSummary]
  );

  const handleRelationSummaryGroundingInspect = useCallback(
    (cardId: string) => {
      handleSummaryGroundingCardInspect(cardId);
    },
    [handleSummaryGroundingCardInspect]
  );

  /**
   * Manual test steps:
   * 1) Enable summary view and hide source cards, then click one grounding item.
   * 2) Confirm the card is focused/revealed without creating dirty state or undo entries.
   * 3) Apply focus/depth so the grounding card is out of scope and click again.
   * 4) Confirm the "hidden by Focus/Depth" message appears and view controls remain unchanged.
   * 5) Click "Show all grounding on canvas", then "Clear reveal", and verify reveal is session-only after reload.
   */

  const handleShowAllSourcesChange = useCallback((value: boolean) => {
    if (!value) {
      setRevealedSourceCardIds(new Set());
      return;
    }

    setRevealedSourceCardIds(new Set(sourceCardsForSelectedCanonical.map((card) => card.id)));
  }, [sourceCardsForSelectedCanonical]);

  useEffect(() => {
    if (!selectedCard || selectedCard.canonicalId || sourceCardsForSelectedCanonical.length === 0) {
      setRevealedSourceCardIds(new Set());
      return;
    }

    const allowedSourceIdSet = new Set(sourceCardsForSelectedCanonical.map((card) => card.id));
    setRevealedSourceCardIds((previousIds) => {
      const nextIds = new Set(Array.from(previousIds).filter((cardId) => allowedSourceIdSet.has(cardId)));
      if (nextIds.size === previousIds.size) {
        return previousIds;
      }
      return nextIds;
    });
  }, [selectedCard, sourceCardsForSelectedCanonical]);

  const handleIslandSelect = useCallback((islandId: string, isShiftPressed: boolean) => {
    if (isPickingEdgeTarget) {
      handleConnectToTarget({ id: islandId, kind: "island" });
      return;
    }

    if (isPreviewingSuggestion && !isAnnotateOverlayEnabled) {
      return;
    }

    if (document && isReadingOrderEditMode && isShiftPressed && visibleIslandIdSet.has(islandId)) {
      const nextReadingOrder = appendReadingOrderEntry(document.readingOrder ?? [], islandId, visibleIslandIdSet);
      if (nextReadingOrder !== (document.readingOrder ?? [])) {
        applyDocumentChange(
          {
            ...document,
            readingOrder: nextReadingOrder,
          },
          "Added island to reading order"
        );
        return;
      }
    }

    setSelectedIslandId(islandId);
    if (isPreviewingSuggestion && isAnnotateOverlayEnabled) {
      setSelectedCardIds([]);
    }
    setSelectedEdgeId(null);
  }, [
    applyDocumentChange,
    document,
    handleConnectToTarget,
    isAnnotateOverlayEnabled,
    isPickingEdgeTarget,
    isPreviewingSuggestion,
    isReadingOrderEditMode,
    visibleIslandIdSet,
  ]);

  useEffect(() => {
    if (selectedEdgeId && !visibleAggregatedEdges.some((edge) => edge.id === selectedEdgeId)) {
      setSelectedEdgeId(null);
    }
  }, [selectedEdgeId, visibleAggregatedEdges]);

  const focusIslandById = useCallback(
    (islandId: string) => {
      if (!document || !canvasCamera) {
        return;
      }

      const island = document.islands.find((item) => item.id === islandId);
      if (!island) {
        setStatusMessage(`Item not found: island:${islandId}`);
        return;
      }

      const cardsById = new Map(document.cards.map((card) => [card.id, card]));
      const islandBounds = getIslandWorldBounds(island, cardsById);
      if (!islandBounds) {
        setStatusMessage(`Item not found: island:${islandId}`);
        return;
      }

      pushCurrentFocusSnapshot();

      const viewport = {
        width: canvasCamera.viewportWidth,
        height: canvasCamera.viewportHeight,
      };
      const fitCamera = fitToBounds(islandBounds, viewport, 48);
      const lodAdjustedCamera = applyIslandLodZoom(fitCamera, lodEnabled, lodThresholds, 4);
      const nextCamera =
        lodEnabled && lodAdjustedCamera.zoom > fitCamera.zoom
          ? enforceMinZoomForBounds(islandBounds, viewport, lodThresholds.close + FOCUS_LOD_EPSILON, 48, { min: 0.2, max: 4 })
          : fitCamera;

      setFocusCardId(null);
      setFocusWorldPoint(null);
      setFocusTarget({ focusIslandId: islandId });
      requestCameraTransform(nextCamera);
    },
    [canvasCamera, document, lodEnabled, lodThresholds, pushCurrentFocusSnapshot, requestCameraTransform]
  );

  const focusCardById = useCallback(
    (cardId: string) => {
      if (!document || !canvasCamera) {
        return;
      }

      const card = document.cards.find((item) => item.id === cardId);
      if (!card) {
        setStatusMessage(`Item not found: card:${cardId}`);
        return;
      }

      pushCurrentFocusSnapshot();
      const nextCamera = fitToBounds(
        getCardWorldBounds(card),
        {
          width: canvasCamera.viewportWidth,
          height: canvasCamera.viewportHeight,
        },
        120
      );

      setFocusTarget({});
      setFocusCardId(null);
      setFocusWorldPoint(null);
      requestCameraTransform(nextCamera);
    },
    [canvasCamera, document, pushCurrentFocusSnapshot, requestCameraTransform]
  );

  const handleFocusIsland = useCallback(() => {
    if (!selectedIsland) {
      return;
    }

    focusIslandById(selectedIsland.id);
  }, [focusIslandById, selectedIsland]);

  const handleClearFocus = useCallback(() => {
    setFocusTarget({});
    setFocusWorldPoint(null);
    setFocusCardId(null);
  }, []);

  const handleToggleIslandFocus = useCallback(
    (islandId: string) => {
      if (!document) {
        return;
      }

      if (focusTarget.focusIslandId === islandId) {
        setFocusTarget({});
        setFocusWorldPoint(null);
        setFocusCardId(null);
        return;
      }

      focusIslandById(islandId);
    },
    [document, focusIslandById, focusTarget.focusIslandId]
  );

  const handleFocusBack = useCallback(() => {
    const { nextHistory, snapshot } = popFocusHistory(focusHistory);
    if (!snapshot) {
      return;
    }

    setFocusHistory(nextHistory);
    setFocusTarget(snapshot.viewState?.focusIslandId ? { focusIslandId: snapshot.viewState.focusIslandId } : {});
    setMaxDepth(snapshot.viewState?.maxDepth ?? "all");
    setFocusCardId(null);
    setFocusWorldPoint(null);
    requestCameraTransform(snapshot.camera);
  }, [focusHistory, requestCameraTransform]);


  const applyViewPreset = useCallback(
    (nextState: {
      maxDepth: ViewMaxDepth;
      hideSourceCards: boolean;
      showReadingOrder: boolean;
      clearRevealedSources?: boolean;
    }) => {
      setFocusTarget({});
      setFocusWorldPoint(null);
      setFocusCardId(null);
      setMaxDepth(nextState.maxDepth);
      setHideSourceCards(nextState.hideSourceCards);
      setShowReadingOrder(nextState.showReadingOrder);
      setIsReadingOrderEditMode(false);
      if (nextState.clearRevealedSources) {
        setRevealedSourceCardIds(new Set());
      }
    },
    []
  );

  const handleApplyBirdsEyePreset = useCallback(() => {
    applyViewPreset({
      maxDepth: 0,
      hideSourceCards: true,
      showReadingOrder: false,
      clearRevealedSources: true,
    });
  }, [applyViewPreset]);

  const handleApplyMidPreset = useCallback(() => {
    applyViewPreset({
      maxDepth: 1,
      hideSourceCards: true,
      showReadingOrder: false,
      clearRevealedSources: true,
    });
  }, [applyViewPreset]);

  const handleApplyDetailPreset = useCallback(() => {
    applyViewPreset({ maxDepth: "all", hideSourceCards: false, showReadingOrder: true });
  }, [applyViewPreset]);

  const handleResetView = useCallback(() => {
    applyViewPreset({
      maxDepth: "all",
      hideSourceCards: true,
      showReadingOrder: false,
      clearRevealedSources: true,
    });
  }, [applyViewPreset]);

  const focusItem = useCallback((kind: "card" | "island", id: string) => {
    if (!document) {
      return;
    }

    if (kind === "card") {
      const targetCard = document.cards.find((card) => card.id === id);
      if (!targetCard) {
        setStatusMessage(`Item not found: ${kind}:${id}`);
        return;
      }

      const isHiddenBySourceControl = hideSourceCards && isSourceCard(targetCard) && !revealedSourceCardIds.has(id);
      if (!focusedVisibleDocument?.cards.some((card) => card.id === id) || hiddenCardIdSet.has(id) || isHiddenBySourceControl) {
        setStatusMessage("Item is hidden by current view controls");
        return;
      }
    }

    if (kind === "island") {
      const hasIsland = document.islands.some((island) => island.id === id);
      if (!hasIsland) {
        setStatusMessage(`Item not found: ${kind}:${id}`);
        return;
      }

      if (!visibleIslandIdSet.has(id)) {
        setStatusMessage("Item is hidden by current view controls");
        return;
      }
    }

    if (kind === "card") {
      focusCardById(id);
    } else {
      focusIslandById(id);
    }

    setFlashReference({ kind, id });
    setFlashRequestSeq((previousSeq) => previousSeq + 1);
  }, [
    document,
    focusCardById,
    focusIslandById,
    focusedVisibleDocument?.cards,
    hiddenCardIdSet,
    hideSourceCards,
    revealedSourceCardIds,
    visibleIslandIdSet,
  ]);

  const handleNarrativeReferenceFocus = useCallback(
    (reference: NarrativeIssueReference) => {
      focusItem(reference.kind, reference.id);
    },
    [focusItem]
  );

  const handleCheckNarrativeConsistency = useCallback(
    async (selectedNarrativeId: string | null) => {
      if (!document || narrativeText.trim().length === 0) {
        return;
      }

      setIsCheckingNarrative(true);
      setNarrativeCheckError(null);
      try {
        const result = await checkNarrative(document, narrativeText, document.readingOrder);
        setNarrativeIssues(result.issues);

        if (!selectedNarrativeId) {
          return;
        }

        const selectedNarrative = (document.narratives ?? []).find((entry) => entry.id === selectedNarrativeId);
        if (!selectedNarrative) {
          return;
        }

        const nextCheck = {
          id: crypto.randomUUID(),
          createdAt: new Date().toISOString(),
          kind: "consistency" as const,
          issues: result.issues,
        };

        const nextNarratives = (document.narratives ?? []).map((entry) =>
          entry.id === selectedNarrativeId
            ? {
                ...entry,
                text: narrativeText,
                checks: [...(entry.checks ?? []), nextCheck],
              }
            : entry
        );

        applyDocumentChange(
          withUpdatedTimestamp({
            ...document,
            narratives: nextNarratives,
          }),
          "Recorded consistency check"
        );
      } catch (error) {
        const message = error instanceof ApiError ? error.message : "Failed to check narrative consistency";
        setNarrativeCheckError(message);
        setNarrativeIssues([]);
      } finally {
        setIsCheckingNarrative(false);
      }
    },
    [applyDocumentChange, document, narrativeText]
  );

  const handleGenerateNarrativeFromReadingOrder = useCallback(async () => {
    if (!document) {
      return;
    }

    setIsGeneratingNarrative(true);
    setNarrativeGenerationError(null);
    try {
      const draftIndex = generatedNarratives.length + 1;
      const result = await generateNarrative(document, `Draft ${draftIndex}`);
      const nextNarrative: Narrative = {
        id: crypto.randomUUID(),
        title: `Generated Draft ${draftIndex}`,
        text: result.text,
        createdAt: new Date().toISOString(),
        basedOnReadingOrder: result.basedOnReadingOrder,
        reviewed: false,
      };
      applyDocumentChange(
        withUpdatedTimestamp({
          ...document,
          narratives: [...(document.narratives ?? []), nextNarrative],
        }),
        "Generated narrative draft"
      );
      setNarrativeText(result.text);
      setNarrativeIssues([]);
      if (result.warnings && result.warnings.length > 0) {
        setNarrativeGenerationError(result.warnings.join(" "));
      }
    } catch (error) {
      const message = error instanceof ApiError ? error.message : "Failed to generate narrative";
      setNarrativeGenerationError(message);
    } finally {
      setIsGeneratingNarrative(false);
    }
  }, [applyDocumentChange, document, generatedNarratives.length]);


  const readingOrderSnippets = useMemo(() => {
    if (!document) {
      return {};
    }

    return buildReadingOrderSnippets(document);
  }, [document]);

  const readingList = useMemo(() => {
    if (!document || !readingNavEnabled) {
      return [] as ReadingItem[];
    }

    return buildReadingList(document, { readingMode, reviewedOnly });
  }, [document, readingMode, readingNavEnabled, reviewedOnly]);

  useEffect(() => {
    if (!readingNavEnabled) {
      return;
    }

    setReadingIndex((previousIndex) => clampReadingIndex(previousIndex, readingList.length));
  }, [readingList.length, readingNavEnabled]);

  const currentReadingItem = readingList[clampReadingIndex(readingIndex, readingList.length)] ?? null;

  useEffect(() => {
    if (!safeMode) {
      return;
    }

    setOutlineIncludeUnreviewed(false);
  }, [safeMode]);

  const handleSetReadingNavEnabled = useCallback((enabled: boolean) => {
    setReadingNavEnabled(enabled);
    if (!enabled) {
      return;
    }

    setReadingIndex((previousIndex) => clampReadingIndex(previousIndex, readingList.length));
  }, [readingList.length]);

  const handleSetReadingMode = useCallback((nextMode: ReadingMode) => {
    setReadingMode(nextMode);
    setReadingIndex(0);
  }, []);

  const handleToggleReviewedOnly = useCallback(() => {
    setReviewedOnly((current) => !current);
    setReadingIndex(0);
  }, []);

  const focusReadingItemAtIndex = useCallback((nextIndex: number) => {
    if (!readingNavEnabled || readingList.length === 0) {
      return;
    }

    const clampedIndex = clampReadingIndex(nextIndex, readingList.length);
    const nextItem = readingList[clampedIndex];
    if (!nextItem) {
      return;
    }

    setReadingIndex(clampedIndex);
    focusItem(nextItem.kind, nextItem.id);
  }, [focusItem, readingList, readingNavEnabled]);

  const handleReadingPrev = useCallback(() => {
    focusReadingItemAtIndex(readingIndex - 1);
  }, [focusReadingItemAtIndex, readingIndex]);

  const handleReadingNext = useCallback(() => {
    focusReadingItemAtIndex(readingIndex + 1);
  }, [focusReadingItemAtIndex, readingIndex]);

  const currentLod = useMemo(() => {
    if (!lodEnabled) {
      return null;
    }

    const zoom = canvasCamera?.zoom ?? 1;
    return getLODLevel(zoom, { lodThresholds, lodLevelOverride });
  }, [canvasCamera?.zoom, lodEnabled, lodLevelOverride, lodThresholds]);

  const buildReadingOutline = useCallback((): string | null => {
    if (!document) {
      setStatusMessage("Nothing to export");
      return null;
    }

    return buildReadingOutlineMd(
      document,
      {
        readingNavEnabled,
        readingIndex,
        readingMode,
        reviewedOnly,
        safeMode,
        lod: currentLod?.level ?? null,
      },
      {
        includeCardTexts: outlineIncludeCardTexts,
        includeRelationSummaries: outlineIncludeRelationSummaries,
        includeUnreviewedSummaries: outlineIncludeUnreviewed,
      },
    );
  }, [
    document,
    outlineIncludeCardTexts,
    outlineIncludeRelationSummaries,
    outlineIncludeUnreviewed,
    readingIndex,
    readingMode,
    readingNavEnabled,
    reviewedOnly,
    safeMode,
    currentLod?.level,
  ]);

  const handleCopyReadingOutlineMd = useCallback(async () => {
    const outline = buildReadingOutline();
    if (!outline) {
      return;
    }

    try {
      await navigator.clipboard.writeText(outline);
      setStatusMessage("Copied reading outline (Markdown)");
    } catch {
      setStatusMessage("Failed to copy reading outline");
    }
  }, [buildReadingOutline]);

  const handleDownloadReadingOutlineMd = useCallback(() => {
    const outline = buildReadingOutline();
    if (!outline) {
      return;
    }

    downloadTextFile("outline.md", "text/markdown", outline);
    setStatusMessage("Downloaded outline.md");
  }, [buildReadingOutline]);

  const handleReadingDisable = useCallback(() => {
    setReadingNavEnabled(false);
  }, []);

  const loneWolfCardIdSet = useMemo(() => {
    if (!focusedVisibleDocument || (!summaryView && !abstractMapView)) {
      return new Set<string>();
    }

    const islandMemberIds = new Set<string>();
    for (const island of focusedVisibleDocument.islands) {
      for (const cardId of island.cardIds) {
        islandMemberIds.add(cardId);
      }
    }

    return new Set(
      focusedVisibleDocument.cards
        .map((card) => card.id)
        .filter((cardId) => !islandMemberIds.has(cardId))
    );
  }, [abstractMapView, focusedVisibleDocument, summaryView]);

  const islandViews = useMemo(() => {
    if (!focusedVisibleDocument) {
      return null;
    }

  return visibleIslands.map((island, index) => (
      <IslandView
        key={island.id}
        island={island}
        cards={focusedVisibleDocument.cards}
        isSelected={selectedIslandId === island.id}
        isShapeStale={stalePolygonIslandIdSet.has(island.id)}
        isPeeking={peekIslandId === island.id}
        summaryView={summaryView || abstractMapView || currentLod?.level === "mid" || currentLod?.level === "far"}
        abstractMapView={abstractMapView || currentLod?.level === "far"}
        showSummary={
          currentLod?.level === "mid"
            ? summaryView || island.summaryReviewed !== false
            : summaryView || abstractMapView || currentLod?.level === "far"
        }
        isCollapsedForView={(summaryView || abstractMapView) ? effectiveCollapsedIslandIdSet.has(island.id) : collapsedIslandIdSet.has(island.id)}
        safeMode={safeMode}
        zIndex={index}
        onSelect={handleIslandSelect}
        onToggleCollapsed={handleIslandCollapsedChange}
        onTitleDoubleClick={handleToggleIslandFocus}
        onFocusIsland={focusIslandById}
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
    focusedVisibleDocument,
    handleIslandCollapsedChange,
    handleIslandSelect,
    isPickingEdgeTarget,
    peekIslandId,
    selectedIslandId,
    stalePolygonIslandIdSet,
    summaryView,
    abstractMapView,
    collapsedIslandIdSet,
    effectiveCollapsedIslandIdSet,
    visibleIslands,
    handleToggleIslandFocus,
    focusIslandById,
    safeMode,
    currentLod,
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

  const aggregatedEdgeInspectorItems = useMemo(() => {
    if (!document || !hideSourceCards) {
      return [] as { id: string; label: string }[];
    }

    const allRenderEdges = getEdgesToRender(document, true);

    return allRenderEdges
      .filter((edge) => edge.isDerived)
      .map((edge) => {
        const fromLabel =
          edge.fromKind === "island"
            ? `Island ${edge.fromId}`
            : (cardsById.get(edge.fromId)?.text ?? edge.fromId);
        const toLabel =
          edge.toKind === "island" ? `Island ${edge.toId}` : (cardsById.get(edge.toId)?.text ?? edge.toId);

        return {
          id: edge.id,
          label: `${fromLabel} → ${toLabel} (${edge.type})`,
        };
      });
  }, [cardsById, document, hideSourceCards]);

  const handlePromoteAggregatedEdge = useCallback(
    (aggregateEdgeId: string) => {
      if (!document) {
        return;
      }

      const aggregatedEdge = getEdgesToRender(document, true).find(
        (edge) => edge.id === aggregateEdgeId && edge.isDerived
      );
      if (!aggregatedEdge) {
        setStatusMessage("Aggregated edge not found");
        return;
      }

      applyDocumentChange(
        {
          ...document,
          edges: [
            ...document.edges,
            {
              id: crypto.randomUUID(),
              fromId: aggregatedEdge.fromId,
              toId: aggregatedEdge.toId,
              fromKind: aggregatedEdge.fromKind,
              toKind: aggregatedEdge.toKind,
              type: aggregatedEdge.type,
            },
          ],
        },
        "Promoted aggregated edge to real edge"
      );
      setStatusMessage("Promoted aggregated edge to real edge");
    },
    [applyDocumentChange, document]
  );

  const handleAddSelectedItemToReadingOrder = useCallback(() => {
    if (!document) {
      return;
    }

    const targetId = selectedIsland?.id ?? selectedCard?.id;
    if (!targetId) {
      return;
    }

    const visibleEntryIdSet = new Set<string>([...visibleCardIdSet, ...visibleIslandIdSet]);
    const nextReadingOrder = appendReadingOrderEntry(document.readingOrder ?? [], targetId, visibleEntryIdSet);
    if (nextReadingOrder === (document.readingOrder ?? [])) {
      return;
    }

    applyDocumentChange(
      {
        ...document,
        readingOrder: nextReadingOrder,
      },
      "Added item to reading order"
    );
  }, [applyDocumentChange, document, selectedCard?.id, selectedIsland?.id, visibleCardIdSet, visibleIslandIdSet]);

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

      const entryId = (document.readingOrder ?? [])[index];
      if (!entryId) {
        return;
      }

      const nextReadingOrder = removeReadingOrderEntry(document.readingOrder ?? [], entryId);
      if (nextReadingOrder === (document.readingOrder ?? [])) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          readingOrder: nextReadingOrder,
        },
        "Removed item from reading order"
      );
    },
    [applyDocumentChange, document]
  );


  const handleRemoveReadingOrderEntry = useCallback(
    (entryId: string) => {
      if (!document) {
        return;
      }

      const nextReadingOrder = removeReadingOrderEntry(document.readingOrder ?? [], entryId);
      if (nextReadingOrder === (document.readingOrder ?? [])) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          readingOrder: nextReadingOrder,
        },
        "Removed item from reading order"
      );
    },
    [applyDocumentChange, document]
  );

  const handleReorderReadingOrderEntry = useCallback(
    (entryId: string, targetEntryId: string, position: "before" | "after") => {
      if (!document) {
        return;
      }

      const nextReadingOrder = moveReadingOrderEntry(document.readingOrder ?? [], entryId, targetEntryId, position);
      if (nextReadingOrder === (document.readingOrder ?? [])) {
        return;
      }

      applyDocumentChange(
        {
          ...document,
          readingOrder: nextReadingOrder,
        },
        "Reordered reading order"
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
    onReadingPathNext: readingNavEnabled ? handleReadingNext : undefined,
    onReadingPathPrev: readingNavEnabled ? handleReadingPrev : undefined,
    onReadingPathToggleReviewedOnly: readingNavEnabled ? handleToggleReviewedOnly : undefined,
    onReadingPathDisable: readingNavEnabled ? handleReadingDisable : undefined,
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
      {focusHistory.length > 0 ? (
        <button
          type="button"
          onClick={handleFocusBack}
          style={{
            border: "1px solid #cbd5e1",
            backgroundColor: "#ffffff",
            color: "#0f172a",
            borderRadius: 6,
            padding: "6px 12px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Back
        </button>
      ) : null}
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
        Import doc JSON (legacy, confirm in Share)
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
        Export doc JSON (legacy)
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

  const getVisibleBoundsExportArea = useCallback(() => {
    if (!focusedVisibleDocument || !canvasCamera) {
      return null;
    }

    const visibleBounds = computeVisibleBounds(focusedVisibleDocument, {
      visibleIslandIds: visibleIslandIdSet,
      hiddenCardIds: hiddenCardIdSet,
      hideSourceCards: hideSourceCards || summaryView || abstractMapView,
      summaryView,
      abstractMapView,
    });

    if (!visibleBounds) {
      return null;
    }

    return {
      x: visibleBounds.x - SVG_VISIBLE_BOUNDS_PADDING,
      y: visibleBounds.y - SVG_VISIBLE_BOUNDS_PADDING,
      w: visibleBounds.w + SVG_VISIBLE_BOUNDS_PADDING * 2,
      h: visibleBounds.h + SVG_VISIBLE_BOUNDS_PADDING * 2,
    };
  }, [abstractMapView, canvasCamera, focusedVisibleDocument, hiddenCardIdSet, hideSourceCards, summaryView, visibleIslandIdSet]);

  const getViewMetadataFilename = useCallback((mode: "viewport" | "bounds", generatedAt: string) => {
    const date = generatedAt.slice(0, 10);
    return `kj-atlas-${date}-${mode}.view.json`;
  }, []);

  const downloadViewMetadata = useCallback(
    (mode: "viewport" | "bounds", bounds?: { x: number; y: number; w: number; h: number }, padding?: number) => {
      if (!document || !canvasCamera) {
        return;
      }

      const generatedAt = new Date().toISOString();
      const metadata = buildExportViewMetadata({
        doc: document,
        camera: canvasCamera,
        viewState: {
          summaryView,
          abstractMapView,
          hideSourceCards,
          maxDepth,
          focusIslandId: focusTarget.focusIslandId ?? null,
          showReadingOrder,
          editReadingOrder: isReadingOrderEditMode,
          readingNavEnabled,
          readingIndex,
          readingMode,
          reviewedOnly,
          safeMode,
          lodEnabled,
          lodThresholds,
          lodLevelOverride,
          lodShowLoneWolvesWhenFar,
          resolvedLodLevel: currentLod?.level,
        },
        exportMode: mode,
        bounds,
        padding,
        generatedAt,
      });

      downloadTextFile(getViewMetadataFilename(mode, generatedAt), "application/json", `${JSON.stringify(metadata, null, 2)}\n`);
    },
    [
      abstractMapView,
      canvasCamera,
      document,
      focusTarget.focusIslandId,
      getViewMetadataFilename,
      hideSourceCards,
      isReadingOrderEditMode,
      readingNavEnabled,
      readingIndex,
      readingMode,
      reviewedOnly,
      maxDepth,
      showReadingOrder,
      summaryView,
      safeMode,
      lodEnabled,
      lodThresholds,
      lodLevelOverride,
      lodShowLoneWolvesWhenFar,
      ]
  );

  const handleExportAbstractMapMarkdownWithPng = useCallback(async () => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = getVisibleBoundsExportArea();
    if (!area) {
      setStatusMessage("Nothing to export");
      return;
    }

    try {
      const pngBlob = await exportCanvasToPngBlob({
        doc: focusedVisibleDocument,
        viewState: {
          visibleIslandIds: visibleIslandIdSet,
          hiddenCardIds: hiddenCardIdSet,
          hideSourceCards: hideSourceCards || summaryView || abstractMapView,
          summaryView,
          abstractMapView,
        },
        camera: canvasCamera,
        area,
        scale: 2,
      });

      const model = buildAbstractMapExport(document, {
        visibleIslandIds: visibleIslandIdSet,
        abstractMapView,
        includeUnreviewedDrafts: !safeMode || includeUnreviewedDraftsInExport,
      });

      const snapshotFilename = "snapshot.png";
      downloadBlobFile(snapshotFilename, pngBlob);
      downloadTextFile("report.md", "text/markdown", exportAbstractMapMarkdown(model, { snapshotFilename }));
      downloadViewMetadata("bounds", area, SVG_VISIBLE_BOUNDS_PADDING);
      setStatusMessage("Exported abstract map report (MD + PNG)");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Report export failed";
      setStatusMessage(`Report export failed: ${message}`);
    }
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getVisibleBoundsExportArea,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const handleExportAbstractMapHtmlWithPng = useCallback(async () => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = getVisibleBoundsExportArea();
    if (!area) {
      setStatusMessage("Nothing to export");
      return;
    }

    try {
      const pngBlob = await exportCanvasToPngBlob({
        doc: focusedVisibleDocument,
        viewState: {
          visibleIslandIds: visibleIslandIdSet,
          hiddenCardIds: hiddenCardIdSet,
          hideSourceCards: hideSourceCards || summaryView || abstractMapView,
          summaryView,
          abstractMapView,
        },
        camera: canvasCamera,
        area,
        scale: 2,
      });

      const model = buildAbstractMapExport(document, {
        visibleIslandIds: visibleIslandIdSet,
        abstractMapView,
        includeUnreviewedDrafts: !safeMode || includeUnreviewedDraftsInExport,
      });

      const snapshotDataUrl = await readBlobAsDataUrl(pngBlob);
      downloadTextFile("report.html", "text/html", exportAbstractMapHTML(model, { snapshotDataUrl }));
      downloadViewMetadata("bounds", area, SVG_VISIBLE_BOUNDS_PADDING);
      setStatusMessage("Exported abstract map report (HTML + PNG)");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Report export failed";
      setStatusMessage(`Report export failed: ${message}`);
    }
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getVisibleBoundsExportArea,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const getSvgExportFilename = useCallback((mode: "viewport" | "visible-bounds") => {
    const date = new Date().toISOString().slice(0, 10);
    return `kj-atlas-${date}-${mode}.svg`;
  }, []);

  const getPngExportFilename = useCallback(
    (mode: "viewport" | "visible-bounds", scale: PngExportScale) => {
      const date = new Date().toISOString().slice(0, 10);
      const scaleSuffix = scale === 2 ? "@2x" : "";
      return `kj-atlas-${date}-${mode}${scaleSuffix}.png`;
    },
    []
  );

  const handleExportSvgViewport = useCallback(() => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = {
      x: (-canvasCamera.panX) / canvasCamera.zoom,
      y: (-canvasCamera.panY) / canvasCamera.zoom,
      w: canvasCamera.viewportWidth / canvasCamera.zoom,
      h: canvasCamera.viewportHeight / canvasCamera.zoom,
    };

    if (area.w <= 0 || area.h <= 0) {
      setStatusMessage("Nothing to export");
      return;
    }

    const svg = exportCanvasToSVG({
      doc: focusedVisibleDocument,
      viewState: {
        visibleIslandIds: visibleIslandIdSet,
        hiddenCardIds: hiddenCardIdSet,
        hideSourceCards: hideSourceCards || summaryView || abstractMapView,
        summaryView,
        abstractMapView,
      },
      camera: canvasCamera,
      area,
    });

    downloadTextFile(getSvgExportFilename("viewport"), "image/svg+xml", svg);
    downloadViewMetadata("viewport", area);
    setStatusMessage("Exported SVG (Viewport)");
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getSvgExportFilename,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const handleExportSvgVisibleBounds = useCallback(() => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const visibleBounds = computeVisibleBounds(focusedVisibleDocument, {
      visibleIslandIds: visibleIslandIdSet,
      hiddenCardIds: hiddenCardIdSet,
      hideSourceCards: hideSourceCards || summaryView || abstractMapView,
      summaryView,
      abstractMapView,
    });

    if (!visibleBounds) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = {
      x: visibleBounds.x - SVG_VISIBLE_BOUNDS_PADDING,
      y: visibleBounds.y - SVG_VISIBLE_BOUNDS_PADDING,
      w: visibleBounds.w + SVG_VISIBLE_BOUNDS_PADDING * 2,
      h: visibleBounds.h + SVG_VISIBLE_BOUNDS_PADDING * 2,
    };

    const svg = exportCanvasToSVG({
      doc: focusedVisibleDocument,
      viewState: {
        visibleIslandIds: visibleIslandIdSet,
        hiddenCardIds: hiddenCardIdSet,
        hideSourceCards: hideSourceCards || summaryView || abstractMapView,
        summaryView,
        abstractMapView,
      },
      camera: canvasCamera,
      area,
    });

    downloadTextFile(getSvgExportFilename("visible-bounds"), "image/svg+xml", svg);
    downloadViewMetadata("bounds", area, SVG_VISIBLE_BOUNDS_PADDING);
    setStatusMessage("Exported SVG (Visible bounds)");
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getSvgExportFilename,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const handleExportPngViewport = useCallback(async () => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = {
      x: (-canvasCamera.panX) / canvasCamera.zoom,
      y: (-canvasCamera.panY) / canvasCamera.zoom,
      w: canvasCamera.viewportWidth / canvasCamera.zoom,
      h: canvasCamera.viewportHeight / canvasCamera.zoom,
    };

    if (area.w <= 0 || area.h <= 0) {
      setStatusMessage("Nothing to export");
      return;
    }


    try {
      const pngBlob = await exportCanvasToPngBlob({
        doc: focusedVisibleDocument,
        viewState: {
          visibleIslandIds: visibleIslandIdSet,
          hiddenCardIds: hiddenCardIdSet,
          hideSourceCards: hideSourceCards || summaryView || abstractMapView,
          summaryView,
          abstractMapView,
        },
        camera: canvasCamera,
        area,
        scale: pngExportScale,
      });
      downloadBlobFile(getPngExportFilename("viewport", pngExportScale), pngBlob);
      downloadViewMetadata("viewport", area);
      setStatusMessage(`Exported PNG (Viewport, ${pngExportScale}x)`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "PNG export failed";
      setStatusMessage(`PNG export failed: ${message}`);
    }
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getPngExportFilename,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    pngExportScale,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const handleExportPngVisibleBounds = useCallback(async () => {
    if (!document || !focusedVisibleDocument || !canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const visibleBounds = computeVisibleBounds(focusedVisibleDocument, {
      visibleIslandIds: visibleIslandIdSet,
      hiddenCardIds: hiddenCardIdSet,
      hideSourceCards: hideSourceCards || summaryView || abstractMapView,
      summaryView,
      abstractMapView,
    });

    if (!visibleBounds) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = {
      x: visibleBounds.x - SVG_VISIBLE_BOUNDS_PADDING,
      y: visibleBounds.y - SVG_VISIBLE_BOUNDS_PADDING,
      w: visibleBounds.w + SVG_VISIBLE_BOUNDS_PADDING * 2,
      h: visibleBounds.h + SVG_VISIBLE_BOUNDS_PADDING * 2,
    };


    try {
      const pngBlob = await exportCanvasToPngBlob({
        doc: focusedVisibleDocument,
        viewState: {
          visibleIslandIds: visibleIslandIdSet,
          hiddenCardIds: hiddenCardIdSet,
          hideSourceCards: hideSourceCards || summaryView || abstractMapView,
          summaryView,
          abstractMapView,
        },
        camera: canvasCamera,
        area,
        scale: pngExportScale,
      });
      downloadBlobFile(getPngExportFilename("visible-bounds", pngExportScale), pngBlob);
      downloadViewMetadata("bounds", area, SVG_VISIBLE_BOUNDS_PADDING);
      setStatusMessage(`Exported PNG (Visible bounds, ${pngExportScale}x)`);
    } catch (error) {
      const message = error instanceof Error ? error.message : "PNG export failed";
      setStatusMessage(`PNG export failed: ${message}`);
    }
  }, [
    abstractMapView,
    canvasCamera,
    document,
    focusedVisibleDocument,
    getPngExportFilename,
    downloadViewMetadata,
    hiddenCardIdSet,
    hideSourceCards,
    pngExportScale,
    summaryView,
    visibleIslandIdSet,
    safeMode,
    includeUnreviewedDraftsInExport,
  ]);

  const handleExportViewMetadataViewport = useCallback(() => {
    if (!canvasCamera) {
      setStatusMessage("Nothing to export");
      return;
    }

    const area = {
      x: (-canvasCamera.panX) / canvasCamera.zoom,
      y: (-canvasCamera.panY) / canvasCamera.zoom,
      w: canvasCamera.viewportWidth / canvasCamera.zoom,
      h: canvasCamera.viewportHeight / canvasCamera.zoom,
    };

    if (area.w <= 0 || area.h <= 0) {
      setStatusMessage("Nothing to export");
      return;
    }

    downloadViewMetadata("viewport", area);
    setStatusMessage("Exported view.json (Viewport)");
  }, [canvasCamera, downloadViewMetadata]);

  const handleExportViewMetadataVisibleBounds = useCallback(() => {
    const area = getVisibleBoundsExportArea();
    if (!area) {
      setStatusMessage("Nothing to export");
      return;
    }

    downloadViewMetadata("bounds", area, SVG_VISIBLE_BOUNDS_PADDING);
    setStatusMessage("Exported view.json (Visible bounds)");
  }, [downloadViewMetadata, getVisibleBoundsExportArea]);

  const handleSafeModeChange = useCallback((nextValue: boolean) => {
    setSafeMode(nextValue);
    if (nextValue) {
      setIncludeUnreviewedDraftsInExport(false);
    }
  }, []);

  const headerViewControls = (
    <div style={{ position: "relative" }}>
      <button
        type="button"
        onClick={() => {
          setIsViewControlsOpen((prev) => !prev);
        }}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "4px 10px",
          fontSize: 12,
          fontWeight: 600,
          cursor: "pointer",
        }}
      >
        View
      </button>
      {isViewControlsOpen ? (
        <div style={{ position: "absolute", top: "calc(100% + 8px)", left: 0, zIndex: 20 }}>
          <ViewControlsPanel
            focusIslandId={focusTarget.focusIslandId}
            onClearFocus={handleClearFocus}
            onApplyBirdsEyePreset={handleApplyBirdsEyePreset}
            onApplyMidPreset={handleApplyMidPreset}
            onApplyDetailPreset={handleApplyDetailPreset}
            onResetView={handleResetView}
            maxDepth={maxDepth}
            maxAvailableDepth={maxAvailableDepth}
            onMaxDepthChange={setMaxDepth}
            hideSourceCards={hideSourceCards}
            onHideSourceCardsChange={setHideSourceCards}
            hideMergedOriginals={hideMergedOriginals}
            onHideMergedOriginalsChange={setHideMergedOriginals}
            summaryView={summaryView}
            onSummaryViewChange={setSummaryView}
            abstractMapView={abstractMapView}
            onAbstractMapViewChange={(nextValue) => {
              setAbstractMapView(nextValue);
              if (nextValue) {
                setSummaryView(true);
              }
            }}
            showReadingOrder={showReadingOrder}
            onShowReadingOrderChange={(nextValue) => {
              setShowReadingOrder(nextValue);
              if (!nextValue) {
                setIsReadingOrderEditMode(false);
              }
            }}
            isReadingOrderEditMode={isReadingOrderEditMode}
            onReadingOrderEditModeChange={setIsReadingOrderEditMode}
            onExportAbstractMapMarkdownWithPng={() => {
              void handleExportAbstractMapMarkdownWithPng();
            }}
            onExportAbstractMapHtmlWithPng={() => {
              void handleExportAbstractMapHtmlWithPng();
            }}
            onExportSvgViewport={handleExportSvgViewport}
            onExportSvgVisibleBounds={handleExportSvgVisibleBounds}
            pngExportScale={pngExportScale}
            onPngExportScaleChange={setPngExportScale}
            onExportPngViewport={() => {
              void handleExportPngViewport();
            }}
            onExportPngVisibleBounds={() => {
              void handleExportPngVisibleBounds();
            }}
            onLoadViewMetadataFile={(file) => {
              void handleLoadViewMetadataFile(file);
            }}
            safeMode={safeMode}
            onSafeModeChange={handleSafeModeChange}
            lodEnabled={lodEnabled}
            onLodEnabledChange={setLodEnabled}
            lodThresholds={lodThresholds}
            onLodThresholdsChange={setLodThresholds}
            currentLodLevel={currentLod?.level ?? null}
            lodShowLoneWolvesWhenFar={lodShowLoneWolvesWhenFar}
            onLodShowLoneWolvesWhenFarChange={setLodShowLoneWolvesWhenFar}
            showLabelBounds={showLabelBounds}
            onShowLabelBoundsChange={setShowLabelBounds}
          />
        </div>
      ) : null}
    </div>
  );

  const structuralDiffPanel = (
    <DiffPanel
      comparisonFileName={comparisonFileName}
      comparisonDocument={comparisonDocument}
      diffResult={diffResult}
      currentCardIdSet={currentCardIdSet}
      currentIslandIdSet={currentIslandIdSet}
      onLoadComparisonDocument={handleLoadComparisonDocumentClick}
      onJumpToItem={(kind, id) => {
        focusItem(kind, id);
      }}
    />
  );

  const headerShareControls = (
    <SharePanel
      isOpen={isSharePanelOpen}
      onToggleOpen={() => {
        setIsSharePanelOpen((previousOpen) => !previousOpen);
      }}
      hasDocument={Boolean(document)}
      isLoading={isLoading}
      onExportSvgViewport={handleExportSvgViewport}
      onExportSvgVisibleBounds={handleExportSvgVisibleBounds}
      pngExportScale={pngExportScale}
      onPngExportScaleChange={setPngExportScale}
      onExportPngViewport={() => {
        void handleExportPngViewport();
      }}
      onExportPngVisibleBounds={() => {
        void handleExportPngVisibleBounds();
      }}
      onExportAbstractMapMarkdownWithPng={() => {
        void handleExportAbstractMapMarkdownWithPng();
      }}
      onExportAbstractMapHtmlWithPng={() => {
        void handleExportAbstractMapHtmlWithPng();
      }}
      safeMode={safeMode}
      includeUnreviewedDrafts={includeUnreviewedDraftsInExport}
      onIncludeUnreviewedDraftsChange={setIncludeUnreviewedDraftsInExport}
      onExportViewViewport={handleExportViewMetadataViewport}
      onExportViewVisibleBounds={handleExportViewMetadataVisibleBounds}
      onLoadViewMetadataFile={(file) => {
        void handleLoadViewMetadataFile(file);
      }}
      onLoadDocumentFile={(file) => {
        void handleLoadDocumentFile(file);
      }}
      pendingImportedDocumentSummary={
        pendingImportedDocument
          ? {
              fileName: pendingImportedDocument.fileName,
              cardCount: pendingImportedDocument.document.cards.length,
              islandCount: pendingImportedDocument.document.islands.length,
              edgeCount: pendingImportedDocument.document.edges.length,
            }
          : null
      }
      importDocumentError={importDocumentError}
      onReplaceCurrentDocument={handleReplaceCurrentDocument}
      onLoadPatchFile={(file) => {
        void handleLoadPatchFile(file);
      }}
      onLoadPatchBaselineFile={(file) => {
        void handleLoadPatchBaselineFile(file);
      }}
      onExportPatchFile={() => {
        void handleExportPatchFile();
      }}
      patchExportAuthor={patchExportAuthor}
      patchExportAuthorNote={patchExportAuthorNote}
      onPatchExportAuthorChange={setPatchExportAuthor}
      onPatchExportAuthorNoteChange={setPatchExportAuthorNote}
      patchTrustLabel={patchTrustLabel}
      onPatchTrustLabelChange={setPatchTrustLabel}
      patchFingerprintStatus={patchFingerprintStatus}
      patchFileName={pendingPatchImport?.fileName ?? null}
      patchImportError={patchImportError}
      patchConflictWarning={patchConflictWarning}
      patchSummary={patchSummary}
      onCopyPatchSummary={() => {
        void handleCopyPatchSummary();
      }}
      patchPreviewItems={patchPreviewItems}
      onPatchItemCheckedChange={(opId, checked) => {
        setPatchSelectedOpIdSet((previous) => {
          const next = new Set(previous);
          if (checked) {
            next.add(opId);
          } else {
            next.delete(opId);
          }
          return next;
        });
      }}
      onConflictResolutionChange={(opId, resolution) => {
        setPatchResolutionsByOpId((previous) => ({
          ...previous,
          [opId]: resolution,
        }));
      }}
      onApplyPatch={handleApplyPatch}
      canApplyPatch={canApplyPatch}
      hasPatchSelection={hasPatchSelection}
      patchLintIssues={patchLintResult?.issues ?? []}
      fixProposals={patchFixProposals}
      selectedFixProposalIds={selectedFixProposalIdSet}
      onFixProposalCheckedChange={handleFixProposalCheckedChange}
      onApplySelectedFixes={handleApplySelectedPatchFixes}
      onResetPatchToOriginal={handleResetPatchToOriginal}
      patchBaselineFileName={patchBaselineFileName}
      patchApplyLogEntries={document?.patchApplyLog ?? []}
      onCopyPatchApplyLogEntry={(entryId) => {
        void handleCopyPatchApplyLogEntry(entryId);
      }}
      structuralDiffSection={structuralDiffPanel}
    />
  );

  return (
    <Shell
      title="kj-atlas Canvas MVP"
      subtitle={`Document: ${activeDocumentId}`}
      headerViewControls={headerViewControls}
      headerShareControls={headerShareControls}
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
          sourceCardsForSelectedCanonical={sourceCardsForSelectedCanonical}
          revealedSourceCardIds={revealedSourceCardIds}
          topContent={
            <>
              <section
                style={{
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  padding: 8,
                  marginBottom: 12,
                  backgroundColor: "#f8fafc",
                }}
              >
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>
                  Legacy entry point. Use “Share &amp; Reproduce” for ordered Diff/Verify flow.
                </div>
                {structuralDiffPanel}
              </section>
              <NarrativesPanel
                narrativeText={narrativeText}
                onNarrativeTextChange={setNarrativeText}
                onCheckConsistency={(selectedNarrativeId) => {
                  void handleCheckNarrativeConsistency(selectedNarrativeId);
                }}
                onGenerateFromReadingOrder={() => {
                  void handleGenerateNarrativeFromReadingOrder();
                }}
                isChecking={isCheckingNarrative}
                isGenerating={isGeneratingNarrative}
                errorMessage={narrativeCheckError}
                generationErrorMessage={narrativeGenerationError}
                issues={narrativeIssues}
                generatedNarratives={generatedNarratives}
                onReferenceClick={handleNarrativeReferenceFocus}
                onFocusItem={focusItem}
                readingOrderSnippets={readingOrderSnippets}
                document={document}
                hideSourceCards={hideSourceCards}
              />
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
          selectedIsland={selectedIsland ? { ...selectedIsland, shapeStale: stalePolygonIslandIdSet.has(selectedIsland.id) } : null}
          selectedCardCount={selectedCardIds.length}
          onCreateRepresentativeCard={handleCreateRepresentativeCard}
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
          onRestoreSummaryHistoryEntry={(historyEntryId) => {
            if (!selectedIsland) {
              return;
            }

            handleRestoreIslandSummaryVersion(selectedIsland.id, historyEntryId);
          }}
          onShowSummaryHistoryGrounding={(groundingIds) => {
            revealCardsTemporarily(groundingIds);
          }}
          onSummaryReviewedChange={(value) => {
            if (!selectedIsland) {
              return;
            }

            handleIslandSummaryReviewedChange(selectedIsland.id, value);
          }}
          onSuggestIslandSummary={() => {
            void handleSuggestIslandSummary();
          }}
          isSuggestingIslandSummary={isSuggestingIslandSummary}
          islandSummarySuggestionWarnings={selectedIsland ? islandSummarySuggestionWarningsByIslandId[selectedIsland.id] ?? [] : []}
          summaryGroundingItems={summaryGroundingItems}
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
          isSelectedIslandCollapsed={selectedIsland ? collapsedIslandIds.has(selectedIsland.id) : false}
          hasIslands={(document?.islands.length ?? 0) > 0}
          isAnyIslandCollapsed={collapsedIslandIds.size > 0}
          onCollapseAllIslands={handleCollapseAllIslands}
          onExpandAllIslands={handleExpandAllIslands}
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
          onFocusIsland={handleFocusIsland}
          onFocusCard={() => {
            if (!selectedCard) {
              return;
            }

            focusCardById(selectedCard.id);
          }}
          summaryView={summaryView}
          abstractMapView={abstractMapView}
          isSelectedIslandTemporarilyRevealed={selectedIsland ? summaryRevealIslandIds.has(selectedIsland.id) : false}
          onToggleSelectedIslandTemporaryReveal={() => {
            if (!selectedIsland) {
              return;
            }

            setSummaryRevealIslandIds((previousIds) => {
              const nextIds = new Set(previousIds);
              if (nextIds.has(selectedIsland.id)) {
                nextIds.delete(selectedIsland.id);
              } else {
                nextIds.add(selectedIsland.id);
              }
              return nextIds;
            });
          }}
          isGridSnapEnabled={isGridSnapEnabled}
          onGridSnapToggle={setIsGridSnapEnabled}
          isPolygonVertexEditEnabled={isPolygonVertexEditEnabled}
          onPolygonVertexEditEnabledChange={setIsPolygonVertexEditEnabled}
          onGenerateIslandPolygon={() => {
            if (!selectedIsland) {
              return;
            }

            handleGenerateIslandPolygon(selectedIsland.id);
          }}
          showCanonicalOnlyEdges={showCanonicalOnlyEdges}
          onShowCanonicalOnlyEdgesChange={setShowCanonicalOnlyEdges}
          onSourceCardInspect={handleSourceCardInspect}
          onSummaryGroundingCardInspect={handleSummaryGroundingCardInspect}
          onShowAllSummaryGrounding={handleShowAllSummaryGrounding}
          onClearTemporaryReveal={clearTemporaryReveal}
          groundingVisibilityMessage={groundingVisibilityMessage}
          onShowAllSourcesChange={handleShowAllSourcesChange}
          document={document}
          selectedIslandRelationEdge={selectedIslandRelationEdge}
          selectedAggregatedEdge={selectedAggregatedEdge}
          onRevealSelectedEdgeSources={handleRevealSelectedEdgeSources}
          onInspectSelectedEdgeCard={handleInspectSelectedEdgeCard}
          selectedRelationSummary={selectedRelationSummary}
          safeMode={safeMode}
          isGeneratingRelationSummary={isGeneratingRelationSummary}
          onGenerateRelationSummary={() => {
            void handleGenerateRelationSummary();
          }}
          onRelationSummaryCommit={handleRelationSummaryCommit}
          onRestoreRelationSummaryHistoryEntry={handleRestoreRelationSummaryHistoryEntry}
          onRelationSummaryReviewedChange={handleRelationSummaryReviewedChange}
          onRelationSummaryGroundingInspect={handleRelationSummaryGroundingInspect}
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
          readingNavEnabled={readingNavEnabled}
          onReadingNavEnabledChange={handleSetReadingNavEnabled}
          readingMode={readingMode}
          onReadingModeChange={handleSetReadingMode}
          reviewedOnly={reviewedOnly}
          onReadingReviewedOnlyToggle={handleToggleReviewedOnly}
          outlineIncludeCardTexts={outlineIncludeCardTexts}
          onOutlineIncludeCardTextsChange={setOutlineIncludeCardTexts}
          outlineIncludeRelationSummaries={outlineIncludeRelationSummaries}
          onOutlineIncludeRelationSummariesChange={setOutlineIncludeRelationSummaries}
          outlineIncludeUnreviewed={outlineIncludeUnreviewed}
          onOutlineIncludeUnreviewedChange={setOutlineIncludeUnreviewed}
          onCopyReadingOutlineMd={() => {
            void handleCopyReadingOutlineMd();
          }}
          onDownloadReadingOutlineMd={handleDownloadReadingOutlineMd}
          readingStep={readingList.length === 0 ? 0 : clampReadingIndex(readingIndex, readingList.length) + 1}
          readingTotal={readingList.length}
          currentReadingLabel={currentReadingItem?.label ?? null}
          onReadingPrev={handleReadingPrev}
          onReadingNext={handleReadingNext}
          readingOrderItems={readingOrderItems}
          canAddSelectedItemToReadingOrder={Boolean(selectedIsland || selectedCard)}
          onAddSelectedItemToReadingOrder={handleAddSelectedItemToReadingOrder}
          onMoveReadingOrderItem={handleMoveReadingOrderItem}
          onRemoveReadingOrderItem={handleRemoveReadingOrderItem}
          aggregatedEdgeInspectorItems={aggregatedEdgeInspectorItems}
          onPromoteAggregatedEdge={handlePromoteAggregatedEdge}
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
      <input
        ref={compareImportInputRef}
        type="file"
        accept="application/json,.json"
        onChange={(event) => {
          void handleComparisonFileChange(event);
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
            onCameraChange={setCanvasCamera}
            cameraTransformRequest={cameraTransformRequest}
            selectedCardIds={selectedCardIds}
            onCardSelect={handleCardSelect}
            onCanvasBackgroundClick={handleCanvasBackgroundClick}
            onMarqueeSelect={handleMarqueeSelect}
            searchQuery={normalizedSearchQuery}
            matchedCardIds={matchedCardIdSet}
            activeMatchedCardId={activeMatchedCardId}
            hiddenCardIds={hiddenCardIdSet}
            hideSourceCards={hideSourceCards || summaryView || abstractMapView}
            deemphasizedCardIds={summaryView || abstractMapView ? loneWolfCardIdSet : undefined}
            viewState={{
              hideSourceCards: hideSourceCards || summaryView || abstractMapView,
              showCanonicalOnlyEdges,
              showReadingOrder,
              showLabelBounds,
            }}
            revealCardIds={mergedRevealCardIds}
            showCanonicalOnlyEdges={showCanonicalOnlyEdges}
            summaryView={summaryView}
            abstractMapView={abstractMapView}
            lodEnabled={lodEnabled}
            lodThresholds={lodThresholds}
            lodLevelOverride={lodLevelOverride}
            lodShowLoneWolvesWhenFar={lodShowLoneWolvesWhenFar}
            effectiveCollapsedIslandIds={effectiveCollapsedIslandIdSet}
            showDerivedIslandEdges={summaryView || abstractMapView || effectiveCollapsedIslandIdSet.size > 0 || currentLod?.level === "far"}
            focusCardId={focusCardId}
            focusWorldPoint={focusWorldPoint}
            focusRequestSeq={focusRequestSeq}
            flashReference={flashReference}
            flashRequestSeq={flashRequestSeq}
            isPickingEdgeTarget={isPickingEdgeTarget}
            suggestionMoveDiffs={suggestionMoveDiffs}
            selectedEdgeId={selectedEdgeId}
            onEdgeSelect={handleEdgeSelect}
            onAggregatedEdgesChange={setVisibleAggregatedEdges}
            showReadingOrder={showReadingOrder}
            readingOrderEditMode={isReadingOrderEditMode}
            onReadingOrderRemove={handleRemoveReadingOrderEntry}
            onReadingOrderReorder={handleReorderReadingOrderEntry}
            visibleIslandIds={visibleIslandIdSet}
            polygonVertexEditIslandId={
              isPolygonVertexEditEnabled && selectedIsland?.shape?.kind === "polygon" ? selectedIsland.id : null
            }
            onPolygonVertexMove={handlePolygonVertexMove}
            onPolygonVertexAdd={handlePolygonVertexAdd}
            onPolygonVertexRemove={handlePolygonVertexRemove}
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
