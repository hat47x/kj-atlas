import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { ContextQueryPreviewPanel } from "./ContextQueryPreviewPanel";
import { buildQueryPreviewState, type ContextQueryDraft } from "../domain/context/query_preview";

function buildDraft(overrides: Partial<ContextQueryDraft> = {}): ContextQueryDraft {
  return {
    queryId: "q-ce1-ui",
    goal: "Draft proposal around evidence clusters",
    scope: "document",
    depth: 2,
    constraints: { tokenBudget: 2048 },
    reviewFilter: "reviewedOnly",
    safeModePolicy: "strict",
    outputMode: "proposal",
    previewConfirmed: true,
    ...overrides,
  };
}

describe("ContextQueryPreviewPanel", () => {
  it("renders CE1 query preview summary and mock bundle footer", () => {
    const draft = buildDraft();
    const html = renderToStaticMarkup(
      React.createElement(ContextQueryPreviewPanel, {
        draft,
        previewState: buildQueryPreviewState(draft),
        latestBundleHash: "hash-ui-001",
        excludedReason: ["unreviewed_filtered"],
        onPreviewConfirmedChange: vi.fn(),
        onSubmit: vi.fn(),
      }),
    );

    expect(html).toContain("CE1 Query Preview");
    expect(html).toContain("queryId: q-ce1-ui");
    expect(html).toContain("scope: document");
    expect(html).toContain("reviewFilter: reviewedOnly");
    expect(html).toContain("safeModePolicy: strict");
    expect(html).toContain("Submit Context Bundle (Mock)");
    expect(html).toContain("Query Preview gate passed.");
    expect(html).toContain("latest bundleHash: hash-ui-001");
    expect(html).toContain("excludedReason: unreviewed_filtered");
  });

  it("shows blockers and disables submit when previewConfirmed is false", () => {
    const draft = buildDraft({ previewConfirmed: false });
    const html = renderToStaticMarkup(
      React.createElement(ContextQueryPreviewPanel, {
        draft,
        previewState: buildQueryPreviewState(draft),
        onPreviewConfirmedChange: vi.fn(),
        onSubmit: vi.fn(),
      }),
    );

    expect(html).toContain("previewConfirmed must be true before submit");
    expect(html).toContain('data-testid="ce1-query-preview-submit"');
    expect(html).toContain("disabled");
  });
});
