import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ImportPanel } from "./ImportPanel";
import { setActiveLocale } from "../i18n/translate";

afterEach(() => {
  setActiveLocale("ja");
});

describe("ImportPanel copy", () => {
  it("renders Japanese dictionary labels by default", () => {
    const html = renderToStaticMarkup(
      React.createElement(ImportPanel, {
        isLoading: false,
        onImportZip: vi.fn(),
        onInvalidFileType: vi.fn(),
        packImportError: null,
        importedPackSummary: null,
      }),
    );

    expect(html).toContain("レビューパックを取り込む (.zip)");
    expect(html).toContain("review-pack .zip をここにドラッグ");
    expect(html).toContain("ZIPを選択…");
  });

  it("renders English labels with locale switch", () => {
    setActiveLocale("en");

    const html = renderToStaticMarkup(
      React.createElement(ImportPanel, {
        isLoading: false,
        onImportZip: vi.fn(),
        onInvalidFileType: vi.fn(),
        packImportError: null,
        importedPackSummary: null,
      }),
    );

    expect(html).toContain("Import review pack (.zip)");
    expect(html).toContain("Drag &amp; drop review-pack .zip here");
    expect(html).toContain("Choose ZIP…");
  });

  it("renders interpolated summary and warning in English", () => {
    setActiveLocale("en");

    const html = renderToStaticMarkup(
      React.createElement(ImportPanel, {
        isLoading: false,
        onImportZip: vi.fn(),
        onInvalidFileType: vi.fn(),
        packImportError: null,
        importedPackSummary: {
          fileName: "sample.zip",
          cardCount: 2,
          islandCount: 1,
          perspectiveMode: "default",
          warningCount: 3,
        },
      }),
    );

    expect(html).toContain("Imported sample.zip: cards 2, islands 1, perspective default");
    expect(html).toContain("Ignored 3 unsupported or non-core file(s).");
  });
});
