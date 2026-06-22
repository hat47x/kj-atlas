import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { readFileSync } from "node:fs";
import { join } from "node:path";

import { ImportPanel } from "./ImportPanel";
import { SharePanel } from "./SharePanel";
import { ReviewDiffPanel } from "./ReviewDiffPanel";
import { DiffPanel } from "./DiffPanel";
import { SuggestionPanel } from "./SuggestionPanel";
import { setActiveLocale } from "../i18n/translate";
import { t } from "../i18n/translate";
import { buildReadOnlyBlockedMessage } from "../domain/policy/read_only";
import type { DocumentV2 } from "../domain/types";


function buildDocumentFixture(): DocumentV2 {
  return {
    version: 2,
    id: "doc-i18n-equivalence",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    islands: [],
    edges: [],
    relationSummaries: [],
  };
}

function buildShareProps() {
  return {
    isOpen: true,
    onToggleOpen: vi.fn(),
    hasDocument: true,
    isLoading: false,
    isReadOnly: false,
    onExportSvgViewport: vi.fn(),
    onExportSvgVisibleBounds: vi.fn(),
    pngExportScale: 1 as const,
    onPngExportScaleChange: vi.fn(),
    onExportPngViewport: vi.fn(),
    onExportPngVisibleBounds: vi.fn(),
    onExportAbstractMapMarkdownWithPng: vi.fn(),
    onExportAbstractMapHtmlWithPng: vi.fn(),
    safeMode: true,
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
    canIncludeTraces: true,
    domainExpressionSummary: {
      unreviewedCards: 0,
      unreviewedIslands: 0,
      holdCards: 0,
      critiqueTargets: 0,
      evidenceLinks: 0,
      contradictionLinks: 0,
      evidenceGapCards: 0,
    },
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

function buildReviewProps() {
  return {
    comparisonFileName: "baseline.json",
    comparisonDocument: buildDocumentFixture(),
    mergeItems: [],
    evaluations: [],
    selectedItemIds: new Set<string>(),
    autoIncludePrerequisites: false,
    onLoadComparisonDocument: vi.fn(),
    onToggleAutoIncludePrerequisites: vi.fn(),
    onItemCheckedChange: vi.fn(),
    onGroupCheckedChange: vi.fn(),
    onApplySelected: vi.fn(),
    onUndoLastMerge: vi.fn(),
    canApply: false,
    isComputingDiff: true,
    onCancelDiff: vi.fn(),
    computeProgressMessage: "working",
    computeProgressPercent: 25,
    isFallbackMode: true,
  };
}


function buildSuggestionProps() {
  return {
    instruction: "layout hints",
    onInstructionChange: vi.fn(),
    onSuggest: vi.fn(),
    onResuggest: vi.fn(),
    onDiscard: vi.fn(),
    hasSuggestion: true,
    isPreviewEnabled: true,
    onPreviewToggle: vi.fn(),
    isAnnotateOverlayEnabled: false,
    onAnnotateOverlayToggle: vi.fn(),
    isSuggesting: false,
    errorMessage: null,
    notes: "memo",
  };
}

function buildDiffProps() {
  return {
    comparisonFileName: "baseline.json",
    comparisonDocument: buildDocumentFixture(),
    diffResult: null,
    currentCardIdSet: new Set<string>(),
    currentIslandIdSet: new Set<string>(),
    onLoadComparisonDocument: vi.fn(),
    onJumpToItem: vi.fn(),
    safeMode: true,
  };
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("i18n functional equivalence", () => {
  it("keeps major workflow labels translatable in English without raw key fallback", () => {
    const keyPattern = /\bt\(\s*["']([^"']+)["']/g;
    const majorFlowFiles = [
      "ImportPanel.tsx",
      "SharePanel.tsx",
      "ReviewDiffPanel.tsx",
      "DiffPanel.tsx",
      "SuggestionPanel.tsx",
      "safe_mode_status.ts",
    ] as const;

    const majorFlowKeys = new Set<string>();
    for (const fileName of majorFlowFiles) {
      const source = readFileSync(join(process.cwd(), "src", "ui", fileName), "utf-8");
      for (const match of source.matchAll(keyPattern)) {
        majorFlowKeys.add(match[1]);
      }
    }

    for (const key of majorFlowKeys) {
      const translated = t(key, undefined, "en");
      expect(translated, `${key} must not fallback to raw key in en locale`).not.toBe(key);
    }
  });

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

  it("keeps ReviewDiffPanel structure equivalent between ja/en", () => {
    const props = buildReviewProps();

    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(ReviewDiffPanel, props));
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(ReviewDiffPanel, props));

    expect(metrics(enHtml)).toEqual(metrics(jaHtml));
    expect(jaHtml).not.toContain("Apply selected merge");
    expect(enHtml).toContain("Apply selected merge");
  });

  it("keeps DiffPanel structure equivalent between ja/en", () => {
    const props = buildDiffProps();

    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(DiffPanel, props));
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(DiffPanel, props));

    expect(metrics(enHtml)).toEqual(metrics(jaHtml));
    expect(jaHtml).not.toContain("Load comparison document (JSON)");
    expect(enHtml).toContain("Load comparison document (JSON)");
  });

  it("keeps SuggestionPanel structure equivalent between ja/en", () => {
    const props = buildSuggestionProps();

    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(SuggestionPanel, props));
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(SuggestionPanel, props));

    expect(metrics(enHtml)).toEqual(metrics(jaHtml));
    expect(jaHtml).toContain("安全上の条件");
    expect(jaHtml).toContain("自動適用なし");
    expect(jaHtml).not.toContain("CE2");
    expect(enHtml).toContain("Safety conditions");
    expect(enHtml).not.toContain("auto_apply_blocked");
    expect(enHtml).not.toContain("Apply suggestion");
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

    expect(jaDiagnosticsRun).toBe("診断を実行");
    expect(enDiagnosticsRun).toBe("Run diagnostics");
    expect(jaClaimTypeUnknown).toBe("不明（未分類）");
    expect(enClaimTypeUnknown).toBe("Unknown");
  });

  it("localizes legacy toolbar/export labels and trace analytics export action", () => {
    setActiveLocale("ja");
    const jaImportLegacy = t("app.toolbar.import_doc_json_legacy");
    const jaExportLegacy = t("view_controls.export_legacy.title");
    const jaTraceAnalytics = t("side_panel.trace.export_analytics");

    setActiveLocale("en");
    const enImportLegacy = t("app.toolbar.import_doc_json_legacy");
    const enExportLegacy = t("view_controls.export_legacy.title");
    const enTraceAnalytics = t("side_panel.trace.export_analytics");

    expect(jaImportLegacy).toContain("旧式");
    expect(enImportLegacy).toContain("Import doc JSON");
    expect(jaExportLegacy).toBe("書き出し（旧式）");
    expect(enExportLegacy).toBe("Export (legacy)");
    expect(jaTraceAnalytics).toContain("書き出す");
    expect(enTraceAnalytics).toBe("Export Trace Analytics");
  });
});
