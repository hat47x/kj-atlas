import { useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { CRITIQUE_TAGS } from "../domain/types";
import type { AggregatedEdgeMeta } from "../canvas/CanvasShell";
import {
  buildIslandRelationExplanation,
  formatIslandRelationExplanationMarkdown,
  type IslandRelationEdgeSelection,
} from "../domain/island_relation_explain";
import type { Card, CritiqueTag, DocumentV2, EvidenceLink, Island, RelationSummary } from "../domain/types";
import { RELATION_SUMMARY_TEXT_MAX_LENGTH } from "../domain/relation_summary_ops";
import type { OutlineQualityReport } from "../domain/view/outline_quality";
import type { Recommendation } from "../domain/view/recommendations";
import type { ContradictionReport, ContradictionSignal } from "../domain/view/contradiction_checks";
import { rankDistributionIslands, type DistributionReport } from "../domain/view/distribution_checks";
import type { ClaimType, ClaimTypeMixReport } from "../domain/view/claim_type_checks";
import type { EvidenceGapReport } from "../domain/view/evidence_gap_checks";
import type { BalanceFinding, DialecticBalanceReport } from "../domain/view/dialectic_balance";
import { downloadTextFile } from "../export/narrative_export";
import { TraceWorkerClient } from "../worker/trace_client";
import type { MergeAuditEntry } from "../domain/view/audit_log";

type SummaryGroundingItem = {
  id: string;
  text: string;
  kind: "canonical" | "source";
};

type ReadingOrderItem = {
  id: string;
  label: string;
};

type AggregatedEdgeInspectorItem = {
  id: string;
  label: string;
};

type SidePanelProps = {
  selectedCard: Card | null;
  sourceCardsForSelectedCanonical: Card[];
  revealedSourceCardIds: Set<string>;
  selectedIsland: Island | null;
  selectedCardCount: number;
  onCreateRepresentativeCard: () => void;
  onCardCritiqueChange: (value: string) => void;
  onCardCritiqueTagsChange: (value: string[]) => void;
  onCardClaimTypeChange: (value: ClaimType) => void;
  onAddEvidenceLink: (payload: { toCardId: string; type: EvidenceLink["type"] }) => void;
  onRemoveEvidenceLink: (evidenceLinkId: string) => void;
  onFocusCardById: (cardId: string) => void;
  onTitleChange: (value: string) => void;
  onTitleReviewedChange: (value: boolean) => void;
  onSummaryTextChange: (value: string) => void;
  onRestoreSummaryHistoryEntry: (historyEntryId: string) => void;
  onShowSummaryHistoryGrounding: (groundingIds: string[]) => void;
  onSummaryReviewedChange: (value: boolean) => void;
  onSuggestIslandSummary: () => void;
  isSuggestingIslandSummary: boolean;
  islandSummarySuggestionWarnings: string[];
  summaryGroundingItems: SummaryGroundingItem[];
  onImageUrlChange: (value: string) => void;
  onImageReviewedChange: (value: boolean) => void;
  onIslandCollapsedChange: (value: boolean) => void;
  isSelectedIslandCollapsed: boolean;
  hasIslands: boolean;
  isAnyIslandCollapsed: boolean;
  onCollapseAllIslands: () => void;
  onExpandAllIslands: () => void;
  onIslandCritiqueChange: (value: string) => void;
  onIslandCritiqueTagsChange: (value: string[]) => void;
  onAddSelectedCards: () => void;
  onRemoveSelectedCards: () => void;
  onDeleteIsland: () => void;
  onFocusIsland: () => void;
  onFocusCard: () => void;
  summaryView: boolean;
  abstractMapView: boolean;
  isSelectedIslandTemporarilyRevealed: boolean;
  onToggleSelectedIslandTemporaryReveal: () => void;
  isGridSnapEnabled: boolean;
  onGridSnapToggle: (value: boolean) => void;
  onGenerateIslandPolygon: () => void;
  isPolygonVertexEditEnabled: boolean;
  onPolygonVertexEditEnabledChange: (value: boolean) => void;
  showCanonicalOnlyEdges: boolean;
  onShowCanonicalOnlyEdgesChange: (value: boolean) => void;
  onSourceCardInspect: (cardId: string) => void;
  onSummaryGroundingCardInspect: (cardId: string) => void;
  onShowAllSummaryGrounding: () => void;
  onClearTemporaryReveal: () => void;
  groundingVisibilityMessage: string | null;
  onShowAllSourcesChange: (value: boolean) => void;
  document: DocumentV2 | null;
  selectedIslandRelationEdge: IslandRelationEdgeSelection | null;
  selectedAggregatedEdge: AggregatedEdgeMeta | null;
  onRevealSelectedEdgeSources: () => void;
  onInspectSelectedEdgeCard: (cardId: string) => void;
  selectedRelationSummary: RelationSummary | null;
  safeMode: boolean;
  isGeneratingRelationSummary: boolean;
  onGenerateRelationSummary: () => void;
  onRelationSummaryCommit: (value: string) => void;
  onRestoreRelationSummaryHistoryEntry: (historyEntryId: string) => void;
  onRelationSummaryReviewedChange: (value: boolean) => void;
  onRelationSummaryGroundingInspect: (cardId: string) => void;
  onAlignLeft: () => void;
  onAlignRight: () => void;
  onAlignTop: () => void;
  onAlignBottom: () => void;
  onDistributeHorizontally: () => void;
  onDistributeVertically: () => void;
  canStartConnect: boolean;
  isPickingEdgeTarget: boolean;
  connectEdgeType: "related" | "negate";
  onConnectEdgeTypeChange: (value: "related" | "negate") => void;
  onStartConnect: () => void;
  onCancelConnect: () => void;
  guidedFlowEnabled: boolean;
  onGuidedFlowEnabledChange: (value: boolean) => void;
  guidedFlowStepId: "review" | "classify" | "evidence" | "contradiction";
  guidedFlowStepIndex: number;
  guidedFlowTotalSteps: number;
  guidedFlowStepTitle: string;
  guidedFlowStepDescription: string;
  guidedFlowStepOptional: boolean;
  guidedFlowTargetIndex: number;
  guidedFlowTargetTotal: number;
  guidedFlowSuggestedActions: string[];
  onGuidedFlowPrevStep: () => void;
  onGuidedFlowNextStep: () => void;
  onGuidedFlowNextTarget: () => void;
  onGuidedFlowOpenRelevantEditor: () => void;
  guidedFlowOpenEditorRequestSeq: number;
  readingNavEnabled: boolean;
  onReadingNavEnabledChange: (value: boolean) => void;
  readingMode: "islands" | "islands+cards";
  onReadingModeChange: (value: "islands" | "islands+cards") => void;
  reviewedOnly: boolean;
  onReadingReviewedOnlyToggle: () => void;
  outlineIncludeCardTexts: boolean;
  onOutlineIncludeCardTextsChange: (value: boolean) => void;
  outlineIncludeRelationSummaries: boolean;
  onOutlineIncludeRelationSummariesChange: (value: boolean) => void;
  outlineIncludeUnreviewed: boolean;
  onOutlineIncludeUnreviewedChange: (value: boolean) => void;
  outlineAppendDiagnostics: boolean;
  onOutlineAppendDiagnosticsChange: (value: boolean) => void;
  outlineAppendRecommendations: boolean;
  onOutlineAppendRecommendationsChange: (value: boolean) => void;
  outlineQualityReport: OutlineQualityReport | null;
  outlineRecommendations: Recommendation[];
  contradictionReport: ContradictionReport | null;
  distributionReport: DistributionReport | null;
  claimTypeMixReport: ClaimTypeMixReport | null;
  evidenceGapReport: EvidenceGapReport | null;
  dialecticBalanceReport: DialecticBalanceReport | null;
  onRunOutlineDiagnostics: () => void;
  isDiagnosticsRunning: boolean;
  onCancelDiagnostics: () => void;
  computeProgressMessage: string | null;
  onFocusOutlineDiagnosticRef: (kind: "island" | "card", id: string) => void;
  onFocusContradictionSignal: (signal: ContradictionSignal) => void;
  onFocusDistributionIsland: (islandId: string) => void;
  onFocusDialecticBalanceFinding: (finding: BalanceFinding) => void;
  onCopyReadingOutlineMd: () => void;
  onDownloadReadingOutlineMd: () => void;
  onEvidenceTraceError: (message: string) => void;
  readingStep: number;
  readingTotal: number;
  currentReadingLabel: string | null;
  onReadingPrev: () => void;
  onReadingNext: () => void;
  readingOrderItems: ReadingOrderItem[];
  canAddSelectedItemToReadingOrder: boolean;
  onAddSelectedItemToReadingOrder: () => void;
  onMoveReadingOrderItem: (index: number, direction: -1 | 1) => void;
  onRemoveReadingOrderItem: (index: number) => void;
  aggregatedEdgeInspectorItems: AggregatedEdgeInspectorItem[];
  onPromoteAggregatedEdge: (edgeId: string) => void;
  evidenceOverlayEnabled: boolean;
  evidenceOverlayScope: "all" | "selection";
  onEnableEvidenceOverlaySelectionExplore: () => void;
  topContent?: ReactNode;
  importedPackSnapshotUrl?: string | null;
  importedPackDiagnosticsMd?: string | null;
  mergeAuditLog: MergeAuditEntry[];
};

export function SidePanel({
  selectedCard,
  sourceCardsForSelectedCanonical,
  revealedSourceCardIds,
  selectedIsland,
  selectedCardCount,
  onCreateRepresentativeCard,
  onCardCritiqueChange,
  onCardCritiqueTagsChange,
  onCardClaimTypeChange,
  onAddEvidenceLink,
  onRemoveEvidenceLink,
  onFocusCardById,
  onTitleChange,
  onTitleReviewedChange,
  onSummaryTextChange,
  onRestoreSummaryHistoryEntry,
  onShowSummaryHistoryGrounding,
  onSummaryReviewedChange,
  onSuggestIslandSummary,
  isSuggestingIslandSummary,
  islandSummarySuggestionWarnings,
  summaryGroundingItems,
  onImageUrlChange,
  onImageReviewedChange,
  onIslandCollapsedChange,
  isSelectedIslandCollapsed,
  hasIslands,
  isAnyIslandCollapsed,
  onCollapseAllIslands,
  onExpandAllIslands,
  onIslandCritiqueChange,
  onIslandCritiqueTagsChange,
  onAddSelectedCards,
  onRemoveSelectedCards,
  onDeleteIsland,
  onFocusIsland,
  onFocusCard,
  summaryView,
  abstractMapView,
  isSelectedIslandTemporarilyRevealed,
  onToggleSelectedIslandTemporaryReveal,
  isGridSnapEnabled,
  onGridSnapToggle,
  onGenerateIslandPolygon,
  isPolygonVertexEditEnabled,
  onPolygonVertexEditEnabledChange,
  showCanonicalOnlyEdges,
  onShowCanonicalOnlyEdgesChange,
  onSourceCardInspect,
  onSummaryGroundingCardInspect,
  onShowAllSummaryGrounding,
  onClearTemporaryReveal,
  groundingVisibilityMessage,
  onShowAllSourcesChange,
  document,
  selectedIslandRelationEdge,
  selectedAggregatedEdge,
  onRevealSelectedEdgeSources,
  onInspectSelectedEdgeCard,
  selectedRelationSummary,
  safeMode,
  isGeneratingRelationSummary,
  onGenerateRelationSummary,
  onRelationSummaryCommit,
  onRestoreRelationSummaryHistoryEntry,
  onRelationSummaryReviewedChange,
  onRelationSummaryGroundingInspect,
  onAlignLeft,
  onAlignRight,
  onAlignTop,
  onAlignBottom,
  onDistributeHorizontally,
  onDistributeVertically,
  canStartConnect,
  isPickingEdgeTarget,
  connectEdgeType,
  onConnectEdgeTypeChange,
  onStartConnect,
  onCancelConnect,
  guidedFlowEnabled,
  onGuidedFlowEnabledChange,
  guidedFlowStepId,
  guidedFlowStepIndex,
  guidedFlowTotalSteps,
  guidedFlowStepTitle,
  guidedFlowStepDescription,
  guidedFlowStepOptional,
  guidedFlowTargetIndex,
  guidedFlowTargetTotal,
  guidedFlowSuggestedActions,
  onGuidedFlowPrevStep,
  onGuidedFlowNextStep,
  onGuidedFlowNextTarget,
  onGuidedFlowOpenRelevantEditor,
  guidedFlowOpenEditorRequestSeq,
  readingNavEnabled,
  onReadingNavEnabledChange,
  readingMode,
  onReadingModeChange,
  reviewedOnly,
  onReadingReviewedOnlyToggle,
  outlineIncludeCardTexts,
  onOutlineIncludeCardTextsChange,
  outlineIncludeRelationSummaries,
  onOutlineIncludeRelationSummariesChange,
  outlineIncludeUnreviewed,
  onOutlineIncludeUnreviewedChange,
  outlineAppendDiagnostics,
  onOutlineAppendDiagnosticsChange,
  outlineAppendRecommendations,
  onOutlineAppendRecommendationsChange,
  outlineQualityReport,
  outlineRecommendations,
  contradictionReport,
  distributionReport,
  claimTypeMixReport,
  evidenceGapReport,
  dialecticBalanceReport,
  onRunOutlineDiagnostics,
  isDiagnosticsRunning,
  onCancelDiagnostics,
  computeProgressMessage,
  onFocusOutlineDiagnosticRef,
  onFocusContradictionSignal,
  onFocusDistributionIsland,
  onFocusDialecticBalanceFinding,
  onCopyReadingOutlineMd,
  onDownloadReadingOutlineMd,
  onEvidenceTraceError,
  readingStep,
  readingTotal,
  currentReadingLabel,
  onReadingPrev,
  onReadingNext,
  readingOrderItems,
  canAddSelectedItemToReadingOrder,
  onAddSelectedItemToReadingOrder,
  onMoveReadingOrderItem,
  onRemoveReadingOrderItem,
  aggregatedEdgeInspectorItems,
  onPromoteAggregatedEdge,
  evidenceOverlayEnabled,
  evidenceOverlayScope,
  onEnableEvidenceOverlaySelectionExplore,
  topContent,
  importedPackSnapshotUrl,
  importedPackDiagnosticsMd,
  mergeAuditLog,
}: SidePanelProps) {
  const [hasImagePreviewError, setHasImagePreviewError] = useState(false);
  const [summaryDraft, setSummaryDraft] = useState("");
  const [expandedSummaryHistoryEntryId, setExpandedSummaryHistoryEntryId] = useState<string | null>(null);
  const [relationSummaryDraft, setRelationSummaryDraft] = useState("");
  const [expandedRelationSummaryHistoryEntryId, setExpandedRelationSummaryHistoryEntryId] = useState<string | null>(null);
  const [expandedMergeAuditEntryId, setExpandedMergeAuditEntryId] = useState<string | null>(null);
  const [relationSummaryFeedback, setRelationSummaryFeedback] = useState<string | null>(null);
  const [copyExplanationFeedback, setCopyExplanationFeedback] = useState<"idle" | "copied" | "failed">("idle");
  const [showOnlyHighImpactRecommendations, setShowOnlyHighImpactRecommendations] = useState(false);
  const [isEvidenceModalOpen, setIsEvidenceModalOpen] = useState(false);
  const [pendingEvidenceType, setPendingEvidenceType] = useState<EvidenceLink["type"]>("supports");
  const [evidenceTargetQuery, setEvidenceTargetQuery] = useState("");
  const [pendingEvidenceTargetId, setPendingEvidenceTargetId] = useState<string>("");
  const [contradictionTraceDepthLimit, setContradictionTraceDepthLimit] = useState(1);
  const [contradictionTraceIncludeSupports, setContradictionTraceIncludeSupports] = useState(true);
  const [isTraceRunning, setIsTraceRunning] = useState(false);
  const [traceProgressMessage, setTraceProgressMessage] = useState<string | null>(null);
  const traceClientRef = useRef<TraceWorkerClient | null>(null);
  const traceAbortRef = useRef<AbortController | null>(null);

  const summaryHistoryEntries = useMemo(() => {
    const entries = selectedIsland?.summaryHistory ?? [];
    return [...entries].reverse();
  }, [selectedIsland?.summaryHistory]);

  const relationSummaryHistoryEntries = useMemo(() => {
    const entries = selectedRelationSummary?.history ?? [];
    return [...entries].reverse();
  }, [selectedRelationSummary?.history]);

  const mergeAuditEntries = useMemo(() => {
    return [...mergeAuditLog].sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  }, [mergeAuditLog]);

  const formatSummaryHistoryTimestamp = (createdAt: string) => {
    const parsedDate = new Date(createdAt);
    if (Number.isNaN(parsedDate.getTime())) {
      return createdAt;
    }

    return parsedDate.toLocaleString();
  };


  const copyText = async (value: string): Promise<boolean> => {
    try {
      await navigator.clipboard.writeText(value);
      return true;
    } catch {
      return false;
    }
  };

  const buildMergeSummaryMarkdown = (entry: MergeAuditEntry): string => {
    const byKind = Object.entries(entry.summary.byKind)
      .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
      .map(([kind, count]) => `- ${kind}: ${count}`)
      .join("\n");
    return [
      `- timestamp: ${entry.createdAt}`,
      `- source: ${entry.source.fileName ?? entry.source.packId ?? "unknown"}`,
      `- source kind: ${entry.source.kind}`,
      `- total items: ${entry.summary.totalItems}`,
      "- by kind:",
      byKind || "- (none)",
      `- item ids: ${(entry.details.itemIds?.ids ?? []).join(", ") || "(none)"}`,
      `- card ids: ${(entry.details.entityIds?.cards?.ids ?? []).join(", ") || "(none)"}`,
      `- island ids: ${(entry.details.entityIds?.islands?.ids ?? []).join(", ") || "(none)"}`,
      `- evidence ids: ${(entry.details.entityIds?.evidence?.ids ?? []).join(", ") || "(none)"}`,
    ].join("\n");
  };

  const renderIdList = (label: string, value?: { ids: string[]; truncatedCount?: number }) => {
    const listed = value?.ids ?? [];
    const truncated = value?.truncatedCount ?? 0;
    return (
      <div>
        {label}: {listed.join(", ") || "(none)"}
        {truncated > 0 ? ` (+${truncated} truncated)` : ""}
      </div>
    );
  };

  const selectedIslandRelationExplanation = useMemo(() => {
    if (!document || !selectedIslandRelationEdge) {
      return null;
    }

    return buildIslandRelationExplanation(document, selectedIslandRelationEdge);
  }, [document, selectedIslandRelationEdge]);

  useEffect(() => {
    setHasImagePreviewError(false);
  }, [selectedIsland?.id, selectedIsland?.imageUrl]);

  useEffect(() => {
    if (guidedFlowOpenEditorRequestSeq <= 0) {
      return;
    }

    if (guidedFlowStepId !== "evidence" && guidedFlowStepId !== "contradiction") {
      return;
    }

    if (!selectedCard) {
      return;
    }

    setIsEvidenceModalOpen(true);
  }, [guidedFlowOpenEditorRequestSeq, guidedFlowStepId, selectedCard]);

  useEffect(() => {
    setSummaryDraft(selectedIsland?.summaryText ?? "");
    setExpandedSummaryHistoryEntryId(null);
  }, [selectedIsland?.id, selectedIsland?.summaryText]);

  useEffect(() => {
    setRelationSummaryDraft(selectedRelationSummary?.text ?? "");
    setExpandedRelationSummaryHistoryEntryId(null);
    setRelationSummaryFeedback(null);
  }, [selectedRelationSummary?.sourceSignature, selectedRelationSummary?.text]);

  useEffect(() => {
    setCopyExplanationFeedback("idle");
  }, [selectedIslandRelationEdge?.edgeId]);

  useEffect(() => {
    return () => {
      traceAbortRef.current?.abort();
      traceClientRef.current?.dispose();
    };
  }, []);

  const hasCardSelection = selectedCardCount > 0;
  const canAlign = selectedCardCount >= 2;
  const hideUnreviewedRelationSummary = safeMode && selectedRelationSummary?.reviewed === false;
  const canDistribute = selectedCardCount >= 3;
  const selectedCardLabel = useMemo(() => {
    if (selectedCardCount === 1) {
      return "1 card selected";
    }

    return `${selectedCardCount} cards selected`;
  }, [selectedCardCount]);

  const visibleRecommendations = useMemo(() => {
    if (!showOnlyHighImpactRecommendations) {
      return outlineRecommendations;
    }

    return outlineRecommendations.filter((recommendation) => recommendation.impactLevel === "high");
  }, [outlineRecommendations, showOnlyHighImpactRecommendations]);

  const outgoingEvidenceLinks = useMemo(() => {
    if (!document || !selectedCard) return [];
    return (document.evidenceLinks ?? []).filter((link) => link.fromCardId === selectedCard.id);
  }, [document, selectedCard]);

  const incomingEvidenceLinks = useMemo(() => {
    if (!document || !selectedCard) return [];
    return (document.evidenceLinks ?? []).filter((link) => link.toCardId === selectedCard.id);
  }, [document, selectedCard]);

  const availableEvidenceTargets = useMemo(() => {
    if (!document || !selectedCard) return [];
    const query = evidenceTargetQuery.trim().toLowerCase();
    return document.cards
      .filter((card) => card.id !== selectedCard.id)
      .filter((card) => (query.length === 0 ? true : card.text.toLowerCase().includes(query) || card.id.toLowerCase().includes(query)))
      .sort((a, b) => a.id.localeCompare(b.id));
  }, [document, evidenceTargetQuery, selectedCard]);

  const evidenceGapFindingsByCode = useMemo(() => {
    const map: Record<"E001" | "E002" | "E003" | "E004", EvidenceGapReport["findings"]> = { E001: [], E002: [], E003: [], E004: [] };
    if (!evidenceGapReport) return map;
    for (const finding of evidenceGapReport.findings) {
      map[finding.code] = [...map[finding.code], finding];
    }
    return map;
  }, [evidenceGapReport]);

  const selectedCardContradictionsCount = useMemo(() => {
    if (!selectedCard || !document) {
      return 0;
    }

    return (document.evidenceLinks ?? []).filter((link) => link.type === "contradicts" && (link.toCardId === selectedCard.id || link.fromCardId === selectedCard.id)).length;
  }, [document, selectedCard]);

  const computeTraceMarkdown = async (kind: "evidence" | "contradiction") => {
    if (!document || !selectedCard) {
      return null;
    }
    if (!traceClientRef.current) {
      traceClientRef.current = new TraceWorkerClient();
    }

    const controller = new AbortController();
    traceAbortRef.current = controller;
    setIsTraceRunning(true);

    const outcome = await traceClientRef.current.computeTrace({
      doc: document,
      options: {
        kind,
        startCardId: selectedCard.id,
        maxHops: contradictionTraceDepthLimit,
        maxNodes: 80,
        safeMode,
        includeRationale: contradictionTraceIncludeSupports,
      },
    }, {
      signal: controller.signal,
      onProgress: (progress) => setTraceProgressMessage(`${kind === "evidence" ? "Evidence" : "Contradiction"} trace: ${progress.stage} (${progress.percent}%)`),
    });

    setIsTraceRunning(false);
    setTraceProgressMessage(null);
    traceAbortRef.current = null;

    if (outcome.status === "cancelled") {
      onEvidenceTraceError("Trace cancelled");
      return null;
    }
    if (outcome.result.traceMd.startsWith("Error:")) {
      onEvidenceTraceError(outcome.result.traceMd);
      return null;
    }

    return outcome.result.traceMd;
  };

  const handleCopyContradictionTrace = async () => {
    const markdown = await computeTraceMarkdown("contradiction");
    if (!markdown) {
      return;
    }

    try {
      await navigator.clipboard.writeText(markdown);
    } catch {
      onEvidenceTraceError("Failed to copy contradiction trace");
    }
  };

  const handleDownloadContradictionTrace = () => {
    void computeTraceMarkdown("contradiction").then((markdown) => {
      if (!markdown) {
        return;
      }
      downloadTextFile("contradiction_trace.md", "text/markdown", markdown);
    });
  };

  const handleCopyEvidenceTrace = async () => {
    const markdown = await computeTraceMarkdown("evidence");
    if (!markdown) {
      return;
    }

    try {
      await navigator.clipboard.writeText(markdown);
    } catch {
      onEvidenceTraceError("Failed to copy evidence trace");
    }
  };

  const handleDownloadEvidenceTrace = () => {
    void computeTraceMarkdown("evidence").then((markdown) => {
      if (!markdown) {
        return;
      }
      downloadTextFile("evidence_trace.md", "text/markdown", markdown);
    });
  };

  const outlineDiagnosticsCounts = useMemo(() => {
    if (!outlineQualityReport) {
      return { error: 0, warn: 0, info: 0 };
    }

    return outlineQualityReport.findings.reduce((acc, finding) => {
      acc[finding.severity] += 1;
      return acc;
    }, { error: 0, warn: 0, info: 0 });
  }, [outlineQualityReport]);


  const claimTypeLabels: Record<ClaimType, string> = {
    fact: "Fact (観測/一次情報)",
    claim: "Claim (主張/解釈)",
    hypothesis: "Hypothesis (仮説)",
    unknown: "Unknown (未分類)",
  };

  const claimTypeBadgeColors: Record<ClaimType, { backgroundColor: string; color: string }> = {
    fact: { backgroundColor: "#dcfce7", color: "#166534" },
    claim: { backgroundColor: "#dbeafe", color: "#1d4ed8" },
    hypothesis: { backgroundColor: "#fef3c7", color: "#92400e" },
    unknown: { backgroundColor: "#e2e8f0", color: "#334155" },
  };

  const contradictionSignalsBySeverity = useMemo(() => {
    if (!contradictionReport) {
      return { warn: [] as ContradictionSignal[], info: [] as ContradictionSignal[] };
    }

    return contradictionReport.signals.reduce((acc, signal) => {
      acc[signal.severity].push(signal);
      return acc;
    }, { warn: [] as ContradictionSignal[], info: [] as ContradictionSignal[] });
  }, [contradictionReport]);

  const islandDistributionRows = useMemo(() => {
    if (!document) {
      return [] as Array<{ id: string; title: string; cardCount: number; degree: number }>;
    }
    const rankings = rankDistributionIslands(document, document.islands.length);
    const islandById = new Map(document.islands.map((island) => [island.id, island] as const));
    return rankings.loaded.map((row) => {
      const island = islandById.get(row.id);
      return {
        id: row.id,
        title: island?.title?.trim() ? island.title : row.id,
        cardCount: row.cardCount,
        degree: row.degree,
      };
    });
  }, [document]);

  const loadedIslands = useMemo(() => {
    return [...islandDistributionRows]
      .sort((left, right) => (right.cardCount - left.cardCount) || (right.degree - left.degree) || left.id.localeCompare(right.id))
      .slice(0, 5);
  }, [islandDistributionRows]);

  const isolatedIslands = useMemo(() => {
    return islandDistributionRows
      .filter((island) => island.degree === 0)
      .sort((left, right) => (right.cardCount - left.cardCount) || left.id.localeCompare(right.id))
      .slice(0, 5);
  }, [islandDistributionRows]);

  const claimTypeMixSection = claimTypeMixReport ? (
    <details style={{ marginTop: 8 }}>
      <summary style={{ fontSize: 12, cursor: "pointer", color: "#7c3aed" }}>
        Claim typing ({claimTypeMixReport.findings.length})
      </summary>
      <div style={{ fontSize: 11, color: "#334155", marginTop: 6 }}>
        cards:{claimTypeMixReport.stats.totalCards} · F/C/H/U:{claimTypeMixReport.stats.countsByType.fact}/{claimTypeMixReport.stats.countsByType.claim}/{claimTypeMixReport.stats.countsByType.hypothesis}/{claimTypeMixReport.stats.countsByType.unknown}
      </div>
      <div style={{ fontSize: 11, color: "#334155", marginTop: 4 }}>
        checked islands:{claimTypeMixReport.stats.islandsChecked} · mixed:{claimTypeMixReport.stats.islandsMixedCount} · hypothesis-dominant:{claimTypeMixReport.stats.islandsHypothesisDominantCount} · unknown-dominant:{claimTypeMixReport.stats.islandsUnknownDominantCount}
      </div>
      {claimTypeMixReport.findings.length === 0 ? (
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No claim typing findings.</div>
      ) : (
        <ul style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
          {claimTypeMixReport.findings.map((finding, index) => (
            <li key={`${finding.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
              <div style={{ fontWeight: 600 }}>[{finding.severity.toUpperCase()}] {finding.code} {finding.title}</div>
              <div>{finding.detail}</div>
              {finding.suggestedAction ? <div style={{ color: "#334155" }}>Action: {finding.suggestedAction}</div> : null}
              {finding.islandIds.length > 0 ? (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                  {finding.islandIds.map((islandId) => (
                    <button key={`${finding.code}_${islandId}`} type="button" onClick={() => { onFocusDistributionIsland(islandId); }} style={{ fontSize: 10, cursor: "pointer" }}>
                      Focus {islandId}
                    </button>
                  ))}
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </details>
  ) : null;

  const evidenceGapSection = evidenceGapReport ? (
    <details style={{ marginTop: 8 }}>
      <summary style={{ fontSize: 12, cursor: "pointer", color: "#7c3aed" }}>Evidence gaps ({evidenceGapReport.findings.length})</summary>
      <div style={{ marginTop: 6, fontSize: 11, color: "#334155", display: "grid", gap: 4 }}>
        <div>Links: {evidenceGapReport.stats.totalLinks} (supports {evidenceGapReport.stats.supportsLinks}, contradicts {evidenceGapReport.stats.contradictsLinks})</div>
        <div>Hypotheses no fact support: {evidenceGapReport.stats.hypothesesWithNoFactSupport}</div>
        <div>Claims no fact support: {evidenceGapReport.stats.claimsWithNoFactSupport}</div>
        <div>Unused facts: {evidenceGapReport.stats.factsUnusedAsEvidence}</div>
        <div>Contradictions needing grounding: {evidenceGapReport.stats.contradictionsWithoutCounterSupport}</div>
      </div>
      {(["E001", "E002", "E003", "E004"] as const).map((code) => {
        const findings = evidenceGapFindingsByCode[code] ?? [];
        if (findings.length === 0) return null;
        const titleByCode: Record<string, string> = {
          E001: "Hypotheses lacking fact support",
          E002: "Claims lacking fact support",
          E003: "Unused facts",
          E004: "Contradictions needing grounding",
        };

        return (
          <details key={code} style={{ marginTop: 6 }}>
            <summary style={{ fontSize: 11, cursor: "pointer", color: "#1f2937" }}>{titleByCode[code]} ({findings.length})</summary>
            <ul style={{ margin: "4px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
              {findings.map((finding, index) => (
                <li key={`${code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
                  <div>{finding.detail}</div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 4 }}>
                    {finding.cardIds.map((cardId) => (
                      <button key={`${code}_${index}_${cardId}`} type="button" style={{ fontSize: 10 }} onClick={() => { onFocusCardById(cardId); }}>
                        Focus card:{cardId}
                      </button>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          </details>
        );
      })}
    </details>
  ) : null;

  const distributionSignalsSection = distributionReport ? (
    <details style={{ marginTop: 8 }}>
      <summary style={{ fontSize: 12, cursor: "pointer", color: "#7c3aed" }}>
        Distribution signals ({distributionReport.findings.length})
      </summary>
      <div style={{ fontSize: 11, color: "#334155", marginTop: 6 }}>
        islands:{distributionReport.stats.islandCount} · cards:{distributionReport.stats.cardCount} · avg:{distributionReport.stats.avgCardsPerIsland.toFixed(2)} · median:{distributionReport.stats.medianCardsPerIsland.toFixed(2)} · p90:{distributionReport.stats.p90CardsPerIsland.toFixed(2)}
      </div>
      {distributionReport.findings.length === 0 ? (
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No distribution signals.</div>
      ) : (
        <ul style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
          {distributionReport.findings.map((finding, index) => (
            <li key={`${finding.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
              <div style={{ fontWeight: 600 }}>[{finding.severity.toUpperCase()}] {finding.code} {finding.title}</div>
              <div>{finding.detail}</div>
              {finding.suggestedAction ? <div style={{ color: "#334155" }}>Action: {finding.suggestedAction}</div> : null}
            </li>
          ))}
        </ul>
      )}
      <div style={{ marginTop: 8 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "#334155" }}>Most loaded islands</div>
        {loadedIslands.length === 0 ? (
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>No islands.</div>
        ) : (
          <ul style={{ margin: "4px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
            {loadedIslands.map((item) => (
              <li key={`loaded_${item.id}`} style={{ fontSize: 11, color: "#0f172a" }}>
                <div>{item.title} · cards:{item.cardCount} · degree:{item.degree}</div>
                <button type="button" onClick={() => { onFocusDistributionIsland(item.id); }} style={{ fontSize: 10, cursor: "pointer", marginTop: 2 }}>Focus</button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div style={{ marginTop: 8 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "#334155" }}>Most isolated islands</div>
        {isolatedIslands.length === 0 ? (
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>No isolated islands.</div>
        ) : (
          <ul style={{ margin: "4px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
            {isolatedIslands.map((item) => (
              <li key={`isolated_${item.id}`} style={{ fontSize: 11, color: "#0f172a" }}>
                <div>{item.title} · cards:{item.cardCount} · degree:{item.degree}</div>
                <button type="button" onClick={() => { onFocusDistributionIsland(item.id); }} style={{ fontSize: 10, cursor: "pointer", marginTop: 2 }}>Focus</button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </details>
  ) : null;

  const dialecticBalanceSection = dialecticBalanceReport ? (
    <details style={{ marginTop: 8 }}>
      <summary style={{ fontSize: 12, cursor: "pointer", color: "#7c3aed" }}>Dialectic balance ({dialecticBalanceReport.findings.length})</summary>
      <div style={{ marginTop: 6, fontSize: 11, color: "#334155", display: "grid", gap: 4 }}>
        <div>hypotheses: {dialecticBalanceReport.stats.hypothesisCount} (supported: {dialecticBalanceReport.stats.hypothesisWithSupportCount}, contradicted: {dialecticBalanceReport.stats.hypothesisWithContradictionCount})</div>
        <div>claims: {dialecticBalanceReport.stats.claimCount} (supported: {dialecticBalanceReport.stats.claimWithSupportCount}, contradicted: {dialecticBalanceReport.stats.claimWithContradictionCount})</div>
        <div>facts: {dialecticBalanceReport.stats.factCount}</div>
        <div>links: supports {dialecticBalanceReport.stats.supportsCount}, contradicts {dialecticBalanceReport.stats.contradictsCount}</div>
      </div>
      {dialecticBalanceReport.findings.length === 0 ? (
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No dialectic balance findings.</div>
      ) : (
        <ul style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
          {dialecticBalanceReport.findings.map((finding, index) => (
            <li key={`${finding.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
              <div style={{ fontWeight: 600 }}>[{finding.severity.toUpperCase()}] {finding.code} {finding.title}</div>
              <div>{finding.detail}</div>
              <div style={{ color: "#334155" }}>Action: {finding.suggestedAction}</div>
              {finding.cardIds && finding.cardIds.length > 0 ? (
                <button
                  type="button"
                  style={{ fontSize: 10, marginTop: 4, cursor: "pointer" }}
                  onClick={() => {
                    onFocusDialecticBalanceFinding(finding);
                  }}
                >
                  Focus sample
                </button>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </details>
  ) : null;


  const handleCopyExplanationClick = async () => {
    if (!selectedIslandRelationExplanation) {
      return;
    }

    try {
      await navigator.clipboard.writeText(formatIslandRelationExplanationMarkdown(selectedIslandRelationExplanation));
      setCopyExplanationFeedback("copied");
    } catch {
      setCopyExplanationFeedback("failed");
    }
  };

  const handleDeleteIslandClick = () => {
    if (!selectedIsland) {
      return;
    }

    const shouldDelete = window.confirm(`Delete island \"${selectedIsland.title ?? selectedIsland.id}\"?`);
    if (!shouldDelete) {
      return;
    }

    onDeleteIsland();
  };

  const handleRemoveSelectedCardsClick = () => {
    if (!selectedIsland || !hasCardSelection) {
      return;
    }

    const shouldRemove = window.confirm(
      `Remove ${selectedCardLabel} from island "${selectedIsland.title ?? selectedIsland.id}"?`
    );
    if (!shouldRemove) {
      return;
    }

    onRemoveSelectedCards();
  };

  const hasSourceCardsForSelectedCanonical = sourceCardsForSelectedCanonical.length > 0;
  const isShowingAllSources =
    hasSourceCardsForSelectedCanonical &&
    sourceCardsForSelectedCanonical.every((card) => revealedSourceCardIds.has(card.id));

  const toggleCritiqueTag = (currentTags: string[] | undefined, tag: CritiqueTag): string[] => {
    const currentTagSet = new Set(currentTags ?? []);
    if (currentTagSet.has(tag)) {
      currentTagSet.delete(tag);
    } else {
      currentTagSet.add(tag);
    }

    return CRITIQUE_TAGS.filter((candidateTag) => currentTagSet.has(candidateTag));
  };

  return (
    <aside
      style={{
        width: 320,
        minWidth: 320,
        borderLeft: "1px solid #e2e8f0",
        backgroundColor: "#ffffff",
        padding: 12,
        boxSizing: "border-box",
        overflowY: "auto",
      }}
    >
      {topContent}
      {importedPackSnapshotUrl || importedPackDiagnosticsMd ? (
        <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0", display: "grid", gap: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>Pack Assets</div>
          {importedPackSnapshotUrl ? (
            <div style={{ display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#334155" }}>Snapshot</div>
              <img src={importedPackSnapshotUrl} alt="Imported review pack snapshot" style={{ width: "100%", border: "1px solid #cbd5e1", borderRadius: 6 }} />
              <a href={importedPackSnapshotUrl} download="snapshot.png" style={{ fontSize: 12, color: "#1d4ed8" }}>
                Download snapshot
              </a>
            </div>
          ) : null}
          {importedPackDiagnosticsMd ? (
            <div style={{ display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#334155" }}>Diagnostics</div>
              <pre style={{ margin: 0, maxHeight: 220, overflow: "auto", whiteSpace: "pre-wrap", fontSize: 11, backgroundColor: "#f8fafc", padding: 8, borderRadius: 6, border: "1px solid #e2e8f0" }}>
                {importedPackDiagnosticsMd}
              </pre>
            </div>
          ) : null}
        </section>
      ) : null}
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <details>
          <summary style={{ fontSize: 14, fontWeight: 700, color: "#0f172a", cursor: "pointer" }}>
            History ({mergeAuditEntries.length})
          </summary>
          <div style={{ marginTop: 8, display: "grid", gap: 8 }}>
            {mergeAuditEntries.length === 0 ? (
              <div style={{ fontSize: 12, color: "#64748b" }}>No merge history yet.</div>
            ) : (
              mergeAuditEntries.map((entry) => {
                const isExpanded = expandedMergeAuditEntryId === entry.id;
                const kindPairs = Object.entries(entry.summary.byKind).sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]));
                const topKinds = kindPairs.slice(0, 3).map(([kind, count]) => `${kind}:${count}`).join(", ");
                const fullKinds = kindPairs.map(([kind, count]) => `${kind}:${count}`).join(", ");
                return (
                  <div key={entry.id} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8 }}>
                    <button
                      type="button"
                      onClick={() => {
                        setExpandedMergeAuditEntryId(isExpanded ? null : entry.id);
                      }}
                      style={{ width: "100%", textAlign: "left", border: "none", background: "transparent", padding: 0, cursor: "pointer", display: "grid", gap: 4 }}
                    >
                      <div style={{ fontSize: 11, color: "#64748b" }}>{formatSummaryHistoryTimestamp(entry.createdAt)}</div>
                      <div style={{ fontSize: 12, color: "#0f172a" }}>{entry.source.fileName ?? entry.source.packId ?? "Unknown source"}</div>
                      <div style={{ fontSize: 11, color: "#334155" }}>{entry.summary.totalItems} items · {topKinds || "no kinds"}</div>
                    </button>
                    {isExpanded ? (
                      <div style={{ marginTop: 8, display: "grid", gap: 6, fontSize: 11, color: "#475569" }}>
                        <div>source kind: {entry.source.kind}</div>
                        <div>by kind: {fullKinds || "(none)"}</div>
                        {renderIdList("item ids", entry.details.itemIds)}
                        {renderIdList("card ids", entry.details.entityIds?.cards)}
                        {renderIdList("island ids", entry.details.entityIds?.islands)}
                        {renderIdList("evidence ids", entry.details.entityIds?.evidence)}
                        {entry.summary.warnings && entry.summary.warnings.length > 0 ? (
                          <div>warnings: {entry.summary.warnings.join(", ")}</div>
                        ) : null}
                        <div style={{ display: "flex", gap: 8 }}>
                          <button
                            type="button"
                            onClick={async () => {
                              await copyText(JSON.stringify(entry, null, 2));
                            }}
                          >
                            Copy entry JSON
                          </button>
                          <button
                            type="button"
                            onClick={async () => {
                              await copyText(buildMergeSummaryMarkdown(entry));
                            }}
                          >
                            Copy summary MD
                          </button>
                        </div>
                      </div>
                    ) : null}
                  </div>
                );
              })
            )}
          </div>
        </details>
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Guided Flow</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", marginBottom: 8 }}>
          <input
            type="checkbox"
            checked={guidedFlowEnabled}
            onChange={(event) => {
              onGuidedFlowEnabledChange(event.target.checked);
            }}
          />
          Enable
        </label>
        <div style={{ fontSize: 12, color: "#334155", marginBottom: 4 }}>
          Step {guidedFlowStepIndex + 1} / {guidedFlowTotalSteps}
        </div>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a" }}>
          {guidedFlowStepTitle}
          {guidedFlowStepOptional ? " (optional)" : ""}
        </div>
        <div style={{ fontSize: 11, color: "#64748b", marginTop: 4 }}>{guidedFlowStepDescription}</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginTop: 8, marginBottom: 8 }}>
          <button
            type="button"
            onClick={onGuidedFlowPrevStep}
            disabled={!guidedFlowEnabled || guidedFlowStepIndex <= 0}
            style={{ cursor: !guidedFlowEnabled || guidedFlowStepIndex <= 0 ? "not-allowed" : "pointer" }}
          >
            Prev step
          </button>
          <button
            type="button"
            onClick={onGuidedFlowNextStep}
            disabled={!guidedFlowEnabled || guidedFlowStepIndex >= guidedFlowTotalSteps - 1}
            style={{ cursor: !guidedFlowEnabled || guidedFlowStepIndex >= guidedFlowTotalSteps - 1 ? "not-allowed" : "pointer" }}
          >
            Next step
          </button>
        </div>
        <div style={{ display: "grid", gap: 8 }}>
          <button
            type="button"
            onClick={onGuidedFlowNextTarget}
            disabled={!guidedFlowEnabled || guidedFlowTargetTotal === 0}
            style={{ cursor: !guidedFlowEnabled || guidedFlowTargetTotal === 0 ? "not-allowed" : "pointer" }}
          >
            Next target
          </button>
          <button
            type="button"
            onClick={onGuidedFlowOpenRelevantEditor}
            disabled={!guidedFlowEnabled}
            style={{ cursor: guidedFlowEnabled ? "pointer" : "not-allowed" }}
          >
            Open relevant editor
          </button>
        </div>
        <div style={{ fontSize: 11, color: "#334155", marginTop: 8 }}>
          {guidedFlowTargetTotal === 0
            ? "No targets"
            : `Target ${Math.min(guidedFlowTargetIndex + 1, guidedFlowTargetTotal)} / ${guidedFlowTargetTotal}`}
        </div>
        {guidedFlowSuggestedActions.length > 0 ? (
          <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#334155", display: "grid", gap: 4 }}>
            {guidedFlowSuggestedActions.map((action) => (
              <li key={action}>{action}</li>
            ))}
          </ul>
        ) : null}
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Aggregated edge inspector</div>
        {aggregatedEdgeInspectorItems.length === 0 ? (
          <div style={{ fontSize: 12, color: "#64748b" }}>No aggregated edges available.</div>
        ) : (
          <div style={{ display: "grid", gap: 8 }}>
            {aggregatedEdgeInspectorItems.map((item) => (
              <div key={item.id} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8 }}>
                <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>{item.label}</div>
                <button
                  type="button"
                  onClick={() => {
                    onPromoteAggregatedEdge(item.id);
                  }}
                  style={{ width: "100%" }}
                >
                  Promote to real edge
                </button>
              </div>
            ))}
          </div>
        )}
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Layout</div>
        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 12,
            color: "#334155",
            marginBottom: 10,
          }}
        >
          <input
            type="checkbox"
            checked={isGridSnapEnabled}
            onChange={(event) => {
              onGridSnapToggle(event.target.checked);
            }}
          />
          Grid Snap (10)
        </label>
        <label
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            fontSize: 12,
            color: "#334155",
            marginBottom: 10,
          }}
        >
          <input
            type="checkbox"
            checked={showCanonicalOnlyEdges}
            onChange={(event) => {
              onShowCanonicalOnlyEdgesChange(event.target.checked);
            }}
          />
          Show canonical-only edges
        </label>
        <div style={{ display: "grid", gap: 6, marginBottom: 8 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeCardTexts}
              onChange={(event) => {
                onOutlineIncludeCardTextsChange(event.target.checked);
              }}
            />
            Include card texts
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeRelationSummaries}
              onChange={(event) => {
                onOutlineIncludeRelationSummariesChange(event.target.checked);
              }}
            />
            Include relation summaries
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeUnreviewed}
              disabled={safeMode}
              onChange={(event) => {
                onOutlineIncludeUnreviewedChange(event.target.checked);
              }}
            />
            Include unreviewed
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineAppendDiagnostics}
              onChange={(event) => {
                onOutlineAppendDiagnosticsChange(event.target.checked);
              }}
            />
            Append diagnostics
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineAppendRecommendations}
              onChange={(event) => {
                onOutlineAppendRecommendationsChange(event.target.checked);
              }}
            />
            Append recommendations
          </label>
          <button type="button" onClick={onRunOutlineDiagnostics} disabled={isDiagnosticsRunning}>{isDiagnosticsRunning ? "Working..." : "Run diagnostics"}</button>{isDiagnosticsRunning ? <button type="button" onClick={onCancelDiagnostics}>Cancel</button> : null}{isDiagnosticsRunning && computeProgressMessage ? <div style={{ fontSize: 12 }}>{computeProgressMessage}</div> : null}
          <div style={{ fontSize: 11, color: "#b45309" }}>Unreviewed content is draft; do not treat as confirmed.</div>
          {safeMode ? <div style={{ fontSize: 11, color: "#b45309" }}>Safe mode: unreviewed drafts are excluded.</div> : null}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <button type="button" onClick={onCopyReadingOutlineMd}>
              Copy outline (MD)
            </button>
            <button type="button" onClick={onDownloadReadingOutlineMd}>
              Download outline.md
            </button>
          </div>
          {outlineQualityReport ? (
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc", marginTop: 8 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a" }}>Quality report</div>
              <div style={{ fontSize: 11, color: "#334155", marginTop: 2 }}>
                Findings: {outlineDiagnosticsCounts.error} errors, {outlineDiagnosticsCounts.warn} warnings, {outlineDiagnosticsCounts.info} infos
                {outlineQualityReport.health !== undefined ? ` · Health ${outlineQualityReport.health}% (heuristic)` : ""}
              </div>
              <details style={{ marginTop: 6 }}>
                <summary style={{ fontSize: 12, cursor: "pointer", color: "#1d4ed8" }}>Show findings</summary>
                {outlineQualityReport.findings.length === 0 ? (
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No findings.</div>
                ) : (
                  <ul style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
                    {outlineQualityReport.findings.map((finding, index) => (
                      <li key={`${finding.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
                        <div style={{ fontWeight: 600 }}>[{finding.severity.toUpperCase()}] {finding.code} {finding.title}</div>
                        <div>{finding.detail}</div>
                        {finding.suggestedAction ? <div style={{ color: "#334155" }}>Action: {finding.suggestedAction}</div> : null}
                        {finding.entityRefs && finding.entityRefs.length > 0 ? (
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                            {finding.entityRefs.map((ref) => (
                              <button
                                key={`${finding.code}_${ref.kind}_${ref.id}`}
                                type="button"
                                onClick={() => {
                                  onFocusOutlineDiagnosticRef(ref.kind, ref.id);
                                }}
                                style={{ fontSize: 10, cursor: "pointer" }}
                              >
                                Focus {ref.kind}:{ref.id}
                              </button>
                            ))}
                          </div>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </details>
              {contradictionReport ? (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ fontSize: 12, cursor: "pointer", color: "#b45309" }}>
                    Contradiction signals ({contradictionReport.stats.signals})
                  </summary>
                  {contradictionReport.signals.length === 0 ? (
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No contradiction signals.</div>
                  ) : (
                    <div style={{ marginTop: 6, display: "grid", gap: 8 }}>
                      {["warn", "info"].map((severity) => {
                        const signals = contradictionSignalsBySeverity[severity as "warn" | "info"];
                        if (signals.length === 0) {
                          return null;
                        }

                        return (
                          <div key={severity}>
                            <div style={{ fontSize: 11, fontWeight: 600, color: severity === "warn" ? "#b45309" : "#334155" }}>
                              {severity.toUpperCase()} ({signals.length})
                            </div>
                            <ul style={{ margin: "4px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
                              {signals.map((signal, index) => (
                                <li key={`${signal.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
                                  <div style={{ fontWeight: 600 }}>[{signal.code}] {signal.title}</div>
                                  <div>{signal.detail}</div>
                                  {signal.suggestedAction ? <div style={{ color: "#334155" }}>Action: {signal.suggestedAction}</div> : null}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      onFocusContradictionSignal(signal);
                                    }}
                                    style={{ fontSize: 10, cursor: "pointer", marginTop: 4 }}
                                  >
                                    Focus
                                  </button>
                                </li>
                              ))}
                            </ul>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </details>
              ) : null}
              {distributionSignalsSection}
              {claimTypeMixSection}
              {evidenceGapSection}
              {dialecticBalanceSection}
              <details style={{ marginTop: 8 }}>
                <summary style={{ fontSize: 12, cursor: "pointer", color: "#1d4ed8" }}>Suggested next steps</summary>
                <label style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, fontSize: 11, color: "#334155" }}>
                  <input
                    type="checkbox"
                    checked={showOnlyHighImpactRecommendations}
                    onChange={(event) => {
                      setShowOnlyHighImpactRecommendations(event.target.checked);
                    }}
                  />
                  Show only high-impact recommendations
                </label>
                {visibleRecommendations.length === 0 ? (
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No recommendations.</div>
                ) : (
                  <ol style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 8 }}>
                    {visibleRecommendations.map((recommendation) => {
                      const firstTarget = recommendation.targetEntities?.[0];
                      return (
                        <li key={recommendation.id} style={{ fontSize: 11, color: "#0f172a" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 600 }}>
                            <span>{recommendation.title}</span>
                            <span style={{ fontSize: 10, border: "1px solid #cbd5e1", borderRadius: 999, padding: "0 6px", color: "#334155" }}>
                              {recommendation.impactLevel}
                            </span>
                          </div>
                          <div>{recommendation.description}</div>
                          <details style={{ marginTop: 4 }}>
                            <summary style={{ cursor: "pointer", color: "#1d4ed8" }}>Details</summary>
                            <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                              {recommendation.suggestedActions.map((action) => (
                                <li key={`${recommendation.id}_${action}`}>{action}</li>
                              ))}
                            </ul>
                            {firstTarget ? (
                              <button
                                type="button"
                                onClick={() => {
                                  onFocusOutlineDiagnosticRef(firstTarget.kind, firstTarget.id);
                                }}
                                style={{ fontSize: 10, cursor: "pointer", marginTop: 4 }}
                              >
                                Focus first target
                              </button>
                            ) : null}
                          </details>
                        </li>
                      );
                    })}
                  </ol>
                )}
              </details>
            </div>
          ) : null}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 8 }}>
          <button type="button" onClick={onAlignLeft} disabled={!canAlign} style={{ cursor: canAlign ? "pointer" : "not-allowed" }}>
            Align Left
          </button>
          <button type="button" onClick={onAlignRight} disabled={!canAlign} style={{ cursor: canAlign ? "pointer" : "not-allowed" }}>
            Align Right
          </button>
          <button type="button" onClick={onAlignTop} disabled={!canAlign} style={{ cursor: canAlign ? "pointer" : "not-allowed" }}>
            Align Top
          </button>
          <button type="button" onClick={onAlignBottom} disabled={!canAlign} style={{ cursor: canAlign ? "pointer" : "not-allowed" }}>
            Align Bottom
          </button>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 8 }}>
          <button
            type="button"
            onClick={onDistributeHorizontally}
            disabled={!canDistribute}
            style={{ cursor: canDistribute ? "pointer" : "not-allowed" }}
          >
            Distribute Horizontally
          </button>
          <button
            type="button"
            onClick={onDistributeVertically}
            disabled={!canDistribute}
            style={{ cursor: canDistribute ? "pointer" : "not-allowed" }}
          >
            Distribute Vertically
          </button>
        </div>
        <button
          type="button"
          onClick={onCreateRepresentativeCard}
          disabled={selectedCardCount < 2}
          style={{ cursor: selectedCardCount >= 2 ? "pointer" : "not-allowed" }}
        >
          Create representative card
        </button>
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Connect</div>
        <label style={{ display: "block", fontSize: 12, color: "#334155", marginBottom: 4 }}>Edge type</label>
        <select
          value={connectEdgeType}
          onChange={(event) => {
            onConnectEdgeTypeChange(event.target.value === "negate" ? "negate" : "related");
          }}
          disabled={isPickingEdgeTarget}
          style={{ width: "100%", marginBottom: 8 }}
        >
          <option value="related">related</option>
          <option value="negate">negate</option>
        </select>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <button
            type="button"
            onClick={onStartConnect}
            disabled={!canStartConnect || isPickingEdgeTarget}
            style={{ cursor: !canStartConnect || isPickingEdgeTarget ? "not-allowed" : "pointer" }}
          >
            Connect
          </button>
          <button
            type="button"
            onClick={onCancelConnect}
            disabled={!isPickingEdgeTarget}
            style={{ cursor: isPickingEdgeTarget ? "pointer" : "not-allowed" }}
          >
            Cancel
          </button>
        </div>
        {isPickingEdgeTarget ? (
          <div style={{ marginTop: 8, fontSize: 12, color: "#334155" }}>Pick target card or island. (Esc to cancel)</div>
        ) : null}
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Reading Path</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", marginBottom: 8 }}>
          <input
            type="checkbox"
            checked={readingNavEnabled}
            onChange={(event) => {
              onReadingNavEnabledChange(event.target.checked);
            }}
          />
          Enable
        </label>
        <label style={{ display: "block", fontSize: 12, color: "#334155", marginBottom: 4 }}>Mode</label>
        <select
          value={readingMode}
          onChange={(event) => {
            onReadingModeChange(event.target.value === "islands+cards" ? "islands+cards" : "islands");
          }}
          disabled={!readingNavEnabled}
          style={{ width: "100%", marginBottom: 8 }}
        >
          <option value="islands">Islands only</option>
          <option value="islands+cards">Islands + cards</option>
        </select>
        <label
          title="Reviewed only filters islands by summary review status; cards are always included in islands+cards mode."
          style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", marginBottom: 8 }}
        >
          <input
            type="checkbox"
            checked={reviewedOnly}
            disabled={!readingNavEnabled}
            onChange={() => {
              onReadingReviewedOnlyToggle();
            }}
          />
          Reviewed only
        </label>
        <div style={{ display: "grid", gap: 6, marginBottom: 8 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeCardTexts}
              onChange={(event) => {
                onOutlineIncludeCardTextsChange(event.target.checked);
              }}
            />
            Include card texts
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeRelationSummaries}
              onChange={(event) => {
                onOutlineIncludeRelationSummariesChange(event.target.checked);
              }}
            />
            Include relation summaries
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineIncludeUnreviewed}
              disabled={safeMode}
              onChange={(event) => {
                onOutlineIncludeUnreviewedChange(event.target.checked);
              }}
            />
            Include unreviewed
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineAppendDiagnostics}
              onChange={(event) => {
                onOutlineAppendDiagnosticsChange(event.target.checked);
              }}
            />
            Append diagnostics
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={outlineAppendRecommendations}
              onChange={(event) => {
                onOutlineAppendRecommendationsChange(event.target.checked);
              }}
            />
            Append recommendations
          </label>
          <button type="button" onClick={onRunOutlineDiagnostics} disabled={isDiagnosticsRunning}>{isDiagnosticsRunning ? "Working..." : "Run diagnostics"}</button>{isDiagnosticsRunning ? <button type="button" onClick={onCancelDiagnostics}>Cancel</button> : null}{isDiagnosticsRunning && computeProgressMessage ? <div style={{ fontSize: 12 }}>{computeProgressMessage}</div> : null}
          <div style={{ fontSize: 11, color: "#b45309" }}>Unreviewed content is draft; do not treat as confirmed.</div>
          {safeMode ? <div style={{ fontSize: 11, color: "#b45309" }}>Safe mode: unreviewed drafts are excluded.</div> : null}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            <button type="button" onClick={onCopyReadingOutlineMd}>
              Copy outline (MD)
            </button>
            <button type="button" onClick={onDownloadReadingOutlineMd}>
              Download outline.md
            </button>
          </div>
          {outlineQualityReport ? (
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc", marginTop: 8 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a" }}>Quality report</div>
              <div style={{ fontSize: 11, color: "#334155", marginTop: 2 }}>
                Findings: {outlineDiagnosticsCounts.error} errors, {outlineDiagnosticsCounts.warn} warnings, {outlineDiagnosticsCounts.info} infos
                {outlineQualityReport.health !== undefined ? ` · Health ${outlineQualityReport.health}% (heuristic)` : ""}
              </div>
              <details style={{ marginTop: 6 }}>
                <summary style={{ fontSize: 12, cursor: "pointer", color: "#1d4ed8" }}>Show findings</summary>
                {outlineQualityReport.findings.length === 0 ? (
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No findings.</div>
                ) : (
                  <ul style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
                    {outlineQualityReport.findings.map((finding, index) => (
                      <li key={`${finding.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
                        <div style={{ fontWeight: 600 }}>[{finding.severity.toUpperCase()}] {finding.code} {finding.title}</div>
                        <div>{finding.detail}</div>
                        {finding.suggestedAction ? <div style={{ color: "#334155" }}>Action: {finding.suggestedAction}</div> : null}
                        {finding.entityRefs && finding.entityRefs.length > 0 ? (
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 4 }}>
                            {finding.entityRefs.map((ref) => (
                              <button
                                key={`${finding.code}_${ref.kind}_${ref.id}`}
                                type="button"
                                onClick={() => {
                                  onFocusOutlineDiagnosticRef(ref.kind, ref.id);
                                }}
                                style={{ fontSize: 10, cursor: "pointer" }}
                              >
                                Focus {ref.kind}:{ref.id}
                              </button>
                            ))}
                          </div>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                )}
              </details>
              {contradictionReport ? (
                <details style={{ marginTop: 8 }}>
                  <summary style={{ fontSize: 12, cursor: "pointer", color: "#b45309" }}>
                    Contradiction signals ({contradictionReport.stats.signals})
                  </summary>
                  {contradictionReport.signals.length === 0 ? (
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No contradiction signals.</div>
                  ) : (
                    <div style={{ marginTop: 6, display: "grid", gap: 8 }}>
                      {["warn", "info"].map((severity) => {
                        const signals = contradictionSignalsBySeverity[severity as "warn" | "info"];
                        if (signals.length === 0) {
                          return null;
                        }

                        return (
                          <div key={severity}>
                            <div style={{ fontSize: 11, fontWeight: 600, color: severity === "warn" ? "#b45309" : "#334155" }}>
                              {severity.toUpperCase()} ({signals.length})
                            </div>
                            <ul style={{ margin: "4px 0 0", paddingLeft: 18, display: "grid", gap: 6 }}>
                              {signals.map((signal, index) => (
                                <li key={`${signal.code}_${index}`} style={{ fontSize: 11, color: "#0f172a" }}>
                                  <div style={{ fontWeight: 600 }}>[{signal.code}] {signal.title}</div>
                                  <div>{signal.detail}</div>
                                  {signal.suggestedAction ? <div style={{ color: "#334155" }}>Action: {signal.suggestedAction}</div> : null}
                                  <button
                                    type="button"
                                    onClick={() => {
                                      onFocusContradictionSignal(signal);
                                    }}
                                    style={{ fontSize: 10, cursor: "pointer", marginTop: 4 }}
                                  >
                                    Focus
                                  </button>
                                </li>
                              ))}
                            </ul>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </details>
              ) : null}
              {distributionSignalsSection}
              {claimTypeMixSection}
              {evidenceGapSection}
              {dialecticBalanceSection}
              <details style={{ marginTop: 8 }}>
                <summary style={{ fontSize: 12, cursor: "pointer", color: "#1d4ed8" }}>Suggested next steps</summary>
                <label style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 6, fontSize: 11, color: "#334155" }}>
                  <input
                    type="checkbox"
                    checked={showOnlyHighImpactRecommendations}
                    onChange={(event) => {
                      setShowOnlyHighImpactRecommendations(event.target.checked);
                    }}
                  />
                  Show only high-impact recommendations
                </label>
                {visibleRecommendations.length === 0 ? (
                  <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>No recommendations.</div>
                ) : (
                  <ol style={{ margin: "6px 0 0", paddingLeft: 18, display: "grid", gap: 8 }}>
                    {visibleRecommendations.map((recommendation) => {
                      const firstTarget = recommendation.targetEntities?.[0];
                      return (
                        <li key={recommendation.id} style={{ fontSize: 11, color: "#0f172a" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 6, fontWeight: 600 }}>
                            <span>{recommendation.title}</span>
                            <span style={{ fontSize: 10, border: "1px solid #cbd5e1", borderRadius: 999, padding: "0 6px", color: "#334155" }}>
                              {recommendation.impactLevel}
                            </span>
                          </div>
                          <div>{recommendation.description}</div>
                          <details style={{ marginTop: 4 }}>
                            <summary style={{ cursor: "pointer", color: "#1d4ed8" }}>Details</summary>
                            <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                              {recommendation.suggestedActions.map((action) => (
                                <li key={`${recommendation.id}_${action}`}>{action}</li>
                              ))}
                            </ul>
                            {firstTarget ? (
                              <button
                                type="button"
                                onClick={() => {
                                  onFocusOutlineDiagnosticRef(firstTarget.kind, firstTarget.id);
                                }}
                                style={{ fontSize: 10, cursor: "pointer", marginTop: 4 }}
                              >
                                Focus first target
                              </button>
                            ) : null}
                          </details>
                        </li>
                      );
                    })}
                  </ol>
                )}
              </details>
            </div>
          ) : null}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 8 }}>
          <button
            type="button"
            onClick={onReadingPrev}
            disabled={!readingNavEnabled || readingTotal === 0 || readingStep <= 1}
            style={{ cursor: !readingNavEnabled || readingTotal === 0 || readingStep <= 1 ? "not-allowed" : "pointer" }}
          >
            Prev
          </button>
          <button
            type="button"
            onClick={onReadingNext}
            disabled={!readingNavEnabled || readingTotal === 0 || readingStep >= readingTotal}
            style={{ cursor: !readingNavEnabled || readingTotal === 0 || readingStep >= readingTotal ? "not-allowed" : "pointer" }}
          >
            Next
          </button>
        </div>
        <div style={{ fontSize: 12, color: "#334155", marginBottom: 4 }}>
          {readingTotal === 0 ? "No readable items" : `Step ${readingStep} / ${readingTotal}`}
        </div>
        <div style={{ fontSize: 12, color: "#64748b" }}>{currentReadingLabel ?? "(none)"}</div>
      </section>
      <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Reading Order</div>
        {canAddSelectedItemToReadingOrder ? (
          <button
            type="button"
            onClick={onAddSelectedItemToReadingOrder}
            style={{
              width: "100%",
              marginBottom: 8,
              border: "1px solid #cbd5e1",
              backgroundColor: "#ffffff",
              color: "#0f172a",
              borderRadius: 6,
              padding: "6px 10px",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            Add to Reading Order
          </button>
        ) : (
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>
            Select one island or one card to add to reading order.
          </div>
        )}
        {readingOrderItems.length === 0 ? (
          <div style={{ fontSize: 12, color: "#64748b" }}>No reading order entries yet.</div>
        ) : (
          <div style={{ display: "grid", gap: 6 }}>
            {readingOrderItems.map((item, index) => (
              <div
                key={`${item.id}_${index}`}
                style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 6, backgroundColor: "#f8fafc" }}
              >
                <div style={{ fontSize: 11, color: "#64748b" }}>{item.id}</div>
                <div style={{ fontSize: 12, color: "#0f172a", marginBottom: 4 }}>{item.label}</div>
                <div style={{ display: "flex", gap: 6 }}>
                  <button
                    type="button"
                    onClick={() => {
                      onMoveReadingOrderItem(index, -1);
                    }}
                    disabled={index === 0}
                    style={{ cursor: index === 0 ? "not-allowed" : "pointer" }}
                  >
                    Up
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      onMoveReadingOrderItem(index, 1);
                    }}
                    disabled={index === readingOrderItems.length - 1}
                    style={{ cursor: index === readingOrderItems.length - 1 ? "not-allowed" : "pointer" }}
                  >
                    Down
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      onRemoveReadingOrderItem(index);
                    }}
                    style={{ cursor: "pointer" }}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
      <section style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Island visibility</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
          <button type="button" onClick={onCollapseAllIslands} disabled={!hasIslands} style={{ width: "100%" }}>
            Collapse all
          </button>
          <button type="button" onClick={onExpandAllIslands} disabled={!isAnyIslandCollapsed} style={{ width: "100%" }}>
            Expand all
          </button>
        </div>
      </section>
      {selectedIsland ? (
        <>
          <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: "#0f172a" }}>Island Editor</div>

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            ID
          </label>
          <input
            type="text"
            readOnly
            value={selectedIsland.id}
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
              backgroundColor: "#f8fafc",
            }}
          />

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            Parent island ID
          </label>
          <input
            type="text"
            readOnly
            value={selectedIsland.parentIslandId ?? ""}
            placeholder="(none)"
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
              backgroundColor: "#f8fafc",
            }}
          />

          {summaryView || abstractMapView ? (
            <div style={{ display: "grid", gap: 8, marginBottom: 10 }}>
              <button type="button" onClick={onToggleSelectedIslandTemporaryReveal} style={{ width: "100%" }}>
                {isSelectedIslandTemporarilyRevealed ? "Hide member cards" : "Reveal member cards temporarily"}
              </button>
              <button type="button" onClick={onClearTemporaryReveal} style={{ width: "100%" }}>
                Clear reveals
              </button>
            </div>
          ) : null}

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12,
              color: "#334155",
              marginBottom: 10,
            }}
          >
            <input
              type="checkbox"
              checked={isSelectedIslandCollapsed}
              onChange={(event) => {
                onIslandCollapsedChange(event.target.checked);
              }}
            />
            Collapsed
          </label>

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            Title
          </label>
          <input
            type="text"
            value={selectedIsland.title ?? ""}
            onChange={(event) => {
              onTitleChange(event.target.value);
            }}
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
            }}
          />
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12,
              color: "#334155",
              marginBottom: 10,
            }}
          >
            <input
              type="checkbox"
              checked={selectedIsland.titleReviewed === true}
              onChange={(event) => {
                onTitleReviewedChange(event.target.checked);
              }}
            />
            Reviewed
          </label>

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            Summary
          </label>
          <button
            type="button"
            onClick={onSuggestIslandSummary}
            disabled={isSuggestingIslandSummary}
            style={{ width: "100%", marginBottom: 8, cursor: isSuggestingIslandSummary ? "not-allowed" : "pointer" }}
          >
            {isSuggestingIslandSummary ? "Suggesting summary..." : "Suggest summary (AI)"}
          </button>
          {selectedIsland.summaryReviewed !== true && typeof selectedIsland.summaryText === "string" && selectedIsland.summaryText.length > 0 ? (
            <div
              style={{
                fontSize: 12,
                color: "#7c2d12",
                backgroundColor: "#ffedd5",
                border: "1px solid #fdba74",
                borderRadius: 6,
                padding: "6px 8px",
                marginBottom: 8,
              }}
            >
              AI draft (unreviewed). Please verify against cards.
            </div>
          ) : null}
          {summaryGroundingItems.length > 0 ? (
            <div style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, marginBottom: 6 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#334155" }}>Grounding cards ({summaryGroundingItems.length})</div>
                <button type="button" onClick={onClearTemporaryReveal} style={{ fontSize: 11, padding: "2px 6px" }}>
                  Clear reveal
                </button>
              </div>
              <button type="button" onClick={onShowAllSummaryGrounding} style={{ width: "100%", marginBottom: 8 }}>
                Show all grounding on canvas
              </button>
              <ol style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
                {summaryGroundingItems.map((item) => (
                  <li key={item.id}>
                    <button
                      type="button"
                      onClick={() => {
                        onSummaryGroundingCardInspect(item.id);
                      }}
                      style={{
                        width: "100%",
                        textAlign: "left",
                        border: "1px solid #cbd5e1",
                        borderRadius: 6,
                        padding: "6px 8px",
                        backgroundColor: "#ffffff",
                        color: "#0f172a",
                        cursor: "pointer",
                        fontSize: 12,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        gap: 8,
                      }}
                    >
                      <span>{item.text.slice(0, 120)}</span>
                      <span
                        style={{
                          borderRadius: 999,
                          border: "1px solid #cbd5e1",
                          padding: "1px 7px",
                          fontSize: 11,
                          color: "#334155",
                          backgroundColor: "#f8fafc",
                          whiteSpace: "nowrap",
                          textTransform: "lowercase",
                        }}
                      >
                        {item.kind}
                      </span>
                    </button>
                  </li>
                ))}
              </ol>
              {groundingVisibilityMessage ? (
                <div style={{ fontSize: 12, color: "#92400e", marginTop: 8 }}>{groundingVisibilityMessage}</div>
              ) : null}
            </div>
          ) : null}
          {islandSummarySuggestionWarnings.length > 0 ? (
            <div style={{ fontSize: 12, color: "#92400e", marginBottom: 8 }}>
              Warnings: {islandSummarySuggestionWarnings.join(" | ")}
            </div>
          ) : null}
          <textarea
            value={summaryDraft}
            onChange={(event) => {
              setSummaryDraft(event.target.value);
            }}
            onBlur={() => {
              onSummaryTextChange(summaryDraft);
            }}
            placeholder="Optional summary for collapsed view"
            rows={3}
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
              resize: "vertical",
            }}
          />
          <details style={{ marginBottom: 10 }}>
            <summary style={{ fontSize: 12, fontWeight: 600, color: "#334155", cursor: "pointer" }}>
              Summary history ({summaryHistoryEntries.length})
            </summary>
            <div style={{ marginTop: 8, display: "grid", gap: 8 }}>
              {summaryHistoryEntries.length === 0 ? (
                <div style={{ fontSize: 12, color: "#64748b" }}>No summary history yet.</div>
              ) : (
                summaryHistoryEntries.map((entry) => {
                  const isExpanded = expandedSummaryHistoryEntryId === entry.id;
                  const preview = (entry.toText ?? "").slice(0, 80);

                  return (
                    <div key={entry.id} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8 }}>
                      <button
                        type="button"
                        onClick={() => {
                          setExpandedSummaryHistoryEntryId(isExpanded ? null : entry.id);
                        }}
                        style={{
                          width: "100%",
                          textAlign: "left",
                          border: "none",
                          background: "transparent",
                          padding: 0,
                          cursor: "pointer",
                          display: "grid",
                          gap: 4,
                        }}
                      >
                        <div style={{ fontSize: 11, color: "#64748b" }}>{formatSummaryHistoryTimestamp(entry.createdAt)}</div>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                          <span
                            style={{
                              borderRadius: 999,
                              border: "1px solid #cbd5e1",
                              padding: "1px 7px",
                              fontSize: 11,
                              color: "#334155",
                              backgroundColor: "#f8fafc",
                              textTransform: "lowercase",
                            }}
                          >
                            {entry.changeKind}
                          </span>
                          <span style={{ fontSize: 12, color: "#0f172a" }}>{preview || "(empty)"}</span>
                        </div>
                        <div style={{ fontSize: 11, color: "#475569" }}>
                          reviewed: {entry.toReviewed === null ? "(unchanged)" : entry.toReviewed ? "true" : "false"}
                        </div>
                      </button>
                      {isExpanded ? (
                        <div style={{ marginTop: 8, display: "grid", gap: 6 }}>
                          <div style={{ fontSize: 11, color: "#475569" }}>From</div>
                          <pre style={{ margin: 0, fontSize: 12, backgroundColor: "#f8fafc", borderRadius: 6, padding: 8, whiteSpace: "pre-wrap" }}>
                            {entry.fromText ?? "(empty)"}
                          </pre>
                          <div style={{ fontSize: 11, color: "#475569" }}>To</div>
                          <pre style={{ margin: 0, fontSize: 12, backgroundColor: "#f8fafc", borderRadius: 6, padding: 8, whiteSpace: "pre-wrap" }}>
                            {entry.toText ?? "(empty)"}
                          </pre>
                          {entry.groundingIds && entry.groundingIds.length > 0 ? (
                            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8 }}>
                              <div style={{ fontSize: 11, color: "#475569" }}>
                                Grounding snapshot: {entry.groundingIds.length}
                              </div>
                              <button
                                type="button"
                                onClick={() => {
                                  onShowSummaryHistoryGrounding(entry.groundingIds ?? []);
                                }}
                                style={{ fontSize: 11, padding: "2px 6px" }}
                              >
                                Show grounding
                              </button>
                            </div>
                          ) : null}
                          <button
                            type="button"
                            onClick={() => {
                              onRestoreSummaryHistoryEntry(entry.id);
                            }}
                            style={{ width: "100%" }}
                          >
                            Restore this version
                          </button>
                        </div>
                      ) : null}
                    </div>
                  );
                })
              )}
            </div>
          </details>

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12,
              color: "#334155",
              marginBottom: 10,
            }}
          >
            <input
              type="checkbox"
              checked={selectedIsland.summaryReviewed === true}
              onChange={(event) => {
                onSummaryReviewedChange(event.target.checked);
              }}
            />
            Reviewed
          </label>

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            Image URL
          </label>
          <input
            type="url"
            value={selectedIsland.imageUrl ?? ""}
            placeholder="https://example.com/image.jpg"
            onChange={(event) => {
              onImageUrlChange(event.target.value);
            }}
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
            }}
          />
          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              fontSize: 12,
              color: "#334155",
              marginBottom: 10,
            }}
          >
            <input
              type="checkbox"
              checked={selectedIsland.imageReviewed === true}
              onChange={(event) => {
                onImageReviewedChange(event.target.checked);
              }}
            />
            Reviewed
          </label>

          <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
            Critique note
          </label>
          <textarea
            value={selectedIsland.critique ?? ""}
            onChange={(event) => {
              onIslandCritiqueChange(event.target.value);
            }}
            placeholder="Optional feedback about this island"
            rows={4}
            style={{
              width: "100%",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 8px",
              boxSizing: "border-box",
              marginBottom: 10,
              resize: "vertical",
            }}
          />
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Critique tags</div>
          <div style={{ display: "grid", gap: 6, marginBottom: 10 }}>
            {CRITIQUE_TAGS.map((tag) => (
              <label key={tag} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                <input
                  type="checkbox"
                  checked={(selectedIsland.critiqueTags ?? []).includes(tag)}
                  onChange={() => {
                    onIslandCritiqueTagsChange(toggleCritiqueTag(selectedIsland.critiqueTags, tag));
                  }}
                />
                {tag}
              </label>
            ))}
          </div>

          <div
            style={{
              height: 96,
              borderRadius: 6,
              border: "1px solid #e2e8f0",
              overflow: "hidden",
              backgroundColor: "#f8fafc",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#94a3b8",
              fontSize: 12,
              marginBottom: 8,
            }}
          >
            {selectedIsland.imageUrl ? (
              hasImagePreviewError ? (
                <span style={{ color: "#b91c1c" }}>Unable to load image preview.</span>
              ) : (
                <img
                  src={selectedIsland.imageUrl}
                  alt="Island preview"
                  onError={() => {
                    setHasImagePreviewError(true);
                  }}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              )
            ) : (
              "No image"
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ fontSize: 12, color: "#64748b" }}>Selection: {selectedCardLabel}</div>
            <button
              type="button"
              onClick={onFocusIsland}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Focus this island
            </button>
            {selectedIsland.shapeStale === true ? (
              <div
                style={{
                  border: "1px solid #f59e0b",
                  backgroundColor: "#fffbeb",
                  color: "#92400e",
                  borderRadius: 6,
                  padding: "6px 10px",
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                Shape is stale
              </div>
            ) : null}
            {selectedIsland.shape?.kind === "polygon" ? (
              <div style={{ display: "grid", gap: 4 }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 13, color: "#0f172a" }}>
                  <input
                    type="checkbox"
                    checked={isPolygonVertexEditEnabled}
                    onChange={(event) => {
                      onPolygonVertexEditEnabledChange(event.target.checked);
                    }}
                  />
                  Edit island boundary
                </label>
                <div style={{ fontSize: 12, color: "#475569" }}>
                  Alt+Click edge: add vertex / Alt+Click vertex: remove
                </div>
              </div>
            ) : null}
            <button
              type="button"
              onClick={onGenerateIslandPolygon}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {selectedIsland.shape?.generatedFrom ? "Reset to generated polygon" : "Regenerate polygon"}
            </button>
            <button
              type="button"
              onClick={onAddSelectedCards}
              disabled={!hasCardSelection}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: hasCardSelection ? "pointer" : "not-allowed",
              }}
            >
              Add selected cards to island ({selectedCardCount})
            </button>
            <button
              type="button"
              onClick={handleRemoveSelectedCardsClick}
              disabled={!hasCardSelection}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: hasCardSelection ? "pointer" : "not-allowed",
              }}
            >
              Remove selected cards from island ({selectedCardCount})
            </button>
            <button
              type="button"
              onClick={handleDeleteIslandClick}
              style={{
                border: "1px solid #fecaca",
                backgroundColor: "#fff1f2",
                color: "#b91c1c",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Delete island
            </button>
          </div>
        </>
      ) : selectedAggregatedEdge ? (
        <>
          <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: "#0f172a" }}>Edge Inspector</div>
          <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>
            Endpoint: {selectedAggregatedEdge.fromLabel ?? selectedAggregatedEdge.fromId} ({selectedAggregatedEdge.fromKind}) → {selectedAggregatedEdge.toLabel ?? selectedAggregatedEdge.toId} ({selectedAggregatedEdge.toKind})
          </div>
          <div style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>Type: {selectedAggregatedEdge.type}</div>
          {selectedAggregatedEdge.isDerivedIslandEdge ? (
            <div style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>
              Count: {selectedAggregatedEdge.aggregateCount ?? selectedAggregatedEdge.sources.length}
            </div>
          ) : null}
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>
            Contributing source edges (
            {selectedAggregatedEdge.isDerivedIslandEdge
              ? selectedAggregatedEdge.contributingEdgeIds?.length ?? 0
              : selectedAggregatedEdge.sources.length}
            )
          </div>
          <div style={{ display: "grid", gap: 4, marginBottom: 8 }}>
            {(selectedAggregatedEdge.isDerivedIslandEdge
              ? (selectedAggregatedEdge.contributingEdgeIds ?? []).map((edgeId) => ({
                  sourceFromCardId: edgeId,
                  sourceToId: "",
                  sourceToKind: "card" as const,
                }))
              : selectedAggregatedEdge.sources
            )
              .slice(0, 20)
              .map((source, index) => (
                <div key={`${source.sourceFromCardId}-${source.sourceToId}-${index}`} style={{ fontSize: 12, color: "#334155" }}>
                  {selectedAggregatedEdge.isDerivedIslandEdge
                    ? source.sourceFromCardId
                    : `${source.sourceFromCardId} → ${source.sourceToId} (${source.sourceToKind})`}
                </div>
              ))}
            {(selectedAggregatedEdge.isDerivedIslandEdge
              ? (selectedAggregatedEdge.contributingEdgeIds?.length ?? 0)
              : selectedAggregatedEdge.sources.length) > 20 ? (
              <div style={{ fontSize: 12, color: "#64748b" }}>+more</div>
            ) : null}
          </div>
          {selectedAggregatedEdge.isDerivedIslandEdge && (selectedAggregatedEdge.contributingCardIds?.length ?? 0) > 0 ? (
            <div style={{ marginBottom: 8 }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Contributing cards</div>
              <div style={{ display: "grid", gap: 4 }}>
                {selectedAggregatedEdge.contributingCardIds?.map((cardId) => (
                  <button
                    key={cardId}
                    type="button"
                    onClick={() => {
                      onInspectSelectedEdgeCard(cardId);
                    }}
                    style={{ textAlign: "left", fontSize: 12 }}
                  >
                    {cardId}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          <button
            type="button"
            onClick={onRevealSelectedEdgeSources}
            style={{
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: "6px 10px",
              backgroundColor: "#ffffff",
              color: "#0f172a",
              cursor: "pointer",
              fontSize: 12,
              fontWeight: 600,
            }}
          >
            Reveal involved source cards
          </button>
          {selectedIslandRelationExplanation ? (
            <div style={{ marginTop: 12, borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
              <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Explanation template (draft)</div>
              <pre
                style={{
                  margin: 0,
                  fontSize: 12,
                  lineHeight: 1.5,
                  whiteSpace: "pre-wrap",
                  border: "1px solid #cbd5e1",
                  borderRadius: 6,
                  padding: 8,
                  backgroundColor: "#f8fafc",
                  color: "#0f172a",
                }}
              >
                {`${selectedIslandRelationExplanation.title}\n\n${selectedIslandRelationExplanation.body}\n\nGrounding edge IDs: ${selectedIslandRelationExplanation.groundingEdgeIds.join(", ") || "(none)"}\nGrounding card IDs: ${selectedIslandRelationExplanation.groundingCardIds.join(", ") || "(none)"}`}
              </pre>
              <button type="button" onClick={handleCopyExplanationClick} style={{ marginTop: 8, fontSize: 12 }}>
                Copy Markdown explanation
              </button>
              {copyExplanationFeedback === "copied" ? (
                <div style={{ fontSize: 12, color: "#166534", marginTop: 6 }}>Copied.</div>
              ) : null}
              {copyExplanationFeedback === "failed" ? (
                <div style={{ fontSize: 12, color: "#b91c1c", marginTop: 6 }}>Copy failed.</div>
              ) : null}
            </div>
          ) : null}
          <div style={{ marginTop: 12, borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
            <button type="button" onClick={onGenerateRelationSummary} disabled={isGeneratingRelationSummary}>
              {isGeneratingRelationSummary ? "Generating..." : "Generate AI relation summary"}
            </button>
            <div style={{ marginTop: 8, fontSize: 12, color: "#7f1d1d" }}>
              Draft (unreviewed). Verify against grounding cards.
            </div>
            {selectedRelationSummary ? (
              <>
                <textarea
                  value={hideUnreviewedRelationSummary ? "UNREVIEWED hidden" : relationSummaryDraft}
                  onChange={(event) => {
                    if (hideUnreviewedRelationSummary) {
                      return;
                    }
                    setRelationSummaryDraft(event.target.value);
                  }}
                  onBlur={() => {
                    if (!hideUnreviewedRelationSummary) {
                      onRelationSummaryCommit(relationSummaryDraft);
                    }
                  }}
                  maxLength={RELATION_SUMMARY_TEXT_MAX_LENGTH}
                  readOnly={hideUnreviewedRelationSummary}
                  style={{
                    width: "100%",
                    marginTop: 8,
                    minHeight: 110,
                    boxSizing: "border-box",
                    ...(hideUnreviewedRelationSummary ? { color: "#92400e", backgroundColor: "#fff7ed", borderColor: "#fdba74" } : {}),
                  }}
                />
                <div style={{ marginTop: 4, fontSize: 11, color: "#64748b" }}>
                  {hideUnreviewedRelationSummary ? "Safe mode: UNREVIEWED hidden" : `${relationSummaryDraft.length}/${RELATION_SUMMARY_TEXT_MAX_LENGTH}`}
                </div>
                <label style={{ marginTop: 6, display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                  <input
                    type="checkbox"
                    checked={selectedRelationSummary.reviewed}
                    onChange={(event) => {
                      onRelationSummaryReviewedChange(event.target.checked);
                    }}
                  />
                  Reviewed
                </label>
                {relationSummaryFeedback ? <div style={{ marginTop: 6, fontSize: 12, color: "#92400e" }}>{relationSummaryFeedback}</div> : null}
                {selectedRelationSummary.warnings && selectedRelationSummary.warnings.length > 0 ? (
                  <div style={{ marginTop: 8, border: "1px solid #fca5a5", backgroundColor: "#fef2f2", borderRadius: 6, padding: 8 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#991b1b", marginBottom: 6 }}>
                      ⚠️ Warnings ({selectedRelationSummary.warnings.length})
                    </div>
                    <ul style={{ margin: 0, paddingLeft: 18, fontSize: 12, color: "#7f1d1d" }}>
                      {selectedRelationSummary.warnings.map((warning, index) => (
                        <li key={`${warning}-${index}`}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                <div style={{ marginTop: 8, fontSize: 12, fontWeight: 600, color: "#334155" }}>Grounding cards</div>
                <div style={{ display: "grid", gap: 4, marginTop: 4 }}>
                  {selectedRelationSummary.groundingCardIds.map((cardId) => (
                    <button key={cardId} type="button" style={{ textAlign: "left", fontSize: 12 }} onClick={() => onRelationSummaryGroundingInspect(cardId)}>
                      {cardId}
                    </button>
                  ))}
                </div>
                <div style={{ marginTop: 8, fontSize: 12, fontWeight: 600, color: "#334155" }}>Grounding edges</div>
                <div style={{ marginTop: 4, fontSize: 12, color: "#334155" }}>
                  {selectedRelationSummary.groundingEdgeIds.join(", ") || "(none)"}
                </div>
                <details style={{ marginTop: 10 }}>
                  <summary style={{ fontSize: 12, fontWeight: 600, color: "#334155", cursor: "pointer" }}>
                    History ({relationSummaryHistoryEntries.length})
                  </summary>
                  <div style={{ marginTop: 8, display: "grid", gap: 8 }}>
                    {relationSummaryHistoryEntries.length === 0 ? (
                      <div style={{ fontSize: 12, color: "#64748b" }}>No relation summary history yet.</div>
                    ) : (
                      relationSummaryHistoryEntries.map((entry) => {
                        const isExpanded = expandedRelationSummaryHistoryEntryId === entry.id;
                        const preview = (entry.toText ?? "").slice(0, 80);

                        return (
                          <div key={entry.id} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8 }}>
                            <button
                              type="button"
                              onClick={() => {
                                setExpandedRelationSummaryHistoryEntryId(isExpanded ? null : entry.id);
                              }}
                              style={{
                                width: "100%",
                                textAlign: "left",
                                border: "none",
                                background: "transparent",
                                padding: 0,
                                cursor: "pointer",
                                display: "grid",
                                gap: 4,
                              }}
                            >
                              <div style={{ fontSize: 11, color: "#64748b" }}>{formatSummaryHistoryTimestamp(entry.createdAt)}</div>
                              <div style={{ display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                                <span
                                  style={{
                                    borderRadius: 999,
                                    border: "1px solid #cbd5e1",
                                    padding: "1px 7px",
                                    fontSize: 11,
                                    color: "#334155",
                                    backgroundColor: "#f8fafc",
                                    textTransform: "lowercase",
                                  }}
                                >
                                  {entry.changeKind}
                                </span>
                                <span style={{ fontSize: 12, color: "#0f172a" }}>{preview || "(empty)"}</span>
                              </div>
                            </button>
                            {isExpanded ? (
                              <div style={{ marginTop: 8, display: "grid", gap: 6 }}>
                                <div style={{ fontSize: 11, color: "#475569" }}>From</div>
                                <pre style={{ margin: 0, fontSize: 12, backgroundColor: "#f8fafc", borderRadius: 6, padding: 8, whiteSpace: "pre-wrap" }}>
                                  {entry.fromText ?? "(empty)"}
                                </pre>
                                <div style={{ fontSize: 11, color: "#475569" }}>To</div>
                                <pre style={{ margin: 0, fontSize: 12, backgroundColor: "#f8fafc", borderRadius: 6, padding: 8, whiteSpace: "pre-wrap" }}>
                                  {entry.toText ?? "(empty)"}
                                </pre>
                                <div style={{ fontSize: 11, color: "#475569" }}>
                                  reviewed: {entry.fromReviewed === null ? "-" : entry.fromReviewed ? "true" : "false"} → {entry.toReviewed === null ? "-" : entry.toReviewed ? "true" : "false"}
                                </div>
                                <div style={{ fontSize: 11, color: "#475569" }}>
                                  warnings snapshot: {(entry.warningsSnapshot ?? []).join(" | ") || "(none)"}
                                </div>
                                <div style={{ fontSize: 11, color: "#475569" }}>
                                  grounding cards snapshot: {(entry.groundingCardIdsSnapshot ?? []).join(", ") || "(none)"}
                                </div>
                                <div style={{ fontSize: 11, color: "#475569" }}>
                                  grounding edges snapshot: {(entry.groundingEdgeIdsSnapshot ?? []).join(", ") || "(none)"}
                                </div>
                                {entry.note ? <div style={{ fontSize: 11, color: "#475569" }}>note: {entry.note}</div> : null}
                                <button
                                  type="button"
                                  onClick={() => {
                                    if (!entry.toText || entry.toText.trim().length === 0) {
                                      setRelationSummaryFeedback("Cannot restore empty text versions.");
                                      return;
                                    }

                                    setRelationSummaryFeedback(null);
                                    onRestoreRelationSummaryHistoryEntry(entry.id);
                                  }}
                                  style={{ width: "100%" }}
                                >
                                  Restore this version
                                </button>
                              </div>
                            ) : null}
                          </div>
                        );
                      })
                    )}
                  </div>
                </details>
              </>
            ) : null}
          </div>

        </>
      ) : hasCardSelection ? (
        <>
          <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: "#0f172a" }}>Card Inspector</div>
          {!selectedCard ? (
            <div style={{ fontSize: 12, color: "#64748b", marginBottom: 12 }}>
              {selectedCardLabel}. Select a single card to edit critique notes.
            </div>
          ) : (
            <>
              <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>{selectedCardLabel}</div>
              <button
                type="button"
                onClick={onFocusCard}
                style={{ width: "100%", marginBottom: 10, fontWeight: 600 }}
              >
                Focus this card
              </button>
              {selectedCard.canonicalId ? (
                <>
                  <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                    canonicalId
                  </label>
                  <input
                    type="text"
                    readOnly
                    value={selectedCard.canonicalId}
                    style={{
                      width: "100%",
                      border: "1px solid #cbd5e1",
                      borderRadius: 6,
                      padding: "6px 8px",
                      boxSizing: "border-box",
                      marginBottom: 12,
                      backgroundColor: "#f8fafc",
                      color: "#334155",
                    }}
                  />
                </>
              ) : null}
              {!selectedCard.canonicalId && hasSourceCardsForSelectedCanonical ? (
                <div style={{ marginBottom: 12 }}>
                  <details>
                    <summary style={{ fontSize: 12, fontWeight: 600, color: "#334155", cursor: "pointer" }}>
                      Sources ({sourceCardsForSelectedCanonical.length})
                    </summary>
                    <div style={{ display: "grid", gap: 6, marginTop: 8 }}>
                      {sourceCardsForSelectedCanonical.map((sourceCard) => (
                        <button
                          key={sourceCard.id}
                          type="button"
                          onClick={() => {
                            onSourceCardInspect(sourceCard.id);
                          }}
                          style={{
                            textAlign: "left",
                            border: "1px solid #cbd5e1",
                            borderRadius: 6,
                            padding: "6px 8px",
                            backgroundColor: revealedSourceCardIds.has(sourceCard.id) ? "#eff6ff" : "#ffffff",
                            color: "#0f172a",
                            cursor: "pointer",
                            fontSize: 12,
                          }}
                        >
                          {sourceCard.text.slice(0, 80)}
                        </button>
                      ))}
                    </div>
                  </details>
                  <label
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 8,
                      fontSize: 12,
                      color: "#334155",
                      marginTop: 8,
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isShowingAllSources}
                      onChange={(event) => {
                        onShowAllSourcesChange(event.target.checked);
                      }}
                    />
                    Show all sources
                  </label>
                </div>
              ) : null}
              <div style={{ marginBottom: 10, display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 600, color: "#334155" }}>Claim type</span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: "2px 8px",
                    borderRadius: 999,
                    ...claimTypeBadgeColors[selectedCard.claimType ?? "unknown"],
                  }}
                >
                  {claimTypeLabels[selectedCard.claimType ?? "unknown"]}
                </span>
              </div>
              <select
                value={selectedCard.claimType ?? "unknown"}
                onChange={(event) => {
                  onCardClaimTypeChange(event.target.value as ClaimType);
                }}
                style={{
                  width: "100%",
                  border: "1px solid #cbd5e1",
                  borderRadius: 6,
                  padding: "6px 8px",
                  boxSizing: "border-box",
                  marginBottom: 12,
                  backgroundColor: "#ffffff",
                  color: "#0f172a",
                }}
              >
                <option value="fact">{claimTypeLabels.fact}</option>
                <option value="claim">{claimTypeLabels.claim}</option>
                <option value="hypothesis">{claimTypeLabels.hypothesis}</option>
                <option value="unknown">{claimTypeLabels.unknown}</option>
              </select>

              <div style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Evidence</div>
                <div style={{ fontSize: 11, color: "#475569", marginBottom: 4 }}>Outgoing</div>
                {outgoingEvidenceLinks.length === 0 ? <div style={{ fontSize: 11, color: "#94a3b8" }}>(none)</div> : (
                  <div style={{ display: "grid", gap: 4, marginBottom: 8 }}>
                    {outgoingEvidenceLinks.map((link) => {
                      const target = document?.cards.find((card) => card.id === link.toCardId);
                      return (
                        <div key={link.id} style={{ fontSize: 11, border: "1px solid #e2e8f0", borderRadius: 6, padding: 6 }}>
                          <div>{link.type} → {target ? target.text.slice(0, 60) : link.toCardId}</div>
                          <div style={{ display: "flex", gap: 6, marginTop: 4 }}>
                            <button type="button" style={{ fontSize: 10 }} onClick={() => { onFocusCardById(link.toCardId); }}>Focus</button>
                            <button type="button" style={{ fontSize: 10 }} onClick={() => { onRemoveEvidenceLink(link.id); }}>Remove</button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                <div style={{ fontSize: 11, color: "#475569", marginBottom: 4 }}>Incoming (read-only)</div>
                {incomingEvidenceLinks.length === 0 ? <div style={{ fontSize: 11, color: "#94a3b8" }}>(none)</div> : (
                  <div style={{ display: "grid", gap: 4 }}>
                    {incomingEvidenceLinks.map((link) => {
                      const source = document?.cards.find((card) => card.id === link.fromCardId);
                      return <div key={link.id} style={{ fontSize: 11 }}>{source ? source.text.slice(0, 60) : link.fromCardId} {link.type} this</div>;
                    })}
                  </div>
                )}
                <button type="button" style={{ marginTop: 8, width: "100%" }} onClick={() => {
                  setIsEvidenceModalOpen(true);
                  setPendingEvidenceType("supports");
                  setEvidenceTargetQuery("");
                  setPendingEvidenceTargetId("");
                }}>
                  Add evidence link…
                </button>
                {isEvidenceModalOpen ? (
                  <div style={{ marginTop: 8, border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6, backgroundColor: "#f8fafc" }}>
                    <select value={pendingEvidenceType} onChange={(event) => { setPendingEvidenceType(event.target.value as EvidenceLink["type"]); }}>
                      <option value="supports">supports</option>
                      <option value="contradicts">contradicts</option>
                    </select>
                    <input value={evidenceTargetQuery} onChange={(event) => { setEvidenceTargetQuery(event.target.value); }} placeholder="Search target card" />
                    <select value={pendingEvidenceTargetId} onChange={(event) => { setPendingEvidenceTargetId(event.target.value); }}>
                      <option value="">Select target</option>
                      {availableEvidenceTargets.map((card) => (
                        <option key={card.id} value={card.id}>{card.text.slice(0, 80)}</option>
                      ))}
                    </select>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button type="button" disabled={!pendingEvidenceTargetId} onClick={() => {
                        if (!pendingEvidenceTargetId) return;
                        onAddEvidenceLink({ toCardId: pendingEvidenceTargetId, type: pendingEvidenceType });
                        setIsEvidenceModalOpen(false);
                      }}>Confirm</button>
                      <button type="button" onClick={() => { setIsEvidenceModalOpen(false); }}>Cancel</button>
                    </div>
                  </div>
                ) : null}
              </div>

              <div style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Evidence trace</div>
                <div style={{ display: "grid", gap: 6 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#334155" }}>Evidence trace</div>
                  <button type="button" disabled={!selectedCard || isTraceRunning} onClick={() => { void handleCopyEvidenceTrace(); }}>
                    {isTraceRunning ? "Working..." : "Copy evidence trace (MD)"}
                  </button>
                  <button type="button" disabled={!selectedCard || isTraceRunning} onClick={handleDownloadEvidenceTrace}>
                    Download evidence_trace.md
                  </button>

                  <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginTop: 8 }}>Contradiction trace</div>
                  <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
                    Depth
                    <select
                      value={contradictionTraceDepthLimit}
                      onChange={(event) => {
                        setContradictionTraceDepthLimit(Number(event.target.value));
                      }}
                    >
                      {[1, 2, 3].map((depth) => (
                        <option key={depth} value={depth}>
                          {depth}
                        </option>
                      ))}
                    </select>
                  </label>
                  <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                    <input
                      type="checkbox"
                      checked={contradictionTraceIncludeSupports}
                      onChange={(event) => {
                        setContradictionTraceIncludeSupports(event.target.checked);
                      }}
                    />
                    Include fact supports
                  </label>
                  <button type="button" disabled={!selectedCard || isTraceRunning} onClick={() => { void handleCopyContradictionTrace(); }}>
                    {isTraceRunning ? "Working..." : "Copy contradiction trace (MD)"}
                  </button>
                  <button type="button" disabled={!selectedCard || isTraceRunning} onClick={handleDownloadContradictionTrace}>
                    Download contradiction_trace.md
                  </button>
                  {isTraceRunning ? <button type="button" onClick={() => traceAbortRef.current?.abort()}>Cancel trace</button> : null}
                  {traceProgressMessage ? <div style={{ fontSize: 11, color: "#334155" }}>{traceProgressMessage}</div> : null}
                  {selectedCardContradictionsCount === 0 ? (
                    <div style={{ fontSize: 11, color: "#94a3b8" }}>No contradiction links found.</div>
                  ) : null}
                </div>
              </div>

              <div style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, marginBottom: 12 }}>
                <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Evidence overlay</div>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>
                  Overlay: {evidenceOverlayEnabled ? "on" : "off"} / scope: {evidenceOverlayScope}
                </div>
                <button
                  type="button"
                  style={{ width: "100%" }}
                  onClick={() => {
                    onEnableEvidenceOverlaySelectionExplore();
                  }}
                >
                  Explore from this card
                </button>
              </div>

              <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 4 }}>
                Critique note
              </label>
              <textarea
                value={selectedCard.critique ?? ""}
                onChange={(event) => {
                  onCardCritiqueChange(event.target.value);
                }}
                placeholder="Optional feedback about this card"
                rows={4}
                style={{
                  width: "100%",
                  border: "1px solid #cbd5e1",
                  borderRadius: 6,
                  padding: "6px 8px",
                  boxSizing: "border-box",
                  marginBottom: 12,
                  resize: "vertical",
                }}
              />
              <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Critique tags</div>
              <div style={{ display: "grid", gap: 6, marginBottom: 12 }}>
                {CRITIQUE_TAGS.map((tag) => (
                  <label key={tag} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                    <input
                      type="checkbox"
                      checked={(selectedCard.critiqueTags ?? []).includes(tag)}
                      onChange={() => {
                        onCardCritiqueTagsChange(toggleCritiqueTag(selectedCard.critiqueTags, tag));
                      }}
                    />
                    {tag}
                  </label>
                ))}
              </div>
            </>
          )}
        </>
      ) : (
        <div style={{ fontSize: 12, color: "#64748b", lineHeight: 1.4 }}>
          Select an island to edit it, or select one or more cards to inspect card details.
        </div>
      )}
    </aside>
  );
}
