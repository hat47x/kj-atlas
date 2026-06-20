import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { SharePanel } from "./SharePanel";
import { setActiveLocale } from "../i18n/translate";

function buildProps(safeMode: boolean, overrides: Partial<React.ComponentProps<typeof SharePanel>> = {}) {
  const props: React.ComponentProps<typeof SharePanel> = {
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

  return { ...props, ...overrides };
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("SharePanel safe mode copy", () => {
  it("shows consistent Japanese safe-mode-on messages", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("共有と再現");
    expect(html).toContain("共有用の書き出し、レビューパックの取り込み、差分確認をここから行います。");
    expect(html).toContain("目的を選ぶ");
    expect(html).toContain("共有用に書き出す");
    expect(html).toContain("取り込む・復元する");
    expect(html).toContain("パッチを確認する");
    expect(html).toContain("差分を確認する");
    expect(html).toContain('aria-controls="share-panel-purpose-export"');
    expect(html).toContain('id="share-panel-purpose-import"');
    expect(html).toContain('aria-label="パネルを閉じる"');
    expect(html).toContain("セーフモード: ON");
    expect(html).toContain("セーフモードが ON です。書き出した要約は既定でプライバシー優先になります。");
    expect(html).toContain("固定マスク対象: 共有 / レビューパック（無効化できません）。");
    expect(html).toContain("共有前チェック");
    expect(html).toContain("SafeMode、公開範囲、未レビュー情報、出力形式を確認してから実行してください。");
    expect(html).toContain("未レビュー情報");
    expect(html).toContain("SafeMode ON のため未レビューのドラフトは含めません。");
    expect(html).toContain("出力形式");
    expect(html).toContain("SVG / PNG / view.json / 概念マップレポート / レビューパック.zip");
    expect(html).not.toContain("未レビューのドラフトを含める");
  });


  it("surfaces domain-expression readiness in the share preflight", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true, {
      domainExpressionSummary: {
        unreviewedCards: 2,
        unreviewedIslands: 1,
        holdCards: 3,
        critiqueTargets: 4,
        evidenceLinks: 5,
        contradictionLinks: 1,
        evidenceGapCards: 2,
      },
    })));

    expect(html).toContain("Domain readiness");
    expect(html).toContain("13 review signals remain");
    expect(html).toContain("Ambiguity / evidence / review summary");
    expect(html).toContain("Unreviewed: cards 2, islands 1");
    expect(html).toContain("Hold / unknown claims: 3");
    expect(html).toContain("Critique or pending feedback targets: 4");
    expect(html).toContain("Evidence links 5, contradictions 1, evidence gaps 2");
  });

  it("shows consistent English safe-mode-off warnings", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(false)));
    expect(html).toContain("SafeMode: OFF");
    expect(html).toContain("SafeMode is OFF. Exports may include raw text. Re-enable SafeMode before external sharing.");
    expect(html).toContain("Locked redaction contexts: Share / Review Pack (cannot be disabled).");
    expect(html).toContain("Preflight check");
    expect(html).toContain("Unreviewed drafts are excluded. Enable them only when the recipient expects draft content.");
    expect(html).toContain("Include unreviewed drafts");
  });
});

describe("SharePanel read-only document loading", () => {
  it("describes opening a validated document for inspection instead of replacing it", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true, {
      isReadOnly: true,
      pendingImportedDocumentSummary: {
        fileName: "inspection.document.json",
        cardCount: 1,
        islandCount: 0,
        edgeCount: 0,
      },
    })));

    expect(html).toContain("open it for inspection without saving");
    expect(html).toContain("Open for inspection");
    expect(html).not.toContain("Replace current document");
  });
});

describe("SharePanel bundle granularity", () => {
  it("keeps the export panel controls within the fixed panel width", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("overflow-x:hidden");
    expect(html).toContain("box-sizing:border-box");
    expect(html).toContain("min-width:0");
    expect(html).toContain("white-space:normal");
  });

  it("renders Japanese granularity options in export section", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("書き出し粒度");
    expect(html).toContain("詳細（トレースをすべて含める）");
    expect(html).toContain("概要（高レベル要約）");
  });

  it("renders English granularity options in export section", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("Export granularity");
    expect(html).toContain("Detail (full trace exports)");
    expect(html).toContain("Overview (high-level summary)");
  });

  it("explains selected-card trace availability in English", () => {
    setActiveLocale("en");

    const unavailableHtml = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true, { canIncludeTraces: false })));
    expect(unavailableHtml).toContain("Traces require a selected card.");

    const availableHtml = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true, { canIncludeTraces: true })));
    expect(availableHtml).toContain("Evidence, contradiction, and analytics traces for the selected card will be included.");
  });
});


describe("SharePanel patch section localization", () => {
  it("renders Japanese patch controls", () => {
    const html = renderToStaticMarkup(React.createElement(SharePanel, buildProps(true)));
    expect(html).toContain("4) パッチを確認");
    expect(html).toContain("patch.json を読み込む");
    expect(html).toContain("6) 差分確認 / 検証");
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
    expect(html).toContain("view の公開範囲");
    expect(html).toContain("パックの公開範囲");
    expect(html).toContain("公開範囲（view）");
    expect(html).toContain("公開範囲（パック）");
    expect(html).toContain('option value="Public"');
    expect(html).toContain('option value="Unlisted"');
    expect(html).toContain('option value="Org"');
    expect(html).toContain('option value="Restricted"');
    expect(html).toContain('option value="Restricted">制限付き</option>');
    expect(html).toContain("view の公開範囲が未指定の場合は、制限付きとして扱います。");
    expect(html).toContain("パックの公開範囲が未指定の場合は、公開として扱います。");
  });
});
