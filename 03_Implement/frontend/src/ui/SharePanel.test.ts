import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { SharePanel } from "./SharePanel";
import { setActiveLocale } from "../i18n/translate";

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
    viewVisibility: "Restricted" as const,
    packVisibility: "Public" as const,
    onViewVisibilityChange: vi.fn(),
    onPackVisibilityChange: vi.fn(),
    onSafeModeChange: vi.fn(),
    includeUnreviewedDrafts: false,
    onIncludeUnreviewedDraftsChange: vi.fn(),
    currentReviewerRef: "user:local:test",
    currentReviewerRefSource: "local" as const,
    onCurrentReviewerRefChange: vi.fn(),
    onResetCurrentReviewerRef: vi.fn(),
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

afterEach(() => {
  setActiveLocale("ja");
});

describe("SharePanel safe mode copy", () => {
  it("shows consistent Japanese safe-mode-on messages", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("セーフモード: ON");
    expect(html).toContain("セーフモードが ON です。エクスポートされた要約は既定でプライバシー優先になります。");
    expect(html).toContain("固定マスク対象: Share / Review Pack（無効化できません）。");
  });

  it("shows consistent English safe-mode-off warnings", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(false)));
    expect(html).toContain("SafeMode: OFF");
    expect(html).toContain("SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.");
    expect(html).toContain("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
  });
});

describe("SharePanel bundle granularity", () => {
  it("renders Japanese granularity options in export section", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("エクスポート粒度");
    expect(html).toContain("Detail（完全な trace を出力）");
    expect(html).toContain("Overview（高レベル要約）");
  });

  it("renders English granularity options in export section", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("Export granularity");
    expect(html).toContain("Detail (full trace exports)");
    expect(html).toContain("Overview (high-level summary)");
  });
});


describe("SharePanel patch section localization", () => {
  it("renders Japanese patch controls", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("4) パッチ");
    expect(html).toContain("patch.json を読み込む");
    expect(html).toContain("6) Diff / Verify");
  });

  it("renders English patch controls", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("4) Patch");
    expect(html).toContain("Load patch.json");
    expect(html).toContain("6) Diff / Verify");
  });
});


describe("SharePanel visibility controls", () => {
  it("renders view/pack visibility selectors with fallback copy", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("View visibility");
    expect(html).toContain("Pack visibility");
    expect(html).toContain('option value="Public"');
    expect(html).toContain('option value="Unlisted"');
    expect(html).toContain('option value="Org"');
    expect(html).toContain('option value="Restricted"');
    expect(html).toContain("Fallback: when view visibility is missing, Restricted is applied.");
    expect(html).toContain("Fallback: when pack visibility is missing, Public is applied.");
  });
});
