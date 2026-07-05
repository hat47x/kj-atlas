import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { EmptyCanvasHint } from "./EmptyCanvasHint";

function renderHint() {
  return renderToStaticMarkup(
    React.createElement(EmptyCanvasHint, {
      onCreateCard: vi.fn(),
      onOpenSample: vi.fn(),
    }),
  );
}

describe("EmptyCanvasHint", () => {
  it("renders the empty canvas first-step hint in Japanese", () => {
    setActiveLocale("ja");

    const html = renderHint();

    expect(html).toContain('data-ui-region="empty-canvas-hint"');
    expect(html).toContain("最初の1枚から始める");
    expect(html).toContain("正しさはあとで見直せます");
    expect(html).toContain("曖昧なまま置いておいて大丈夫です");
    expect(html).toContain("最初のカードを書く");
    expect(html).toContain("サンプルを見る");
  });

  it("renders stable English copy", () => {
    setActiveLocale("en");

    const html = renderHint();

    expect(html).toContain("Start with one card");
    expect(html).toContain("Correctness can wait");
    expect(html).toContain("Write first card");
    expect(html).toContain("View sample");
  });
});
