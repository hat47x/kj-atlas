import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { SharePanel } from "./SharePanel";

function buildProps(safeMode: boolean) {
  return {
    isOpen: true,
    onToggleOpen: vi.fn(),
    hasDocument: true,
    isLoading: false,
    onExportSvgViewport: vi.fn(),
    onExportSvgVisibleBounds: vi.fn(),
    pngExportScale: 1 as const,
    onPngExportScaleChange: vi.fn(),
    onExportPngViewport: vi.fn(),
    onExportPngVisibleBounds: vi.fn(),
    onExportAbstractMapMarkdownWithPng: vi.fn(),
    onExportAbstractMapHtmlWithPng: vi.fn(),
    safeMode,
    onSafeModeChange: vi.fn(),
    includeUnreviewedDrafts: false,
    onIncludeUnreviewedDraftsChange: vi.fn(),
    onExportViewViewport: vi.fn(),
    onExportViewVisibleBounds: vi.fn(),
    onExportBundleZip: vi.fn(),
    isBundleExportRunning: false,
    onCancelBundleExport: vi.fn(),
    computeProgressMessage: null,
    canIncludeTraces: false,
    onLoadViewMetadataFile: vi.fn(),
    onLoadDocumentFile: vi.fn(),
    onImportReviewPackFile: vi.fn(),
    onInvalidReviewPackFileType: vi.fn(),
    packImportError: null,
    importedPackSummary: null,
    pendingImportedDocumentSummary: null,
    importDocumentError: null,
    onReplaceCurrentDocument: vi.fn(),
    onLoadPatchFile: vi.fn(),
    onLoadPatchBaselineFile: vi.fn(),
    onExportPatchFile: vi.fn(),
    patchExportAuthor: "",
    patchExportAuthorNote: "",
    onPatchExportAuthorChange: vi.fn(),
    onPatchExportAuthorNoteChange: vi.fn(),
    patchTrustLabel: "untrusted" as const,
    onPatchTrustLabelChange: vi.fn(),
    patchFingerprintStatus: null,
    patchFileName: null,
    patchImportError: null,
    patchConflictWarning: null,
    patchSummary: null,
    onCopyPatchSummary: vi.fn(),
    patchPreviewItems: [],
    onPatchItemCheckedChange: vi.fn(),
    onConflictResolutionChange: vi.fn(),
    onApplyPatch: vi.fn(),
    canApplyPatch: false,
    hasPatchSelection: false,
    patchLintIssues: [],
    fixProposals: [],
    selectedFixProposalIds: new Set<string>(),
    onFixProposalCheckedChange: vi.fn(),
    onApplySelectedFixes: vi.fn(),
    onResetPatchToOriginal: vi.fn(),
    patchBaselineFileName: null,
    patchApplyLogEntries: [],
    onCopyPatchApplyLogEntry: vi.fn(),
    structuralDiffSection: null,
  };
}

describe("SharePanel safe mode copy", () => {
  it("shows consistent safe-mode-on messages", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("SafeMode: ON");
    expect(html).toContain("SafeMode is ON. Exported summaries stay privacy-first by default.");
    expect(html).toContain("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
  });

  it("shows consistent safe-mode-off warnings", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(false)));
    expect(html).toContain("SafeMode: OFF");
    expect(html).toContain("SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.");
    expect(html).toContain("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
  });
});

describe("SharePanel bundle granularity", () => {
  it("renders granularity options in export section", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("Export granularity");
    expect(html).toContain("Detail (full trace exports)");
    expect(html).toContain("Overview (high-level summary)");
  });
});
