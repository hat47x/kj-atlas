import { useEffect, useMemo, useState, type ReactNode } from "react";

import { CRITIQUE_TAGS } from "../domain/types";
import type { AggregatedEdgeMeta } from "../canvas/CanvasShell";
import type { Card, CritiqueTag, Island } from "../domain/types";

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
  onCardCritiqueChange: (value: string) => void;
  onCardCritiqueTagsChange: (value: string[]) => void;
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
  onIslandCritiqueChange: (value: string) => void;
  onIslandCritiqueTagsChange: (value: string[]) => void;
  onAddSelectedCards: () => void;
  onRemoveSelectedCards: () => void;
  onDeleteIsland: () => void;
  onFocusIsland: () => void;
  summaryView: boolean;
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
  selectedAggregatedEdge: AggregatedEdgeMeta | null;
  onRevealSelectedEdgeSources: () => void;
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
  readingOrderItems: ReadingOrderItem[];
  canAddSelectedItemToReadingOrder: boolean;
  onAddSelectedItemToReadingOrder: () => void;
  onMoveReadingOrderItem: (index: number, direction: -1 | 1) => void;
  onRemoveReadingOrderItem: (index: number) => void;
  aggregatedEdgeInspectorItems: AggregatedEdgeInspectorItem[];
  onPromoteAggregatedEdge: (edgeId: string) => void;
  topContent?: ReactNode;
};

export function SidePanel({
  selectedCard,
  sourceCardsForSelectedCanonical,
  revealedSourceCardIds,
  selectedIsland,
  selectedCardCount,
  onCardCritiqueChange,
  onCardCritiqueTagsChange,
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
  onIslandCritiqueChange,
  onIslandCritiqueTagsChange,
  onAddSelectedCards,
  onRemoveSelectedCards,
  onDeleteIsland,
  onFocusIsland,
  summaryView,
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
  selectedAggregatedEdge,
  onRevealSelectedEdgeSources,
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
  readingOrderItems,
  canAddSelectedItemToReadingOrder,
  onAddSelectedItemToReadingOrder,
  onMoveReadingOrderItem,
  onRemoveReadingOrderItem,
  aggregatedEdgeInspectorItems,
  onPromoteAggregatedEdge,
  topContent,
}: SidePanelProps) {
  const [hasImagePreviewError, setHasImagePreviewError] = useState(false);
  const [summaryDraft, setSummaryDraft] = useState("");
  const [expandedSummaryHistoryEntryId, setExpandedSummaryHistoryEntryId] = useState<string | null>(null);

  const summaryHistoryEntries = useMemo(() => {
    const entries = selectedIsland?.summaryHistory ?? [];
    return [...entries].reverse();
  }, [selectedIsland?.summaryHistory]);

  const formatSummaryHistoryTimestamp = (createdAt: string) => {
    const parsedDate = new Date(createdAt);
    if (Number.isNaN(parsedDate.getTime())) {
      return createdAt;
    }

    return parsedDate.toLocaleString();
  };

  useEffect(() => {
    setHasImagePreviewError(false);
  }, [selectedIsland?.id, selectedIsland?.imageUrl]);

  useEffect(() => {
    setSummaryDraft(selectedIsland?.summaryText ?? "");
    setExpandedSummaryHistoryEntryId(null);
  }, [selectedIsland?.id, selectedIsland?.summaryText]);

  const hasCardSelection = selectedCardCount > 0;
  const canAlign = selectedCardCount >= 2;
  const canDistribute = selectedCardCount >= 3;
  const selectedCardLabel = useMemo(() => {
    if (selectedCardCount === 1) {
      return "1 card selected";
    }

    return `${selectedCardCount} cards selected`;
  }, [selectedCardCount]);

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

          {summaryView ? (
            <button
              type="button"
              onClick={onToggleSelectedIslandTemporaryReveal}
              style={{ marginBottom: 10, width: "100%" }}
            >
              {isSelectedIslandTemporarilyRevealed ? "Hide members" : "Show members (temporarily)"}
            </button>
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
              checked={selectedIsland.collapsed === true}
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
              Focus selected island
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
                  Edit polygon vertices
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
            Endpoint: {selectedAggregatedEdge.fromId} ({selectedAggregatedEdge.fromKind}) → {selectedAggregatedEdge.toId} ({selectedAggregatedEdge.toKind})
          </div>
          <div style={{ fontSize: 12, color: "#334155", marginBottom: 8 }}>Type: {selectedAggregatedEdge.type}</div>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>
            Contributing source edges ({selectedAggregatedEdge.sources.length})
          </div>
          <div style={{ display: "grid", gap: 4, marginBottom: 8 }}>
            {selectedAggregatedEdge.sources.slice(0, 20).map((source, index) => (
              <div key={`${source.sourceFromCardId}-${source.sourceToId}-${index}`} style={{ fontSize: 12, color: "#334155" }}>
                {source.sourceFromCardId} → {source.sourceToId} ({source.sourceToKind})
              </div>
            ))}
            {selectedAggregatedEdge.sources.length > 20 ? (
              <div style={{ fontSize: 12, color: "#64748b" }}>+more</div>
            ) : null}
          </div>
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
