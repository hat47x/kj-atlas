import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { ImportPanel } from "./ImportPanel";
import { SharePanel } from "./SharePanel";
import { setActiveLocale } from "../i18n/translate";
import { t } from "../i18n/translate";
import { buildReadOnlyBlockedMessage } from "../domain/policy/read_only";

function buildShareProps() {
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
    safeMode: true,
    onSafeModeChange: vi.fn(),
    includeUnreviewedDrafts: false,
    onIncludeUnreviewedDraftsChange: vi.fn(),
    onExportViewViewport: vi.fn(),
    onExportViewVisibleBounds: vi.fn(),
    onExportBundleZip: vi.fn(),
    isBundleExportRunning: false,
    onCancelBundleExport: vi.fn(),
    computeProgressMessage: null,
    canIncludeTraces: true,
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

function metrics(html: string) {
  return {
    buttonCount: (html.match(/<button/g) ?? []).length,
    checkboxCount: (html.match(/type="checkbox"/g) ?? []).length,
    detailsCount: (html.match(/<details/g) ?? []).length,
  };
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("i18n functional equivalence", () => {
  it("keeps ImportPanel structure equivalent between ja/en", () => {
    const props = {
      isLoading: false,
      onImportZip: vi.fn(),
      onInvalidFileType: vi.fn(),
      packImportError: null,
      importedPackSummary: null,
    };

    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(ImportPanel, props));
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(ImportPanel, props));

    expect(metrics(enHtml)).toEqual(metrics(jaHtml));
  });

  it("keeps SharePanel interactive structure equivalent between ja/en", () => {
    const props = buildShareProps();

    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(SharePanel, props));
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(SharePanel, props));

    expect(metrics(enHtml)).toEqual(metrics(jaHtml));
  });

  it("keeps read-only blocking behavior locale-independent", () => {
    setActiveLocale("ja");
    const ja = buildReadOnlyBlockedMessage("save");
    setActiveLocale("en");
    const en = buildReadOnlyBlockedMessage("save");

    expect(ja.includes("save")).toBe(true);
    expect(en.includes("save")).toBe(true);
    expect(ja).not.toBe(en);
  });

  it("keeps diagnostics controls and claim-type labels localized in ja/en", () => {
    setActiveLocale("ja");
    const jaDiagnosticsRun = t("side_panel.outline.run_diagnostics");
    const jaClaimTypeUnknown = t("side_panel.claim_type.unknown");

    setActiveLocale("en");
    const enDiagnosticsRun = t("side_panel.outline.run_diagnostics");
    const enClaimTypeUnknown = t("side_panel.claim_type.unknown");

    expect(jaDiagnosticsRun).toBe("diagnostics を実行");
    expect(enDiagnosticsRun).toBe("Run diagnostics");
    expect(jaClaimTypeUnknown).toBe("Unknown (未分類)");
    expect(enClaimTypeUnknown).toBe("Unknown");
  });
});
