import type { ReactNode } from "react";

import type { Island } from "../domain/types";

type SidePanelProps = {
  selectedIsland: Island | null;
  selectedCardCount: number;
  onTitleChange: (value: string) => void;
  onImageUrlChange: (value: string) => void;
  onAddSelectedCards: () => void;
  onRemoveSelectedCards: () => void;
  onDeleteIsland: () => void;
  topContent?: ReactNode;
};

export function SidePanel({
  selectedIsland,
  selectedCardCount,
  onTitleChange,
  onImageUrlChange,
  onAddSelectedCards,
  onRemoveSelectedCards,
  onDeleteIsland,
  topContent,
}: SidePanelProps) {
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
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 12, color: "#0f172a" }}>Island Editor</div>
      {!selectedIsland ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>Select an island from the canvas.</div>
      ) : (
        <>
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
              marginBottom: 12,
            }}
          >
            {selectedIsland.imageUrl ? (
              <img
                src={selectedIsland.imageUrl}
                alt="Island preview"
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            ) : (
              "No image"
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{ fontSize: 12, color: "#64748b" }}>Selected cards: {selectedCardCount}</div>
            <button
              type="button"
              onClick={onAddSelectedCards}
              disabled={selectedCardCount === 0}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: selectedCardCount === 0 ? "not-allowed" : "pointer",
              }}
            >
              Add selected cards to island
            </button>
            <button
              type="button"
              onClick={onRemoveSelectedCards}
              disabled={selectedCardCount === 0}
              style={{
                border: "1px solid #cbd5e1",
                backgroundColor: "#ffffff",
                color: "#0f172a",
                borderRadius: 6,
                padding: "6px 10px",
                fontWeight: 600,
                cursor: selectedCardCount === 0 ? "not-allowed" : "pointer",
              }}
            >
              Remove selected cards from island
            </button>
            <button
              type="button"
              onClick={onDeleteIsland}
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
      )}
    </aside>
  );
}
