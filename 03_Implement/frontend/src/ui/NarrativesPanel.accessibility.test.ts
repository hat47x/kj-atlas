import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import type { DocumentV1, Narrative } from "../domain/types";
import { setActiveLocale } from "../i18n/translate";
import { NarrativesPanel } from "./NarrativesPanel";

const documentFixture: DocumentV1 = {
  version: 1,
  id: "doc-a11y-narrative",
  createdAt: "2026-06-22T00:00:00.000Z",
  updatedAt: "2026-06-22T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [{ id: "card-1", text: "Grounded source", x: 100, y: 100 }],
  edges: [],
  islands: [],
};

const narrativeFixture: Narrative = {
  id: "narrative-1",
  title: "Review narrative",
  text: "Draft explanation",
  createdAt: "2026-06-22T00:00:00.000Z",
  basedOnReadingOrder: ["card-1"],
  reviewed: false,
  checks: [
    {
      id: "check-1",
      kind: "consistency",
      createdAt: "2026-06-22T00:00:00.000Z",
      issues: [{ severity: "warn", message: "Check this statement" }],
    },
  ],
};

function renderPanel(overrides: Partial<React.ComponentProps<typeof NarrativesPanel>> = {}): string {
  const props: React.ComponentProps<typeof NarrativesPanel> = {
    narrativeText: "Draft explanation",
    onNarrativeTextChange: vi.fn(),
    onCheckConsistency: vi.fn(),
    onGenerateFromReadingOrder: vi.fn(),
    isChecking: false,
    isGenerating: false,
    errorMessage: null,
    generationErrorMessage: null,
    issues: [],
    generatedNarratives: [narrativeFixture],
    onReferenceClick: vi.fn(),
    document: documentFixture,
    hideSourceCards: false,
    safeMode: true,
    onFocusItem: vi.fn(),
    ...overrides,
  };

  return renderToStaticMarkup(React.createElement(NarrativesPanel, props));
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("NarrativesPanel accessibility (UQ-2)", () => {
  it("names the panel and narrative input", () => {
    setActiveLocale("en");
    const html = renderPanel();

    expect(html).toMatch(/<section aria-labelledby="[^"]+"/);
    expect(html).toMatch(/<div id="[^"]+"[^>]*>Narrative \(draft\)<\/div>/);
    expect(html).toContain('aria-label="Narrative (draft)"');
  });

  it("exposes selected narratives and collapsed consistency checks", () => {
    setActiveLocale("en");
    const html = renderPanel();

    expect(html).toContain('aria-pressed="true"');
    expect(html).toContain('aria-expanded="false"');
  });

  it("announces consistency and generation failures as alerts", () => {
    const html = renderPanel({
      errorMessage: "Consistency check failed",
      generationErrorMessage: "Generation failed",
    });

    expect(html.match(/role="alert"/g)).toHaveLength(2);
    expect(html).toContain("Consistency check failed");
    expect(html).toContain("Generation failed");
  });
});
