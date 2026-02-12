import { useEffect, useMemo, useState, type ReactNode } from "react";

import type { Card, Island } from "../domain/types";

type SidePanelProps = {
  selectedCard: Card | null;
  selectedIsland: Island | null;
  selectedCardCount: number;
  onCardCritiqueChange: (value: string) => void;
  onTitleChange: (value: string) => void;
  onImageUrlChange: (value: string) => void;
  onIslandCritiqueChange: (value: string) => void;
  onAddSelectedCards: () => void;
  onRemoveSelectedCards: () => void;
  onDeleteIsland: () => void;
  isGridSnapEnabled: boolean;
  onGridSnapToggle: (value: boolean) => void;
  onAlignLeft: () => void;
  onAlignRight: () => void;
  onAlignTop: () => void;
  onAlignBottom: () => void;
  onDistributeHorizontally: () => void;
  onDistributeVertically: () => void;
  topContent?: ReactNode;
};

export function SidePanel({
  selectedCard,
  selectedIsland,
  selectedCardCount,
  onCardCritiqueChange,
  onTitleChange,
  onImageUrlChange,
  onIslandCritiqueChange,
  onAddSelectedCards,
  onRemoveSelectedCards,
  onDeleteIsland,
  isGridSnapEnabled,
  onGridSnapToggle,
  onAlignLeft,
  onAlignRight,
  onAlignTop,
  onAlignBottom,
  onDistributeHorizontally,
  onDistributeVertically,
  topContent,
}: SidePanelProps) {
  const [hasImagePreviewError, setHasImagePreviewError] = useState(false);

  useEffect(() => {
    setHasImagePreviewError(false);
  }, [selectedIsland?.id, selectedIsland?.imageUrl]);

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
