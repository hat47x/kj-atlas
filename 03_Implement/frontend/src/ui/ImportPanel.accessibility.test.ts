import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ImportPanel } from "./ImportPanel";
import { setActiveLocale } from "../i18n/translate";

describe("ImportPanel accessibility (UQ-2)", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  const renderPanel = () =>
    renderToStaticMarkup(
      createElement(ImportPanel, {
        onImportReviewPack: vi.fn(),
        onImportDocument: vi.fn(),
        isReadOnly: false,
        safeMode: true,
      })
    );

  it("has accessible title", () => {
    const html = renderPanel();
    expect(html).toContain("レビューパック");
  });

  it("file input is present for screen readers", () => {
    const html = renderPanel();
    expect(html).toContain('type="file"');
    expect(html).toContain('accept=".zip,application/zip"');
  });

  it("drop zone instruction is visible", () => {
    const html = renderPanel();
    expect(html).toContain("ドラッグ");
  });

  it("choose file button is reachable", () => {
    const html = renderPanel();
    expect(html).toContain("ZIPファイルを選択");
  });
});
