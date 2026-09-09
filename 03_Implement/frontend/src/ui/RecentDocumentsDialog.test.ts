import React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import type { DocumentListItem } from "../api/client";
import { RecentDocumentsDialog } from "./RecentDocumentsDialog";

type Props = Parameters<typeof RecentDocumentsDialog>[0];

function baseProps(overrides: Partial<Props> = {}): Props {
  return {
    isOpen: true,
    onClose: vi.fn(),
    triggerRef: { current: null },
    recentDocumentIds: [],
    selectedRecentDocumentId: "",
    onSelectedRecentDocumentChange: vi.fn(),
    onOpenRecent: vi.fn(),
    isLoading: false,
    activeDocumentId: "active-doc",
    documents: null,
    isCanvasListLoading: false,
    myDocumentsOnly: false,
    onMyDocumentsOnlyChange: vi.fn(),
    onArchiveDocument: vi.fn(),
    onUnarchiveDocument: vi.fn(),
    isArchiving: false,
    ...overrides,
  };
}

function serverDocuments(): DocumentListItem[] {
  return [{
    id: "server-doc",
    title: "Server document",
    lifecycle_state: "active",
  } as DocumentListItem];
}

afterEach(() => {
  setActiveLocale("ja");
});

describe("RecentDocumentsDialog server document list", () => {
  it("offers Open when only the server list has document choices", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(
      RecentDocumentsDialog,
      baseProps({
        documents: serverDocuments(),
        recentDocumentIds: [],
        selectedRecentDocumentId: "server-doc",
      }),
    ));

    expect(html).toContain("Server document (server-doc)");
    expect(html).toMatch(/<button[^>]*>Open<\/button>/);
    expect(html).not.toMatch(/<button[^>]*disabled[^>]*>Open<\/button>/);
  });

  it("does not offer Open when neither server nor recent choices exist", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(
      RecentDocumentsDialog,
      baseProps(),
    ));

    expect(html).not.toMatch(/<button[^>]*>Open<\/button>/);
  });

  it("keeps Open disabled for the active document", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(
      RecentDocumentsDialog,
      baseProps({
        documents: serverDocuments(),
        selectedRecentDocumentId: "active-doc",
      }),
    ));

    expect(html).toMatch(/<button[^>]*disabled[^>]*>Open<\/button>/);
  });
});
