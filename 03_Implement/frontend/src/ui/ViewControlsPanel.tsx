import type { CSSProperties } from "react";

type ViewControlsPanelProps = {
  focusIslandId?: string;
  onClearFocus: () => void;
  maxDepth: number | "all";
  maxAvailableDepth: number;
  onMaxDepthChange: (value: number | "all") => void;
  hideSourceCards: boolean;
  onHideSourceCardsChange: (value: boolean) => void;
  summaryView: boolean;
  onSummaryViewChange: (value: boolean) => void;
  abstractMapView: boolean;
  onAbstractMapViewChange: (value: boolean) => void;
  showReadingOrder: boolean;
  onShowReadingOrderChange: (value: boolean) => void;
  isReadingOrderEditMode: boolean;
  onReadingOrderEditModeChange?: (value: boolean) => void;
  onApplyBirdsEyePreset: () => void;
  onApplyMidPreset: () => void;
  onApplyDetailPreset: () => void;
  onResetView?: () => void;
  onExportAbstractMapMarkdown: () => void;
  onExportAbstractMapHtml: () => void;
};

const sectionStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  paddingBottom: 10,
  marginBottom: 10,
  borderBottom: "1px solid #e2e8f0",
};

export function ViewControlsPanel({
  focusIslandId,
  onClearFocus,
  maxDepth,
  maxAvailableDepth,
  onMaxDepthChange,
  hideSourceCards,
  onHideSourceCardsChange,
  summaryView,
  onSummaryViewChange,
  abstractMapView,
  onAbstractMapViewChange,
  showReadingOrder,
  onShowReadingOrderChange,
  isReadingOrderEditMode,
  onReadingOrderEditModeChange,
  onApplyBirdsEyePreset,
  onApplyMidPreset,
  onApplyDetailPreset,
  onResetView,
  onExportAbstractMapMarkdown,
  onExportAbstractMapHtml,
}: ViewControlsPanelProps) {
  return (
    <div
      style={{
        width: 300,
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        backgroundColor: "#ffffff",
        padding: 10,
        boxShadow: "0 12px 24px rgba(15, 23, 42, 0.18)",
      }}
    >
      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Viewpoint presets</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={onApplyBirdsEyePreset} style={{ cursor: "pointer" }}>
            Bird’s-eye
          </button>
          <button type="button" onClick={onApplyMidPreset} style={{ cursor: "pointer" }}>
            Mid
          </button>
          <button type="button" onClick={onApplyDetailPreset} style={{ cursor: "pointer" }}>
            Detail
          </button>
          {onResetView ? (
            <button type="button" onClick={onResetView} style={{ cursor: "pointer" }}>
              Reset view
            </button>
          ) : null}
        </div>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Focus</div>
        <div style={{ fontSize: 12, color: "#475569" }}>Current: {focusIslandId ?? "(none)"}</div>
        <button type="button" onClick={onClearFocus} disabled={!focusIslandId} style={{ cursor: focusIslandId ? "pointer" : "not-allowed" }}>
          Clear focus
        </button>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Depth</div>
        <select
          value={maxDepth === "all" ? "all" : String(maxDepth)}
          onChange={(event) => {
            if (event.target.value === "all") {
              onMaxDepthChange("all");
              return;
            }

            onMaxDepthChange(Number(event.target.value));
          }}
        >
          <option value="all">All</option>
          {Array.from({ length: maxAvailableDepth + 1 }, (_, depth) => (
            <option key={depth} value={depth}>
              Depth {depth}
            </option>
          ))}
        </select>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Canonical view</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={hideSourceCards}
            onChange={(event) => {
              onHideSourceCardsChange(event.target.checked);
            }}
          />
          Hide source cards
        </label>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Summary view</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={summaryView || abstractMapView}
            disabled={abstractMapView}
            onChange={(event) => {
              onSummaryViewChange(event.target.checked);
            }}
          />
          Summary view {abstractMapView ? "(implied by abstract map)" : ""}
        </label>
        <div style={{ fontSize: 11, color: "#64748b" }}>
          Shows island summaries and hides member cards. Use Peek/Focus to inspect details.
        </div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={abstractMapView}
            onChange={(event) => {
              onAbstractMapViewChange(event.target.checked);
            }}
          />
          Abstract map view
        </label>
        {abstractMapView ? (
          <>
            <div style={{ fontSize: 11, color: "#64748b" }}>
              Abstract view: shows island summaries. Cards are hidden by default. UNREVIEWED summaries are drafts.
            </div>
            <div style={{ fontSize: 11, color: "#64748b" }}>Dashed edges are derived from hidden source relations.</div>
          </>
        ) : null}
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Reading order overlay</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={showReadingOrder}
            onChange={(event) => {
              onShowReadingOrderChange(event.target.checked);
            }}
          />
          Show reading order
        </label>
        {onReadingOrderEditModeChange ? (
          <label title="Shift+Click card/island to add. Alt+Click badge to remove. Drag badges to reorder." style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: showReadingOrder ? "#334155" : "#94a3b8" }}>
            <input
              type="checkbox"
              checked={isReadingOrderEditMode}
              disabled={!showReadingOrder}
              onChange={(event) => {
                onReadingOrderEditModeChange(event.target.checked);
              }}
            />
            Edit reading order
          </label>
        ) : null}
      </div>

      <div style={{ fontSize: 12, color: "#64748b" }} title="Hold Peek on a collapsed island to reveal members.">
        Hold Peek on a collapsed island to reveal members.
      </div>

      <div style={{ ...sectionStyle, marginTop: 10, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Export</div>
        <button type="button" onClick={onExportAbstractMapMarkdown} style={{ cursor: "pointer" }}>
          Export Abstract Map (Markdown)
        </button>
        <button type="button" onClick={onExportAbstractMapHtml} style={{ cursor: "pointer" }}>
          Export Abstract Map (HTML)
        </button>
      </div>
    </div>
  );
}
