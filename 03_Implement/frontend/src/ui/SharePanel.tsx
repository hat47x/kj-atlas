import { useRef } from "react";
import type { ChangeEvent, ReactNode } from "react";
import type { PatchSummaryModel } from "../domain/patch/patch_summary";
import type { PatchApplyLogEntry } from "../domain/types";

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
  onLoadViewMetadataFile,
  onLoadDocumentFile,
  pendingImportedDocumentSummary,
  importDocumentError,
  onReplaceCurrentDocument,
  onLoadPatchFile,
  onLoadPatchBaselineFile,
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
  patchBaselineFileName,
  patchApplyLogEntries,
  onCopyPatchApplyLogEntry,
  structuralDiffSection,
}: SharePanelProps) {
  const viewMetadataInputRef = useRef<HTMLInputElement | null>(null);
  const importDocumentInputRef = useRef<HTMLInputElement | null>(null);
  const patchInputRef = useRef<HTMLInputElement | null>(null);
  const patchBaselineInputRef = useRef<HTMLInputElement | null>(null);

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


  const sortedPatchApplyLogEntries = [...patchApplyLogEntries].sort((left, right) => right.createdAt.localeCompare(left.createdAt));

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
            {patchImportError ? <div style={{ fontSize: 12, color: "#b91c1c", whiteSpace: "pre-wrap" }}>{patchImportError}</div> : null}
            {patchConflictWarning ? <div style={{ fontSize: 12, color: "#b45309", whiteSpace: "pre-wrap" }}>{patchConflictWarning}</div> : null}
            {patchSummary ? (
              <div style={{ border: "1px solid #cbd5e1", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc", display: "grid", gap: 6 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{patchSummary.headline}</div>
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
                  <div key={item.opId} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, display: "grid", gap: 6 }}>
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
                    </div>
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
                  Apply patch
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
                        edges +{entry.stats.upsertEdges}/-{entry.stats.deleteEdges}, relations +{entry.stats.upsertRelationSummaries}/-{entry.stats.deleteRelationSummaries}
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
