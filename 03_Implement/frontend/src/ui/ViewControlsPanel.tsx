import { useRef } from "react";
import type { CSSProperties, ChangeEvent } from "react";
import type { LODLevel, LODThresholds } from "../domain/view/lod";

type ViewControlsPanelProps = {
  focusIslandId?: string;
  onClearFocus: () => void;
  maxDepth: number | "all";
  maxAvailableDepth: number;
  onMaxDepthChange: (value: number | "all") => void;
  hideSourceCards: boolean;
  onHideSourceCardsChange: (value: boolean) => void;
  hideMergedOriginals: boolean;
  onHideMergedOriginalsChange: (value: boolean) => void;
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
  onExportAbstractMapMarkdownWithPng: () => void;
  onExportAbstractMapHtmlWithPng: () => void;
  onExportSvgViewport: () => void;
  onExportSvgVisibleBounds: () => void;
  pngExportScale: 1 | 2;
  onPngExportScaleChange: (value: 1 | 2) => void;
  onExportPngViewport: () => void;
  onExportPngVisibleBounds: () => void;
  onLoadViewMetadataFile: (file: File) => void;
  safeMode: boolean;
  onSafeModeChange: (value: boolean) => void;
  lodEnabled: boolean;
  onLodEnabledChange: (value: boolean) => void;
  lodThresholds?: LODThresholds;
  onLodThresholdsChange?: (value: LODThresholds) => void;
  currentLodLevel?: LODLevel | null;
  lodShowLoneWolvesWhenFar: boolean;
  onLodShowLoneWolvesWhenFarChange: (value: boolean) => void;
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
  hideMergedOriginals,
  onHideMergedOriginalsChange,
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
  onExportAbstractMapMarkdownWithPng,
  onExportAbstractMapHtmlWithPng,
  onExportSvgViewport,
  onExportSvgVisibleBounds,
  pngExportScale,
  onPngExportScaleChange,
  onExportPngViewport,
  onExportPngVisibleBounds,
  onLoadViewMetadataFile,
  safeMode,
  onSafeModeChange,
  lodEnabled,
  onLodEnabledChange,
  lodThresholds,
  onLodThresholdsChange,
  currentLodLevel,
  lodShowLoneWolvesWhenFar,
  onLodShowLoneWolvesWhenFarChange,
}: ViewControlsPanelProps) {
  const viewMetadataInputRef = useRef<HTMLInputElement | null>(null);

  const handleViewMetadataFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadViewMetadataFile(selectedFile);
  };

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
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={hideMergedOriginals}
            onChange={(event) => {
              onHideMergedOriginalsChange(event.target.checked);
            }}
          />
          Hide merged originals
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

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Level of detail (LOD)</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={lodEnabled}
            onChange={(event) => {
              onLodEnabledChange(event.target.checked);
            }}
          />
          Auto detail by zoom (LOD)
        </label>
        <div style={{ fontSize: 12, color: "#475569" }}>
          Current detail: {lodEnabled ? currentLodLevel ? currentLodLevel.toUpperCase() : "(calculating...)" : "OFF"}
        </div>
        <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.4 }}>
          Close = full cards, Mid = compact cards, Far = islands and island relations.
        </div>
        {lodEnabled && currentLodLevel === "far" ? (
          <div style={{ fontSize: 11, color: "#475569" }}>LOD Far: islands are virtually collapsed</div>
        ) : null}
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={lodShowLoneWolvesWhenFar}
            onChange={(event) => {
              onLodShowLoneWolvesWhenFarChange(event.target.checked);
            }}
          />
          Keep lone wolves when far
        </label>
        {lodThresholds && onLodThresholdsChange ? (
          <>
            <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
              Close threshold ({lodThresholds.close.toFixed(2)})
              <input
                type="range"
                min={0.6}
                max={2}
                step={0.05}
                value={lodThresholds.close}
                onChange={(event) => {
                  const nextClose = Number(event.target.value);
                  onLodThresholdsChange({ close: Math.max(nextClose, lodThresholds.mid), mid: lodThresholds.mid });
                }}
              />
            </label>
            <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
              Mid threshold ({lodThresholds.mid.toFixed(2)})
              <input
                type="range"
                min={0.2}
                max={1.5}
                step={0.05}
                value={lodThresholds.mid}
                onChange={(event) => {
                  const nextMid = Number(event.target.value);
                  onLodThresholdsChange({ close: Math.max(lodThresholds.close, nextMid), mid: nextMid });
                }}
              />
            </label>
          </>
        ) : null}
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Safety</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={safeMode}
            onChange={(event) => {
              onSafeModeChange(event.target.checked);
            }}
          />
          Safe mode (hide UNREVIEWED drafts)
        </label>
      </div>

      <div style={{ ...sectionStyle, marginTop: 10, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>Export (legacy)</div>
        <div style={{ fontSize: 11, color: "#64748b" }}>Deprecated entry point. Use “Share &amp; Reproduce” for the canonical flow.</div>
        <button type="button" onClick={onExportSvgViewport} style={{ cursor: "pointer" }}>
          Export SVG (Viewport)
        </button>
        <button type="button" onClick={onExportSvgVisibleBounds} style={{ cursor: "pointer" }}>
          Export SVG (Visible bounds)
        </button>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          PNG scale
          <select
            value={String(pngExportScale)}
            onChange={(event) => {
              onPngExportScaleChange(event.target.value === "2" ? 2 : 1);
            }}
          >
            <option value="1">1x</option>
            <option value="2">2x</option>
          </select>
        </label>
        <button type="button" onClick={onExportPngViewport} style={{ cursor: "pointer" }}>
          Export PNG (Viewport)
        </button>
        <button type="button" onClick={onExportPngVisibleBounds} style={{ cursor: "pointer" }}>
          Export PNG (Visible bounds)
        </button>
        <button type="button" onClick={onExportAbstractMapMarkdownWithPng} style={{ cursor: "pointer" }}>
          Export Abstract Map Report (MD + PNG)
        </button>
        <button type="button" onClick={onExportAbstractMapHtmlWithPng} style={{ cursor: "pointer" }}>
          Export Abstract Map Report (HTML + PNG)
        </button>
        <button
          type="button"
          onClick={() => {
            viewMetadataInputRef.current?.click();
          }}
          style={{ cursor: "pointer" }}
        >
          Load view metadata (JSON)
        </button>
        <input
          ref={viewMetadataInputRef}
          type="file"
          accept="application/json,.json"
          onChange={handleViewMetadataFileChange}
          style={{ display: "none" }}
        />
      </div>
    </div>
  );
}
