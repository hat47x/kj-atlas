import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { StartPanel } from "./StartPanel";
import { setActiveLocale } from "../i18n/translate";

function buildProps(overrides: Partial<React.ComponentProps<typeof StartPanel>> = {}) {
  return {
    isOpen: true,
    safeMode: true,
    isLoading: false,
    isSaving: false,
    hasDocument: true,
    onClose: vi.fn(),
    onCreateDocument: vi.fn(),
    onOpenSampleDocument: vi.fn(),
    onLoadDocumentFile: vi.fn(),
    onImportReviewPackFile: vi.fn(),
    ...overrides,
  } satisfies React.ComponentProps<typeof StartPanel>;
}

describe("StartPanel", () => {
  it("shows the first-run document entry actions in Japanese", () => {
    setActiveLocale("ja");

    const html = renderToStaticMarkup(React.createElement(StartPanel, buildProps()));

    expect(html).toContain("文書を開く・作成する");
    expect(html).toContain("新しい文書を作成");
    expect(html).toContain("サンプルを開く");
    expect(html).toContain("文書ファイルを読み込む");
    expect(html).toContain("レビューパックを取り込む");
    expect(html).toContain("安全状態: セーフモード: ON");
  });

  it("uses English copy when the locale is English", () => {
    setActiveLocale("en");

    const html = renderToStaticMarkup(React.createElement(StartPanel, buildProps({ safeMode: false })));

    expect(html).toContain("Open or create a document");
    expect(html).toContain("Create new document");
    expect(html).toContain("Open sample");
    expect(html).toContain("Load document file");
    expect(html).toContain("Import review pack");
    expect(html).toContain("Safety state: SafeMode: OFF");
  });

  it("does not render when closed", () => {
    setActiveLocale("ja");

    const html = renderToStaticMarkup(React.createElement(StartPanel, buildProps({ isOpen: false })));

    expect(html).toBe("");
  });
});
