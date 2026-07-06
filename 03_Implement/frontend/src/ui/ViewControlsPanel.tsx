import { useRef } from "react";
import type { CSSProperties, ChangeEvent } from "react";
import type { LODLevel, LODThresholds } from "../domain/view/lod";
import type { HierarchyLevel } from "../domain/view/hierarchy_level";
import type { PerspectiveMode } from "../domain/view/perspective";
import type { ViewPreset } from "../domain/view/presets";
import { t } from "../i18n/translate";

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
  hierarchyLevel: HierarchyLevel;
  onHierarchyLevelChange: (value: HierarchyLevel) => void;
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
  emptyCanvasHintCompleted: boolean;
  onResetEmptyCanvasHint: () => void;
  isCanvasLegendOpen: boolean;
  onToggleCanvasLegend: () => void;
  showProtectionMarks: boolean;
  onToggleProtectionMarks: () => void;
  lodEnabled: boolean;
  onLodEnabledChange: (value: boolean) => void;
  lodThresholds?: LODThresholds;
  onLodThresholdsChange?: (value: LODThresholds) => void;
  currentLodLevel?: LODLevel | null;
  lodShowLoneWolvesWhenFar: boolean;
  onLodShowLoneWolvesWhenFarChange: (value: boolean) => void;
  showLabelBounds: boolean;
  onShowLabelBoundsChange: (value: boolean) => void;
  evidenceOverlayEnabled: boolean;
  onEvidenceOverlayEnabledChange: (value: boolean) => void;
  evidenceOverlayMode: "supports" | "contradicts" | "both";
  onEvidenceOverlayModeChange: (value: "supports" | "contradicts" | "both") => void;
  evidenceOverlayDepth: number;
  onEvidenceOverlayDepthChange: (value: number) => void;
  evidenceOverlayScope: "all" | "selection";
  onEvidenceOverlayScopeChange: (value: "all" | "selection") => void;
  evidenceOverlayDimOthers: boolean;
  onEvidenceOverlayDimOthersChange: (value: boolean) => void;
  perspectiveMode: PerspectiveMode;
  onPerspectiveModeChange: (value: PerspectiveMode) => void;
  perspectiveStrictFilter: boolean;
  onPerspectiveStrictFilterChange: (value: boolean) => void;
  viewPresets: ViewPreset[];
  activePresetId: string | null;
  onSaveViewPreset: () => void;
  onApplyViewPreset: (presetId: string) => void;
  onRenameViewPreset: (presetId: string) => void;
  onDeleteViewPreset: (presetId: string) => void;
  perspectiveHint?: string | null;
};

const sectionStyle: CSSProperties = {
  display: "grid",
  gap: 8,
  paddingBottom: 10,
  marginBottom: 10,
  borderBottom: "1px solid #e2e8f0",
};

function lodLevelLabel(level: LODLevel): string {
  if (level === "close") return t("view_controls.lod.level_close");
  if (level === "mid") return t("view_controls.lod.level_mid");
  return t("view_controls.lod.level_far");
}

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
  hierarchyLevel,
  onHierarchyLevelChange,
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
  emptyCanvasHintCompleted,
  onResetEmptyCanvasHint,
  isCanvasLegendOpen,
  onToggleCanvasLegend,
  showProtectionMarks,
  onToggleProtectionMarks,
  lodEnabled,
  onLodEnabledChange,
  lodThresholds,
  onLodThresholdsChange,
  currentLodLevel,
  lodShowLoneWolvesWhenFar,
  onLodShowLoneWolvesWhenFarChange,
  showLabelBounds,
  onShowLabelBoundsChange,
  evidenceOverlayEnabled,
  onEvidenceOverlayEnabledChange,
  evidenceOverlayMode,
  onEvidenceOverlayModeChange,
  evidenceOverlayDepth,
  onEvidenceOverlayDepthChange,
  evidenceOverlayScope,
  onEvidenceOverlayScopeChange,
  evidenceOverlayDimOthers,
  onEvidenceOverlayDimOthersChange,
  perspectiveMode,
  onPerspectiveModeChange,
  perspectiveStrictFilter,
  onPerspectiveStrictFilterChange,
  viewPresets,
  activePresetId,
  onSaveViewPreset,
  onApplyViewPreset,
  onRenameViewPreset,
  onDeleteViewPreset,
  perspectiveHint,
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
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.viewpoint_presets.title")}</div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={onApplyBirdsEyePreset} style={{ cursor: "pointer" }}>
            {t("view_controls.viewpoint_presets.birds_eye")}
          </button>
          <button type="button" onClick={onApplyMidPreset} style={{ cursor: "pointer" }}>
            {t("view_controls.viewpoint_presets.mid")}
          </button>
          <button type="button" onClick={onApplyDetailPreset} style={{ cursor: "pointer" }}>
            {t("view_controls.viewpoint_presets.detail")}
          </button>
          <div style={{ display: "grid", gap: 4 }}>
            <div style={{ fontSize: 11, color: "#64748b" }}>{t("view_controls.viewpoint_presets.structure_level")}</div>
            <div style={{ display: "inline-flex", border: "1px solid #cbd5e1", borderRadius: 6, overflow: "hidden" }}>
              {([
                { id: "overview", label: t("view_controls.hierarchy.overview") },
                { id: "detail", label: t("view_controls.hierarchy.detail") },
              ] as const).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onHierarchyLevelChange(item.id);
                  }}
                  style={{
                    cursor: "pointer",
                    border: "none",
                    borderRight: item.id === "detail" ? "none" : "1px solid #cbd5e1",
                    padding: "4px 8px",
                    backgroundColor: hierarchyLevel === item.id ? "#e2e8f0" : "#ffffff",
                    color: hierarchyLevel === item.id ? "#0f172a" : "#334155",
                    fontWeight: hierarchyLevel === item.id ? 700 : 500,
                    fontSize: 12,
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>
          </div>
          <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "#334155" }}>
            {t("view_controls.viewpoint_presets.structure_level")}
            <select
              value={hierarchyLevel}
              onChange={(event) => {
                onHierarchyLevelChange(event.target.value as HierarchyLevel);
              }}
              style={{ fontSize: 12 }}
            >
              <option value="overview">{t("view_controls.hierarchy.overview")}</option>
              <option value="mid">{t("view_controls.hierarchy.mid")}</option>
              <option value="detail">{t("view_controls.hierarchy.detail")}</option>
            </select>
          </label>
          <div style={{ display: "grid", gap: 4, minWidth: 240 }}>
            <div style={{ display: "inline-flex", border: "1px solid #cbd5e1", borderRadius: 6, overflow: "hidden" }}>
              {([
                { id: "overview", label: t("view_controls.hierarchy.overview") },
                { id: "mid", label: t("view_controls.hierarchy.mid") },
                { id: "detail", label: t("view_controls.hierarchy.detail") },
              ] as const).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => {
                    onHierarchyLevelChange(item.id);
                  }}
                  style={{
                    cursor: "pointer",
                    border: "none",
                    borderRight: item.id === "detail" ? "none" : "1px solid #cbd5e1",
                    padding: "4px 8px",
                    backgroundColor: hierarchyLevel === item.id ? "#e2e8f0" : "#ffffff",
                    color: hierarchyLevel === item.id ? "#0f172a" : "#334155",
                    fontWeight: hierarchyLevel === item.id ? 700 : 500,
                    fontSize: 12,
                  }}
                >
                  {item.label}
                </button>
              ))}
            </div>
            <div style={{ fontSize: 11, color: "#64748b" }}>{t("view_controls.viewpoint_presets.shortcut")}</div>
          </div>
          {onResetView ? (
            <button type="button" onClick={onResetView} style={{ cursor: "pointer" }}>
              {t("view_controls.viewpoint_presets.reset")}
            </button>
          ) : null}
        </div>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.focus.title")}</div>
        <div style={{ fontSize: 12, color: "#475569" }}>{t("view_controls.focus.current", { id: focusIslandId ?? t("view_controls.focus.none") })}</div>
        <button type="button" onClick={onClearFocus} disabled={!focusIslandId} style={{ cursor: focusIslandId ? "pointer" : "not-allowed" }}>
          {t("view_controls.focus.clear")}
        </button>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.depth.title")}</div>
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
          <option value="all">{t("view_controls.depth.all")}</option>
          {Array.from({ length: maxAvailableDepth + 1 }, (_, depth) => (
            <option key={depth} value={depth}>
              {t("view_controls.depth.level", { depth })}
            </option>
          ))}
        </select>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.perspective.title")}</div>
        <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
          {t("view_controls.perspective.mode")}
          <select
            value={perspectiveMode}
            onChange={(event) => {
              onPerspectiveModeChange(event.target.value as PerspectiveMode);
            }}
          >
            <option value="default">{t("view_controls.perspective.default")}</option>
            <option value="facts">{t("view_controls.perspective.facts")}</option>
            <option value="claims">{t("view_controls.perspective.claims")}</option>
            <option value="hypotheses">{t("view_controls.perspective.hypotheses")}</option>
            <option value="unknown">{t("view_controls.perspective.unknown")}</option>
            <option value="evidence">{t("view_controls.perspective.evidence")}</option>
            <option value="contradiction">{t("view_controls.perspective.contradiction")}</option>
            <option value="review">{t("view_controls.perspective.review_view")}</option>
          </select>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={perspectiveStrictFilter}
            onChange={(event) => {
              onPerspectiveStrictFilterChange(event.target.checked);
            }}
          />
          {t("view_controls.perspective.strict_filter")}
        </label>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <button type="button" onClick={onSaveViewPreset} style={{ cursor: "pointer" }}>
            {t("view_controls.perspective.save_preset")}
          </button>
        </div>
        <div style={{ fontSize: 11, color: "#475569" }}>
          {t("view_controls.perspective.current_preset", { name: viewPresets.find((preset) => preset.id === activePresetId)?.name ?? t("view_controls.perspective.custom") })}
        </div>
        <div style={{ display: "grid", gap: 6 }}>
          {viewPresets.map((preset) => {
            const isCurrent = preset.id === activePresetId;
            return (
              <div
                key={preset.id}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 8,
                  padding: "6px 8px",
                  border: `1px solid ${isCurrent ? "#2563eb" : "#cbd5e1"}`,
                  borderRadius: 6,
                }}
              >
                <div style={{ fontSize: 12, fontWeight: isCurrent ? 700 : 500, color: "#0f172a" }}>
                  {preset.name} {isCurrent ? t("view_controls.perspective.current_suffix") : ""}
                </div>
                <div style={{ display: "flex", gap: 4 }}>
                  <button type="button" onClick={() => onApplyViewPreset(preset.id)}>{t("view_controls.perspective.apply")}</button>
                  <button type="button" onClick={() => onRenameViewPreset(preset.id)}>{t("view_controls.perspective.rename")}</button>
                  <button
                    type="button"
                    onClick={() => onDeleteViewPreset(preset.id)}
                    disabled={preset.id.startsWith("default-")}
                    title={preset.id.startsWith("default-") ? t("view_controls.perspective.default_cannot_delete") : undefined}
                  >
                    {t("view_controls.perspective.delete")}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
        {perspectiveHint ? <div style={{ fontSize: 11, color: "#475569" }}>{perspectiveHint}</div> : null}
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.evidence.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={evidenceOverlayEnabled}
            onChange={(event) => {
              onEvidenceOverlayEnabledChange(event.target.checked);
            }}
          />
          {t("view_controls.evidence.enable")}
        </label>
        <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
          {t("view_controls.evidence.mode")}
          <select
            value={evidenceOverlayMode}
            onChange={(event) => {
              onEvidenceOverlayModeChange(event.target.value as "supports" | "contradicts" | "both");
            }}
          >
            <option value="supports">{t("view_controls.evidence.supports")}</option>
            <option value="contradicts">{t("view_controls.evidence.contradicts")}</option>
            <option value="both">{t("view_controls.evidence.both")}</option>
          </select>
        </label>
        <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
          {t("view_controls.evidence.depth")}
          <select
            value={String(Math.max(1, Math.min(3, evidenceOverlayDepth)))}
            onChange={(event) => {
              onEvidenceOverlayDepthChange(Number(event.target.value));
            }}
          >
            <option value="1">{t("view_controls.evidence.hops", { count: 1 })}</option>
            <option value="2">{t("view_controls.evidence.hops", { count: 2 })}</option>
            <option value="3">{t("view_controls.evidence.hops", { count: 3 })}</option>
          </select>
        </label>
        <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
          {t("view_controls.evidence.scope")}
          <select
            value={evidenceOverlayScope}
            onChange={(event) => {
              onEvidenceOverlayScopeChange(event.target.value as "all" | "selection");
            }}
          >
            <option value="selection">{t("view_controls.evidence.selection")}</option>
            <option value="all">{t("view_controls.evidence.all")}</option>
          </select>
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={evidenceOverlayDimOthers}
            onChange={(event) => {
              onEvidenceOverlayDimOthersChange(event.target.checked);
            }}
          />
          {t("view_controls.evidence.dim_non_participating")}
        </label>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.canonical.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={hideSourceCards}
            onChange={(event) => {
              onHideSourceCardsChange(event.target.checked);
            }}
          />
          {t("view_controls.canonical.hide_source_cards")}
        </label>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={hideMergedOriginals}
            onChange={(event) => {
              onHideMergedOriginalsChange(event.target.checked);
            }}
          />
          {t("view_controls.canonical.hide_merged_originals")}
        </label>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.summary.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={summaryView || abstractMapView}
            disabled={abstractMapView}
            onChange={(event) => {
              onSummaryViewChange(event.target.checked);
            }}
          />
          {t("view_controls.summary.toggle")} {abstractMapView ? t("view_controls.summary.implied") : ""}
        </label>
        <div style={{ fontSize: 11, color: "#64748b" }}>
          {t("view_controls.summary.help")}
        </div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={abstractMapView}
            onChange={(event) => {
              onAbstractMapViewChange(event.target.checked);
            }}
          />
          {t("view_controls.summary.abstract_map")}
        </label>
        {abstractMapView ? (
          <>
            <div style={{ fontSize: 11, color: "#64748b" }}>
              {t("view_controls.summary.abstract_help")}
            </div>
            <div style={{ fontSize: 11, color: "#64748b" }}>{t("view_controls.summary.abstract_edges")}</div>
          </>
        ) : null}
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.reading_order.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={showReadingOrder}
            onChange={(event) => {
              onShowReadingOrderChange(event.target.checked);
            }}
          />
          {t("view_controls.reading_order.show")}
        </label>
        {onReadingOrderEditModeChange ? (
          <label title={t("view_controls.reading_order.edit_help")} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: showReadingOrder ? "#334155" : "#94a3b8" }}>
            <input
              type="checkbox"
              checked={isReadingOrderEditMode}
              disabled={!showReadingOrder}
              onChange={(event) => {
                onReadingOrderEditModeChange(event.target.checked);
              }}
            />
            {t("view_controls.reading_order.edit")}
          </label>
        ) : null}
      </div>

      <div style={{ fontSize: 12, color: "#64748b" }} title={t("view_controls.peek_help")}>
        {t("view_controls.peek_help")}
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.lod.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={lodEnabled}
            onChange={(event) => {
              onLodEnabledChange(event.target.checked);
            }}
          />
          {t("view_controls.lod.auto")}
        </label>
        <div style={{ fontSize: 12, color: "#475569" }}>
          {t("view_controls.lod.current", { value: lodEnabled ? currentLodLevel ? lodLevelLabel(currentLodLevel) : t("view_controls.lod.calculating") : t("view_controls.lod.off") })}
        </div>
        <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.4 }}>
          {t("view_controls.lod.legend")}
        </div>
        {lodEnabled && currentLodLevel === "far" ? (
          <div style={{ fontSize: 11, color: "#475569" }}>{t("view_controls.lod.far_hint")}</div>
        ) : null}
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={lodShowLoneWolvesWhenFar}
            onChange={(event) => {
              onLodShowLoneWolvesWhenFarChange(event.target.checked);
            }}
          />
          {t("view_controls.lod.keep_lone_wolves")}
        </label>
        {lodThresholds && onLodThresholdsChange ? (
          <>
            <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#475569" }}>
              {t("view_controls.lod.close_threshold", { value: lodThresholds.close.toFixed(2) })}
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
              {t("view_controls.lod.mid_threshold", { value: lodThresholds.mid.toFixed(2) })}
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
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.label_culling.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={showLabelBounds}
            onChange={(event) => {
              onShowLabelBoundsChange(event.target.checked);
            }}
          />
          {t("view_controls.label_culling.show_bounds")}
        </label>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.safety.title")}</div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          <input
            type="checkbox"
            checked={safeMode}
            onChange={(event) => {
              onSafeModeChange(event.target.checked);
            }}
          />
          {t("view_controls.safety.safe_mode")}
        </label>
      </div>

      <div style={sectionStyle}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.onboarding.title")}</div>
        <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.4 }}>
          {t(emptyCanvasHintCompleted ? "view_controls.onboarding.empty_canvas_completed" : "view_controls.onboarding.empty_canvas_available")}
        </div>
        <button
          type="button"
          onClick={onResetEmptyCanvasHint}
          disabled={!emptyCanvasHintCompleted}
          style={{ cursor: emptyCanvasHintCompleted ? "pointer" : "not-allowed" }}
        >
          {t("view_controls.onboarding.reset_empty_canvas")}
        </button>
        <button
          type="button"
          data-focus-return-id="legend-trigger"
          onClick={onToggleCanvasLegend}
          aria-pressed={isCanvasLegendOpen}
          style={{ cursor: "pointer" }}
        >
          {t(isCanvasLegendOpen ? "view_controls.legend.toggle_hide" : "view_controls.legend.toggle_show")}
        </button>
        <button
          type="button"
          onClick={onToggleProtectionMarks}
          aria-pressed={showProtectionMarks}
          style={{ cursor: "pointer" }}
        >
          {t(showProtectionMarks ? "view_controls.protection.toggle_hide" : "view_controls.protection.toggle_show")}
        </button>
      </div>

      <div style={{ ...sectionStyle, marginTop: 10, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("view_controls.export_legacy.title")}</div>
        <div style={{ fontSize: 11, color: "#64748b" }}>{t("view_controls.export_legacy.hint")}</div>
        <button type="button" onClick={onExportSvgViewport} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.svg_viewport")}
        </button>
        <button type="button" onClick={onExportSvgVisibleBounds} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.svg_visible")}
        </button>
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
          {t("view_controls.export_legacy.png_scale")}
          <select
            value={String(pngExportScale)}
            onChange={(event) => {
              onPngExportScaleChange(event.target.value === "2" ? 2 : 1);
            }}
          >
            <option value="1">{t("view_controls.export_legacy.png_scale_1x")}</option>
            <option value="2">{t("view_controls.export_legacy.png_scale_2x")}</option>
          </select>
        </label>
        <button type="button" onClick={onExportPngViewport} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.png_viewport")}
        </button>
        <button type="button" onClick={onExportPngVisibleBounds} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.png_visible")}
        </button>
        <button type="button" onClick={onExportAbstractMapMarkdownWithPng} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.abstract_map_md")}
        </button>
        <button type="button" onClick={onExportAbstractMapHtmlWithPng} style={{ cursor: "pointer" }}>
          {t("view_controls.export_legacy.abstract_map_html")}
        </button>
        <button
          type="button"
          onClick={() => {
            viewMetadataInputRef.current?.click();
          }}
          style={{ cursor: "pointer" }}
        >
          {t("view_controls.export_legacy.load_view_metadata")}
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
