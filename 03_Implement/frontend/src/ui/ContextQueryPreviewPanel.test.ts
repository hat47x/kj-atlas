import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { ContextQueryPreviewPanel } from "./ContextQueryPreviewPanel";
import { buildQueryPreviewState, type ContextQueryDraft } from "../domain/context/query_preview";
import { setActiveLocale } from "../i18n/translate";

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

afterEach(() => {
  setActiveLocale("ja");
});

describe("ContextQueryPreviewPanel", () => {
  it("renders user-facing English labels instead of internal contract values", () => {
    setActiveLocale("en");
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

    expect(html).toContain("Review context search");
    expect(html).toContain("query ID: q-ce1-ui");
    expect(html).toContain("search target: Entire document");
    expect(html).toContain("review status: Reviewed content only");
    expect(html).toContain("safe mode: Strict");
    expect(html).toContain("Create context information");
    expect(html).toContain("Context information is ready to create.");
    expect(html).toContain("latest result ID: hash-ui-001");
    expect(html).toContain("exclusion reason: Unreviewed content excluded");
    expect(html).not.toContain("reviewedOnly");
    expect(html).not.toContain("unreviewed_filtered");
  });

  it("shows blockers and disables submit when previewConfirmed is false", () => {
    setActiveLocale("en");
    const draft = buildDraft({ previewConfirmed: false });
    const html = renderToStaticMarkup(
      React.createElement(ContextQueryPreviewPanel, {
        draft,
        previewState: buildQueryPreviewState(draft),
        onPreviewConfirmedChange: vi.fn(),
        onSubmit: vi.fn(),
      }),
    );

    expect(html).toContain("Confirm that you reviewed the search conditions.");
    expect(html).toContain('data-testid="ce1-query-preview-submit"');
    expect(html).toContain("disabled");
    expect(html).toContain("Cannot create context information: Confirm that you reviewed the search conditions.");
    expect(html).toContain('title="Confirm that you reviewed the search conditions."');
    expect(html).not.toContain("previewConfirmed");
  });

  it("shows safeMode guard when includeUnreviewed is selected", () => {
    setActiveLocale("en");
    const draft = buildDraft({ reviewFilter: "includeUnreviewed" });
    const html = renderToStaticMarkup(
      React.createElement(ContextQueryPreviewPanel, {
        draft,
        previewState: buildQueryPreviewState(draft),
        onPreviewConfirmedChange: vi.fn(),
        onSubmit: vi.fn(),
      }),
    );

    expect(html).toContain("Safe mode requires the search to use reviewed content only.");
    expect(html).toContain("review status: Include unreviewed content");
    expect(html).not.toContain("reviewFilter");
  });

  it("uses plain Japanese labels and actionable blockers", () => {
    setActiveLocale("ja");
    const draft = buildDraft({ reviewFilter: "includeUnreviewed" });
    const html = renderToStaticMarkup(
      React.createElement(ContextQueryPreviewPanel, {
        draft,
        previewState: buildQueryPreviewState(draft),
        latestBundleHash: "hash-ui-002",
        excludedReason: ["unreviewed_filtered"],
        onPreviewConfirmedChange: vi.fn(),
        onSubmit: vi.fn(),
      }),
    );

    expect(html).toContain("コンテキスト検索の送信前確認");
    expect(html).toContain("検索対象: 文書全体");
    expect(html).toContain("対象とするレビュー状態: 未レビューを含む");
    expect(html).toContain("セーフモード: 厳格");
    expect(html).toContain("セーフモードが有効なため、レビュー済みの内容だけを対象にしてください。");
    expect(html).toContain("最新の生成結果ID: hash-ui-002");
    expect(html).toContain("除外理由: 未レビューの内容を除外");
    expect(html).not.toContain("includeUnreviewed");
    expect(html).not.toContain("unreviewed_filtered");
    expect(html).not.toContain("Mock");
  });
});
