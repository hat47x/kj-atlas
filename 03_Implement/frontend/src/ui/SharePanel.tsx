import { useRef, useState } from "react";
import type { ChangeEvent, ReactNode } from "react";
import type { PatchSummaryModel } from "../domain/patch/patch_summary";
import type { PatchApplyLogEntry } from "../domain/types";
import type { PatchLintIssue } from "../domain/patch/patch_lint";
import type { FixProposal } from "../domain/patch/patch_fix";
import type { TrustLabel } from "../domain/patch/patch_types";

type SharePanelProps = {
  isOpen: boolean;
  onToggleOpen: () => void;
  hasDocument: boolean;
  isLoading: boolean;
  onExportSvgViewport: () => void;
  onExportSvgVisibleBounds: () => void;
  pngExportScale: 1 | 2;
  onPngExportScaleChange: (value: 1 | 2) => void;
  onExportPngViewport: () => void;
  onExportPngVisibleBounds: () => void;
  onExportAbstractMapMarkdownWithPng: () => void;
  onExportAbstractMapHtmlWithPng: () => void;
  safeMode: boolean;
  includeUnreviewedDrafts: boolean;
  onIncludeUnreviewedDraftsChange: (value: boolean) => void;
  onExportViewViewport: () => void;
  onExportViewVisibleBounds: () => void;
  onExportBundleZip: (options: { includeOutline: boolean; includeDiagnostics: boolean; includeSelectedCardTraces: boolean }) => void;
  canIncludeTraces: boolean;
  onLoadViewMetadataFile: (file: File) => void;
  onLoadDocumentFile: (file: File) => void;
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
  gap: 8,
  paddingBottom: 10,
  marginBottom: 10,
  borderBottom: "1px solid #e2e8f0",
} as const;

export function SharePanel({
  isOpen,
  onToggleOpen,
  hasDocument,
  isLoading,
  onExportSvgViewport,
  onExportSvgVisibleBounds,
  pngExportScale,
  onPngExportScaleChange,
  onExportPngViewport,
  onExportPngVisibleBounds,
  onExportAbstractMapMarkdownWithPng,
  onExportAbstractMapHtmlWithPng,
  safeMode,
  includeUnreviewedDrafts,
  onIncludeUnreviewedDraftsChange,
  onExportViewViewport,
  onExportViewVisibleBounds,
  onExportBundleZip,
  canIncludeTraces,
  onLoadViewMetadataFile,
  onLoadDocumentFile,
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
  const viewMetadataInputRef = useRef<HTMLInputElement | null>(null);
  const importDocumentInputRef = useRef<HTMLInputElement | null>(null);
  const patchInputRef = useRef<HTMLInputElement | null>(null);
  const patchBaselineInputRef = useRef<HTMLInputElement | null>(null);

  const [bundleIncludeOutline, setBundleIncludeOutline] = useState(true);
  const [bundleIncludeDiagnostics, setBundleIncludeDiagnostics] = useState(true);
  const [bundleIncludeSelectedCardTraces, setBundleIncludeSelectedCardTraces] = useState(true);


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

  const lintErrors = patchLintIssues.filter((item) => item.severity === "error");
  const lintWarnings = patchLintIssues.filter((item) => item.severity === "warn");
  const lintInfos = patchLintIssues.filter((item) => item.severity === "info");

  const sortedPatchApplyLogEntries = [...patchApplyLogEntries].sort((left, right) => right.createdAt.localeCompare(left.createdAt));
  const shortFingerprint = (value: string | undefined): string => {
    if (!value) return "(n/a)";
    if (value.length <= 20) return value;
    return `${value.slice(0, 10)}…${value.slice(-6)}`;
  };

  return (
    <div style={{ position: "relative" }}>
      <button
        type="button"
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
        Share &amp; Reproduce
      </button>
      {isOpen ? (
        <section
          style={{
            position: "absolute",
            top: "calc(100% + 8px)",
            left: 0,
            zIndex: 20,
            width: 340,
            border: "1px solid #cbd5e1",
            borderRadius: 8,
            backgroundColor: "#ffffff",
            padding: 10,
            boxShadow: "0 12px 24px rgba(15, 23, 42, 0.18)",
          }}
        >
          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>1) Export package</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Export reproducible artifacts first (SVG/PNG/report + view.json metadata).
            </div>
            <button type="button" onClick={onExportSvgViewport} disabled={!hasDocument || isLoading}>
              Export SVG (Viewport)
            </button>
            <button type="button" onClick={onExportSvgVisibleBounds} disabled={!hasDocument || isLoading}>
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
            <button type="button" onClick={onExportPngViewport} disabled={!hasDocument || isLoading}>
              Export PNG (Viewport)
            </button>
            <button type="button" onClick={onExportPngVisibleBounds} disabled={!hasDocument || isLoading}>
              Export PNG (Visible bounds)
            </button>
            <button type="button" onClick={onExportAbstractMapMarkdownWithPng} disabled={!hasDocument || isLoading}>
              Export Report (MD + PNG)
            </button>
            <button type="button" onClick={onExportAbstractMapHtmlWithPng} disabled={!hasDocument || isLoading}>
              Export Report (HTML + PNG)
            </button>
            {safeMode ? (
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                <input
                  type="checkbox"
                  checked={includeUnreviewedDrafts}
                  onChange={(event) => {
                    onIncludeUnreviewedDraftsChange(event.target.checked);
                  }}
                />
                Include unreviewed drafts
              </label>
            ) : null}
            <button type="button" onClick={onExportViewViewport} disabled={!hasDocument || isLoading}>
              Export view.json (Viewport)
            </button>
            <button type="button" onClick={onExportViewVisibleBounds} disabled={!hasDocument || isLoading}>
              Export view.json (Visible bounds)
            </button>
            <div style={{ borderTop: "1px dashed #e2e8f0", paddingTop: 8, marginTop: 4, display: "grid", gap: 6 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                <input
                  type="checkbox"
                  checked={bundleIncludeOutline}
                  onChange={(event) => {
                    setBundleIncludeOutline(event.target.checked);
                  }}
                />
                Include outline
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
                <input
                  type="checkbox"
                  checked={bundleIncludeDiagnostics}
                  onChange={(event) => {
                    setBundleIncludeDiagnostics(event.target.checked);
                  }}
                />
                Include diagnostics
              </label>
              <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: canIncludeTraces ? "#334155" : "#94a3b8" }}>
                <input
                  type="checkbox"
                  checked={bundleIncludeSelectedCardTraces}
                  disabled={!canIncludeTraces}
                  onChange={(event) => {
                    setBundleIncludeSelectedCardTraces(event.target.checked);
                  }}
                />
                Include traces for selected card
              </label>
              <div style={{ fontSize: 11, color: "#64748b" }}>Traces require a selected card.</div>
              <button
                type="button"
                onClick={() => {
                  onExportBundleZip({
                    includeOutline: bundleIncludeOutline,
                    includeDiagnostics: bundleIncludeDiagnostics,
                    includeSelectedCardTraces: bundleIncludeSelectedCardTraces && canIncludeTraces,
                  });
                }}
                disabled={!hasDocument || isLoading}
              >
                Export bundle (.zip)
              </button>
            </div>
          </div>

          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>2) Restore view</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>Load view.json to restore camera and view toggles only.</div>
            <button
              type="button"
              onClick={() => {
                viewMetadataInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              Import view.json
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
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>3) Load document.json</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Validate DocumentV2 JSON first, then explicitly replace the current document.
            </div>
            <button
              type="button"
              onClick={() => {
                importDocumentInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              Load document.json
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
                  cards: {pendingImportedDocumentSummary.cardCount} / islands: {pendingImportedDocumentSummary.islandCount} / edges: {pendingImportedDocumentSummary.edgeCount}
                </div>
                <button type="button" onClick={onReplaceCurrentDocument} disabled={isLoading}>
                  Replace current document
                </button>
              </div>
            ) : null}
          </div>

          <div style={{ ...sectionStyle, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>4) Patch</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Import patch JSON and optional baseline JSON for 3-way conflict detection.
            </div>
            <button
              type="button"
              onClick={() => {
                patchInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              Load patch.json
            </button>
            <input ref={patchInputRef} type="file" accept="application/json,.json" onChange={handlePatchFileChange} style={{ display: "none" }} />
            <button
              type="button"
              onClick={() => {
                patchBaselineInputRef.current?.click();
              }}
              disabled={isLoading}
            >
              Load baseline document.json (optional)
            </button>
            <input
              ref={patchBaselineInputRef}
              type="file"
              accept="application/json,.json"
              onChange={handlePatchBaselineFileChange}
              style={{ display: "none" }}
            />
            {patchFileName ? <div style={{ fontSize: 12, color: "#334155" }}>Patch: {patchFileName}</div> : null}
            {patchBaselineFileName ? <div style={{ fontSize: 12, color: "#334155" }}>Baseline: {patchBaselineFileName}</div> : null}
            <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
              Trust label (view only)
              <select
                value={patchTrustLabel}
                onChange={(event) => {
                  onPatchTrustLabelChange(event.target.value as TrustLabel);
                }}
                style={{ fontSize: 12 }}
              >
                <option value="unknown">Unknown</option>
                <option value="trusted">Trusted</option>
                <option value="untrusted">Untrusted</option>
              </select>
            </label>
            {patchFingerprintStatus ? (
              <div style={{ fontSize: 12, color: "#334155", display: "grid", gap: 2 }}>
                <strong>Integrity: {patchFingerprintStatus.status}</strong>
                <span>expected: {shortFingerprint(patchFingerprintStatus.expected)}</span>
                <span>actual: {shortFingerprint(patchFingerprintStatus.actual)}</span>
              </div>
            ) : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>Export patch.json</div>
              <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#334155" }}>
                Author (optional)
                <input value={patchExportAuthor} onChange={(event) => { onPatchExportAuthorChange(event.target.value); }} />
              </label>
              <label style={{ display: "grid", gap: 4, fontSize: 11, color: "#334155" }}>
                Author note (optional)
                <input value={patchExportAuthorNote} onChange={(event) => { onPatchExportAuthorNoteChange(event.target.value); }} />
              </label>
              <button type="button" onClick={onExportPatchFile} disabled={isLoading || !patchFileName}>Download patch.json (with fingerprint)</button>
            </div>
            {patchImportError ? <div style={{ fontSize: 12, color: "#b91c1c", whiteSpace: "pre-wrap" }}>{patchImportError}</div> : null}
            {patchConflictWarning ? <div style={{ fontSize: 12, color: "#b45309", whiteSpace: "pre-wrap" }}>{patchConflictWarning}</div> : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>Lint</div>
              <div style={{ fontSize: 11, color: "#334155" }}>Errors ({lintErrors.length}) / Warnings ({lintWarnings.length}) / Info ({lintInfos.length})</div>
              <details>
                <summary style={{ cursor: "pointer", fontSize: 11, color: "#b91c1c" }}>Errors ({lintErrors.length})</summary>
                <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#7f1d1d", display: "grid", gap: 2 }}>
                  {lintErrors.length === 0 ? <li>(none)</li> : lintErrors.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                </ul>
              </details>
              <details>
                <summary style={{ cursor: "pointer", fontSize: 11, color: "#b45309" }}>Warnings ({lintWarnings.length})</summary>
                <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#92400e", display: "grid", gap: 2 }}>
                  {lintWarnings.length === 0 ? <li>(none)</li> : lintWarnings.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                </ul>
              </details>
              {lintInfos.length > 0 ? (
                <details>
                  <summary style={{ cursor: "pointer", fontSize: 11, color: "#475569" }}>Info ({lintInfos.length})</summary>
                  <ul style={{ margin: "6px 0 0", paddingLeft: 18, fontSize: 11, color: "#475569", display: "grid", gap: 2 }}>
                    {lintInfos.map((issue, index) => <li key={`${issue.code}-${issue.opId ?? "global"}-${index}`}>{issue.code}: {issue.message}{issue.opId ? <> (<a href={`#patch-op-${issue.opId}`}>op:{issue.opId}</a>)</> : ""}</li>)}
                  </ul>
                </details>
              ) : null}
              {lintErrors.length > 0 ? <div style={{ fontSize: 11, color: "#b91c1c" }}>Resolve lint errors first.</div> : null}
            <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>Fix suggestions ({fixProposals.length})</div>
              {fixProposals.length === 0 ? (
                <div style={{ fontSize: 11, color: "#64748b" }}>No auto-fix proposal for current lint issues.</div>
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
                      <span style={{ color: "#64748b" }}>affected ops: {proposal.affectedOpIds.length}</span>
                    </label>
                  ))}
                </div>
              )}
              <div style={{ display: "flex", gap: 8 }}>
                <button type="button" onClick={onApplySelectedFixes} disabled={isLoading || selectedFixProposalIds.size === 0}>
                  Apply selected fixes to patch
                </button>
                <button type="button" onClick={onResetPatchToOriginal} disabled={isLoading || !patchFileName}>
                  Reset patch to original
                </button>
              </div>
            </div>
            </div>
            {patchSummary ? (
              <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc", display: "grid", gap: 6 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{patchSummary.headline}</div>
                <div style={{ fontSize: 11, color: "#334155" }}>Trust label: <strong>{patchTrustLabel}</strong></div>
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
                  Copy summary (Markdown)
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
                          CONFLICT
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
                          LINT {item.lintIssueCount}
                        </span>
                      ) : null}
                    </div>
                    {item.lintIssueCount > 0 ? (
                      <div style={{ fontSize: 11, color: item.lintErrorCount > 0 ? "#b91c1c" : "#b45309" }}>Lint: {item.lintIssueCodes.join(", ")}</div>
                    ) : null}
                    {item.conflict ? (
                      <>
                        <div style={{ fontSize: 11, color: "#b45309" }}>Choose resolution to apply. {item.reason ?? ""}</div>
                        <div style={{ fontSize: 11, color: "#475569", whiteSpace: "pre-wrap" }}>
                          base: {item.baseSnippet ?? "(none)"}
                          {"\n"}
                          yours: {item.yourSnippet ?? "(none)"}
                          {"\n"}
                          theirs: {item.theirSnippet ?? "(none)"}
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
                          Use yours
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
                          Use theirs
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
                          Skip
                        </label>
                      </>
                    ) : null}
                  </div>
                ))}
                <button type="button" onClick={onApplyPatch} disabled={!canApplyPatch || isLoading}>
                  {lintErrors.length > 0 ? "Resolve lint errors first" : hasPatchSelection ? "Apply patch" : "Select operations to apply"}
                </button>
              </div>
            ) : null}
          </div>



          <div style={sectionStyle}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>5) Apply log ({patchApplyLogEntries.length})</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>Persistent patch apply history for this document (newest first).</div>
            {sortedPatchApplyLogEntries.length === 0 ? (
              <div style={{ fontSize: 12, color: "#94a3b8" }}>No patch apply log entries yet.</div>
            ) : (
              <div style={{ display: "grid", gap: 8 }}>
                {sortedPatchApplyLogEntries.map((entry) => (
                  <details key={entry.id} style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8 }}>
                    <summary style={{ cursor: "pointer", fontSize: 12, color: "#0f172a" }}>
                      {entry.createdAt} · {entry.patchTitle ?? entry.patchSourceSignature ?? entry.id}
                    </summary>
                    <div style={{ marginTop: 8, display: "grid", gap: 6, fontSize: 11, color: "#334155" }}>
                      <div>
                        stats: cards +{entry.stats.upsertCards}/-{entry.stats.deleteCards}, islands +{entry.stats.upsertIslands}/-{entry.stats.deleteIslands},
                        edges +{entry.stats.upsertEdges}/-{entry.stats.deleteEdges}, relations +{entry.stats.upsertRelationSummaries}/-{entry.stats.deleteRelationSummaries}, evidence +{entry.stats.upsertEvidenceLinks}/-{entry.stats.deleteEvidenceLinks}
                      </div>
                      {entry.conflictMeta ? (
                        <div>
                          conflicts: total {entry.conflictMeta.totalConflicts}, yours {entry.conflictMeta.chosenYours}, theirs {entry.conflictMeta.chosenTheirs},
                          skip {entry.conflictMeta.chosenSkip}
                        </div>
                      ) : null}
                      {entry.note ? <div>note: {entry.note}</div> : null}
                      <details>
                        <summary style={{ cursor: "pointer" }}>appliedOpIds ({entry.appliedOpIds.length})</summary>
                        <ul style={{ margin: "6px 0 0", paddingLeft: 18 }}>
                          {entry.appliedOpIds.length === 0 ? <li>(none)</li> : entry.appliedOpIds.map((opId) => <li key={opId}>{opId}</li>)}
                        </ul>
                      </details>
                      <button
                        type="button"
                        onClick={() => {
                          onCopyPatchApplyLogEntry(entry.id);
                        }}
                        disabled={isLoading}
                      >
                        Copy log entry (Markdown)
                      </button>
                    </div>
                  </details>
                ))}
              </div>
            )}
          </div>

          <div style={{ ...sectionStyle, marginBottom: 0, paddingBottom: 0, borderBottom: "none" }}>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>6) Diff / Verify</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>
              Structural doc diff (F3). Image diff (G2) and snapshot bundle verify (G3) remain available from legacy tools.
            </div>
            {structuralDiffSection}
          </div>
        </section>
      ) : null}
    </div>
  );
}
