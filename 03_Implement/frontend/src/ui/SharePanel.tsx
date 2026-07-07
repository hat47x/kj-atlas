import { useEffect, useId, useRef, useState } from "react";
import type { ChangeEvent, KeyboardEvent as ReactKeyboardEvent, ReactNode } from "react";
import type { PatchSummaryModel } from "../domain/patch/patch_summary";
import type { PatchApplyLogEntry } from "../domain/types";
import type { PatchLintIssue } from "../domain/patch/patch_lint";
import type { FixProposal } from "../domain/patch/patch_fix";
import type { TrustLabel } from "../domain/patch/patch_types";
import { ImportPanel } from "./ImportPanel";
import { getExportSafetyWarning, getSafeModeIndicator, getSafeModeLockedContextLabel } from "./safe_mode_status";
import { t } from "../i18n/translate";
import type { ExportGranularity } from "../export/bundle_export";
import { PUBLISH_VISIBILITY_VALUES, type PublishVisibility } from "../domain/policy/publish_visibility";

export type DomainExpressionShareSummary = {
  unreviewedCards: number;
  unreviewedIslands: number;
  holdCards: number;
  critiqueTargets: number;
  evidenceLinks: number;
  contradictionLinks: number;
  evidenceGapCards: number;
};

type SharePanelProps = {
  isOpen: boolean;
  onToggleOpen: () => void;
  isAdvancedUiEnabled?: boolean;
  hasDocument: boolean;
  isLoading: boolean;
  isReadOnly: boolean;
  onExportSvgViewport: () => void;
  onExportSvgVisibleBounds: () => void;
  pngExportScale: 1 | 2;
  onPngExportScaleChange: (value: 1 | 2) => void;
  onExportPngViewport: () => void;
  onExportPngVisibleBounds: () => void;
  onExportAbstractMapMarkdownWithPng: () => void;
  onExportAbstractMapHtmlWithPng: () => void;
  safeMode: boolean;
  viewVisibility: PublishVisibility;
  packVisibility: PublishVisibility;
  onViewVisibilityChange: (value: PublishVisibility) => void;
  onPackVisibilityChange: (value: PublishVisibility) => void;
  onSafeModeChange: (value: boolean) => void;
  includeUnreviewedDrafts: boolean;
  onIncludeUnreviewedDraftsChange: (value: boolean) => void;
  currentReviewerRef: string;
  currentReviewerRefSource: "local" | "sso" | "unknown";
  onCurrentReviewerRefChange: (value: string) => void;
  onResetCurrentReviewerRef: () => void;
  onExportViewViewport: () => void;
  onExportViewVisibleBounds: () => void;
  onExportBundleZip: (options: { includeOutline: boolean; includeDiagnostics: boolean; includeSelectedCardTraces: boolean; exportGranularity: ExportGranularity }) => void;
  isBundleExportRunning: boolean;
  onCancelBundleExport: () => void;
  computeProgressMessage: string | null;
  canIncludeTraces: boolean;
  domainExpressionSummary: DomainExpressionShareSummary;
  onLoadViewMetadataFile: (file: File) => void;
  onLoadDocumentFile: (file: File) => void;
  onImportReviewPackFile: (file: File) => void;
  onInvalidReviewPackFileType: () => void;
  packImportError: string | null;
  importedPackSummary: {
    fileName: string;
    cardCount: number;
    islandCount: number;
    perspectiveMode: string;
    visibility: string;
    warningCount: number;
  } | null;
  pendingImportedDocumentSummary: {
    fileName: string;
    cardCount: number;
    islandCount: number;
    edgeCount: number;
  } | null;
  importDocumentError: string | null;
  onReplaceCurrentDocument: () => void;
  onLoadPatchFile: (file: File) => void;
  onLoadPatchBaselineFile: (file: File) => void;
  onExportPatchFile: () => void;
  patchExportAuthor: string;
  patchExportAuthorNote: string;
  onPatchExportAuthorChange: (value: string) => void;
  onPatchExportAuthorNoteChange: (value: string) => void;
  patchTrustLabel: TrustLabel;
  onPatchTrustLabelChange: (value: TrustLabel) => void;
  patchFingerprintStatus: { status: string; expected?: string; actual?: string } | null;
  patchFileName: string | null;
  patchImportError: string | null;
  patchConflictWarning: string | null;
  patchSummary: PatchSummaryModel | null;
  onCopyPatchSummary: () => void;
  patchPreviewItems: {
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
    resolution?: "yours" | "theirs" | "skip";
  }[];
  onPatchItemCheckedChange: (opId: string, checked: boolean) => void;
  onConflictResolutionChange: (opId: string, resolution: "yours" | "theirs" | "skip") => void;
  onApplyPatch: () => void;
  canApplyPatch: boolean;
  hasPatchSelection: boolean;
  patchLintIssues: PatchLintIssue[];
  fixProposals: FixProposal[];
  selectedFixProposalIds: Set<string>;
  onFixProposalCheckedChange: (fixId: string, checked: boolean) => void;
  onApplySelectedFixes: () => void;
  onResetPatchToOriginal: () => void;
  patchBaselineFileName: string | null;
  patchApplyLogEntries: PatchApplyLogEntry[];
  onCopyPatchApplyLogEntry: (entryId: string) => void;
  structuralDiffSection: ReactNode;
};

const sectionStyle = {
  display: "grid",
  gridTemplateColumns: "minmax(0, 1fr)",
  gap: 8,
  paddingBottom: 10,
  marginBottom: 10,
  borderBottom: "1px solid #e2e8f0",
  boxSizing: "border-box",
  minWidth: 0,
  maxWidth: "100%",
} as const;

const borderedPanelStyle = {
  boxSizing: "border-box",
  gridTemplateColumns: "minmax(0, 1fr)",
  minWidth: 0,
  maxWidth: "100%",
} as const;

const wrapRowStyle = {
  minWidth: 0,
  maxWidth: "100%",
  flexWrap: "wrap",
} as const;

const textInputStyle = {
  width: "100%",
  minWidth: 0,
  boxSizing: "border-box",
} as const;

const actionButtonStyle = {
  boxSizing: "border-box",
  minWidth: 0,
  maxWidth: "100%",
  overflowWrap: "anywhere",
  whiteSpace: "normal",
} as const;

const purposeGridStyle = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: 6,
} as const;

const purposeButtonStyle = {
  ...actionButtonStyle,
  display: "grid",
  gap: 2,
  width: "100%",
  border: "1px solid #cbd5e1",
  borderRadius: 8,
  padding: 8,
  backgroundColor: "#f8fafc",
  color: "#0f172a",
  cursor: "pointer",
  textAlign: "left",
} as const;

const preflightPanelStyle = {
  display: "grid",
  gap: 6,
  border: "1px solid #cbd5e1",
  borderRadius: 8,
  padding: 8,
  backgroundColor: "#f8fafc",
  ...borderedPanelStyle,
} as const;

const preflightGridStyle = {
  display: "grid",
  gap: 5,
  margin: 0,
} as const;

const preflightRowStyle = {
  display: "grid",
  gridTemplateColumns: "minmax(90px, 0.45fr) minmax(0, 1fr)",
  gap: 6,
  alignItems: "start",
} as const;

const preflightTermStyle = {
  margin: 0,
  fontSize: 11,
  fontWeight: 700,
  color: "#334155",
} as const;

const preflightValueStyle = {
  margin: 0,
  fontSize: 11,
  color: "#0f172a",
  overflowWrap: "anywhere",
} as const;

function publishVisibilityLabel(value: PublishVisibility): string {
  switch (value) {
    case "Org":
      return t("share.panel.visibility.org");
    case "Public":
      return t("share.panel.visibility.public");
    case "Restricted":
      return t("share.panel.visibility.restricted");
    case "Unlisted":
    default:
      return t("share.panel.visibility.unlisted");
  }
}

function bundleGranularityLabel(value: ExportGranularity): string {
  return value === "detail"
    ? t("share.panel.export.bundle_granularity_detail")
    : t("share.panel.export.bundle_granularity_overview");
}

const purposeLinks = [
  {
    id: "share-panel-purpose-export",
    labelKey: "share.panel.purpose.export",
    hintKey: "share.panel.purpose.export_hint",
  },
  {
    id: "share-panel-purpose-import",
    labelKey: "share.panel.purpose.import",
    hintKey: "share.panel.purpose.import_hint",
  },
  {
    id: "share-panel-purpose-patch",
    labelKey: "share.panel.purpose.patch",
    hintKey: "share.panel.purpose.patch_hint",
  },
  {
    id: "share-panel-purpose-diff",
    labelKey: "share.panel.purpose.diff",
    hintKey: "share.panel.purpose.diff_hint",
  },
] as const;

const sharePanelLayoutCss = `
  .kj-atlas-share-panel,
  .kj-atlas-share-panel * {
    box-sizing: border-box;
    min-width: 0;
    max-width: 100%;
    white-space: normal;
  }

  .kj-atlas-share-panel button,
  .kj-atlas-share-panel input,
  .kj-atlas-share-panel select,
  .kj-atlas-share-panel textarea {
    max-width: 100%;
  }

  .kj-atlas-share-panel button,
  .kj-atlas-share-panel label,
  .kj-atlas-share-panel summary {
    overflow-wrap: anywhere;
  }

  .kj-atlas-share-panel button {
    white-space: normal;
  }
`;

export function SharePanel({
  isOpen,
  onToggleOpen,
  isAdvancedUiEnabled = false,
  hasDocument,
  isLoading,
  isReadOnly,
  onExportSvgViewport,
  onExportSvgVisibleBounds,
  pngExportScale,
  onPngExportScaleChange,
  onExportPngViewport,
  onExportPngVisibleBounds,
  onExportAbstractMapMarkdownWithPng,
  onExportAbstractMapHtmlWithPng,
  safeMode,
  viewVisibility,
  packVisibility,
  onViewVisibilityChange,
  onPackVisibilityChange,
  onSafeModeChange,
  includeUnreviewedDrafts,
  onIncludeUnreviewedDraftsChange,
  currentReviewerRef,
  currentReviewerRefSource,
  onCurrentReviewerRefChange,
  onResetCurrentReviewerRef,
  onExportViewViewport,
  onExportViewVisibleBounds,
  onExportBundleZip,
  isBundleExportRunning,
  onCancelBundleExport,
  computeProgressMessage,
  canIncludeTraces,
  domainExpressionSummary,
  onLoadViewMetadataFile,
  onLoadDocumentFile,
  onImportReviewPackFile,
  onInvalidReviewPackFileType,
  packImportError,
  importedPackSummary,
  pendingImportedDocumentSummary,
  importDocumentError,
  onReplaceCurrentDocument,
  onLoadPatchFile,
  onLoadPatchBaselineFile,
  onExportPatchFile,
  patchExportAuthor,
  patchExportAuthorNote,
  onPatchExportAuthorChange,
  onPatchExportAuthorNoteChange,
  patchTrustLabel,
  onPatchTrustLabelChange,
  patchFingerprintStatus,
  patchFileName,
  patchImportError,
  patchConflictWarning,
  patchSummary,
  onCopyPatchSummary,
  patchPreviewItems,
  onPatchItemCheckedChange,
  onConflictResolutionChange,
  onApplyPatch,
  canApplyPatch,
  hasPatchSelection,
  patchLintIssues,
  fixProposals,
  selectedFixProposalIds,
  onFixProposalCheckedChange,
  onApplySelectedFixes,
  onResetPatchToOriginal,
  patchBaselineFileName,
  patchApplyLogEntries,
  onCopyPatchApplyLogEntry,
  structuralDiffSection,
}: SharePanelProps) {
  const panelRef = useRef<HTMLElement | null>(null);
  const triggerButtonRef = useRef<HTMLButtonElement | null>(null);
  const viewMetadataInputRef = useRef<HTMLInputElement | null>(null);
  const importDocumentInputRef = useRef<HTMLInputElement | null>(null);
  const patchInputRef = useRef<HTMLInputElement | null>(null);
  const patchBaselineInputRef = useRef<HTMLInputElement | null>(null);

  const [bundleIncludeOutline, setBundleIncludeOutline] = useState(true);
  const [bundleIncludeDiagnostics, setBundleIncludeDiagnostics] = useState(true);
  const [bundleIncludeSelectedCardTraces, setBundleIncludeSelectedCardTraces] = useState(true);
  const [bundleExportGranularity, setBundleExportGranularity] = useState<ExportGranularity>("detail");
  const bundleGranularityFieldName = useId();
  const bundleTraceHintId = useId();


  const handleViewMetadataFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadViewMetadataFile(selectedFile);
  };

  const handleDocumentFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadDocumentFile(selectedFile);
  };

  const handlePatchFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadPatchFile(selectedFile);
  };

  const handlePatchBaselineFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    event.target.value = "";

    if (!selectedFile) {
      return;
    }

    onLoadPatchBaselineFile(selectedFile);
  };



  useEffect(() => {
    if (!isOpen) {
      return;
    }

    const frame = window.requestAnimationFrame(() => {
      panelRef.current?.focus();
    });

    return () => window.cancelAnimationFrame(frame);
  }, [isOpen]);

  const closePanelAndRestoreFocus = () => {
    onToggleOpen();
    window.requestAnimationFrame(() => {
      triggerButtonRef.current?.focus();
    });
  };

  const handlePurposeClick = (sectionId: string) => {
    const target = panelRef.current?.querySelector<HTMLElement>(`#${sectionId}`);
    target?.scrollIntoView({ block: "start", behavior: "smooth" });
    target?.focus({ preventScroll: true });
  };

  const handlePanelKeyDown = (event: ReactKeyboardEvent<HTMLElement>) => {
    if (event.key === "Escape") {
      event.preventDefault();
      closePanelAndRestoreFocus();
    }
  };

    const lintErrors = patchLintIssues.filter((item) => item.severity === "error");
  const lintWarnings = patchLintIssues.filter((item) => item.severity === "warn");
  const lintInfos = patchLintIssues.filter((item) => item.severity === "info");

  const sortedPatchApplyLogEntries = [...patchApplyLogEntries].sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  const safeModeIndicator = getSafeModeIndicator(safeMode);
  const safeModeWarning = getExportSafetyWarning(safeMode);
  const unreviewedDraftPolicy = safeMode
    ? t("share.panel.preflight.unreviewed.safe_mode")
    : includeUnreviewedDrafts
      ? t("share.panel.preflight.unreviewed.included")
      : t("share.panel.preflight.unreviewed.excluded");
  const canUseSelectedCardTraces = canIncludeTraces && bundleExportGranularity === "detail";
  const selectedCardTracesChecked = bundleIncludeSelectedCardTraces && canUseSelectedCardTraces;
  const selectedCardTraceHint = !canIncludeTraces
    ? t("share.panel.export.bundle_trace_hint")
    : bundleExportGranularity === "overview"
      ? t("share.panel.export.bundle_trace_hint_overview")
      : t("share.panel.export.bundle_trace_hint_available");
  const unreviewedTotal = domainExpressionSummary.unreviewedCards + domainExpressionSummary.unreviewedIslands;
  const unresolvedDomainSignals = domainExpressionSummary.holdCards + domainExpressionSummary.critiqueTargets + domainExpressionSummary.evidenceGapCards + domainExpressionSummary.contradictionLinks;
  const domainReadinessTone = unresolvedDomainSignals === 0 && unreviewedTotal === 0 ? "safe" : "warn";

  const shortFingerprint = (value: string | undefined): string => {
    if (!value) return t("share.panel.patch.not_available");
    if (value.length <= 20) return value;
    return `${value.slice(0, 10)}…${value.slice(-6)}`;
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        ref={triggerButtonRef}
        data-focus-return-id="share-panel-trigger"
        type="button"
        aria-haspopup="dialog"
        aria-expanded={isOpen}
        aria-controls="share-replay-panel"
        onClick={onToggleOpen}
        style={{
          border: "1px solid #cbd5e1",
          backgroundColor: "#ffffff",
          color: "#0f172a",
          borderRadius: 6,
          padding: "4px 10px",
          fontSize: 12,
          fontWeight: 700,
          cursor: "pointer",
        }}
      >
        {t("share.panel.trigger")}
      </button>
      {isOpen ? (
        <>
          <style>{sharePanelLayoutCss}</style>
          <section
            id="share-replay-panel"
            ref={panelRef}
            className="kj-atlas-share-panel"
            data-panel="share-replay"
            tabIndex={-1}
            role="dialog"
            aria-label={t("share.panel.trigger")}
            onKeyDown={handlePanelKeyDown}
            style={{
              position: "fixed",
              top: "var(--kj-atlas-header-panel-top, 72px)",
              left: 16,
              zIndex: 50,
              width: "min(340px, calc(100vw - 32px))",
              maxHeight: "calc(100vh - var(--kj-atlas-header-panel-top, 72px) - 16px)",
              boxSizing: "border-box",
              overflowX: "hidden",
              overflowY: "auto",
              border: "1px solid #cbd5e1",
              borderRadius: 8,
              backgroundColor: "#ffffff",
              padding: 10,
              boxShadow: "0 12px 24px rgba(15, 23, 42, 0.18)",
            }}
          >
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
            <button type="button" onClick={closePanelAndRestoreFocus} aria-label={t("share.panel.close")}>×</button>
          </div>
          <div style={{ ...sectionStyle, paddingBottom: 8 }}>
            <div style={{ fontSize: 14, fontWeight: 800, color: "#0f172a" }}>{t("share.panel.title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{t("share.panel.intent_hint")}</div>
          </div>
          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.purpose.section_title")}</div>
            <div style={purposeGridStyle}>
              {purposeLinks
                .filter(
                  (link) =>
                    isAdvancedUiEnabled ||
                    (link.id !== "share-panel-purpose-patch" && link.id !== "share-panel-purpose-diff")
                )
                .map((link) => (
                <button
                  key={link.id}
                  type="button"
                  aria-controls={link.id}
                  onClick={() => handlePurposeClick(link.id)}
                  style={purposeButtonStyle}
                >
                  <span style={{ fontSize: 12, fontWeight: 700 }}>{t(link.labelKey)}</span>
                  <span style={{ fontSize: 11, color: "#475569" }}>{t(link.hintKey)}</span>
                </button>
              ))}
            </div>
          </div>
          <div id="share-panel-purpose-import" tabIndex={-1} style={sectionStyle}>
            <ImportPanel
              isLoading={isLoading}
              onImportZip={onImportReviewPackFile}
              onInvalidFileType={onInvalidReviewPackFileType}
              packImportError={packImportError}
              importedPackSummary={importedPackSummary}
            />
          </div>

          <div id="share-panel-purpose-export" tabIndex={-1} style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.export.section_title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              {t("share.panel.export.section_hint")}
            </div>
            <div
              style={{
                border: safeModeIndicator.tone === "safe" ? "1px solid #86efac" : "1px solid #fdba74",
                backgroundColor: safeModeIndicator.tone === "safe" ? "#f0fdf4" : "#fff7ed",
                borderRadius: 8,
                padding: 8,
                ...borderedPanelStyle,
                display: "grid",
                gap: 6,
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 8, ...wrapRowStyle }}>
                <strong style={{ fontSize: 12, color: "#0f172a" }}>{safeModeIndicator.label}</strong>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                  <input
                    type="checkbox"
                    checked={safeMode}
                    onChange={(event) => {
                      onSafeModeChange(event.target.checked);
                    }}
                  />
                  {t("share.panel.export.enable_safe_mode")}
                </label>
              </div>
              <div style={{ fontSize: 11, color: "#475569" }}>{safeModeIndicator.detail}</div>
              <div style={{ fontSize: 11, color: safeModeIndicator.tone === "safe" ? "#166534" : "#9a3412", fontWeight: 600 }}>
                {safeModeWarning}
              </div>
              <div style={{ fontSize: 11, color: "#64748b" }}>{getSafeModeLockedContextLabel()}</div>
            </div>
            {isAdvancedUiEnabled ? (
            <div style={{ display: "grid", gap: 4, border: "1px solid #e2e8f0", borderRadius: 8, padding: 8, ...borderedPanelStyle }}>
              <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
                <span style={{ fontWeight: 600, color: "#0f172a" }}>
                  {t("share.panel.reviewer.current", { source: currentReviewerRefSource === "sso" ? "SSO" : currentReviewerRefSource })}
                </span>
                <input
                  type="text"
                  value={currentReviewerRef}
                  onChange={(event) => {
                    onCurrentReviewerRefChange(event.target.value);
                  }}
                  placeholder={currentReviewerRefSource === "sso" ? "user:sso:<provider>:<subject>" : "user:local:..."}
                  readOnly={currentReviewerRefSource === "sso"}
                  style={textInputStyle}
                />
              </label>
              <button type="button" onClick={onResetCurrentReviewerRef} disabled={currentReviewerRefSource === "sso"} style={actionButtonStyle}>
                {t("share.panel.reviewer.generate")}
              </button>
              <div style={{ fontSize: 11, color: "#64748b" }}>{t("share.panel.reviewer.sso_readonly_hint")}</div>
              <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
                <span style={{ fontWeight: 600, color: "#0f172a" }}>{t("share.panel.visibility.view")}</span>
                <select
                  value={viewVisibility}
                  onChange={(event) => {
                    if (PUBLISH_VISIBILITY_VALUES.includes(event.target.value as PublishVisibility)) {
                      onViewVisibilityChange(event.target.value as PublishVisibility);
                    }
                  }}
                  style={textInputStyle}
                >
                  {PUBLISH_VISIBILITY_VALUES.map((value) => (
                    <option key={value} value={value}>{publishVisibilityLabel(value)}</option>
                  ))}
                </select>
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
                <span style={{ fontWeight: 600, color: "#0f172a" }}>{t("share.panel.visibility.pack")}</span>
                <select
                  value={packVisibility}
                  onChange={(event) => {
                    if (PUBLISH_VISIBILITY_VALUES.includes(event.target.value as PublishVisibility)) {
                      onPackVisibilityChange(event.target.value as PublishVisibility);
                    }
                  }}
                  style={textInputStyle}
                >
                  {PUBLISH_VISIBILITY_VALUES.map((value) => (
                    <option key={`pack-${value}`} value={value}>{publishVisibilityLabel(value)}</option>
                  ))}
                </select>
              </label>
              <div style={{ fontSize: 11, color: "#64748b" }}>{t("share.panel.visibility.view_fallback")}</div>
              <div style={{ fontSize: 11, color: "#64748b" }}>{t("share.panel.visibility.pack_fallback")}</div>
            </div>
            ) : null}
            <div style={preflightPanelStyle}>
              <div style={{ fontSize: 12, fontWeight: 800, color: "#0f172a" }}>{t("share.panel.preflight.title")}</div>
              <div style={{ fontSize: 11, color: "#475569" }}>{t("share.panel.preflight.hint")}</div>
              <div style={{ fontSize: 11, color: viewVisibility === packVisibility ? "#475569" : "#9a3412", fontWeight: viewVisibility === packVisibility ? 400 : 700 }}>
                {t("share.panel.preflight.visibility_scope_hint")}
              </div>
              <dl style={preflightGridStyle}>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.safe_mode")}</dt>
                  <dd style={preflightValueStyle}>{safeModeIndicator.label}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.view_visibility")}</dt>
                  <dd style={preflightValueStyle}>{publishVisibilityLabel(viewVisibility)}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.pack_visibility")}</dt>
                  <dd style={preflightValueStyle}>{publishVisibilityLabel(packVisibility)}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.unreviewed")}</dt>
                  <dd style={preflightValueStyle}>{unreviewedDraftPolicy}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.output_formats")}</dt>
                  <dd style={preflightValueStyle}>{t("share.panel.preflight.output_formats_value")}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.bundle_granularity")}</dt>
                  <dd style={preflightValueStyle}>{bundleGranularityLabel(bundleExportGranularity)}</dd>
                </div>
                <div style={preflightRowStyle}>
                  <dt style={preflightTermStyle}>{t("share.panel.preflight.domain_readiness")}</dt>
                  <dd style={{ ...preflightValueStyle, color: domainReadinessTone === "safe" ? "#166534" : "#9a3412", fontWeight: 700 }}>
                    {domainReadinessTone === "safe"
                      ? t("share.panel.preflight.domain_readiness_clear")
                      : t("share.panel.preflight.domain_readiness_attention", { count: unresolvedDomainSignals + unreviewedTotal })}
                  </dd>
                </div>
              </dl>
              <div
                data-testid="share-domain-expression-summary"
                style={{
                  display: "grid",
                  gap: 4,
                  border: "1px solid #e2e8f0",
                  borderRadius: 6,
                  padding: 6,
                  backgroundColor: "#ffffff",
                  fontSize: 11,
                  color: "#334155",
                }}
              >
                <div style={{ fontWeight: 800, color: "#0f172a" }}>{t("share.panel.preflight.domain_summary_title")}</div>
                <div>{t("share.panel.preflight.domain_summary_review", { cards: domainExpressionSummary.unreviewedCards, islands: domainExpressionSummary.unreviewedIslands })}</div>
                <div>{t("share.panel.preflight.domain_summary_hold", { count: domainExpressionSummary.holdCards })}</div>
                <div>{t("share.panel.preflight.domain_summary_critique", { count: domainExpressionSummary.critiqueTargets })}</div>
                <div>{t("share.panel.preflight.domain_summary_evidence", { links: domainExpressionSummary.evidenceLinks, contradictions: domainExpressionSummary.contradictionLinks, gaps: domainExpressionSummary.evidenceGapCards })}</div>
                <div style={{ color: "#64748b" }}>{t("share.panel.preflight.domain_summary_hint")}</div>
              </div>
            </div>
            <button type="button" onClick={onExportSvgViewport} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.svg_viewport")}
            </button>
            <button type="button" onClick={onExportSvgVisibleBounds} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.svg_visible")}
            </button>
            <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
              {t("share.panel.export.png_scale")}
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
            <button type="button" onClick={onExportPngViewport} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.png_viewport")}
            </button>
            <button type="button" onClick={onExportPngVisibleBounds} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.png_visible")}
            </button>
            <button type="button" onClick={onExportAbstractMapMarkdownWithPng} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.abstract_md")}
            </button>
            <button type="button" onClick={onExportAbstractMapHtmlWithPng} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.abstract_html")}
            </button>
            {!safeMode ? (
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                <input
                  type="checkbox"
                  checked={includeUnreviewedDrafts}
                  onChange={(event) => {
                    onIncludeUnreviewedDraftsChange(event.target.checked);
                  }}
                />
                {t("share.panel.export.include_drafts")}
              </label>
            ) : null}
            <button type="button" onClick={onExportViewViewport} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.view_viewport")}
            </button>
            <button type="button" onClick={onExportViewVisibleBounds} disabled={!hasDocument || isLoading} style={actionButtonStyle}>
              {t("share.panel.export.view_visible")}
            </button>
            <div style={{ borderTop: "1px dashed #e2e8f0", paddingTop: 8, marginTop: 4, display: "grid", gap: 6, ...borderedPanelStyle }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.export.bundle_title")}</div>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                <input
                  type="checkbox"
                  checked={bundleIncludeOutline}
                  onChange={(event) => {
                    setBundleIncludeOutline(event.target.checked);
                  }}
                />
                {t("share.panel.export.bundle_include_outline")}
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                <input
                  type="checkbox"
                  checked={bundleIncludeDiagnostics}
                  onChange={(event) => {
                    setBundleIncludeDiagnostics(event.target.checked);
                  }}
                />
                {t("share.panel.export.bundle_include_diagnostics")}
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: canUseSelectedCardTraces ? "#334155" : "#94a3b8", ...wrapRowStyle }}>
                <input
                  type="checkbox"
                  checked={selectedCardTracesChecked}
                  disabled={!canUseSelectedCardTraces}
                  onChange={(event) => {
                    setBundleIncludeSelectedCardTraces(event.target.checked);
                  }}
                />
                {t("share.panel.export.bundle_include_traces")}
              </label>
              <fieldset
                aria-describedby={bundleTraceHintId}
                style={{ display: "grid", gap: 6, border: 0, padding: 0, margin: 0 }}
              >
                <legend style={{ fontSize: 12, fontWeight: 600, color: "#334155", padding: 0 }}>
                  {t("share.panel.export.bundle_granularity")}
                </legend>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                  <input
                    type="radio"
                    name={bundleGranularityFieldName}
                    value="detail"
                    checked={bundleExportGranularity === "detail"}
                    onChange={() => setBundleExportGranularity("detail")}
                  />
                  {t("share.panel.export.bundle_granularity_detail")}
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155", ...wrapRowStyle }}>
                  <input
                    type="radio"
                    name={bundleGranularityFieldName}
                    value="overview"
                    checked={bundleExportGranularity === "overview"}
                    onChange={() => setBundleExportGranularity("overview")}
                  />
                  {t("share.panel.export.bundle_granularity_overview")}
                </label>
              </fieldset>
              <div id={bundleTraceHintId} style={{ fontSize: 11, color: "#64748b" }}>{selectedCardTraceHint}</div>
              <button
                type="button"
                onClick={() => {
                  onExportBundleZip({
                    includeOutline: bundleIncludeOutline,
                    includeDiagnostics: bundleIncludeDiagnostics,
                    includeSelectedCardTraces: selectedCardTracesChecked,
                    exportGranularity: bundleExportGranularity,
                  });
                }}
                disabled={!hasDocument || isLoading || isBundleExportRunning}
                style={actionButtonStyle}
              >
                {isBundleExportRunning ? t("share.panel.export.bundle_working") : t("share.panel.export.bundle_export")}
              </button>
              {isBundleExportRunning ? <button type="button" onClick={onCancelBundleExport} style={actionButtonStyle}>{t("share.panel.export.bundle_cancel")}</button> : null}
              {isBundleExportRunning && computeProgressMessage ? <div style={{ fontSize: 12 }}>{computeProgressMessage}</div> : null}
            </div>
          </div>

          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.restore.section_title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{t("share.panel.restore.section_hint")}</div>
            <button
              type="button"
              onClick={() => {
                viewMetadataInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              {t("share.panel.restore.import_view")}
            </button>
            <input
              ref={viewMetadataInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handleViewMetadataFileChange}
              style={{ display: "none" }}
            />
          </div>

          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.load_document.section_title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              {t(isReadOnly ? "share.panel.load_document.section_hint_read_only" : "share.panel.load_document.section_hint")}
            </div>
            <button
              type="button"
              onClick={() => {
                importDocumentInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              {t("share.panel.load_document.load")}
            </button>
            <input
              ref={importDocumentInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handleDocumentFileChange}
              style={{ display: "none" }}
            />
            {importDocumentError ? (
              <div style={{ fontSize: 12, color: "#b91c1c", whiteSpace: "pre-wrap" }}>{importDocumentError}</div>
            ) : null}
            {pendingImportedDocumentSummary ? (
              <div
                style={{
                  border: "1px solid #cbd5e1",
                  borderRadius: 6,
                  padding: 8,
                  backgroundColor: "#f8fafc",
                  display: "grid",
                  gap: 6,
                }}
              >
                <div style={{ fontSize: 12, color: "#0f172a", fontWeight: 600 }}>{pendingImportedDocumentSummary.fileName}</div>
                <div style={{ fontSize: 12, color: "#334155" }}>
                  {t("share.panel.load_document.summary", { cardCount: pendingImportedDocumentSummary.cardCount, islandCount: pendingImportedDocumentSummary.islandCount, edgeCount: pendingImportedDocumentSummary.edgeCount })}
                </div>
                <button type="button" onClick={onReplaceCurrentDocument} disabled={isLoading}>
                  {t(isReadOnly ? "share.panel.load_document.open_read_only" : "share.panel.load_document.replace")}
                </button>
              </div>
            ) : null}
          </div>

          {isAdvancedUiEnabled ? (
          <>
          <div id="share-panel-purpose-patch" tabIndex={-1} style={{ ...sectionStyle, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.patch.section_title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              {t("share.panel.patch.section_hint")}
            </div>
            <button
              type="button"
              onClick={() => {
                patchInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              {t("share.panel.patch.load_patch")}
            </button>
            <input ref={patchInputRef} type="file" accept="application/json,.json" onChange={handlePatchFileChange} style={{ display: "none" }} />
            <button
              type="button"
              onClick={() => {
                patchBaselineInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              {t("share.panel.patch.load_baseline")}
            </button>
            <input
              ref={patchBaselineInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handlePatchBaselineFileChange}
              style={{ display: "none" }}
            />
            {patchFileName ? <div style={{ fontSize: 12, color: "#334155" }}>{t("share.panel.patch.file", { fileName: patchFileName })}</div> : null}
            {patchBaselineFileName ? <div style={{ fontSize: 12, color: "#334155" }}>{t("share.panel.patch.baseline", { fileName: patchBaselineFileName })}</div> : null}
            <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
              {t("share.panel.patch.trust_label")}
              <select
                value={patchTrustLabel}
                onChange={(event) => {
                  onPatchTrustLabelChange(event.target.value as TrustLabel);
                }}
                style={{ fontSize: 12 }}
              >
                <option value="unknown">{t("share.panel.patch.trust.unknown")}</option>
                <option value="trusted">{t("share.panel.patch.trust.trusted")}</option>
                <option value="untrusted">{t("share.panel.patch.trust.untrusted")}</option>
              </select>
            </label>
            {patchFingerprintStatus ? (
              <div style={{ fontSize: 12, color: "#334155", display: "grid", gap: 2 }}>
                <strong>{t("share.panel.patch.integrity", { status: patchFingerprintStatus.status })}</strong>
                <span>{t("share.panel.patch.expected", { value: shortFingerprint(patchFingerprintStatus.expected) })}</span>
                <span>{t("share.panel.patch.actual", { value: shortFingerprint(patchFingerprintStatus.actual) })}</span>
              </div>
            ) : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.patch.export.title")}</div>
              <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#334155" }}>
                {t("share.panel.patch.export.author")}
                <input value={patchExportAuthor} onChange={(event) => { onPatchExportAuthorChange(event.target.value); }} />
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#334155" }}>
                {t("share.panel.patch.export.author_note")}
                <input value={patchExportAuthorNote} onChange={(event) => { onPatchExportAuthorNoteChange(event.target.value); }} />
              </label>
              <button type="button" onClick={onExportPatchFile} disabled={isLoading || !patchFileName}>{t("share.panel.patch.export.download")}</button>
            </div>
            {patchImportError ? <div style={{ fontSize: 12, color: "#b91c1c", whiteSpace: "pre-wrap" }}>{patchImportError}</div> : null}
            {patchConflictWarning ? <div style={{ fontSize: 12, color: "#b45309", whiteSpace: "pre-wrap" }}>{patchConflictWarning}</div> : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.patch.lint.title")}</div>
              <div style={{ fontSize: 11, color: "#334155" }}>{t("share.panel.patch.lint.summary", { errors: lintErrors.length, warnings: lintWarnings.length, info: lintInfos.length })}</div>
              <details>
                <summary style={{ cursor: "pointer", fontSize: 11, color: "#b91c1c" }}>{t("share.panel.patch.lint.errors", { count: lintErrors.length })}</summary>
                <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#7f1d1d", display: "grid", gap: 2 }}>
                  {lintErrors.length === 0 ? <li>{t("share.panel.patch.none")}</li> : lintErrors.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                </ul>
              </details>
              <details>
                <summary style={{ cursor: "pointer", fontSize: 11, color: "#b45309" }}>{t("share.panel.patch.lint.warnings", { count: lintWarnings.length })}</summary>
                <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#92400e", display: "grid", gap: 2 }}>
                  {lintWarnings.length === 0 ? <li>{t("share.panel.patch.none")}</li> : lintWarnings.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                </ul>
              </details>
              {lintInfos.length > 0 ? (
                <details>
                  <summary style={{ cursor: "pointer", fontSize: 11, color: "#475569" }}>{t("share.panel.patch.lint.info", { count: lintInfos.length })}</summary>
                  <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#475569", display: "grid", gap: 2 }}>
                    {lintInfos.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                  </ul>
                </details>
              ) : null}
              {lintErrors.length > 0 ? <div style={{ fontSize: 11, color: "#b91c1c" }}>{t("share.panel.patch.resolve_lint_first")}</div> : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.patch.fix_suggestions", { count: fixProposals.length })}</div>
              {fixProposals.length === 0 ? (
                <div style={{ fontSize: 11, color: "#64748b" }}>{t("share.panel.patch.fix_none")}</div>
              ) : (
                <div style={{ display: "grid", gap: 6 }}>
                  {fixProposals.map((proposal) => (
                    <label key={proposal.fixId} style={{ display: "grid", gap: 2, fontSize: 11, color: "#334155", border: "1px solid #e2e8f0", borderRadius: 6, padding: 6 }}>
                      <span style={{ display: "flex", gap: 6, alignItems: "center" }}>
                        <input
                          type="checkbox"
                          checked={selectedFixProposalIds.has(proposal.fixId)}
                          onChange={(event) => {
                            onFixProposalCheckedChange(proposal.fixId, event.target.checked);
                          }}
                        />
                        <strong>{proposal.title}</strong>
                      </span>
                      <span>{proposal.description}</span>
                      <span style={{ color: "#64748b" }}>{t("share.panel.patch.fix_affected_ops", { count: proposal.affectedOpIds.length })}</span>
                    </label>
                  ))}
                </div>
              )}
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" onClick={onApplySelectedFixes} disabled={isLoading || selectedFixProposalIds.size === 0}>
                  {t("share.panel.patch.fix_apply_selected")}
                </button>
                <button type="button" onClick={onResetPatchToOriginal} disabled={isLoading || !patchFileName}>
                  {t("share.panel.patch.fix_reset")}
                </button>
              </div>
            </div>
            </div>
            {patchSummary ? (
              <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc", display: "grid", gap: 6 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{patchSummary.headline}</div>
                <div style={{ fontSize: 11, color: "#334155" }}>{t("share.panel.patch.summary.trust_label")} <strong>{patchTrustLabel}</strong></div>
                <div style={{ fontSize: 11, color: "#334155", display: "grid", gap: 2 }}>
                  <div>
                    cards +{patchSummary.stats.upsertCards} / -{patchSummary.stats.deleteCards}, islands +{patchSummary.stats.upsertIslands} / -
                    {patchSummary.stats.deleteIslands}
                  </div>
                  <div>
                    edges +{patchSummary.stats.upsertEdges} / -{patchSummary.stats.deleteEdges}, relations +
                    {patchSummary.stats.upsertRelationSummaries} / -{patchSummary.stats.deleteRelationSummaries}
                  </div>
                </div>
                {patchSummary.highlights.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: "#334155", display: "grid", gap: 2 }}>
                    {patchSummary.highlights.map((item, index) => (
                      <li key={`${item.label}-${index}`}>
                        <strong>{item.label}:</strong> {item.detail}
                      </li>
                    ))}
                  </ul>
                ) : null}
                {patchSummary.warnings.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: 18, fontSize: 11, color: "#b45309", display: "grid", gap: 2 }}>
                    {patchSummary.warnings.map((warning, index) => (
                      <li key={`${warning}-${index}`}>{warning}</li>
                    ))}
                  </ul>
                ) : null}
                <button type="button" onClick={onCopyPatchSummary} disabled={isLoading}>
                  {t("share.panel.patch.summary.copy")}
                </button>
              </div>
            ) : null}
            {patchPreviewItems.length > 0 ? (
              <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 8 }}>
                {patchPreviewItems.map((item) => (
                  <div id={`patch-op-${item.opId}`} key={item.opId} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#0f172a" }}>
                      <label style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <input
                          type="checkbox"
                          checked={item.checked}
                          disabled={!item.canToggle}
                          onChange={(event) => {
                            onPatchItemCheckedChange(item.opId, event.target.checked);
                          }}
                        />
                        {item.kind} · {item.entityKey}
                      </label>
                      {item.conflict ? (
                        <span style={{ fontSize: 10, fontWeight: 700, color: "#b91c1c", border: "1px solid #fecaca", borderRadius: 9999, padding: "1px 6px" }}>
                          {t("share.panel.patch.conflict_badge")}
                        </span>
                      ) : null}
                      {item.lintIssueCount > 0 ? (
                        <span
                          style={{
                            fontSize: 10,
                            fontWeight: 700,
                            color: item.lintErrorCount > 0 ? "#b91c1c" : "#92400e",
                            border: `1px solid ${item.lintErrorCount > 0 ? "#fecaca" : "#fcd34d"}`,
                            borderRadius: 9999,
                            padding: "1px 6px",
                          }}
                        >
                          {t("share.panel.patch.lint_badge", { count: item.lintIssueCount })}
                        </span>
                      ) : null}
                    </div>
                    {item.lintIssueCount > 0 ? (
                      <div style={{ fontSize: 11, color: item.lintErrorCount > 0 ? "#b91c1c" : "#b45309" }}>{t("share.panel.patch.lint.codes", { codes: item.lintIssueCodes.join(", ") })}</div>
                    ) : null}
                    {item.conflict ? (
                      <>
                        <div style={{ fontSize: 11, color: "#b45309" }}>{t("share.panel.patch.conflict.choose_resolution", { reason: item.reason ?? "" })}</div>
                        <div style={{ fontSize: 11, color: "#475569", whiteSpace: "pre-wrap" }}>
                          {t("share.panel.patch.conflict.base", { value: item.baseSnippet ?? t("share.panel.patch.none") })}
                          {"\n"}
                          {t("share.panel.patch.conflict.yours", { value: item.yourSnippet ?? t("share.panel.patch.none") })}
                          {"\n"}
                          {t("share.panel.patch.conflict.theirs", { value: item.theirSnippet ?? t("share.panel.patch.none") })}
                        </div>
                        <label style={{ display: "flex", gap: 6, fontSize: 12, color: "#334155" }}>
                          <input
                            type="radio"
                            name={`resolution-${item.opId}`}
                            checked={item.resolution === "yours"}
                            onChange={() => {
                              onConflictResolutionChange(item.opId, "yours");
                            }}
                          />
                          {t("share.panel.patch.conflict.use_yours")}
                        </label>
                        <label style={{ display: "flex", gap: 6, fontSize: 12, color: "#334155" }}>
                          <input
                            type="radio"
                            name={`resolution-${item.opId}`}
                            checked={item.resolution === "theirs"}
                            onChange={() => {
                              onConflictResolutionChange(item.opId, "theirs");
                            }}
                          />
                          {t("share.panel.patch.conflict.use_theirs")}
                        </label>
                        <label style={{ display: "flex", gap: 6, fontSize: 12, color: "#334155" }}>
                          <input
                            type="radio"
                            name={`resolution-${item.opId}`}
                            checked={item.resolution === "skip"}
                            onChange={() => {
                              onConflictResolutionChange(item.opId, "skip");
                            }}
                          />
                          {t("share.panel.patch.conflict.skip")}
                        </label>
                      </>
                    ) : null}
                  </div>
                ))}
                <button type="button" onClick={onApplyPatch} disabled={!canApplyPatch || isLoading}>
                  {lintErrors.length > 0 ? t("share.panel.patch.resolve_lint_first") : hasPatchSelection ? t("share.panel.patch.apply") : t("share.panel.patch.select_operations")}
                </button>
              </div>
            ) : null}
          </div>



          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.patch.apply_log.title", { count: patchApplyLogEntries.length })}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{t("share.panel.patch.apply_log.hint")}</div>
            {sortedPatchApplyLogEntries.length === 0 ? (
              <div style={{ fontSize: 12, color: "#94a3b8" }}>{t("share.panel.patch.apply_log.empty")}</div>
            ) : (
              <div style={{ display: "grid", gap: 8 }}>
                {sortedPatchApplyLogEntries.map((entry) => (
                  <details key={entry.id} style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8 }}>
                    <summary style={{ cursor: "pointer", fontSize: 12, color: "#0f172a" }}>
                      {entry.createdAt} · {entry.patchTitle ?? entry.patchSourceSignature ?? entry.id}
                    </summary>
                    <div style={{ marginTop: 8, display: "grid", gap: 6, fontSize: 11, color: "#334155" }}>
                      <div>
                        {t("share.panel.patch.apply_log.stats_prefix")} cards +{entry.stats.upsertCards}/-{entry.stats.deleteCards}, islands +{entry.stats.upsertIslands}/-{entry.stats.deleteIslands},
                        edges +{entry.stats.upsertEdges}/-{entry.stats.deleteEdges}, relations +{entry.stats.upsertRelationSummaries}/-{entry.stats.deleteRelationSummaries}, evidence +{entry.stats.upsertEvidenceLinks}/-{entry.stats.deleteEvidenceLinks}
                      </div>
                      {entry.conflictMeta ? (
                        <div>
                          {t("share.panel.patch.apply_log.conflicts", { total: entry.conflictMeta.totalConflicts, yours: entry.conflictMeta.chosenYours, theirs: entry.conflictMeta.chosenTheirs, skip: entry.conflictMeta.chosenSkip })}
                        </div>
                      ) : null}
                      {entry.note ? <div>{t("share.panel.patch.apply_log.note", { note: entry.note })}</div> : null}
                      <details>
                        <summary style={{ cursor: "pointer" }}>{t("share.panel.patch.apply_log.applied_op_ids", { count: entry.appliedOpIds.length })}</summary>
                        <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
                          {entry.appliedOpIds.length === 0 ? <li>{t("share.panel.patch.none")}</li> : entry.appliedOpIds.map((opId) => <li key={opId}>{opId}</li>)}
                        </ul>
                      </details>
                      <button
                        type="button"
                        onClick={() => {
                          onCopyPatchApplyLogEntry(entry.id);
                        }}
                        disabled={isLoading}
                      >
                        {t("share.panel.patch.apply_log.copy")}
                      </button>
                    </div>
                  </details>
                ))}
              </div>
            )}
          </div>

          <div id="share-panel-purpose-diff" tabIndex={-1} style={{ ...sectionStyle, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{t("share.panel.diff.section_title")}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              {t("share.panel.diff.section_hint")}
            </div>
            {structuralDiffSection}
          </div>
          </>
          ) : null}
          </section>
        </>
      ) : null}
    </div>
  );
}
