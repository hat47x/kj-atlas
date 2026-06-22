import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { ShelfPanel } from "./ShelfPanel";
import { setActiveLocale } from "../i18n/translate";
import type { Card, ShelfEntry } from "../domain/types";

function makeCard(overrides: Partial<Card> = {}): Card {
  return { id: "c1", text: "test card", x: 0, y: 0, ...overrides };
}

function makeShelfEntry(overrides: Partial<ShelfEntry> = {}): ShelfEntry {
  return { cardId: "c1", shelvedAt: "2026-06-21T00:00:00Z", ...overrides };
}

describe("ShelfPanel", () => {
  it("renders nothing when shelf is empty", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, { cards: [], shelf: [] })
    );
    expect(html).toBe("");
  });

  it("shows shelved card with restore button", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "c1", text: "shelved thought" })];
    const shelf: ShelfEntry[] = [makeShelfEntry({ cardId: "c1" })];
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, { cards, shelf })
    );
    expect(html).toContain("shelved thought");
    expect(html).toContain("Restore");
  });

  it("shows shelf reason when provided", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "c1", text: "maybe later" })];
    const shelf: ShelfEntry[] = [
      makeShelfEntry({ cardId: "c1", reason: "revisit after review" }),
    ];
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, { cards, shelf })
    );
    expect(html).toContain("revisit after review");
  });

  it("disables restore in read-only mode", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, {
        cards: [makeCard()],
        shelf: [makeShelfEntry()],
        isReadOnly: true,
        onRestoreCard: () => {},
      })
    );

    expect(html).toContain("<button");
    expect(html).toContain("disabled");
  });

  it("filters out shelf entries for missing cards", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "keep", text: "kept card" })];
    const shelf: ShelfEntry[] = [
      makeShelfEntry({ cardId: "keep" }),
      makeShelfEntry({ cardId: "missing" }),
    ];
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, { cards, shelf })
    );
    expect(html).toContain("kept card");
    expect(html).not.toContain("missing");
  });

  it("renders focusable card text", () => {
    setActiveLocale("en");
    const cards: Card[] = [makeCard({ id: "c1", text: "focus me" })];
    const shelf: ShelfEntry[] = [makeShelfEntry({ cardId: "c1" })];
    const html = renderToStaticMarkup(
      React.createElement(ShelfPanel, {
        cards,
        shelf,
        onFocusCard: () => {},
      })
    );
    expect(html).toContain("focus me");
  });
});
