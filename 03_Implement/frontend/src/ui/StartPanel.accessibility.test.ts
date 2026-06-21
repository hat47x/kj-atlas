import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { StartPanel } from "./StartPanel";
import { setActiveLocale } from "../i18n/translate";

describe("StartPanel accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  const renderPanel = () =>
    renderToStaticMarkup(
      createElement(StartPanel, {
        currentDocumentId: "doc-1",
        isDirty: false,
        isLoading: false,
        isReadOnly: false,
        isSaving: false,
        recentDocumentIds: [],
        safeMode: true,
        selectedRecentDocumentId: "",
        onClose: vi.fn(),
        onCreateNew: vi.fn(),
        onImportReviewPack: vi.fn(),
        onLoadDocumentFile: vi.fn(),
        onOpenRecent: vi.fn(),
        onOpenSample: vi.fn(),
        onSelectedRecentDocumentChange: vi.fn(),
      })
    );

  it("has dialog role for modal semantics", () => {
    const html = renderPanel();
    expect(html).toContain('role="dialog"');
    expect(html).toContain('aria-modal="true"');
  });

  it("has accessible label on the dialog", () => {
    const html = renderPanel();
    expect(html).toContain('aria-label=');
  });

  it("SafeMode status is visible in Japanese", () => {
    const html = renderPanel();
    expect(html).toContain("セーフモード: ON");
  });

  it("create new document button is reachable", () => {
    const html = renderPanel();
    expect(html).toContain("作成");
  });

  it("sample button is reachable", () => {
    const html = renderPanel();
    expect(html).toContain("サンプル");
  });

  it("close button has accessible label in Japanese", () => {
    const html = renderPanel();
    expect(html).toContain('aria-label="開始パネルを閉じる"');
  });
});
