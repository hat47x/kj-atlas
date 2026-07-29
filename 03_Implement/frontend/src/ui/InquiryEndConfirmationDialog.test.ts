import React from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { InquiryEndConfirmationDialog } from "./InquiryEndConfirmationDialog";

describe("inquiry end confirmation dialog (DOMAIN-W-ITERATION-01 AC-13)", () => {
  afterEach(() => setActiveLocale("ja"));

  it("offers save, discard, and cancel as an alertdialog, matching A-1's pattern", () => {
    const html = renderToStaticMarkup(React.createElement(
      InquiryEndConfirmationDialog,
      { onDecision: vi.fn() },
    ));

    expect(html).toContain('role="alertdialog"');
    expect(html).toContain('aria-modal="true"');
    expect(html).toContain("保存して終了");
    expect(html).toContain("保存せず閉じる");
    expect(html).toContain("続ける");
  });

  it("disables every decision while processing and announces progress", () => {
    const html = renderToStaticMarkup(React.createElement(
      InquiryEndConfirmationDialog,
      { isProcessing: true, onDecision: vi.fn() },
    ));

    expect(html.match(/disabled/g)).toHaveLength(3);
    expect(html).toContain('role="status"');
    expect(html).toContain('aria-live="polite"');
  });

  it("keeps the same decision contract in English", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(
      InquiryEndConfirmationDialog,
      { onDecision: vi.fn() },
    ));

    expect(html).toContain("Save and end");
    expect(html).toContain("Close without saving");
    expect(html).toContain("Continue");
  });

  it("defaults focus to cancel and maps Escape to the cancel decision", () => {
    const source = readFileSync(
      resolve(__dirname, "InquiryEndConfirmationDialog.tsx"),
      "utf8",
    );
    expect(source).toContain("cancelButtonRef.current?.focus()");
    expect(source).toContain('event.key === "Escape"');
    expect(source).toContain('onDecision("cancel")');
    expect(source).toContain('event.key !== "Tab"');
    expect(source).toContain('"button:not([disabled])"');
  });

  it("never interpolates round/card content (SafeMode default ON by construction)", () => {
    const source = readFileSync(
      resolve(__dirname, "InquiryEndConfirmationDialog.tsx"),
      "utf8",
    );
    // Only static t(...) calls with no second (interpolation) argument.
    const tCalls = [...source.matchAll(/t\("inquiry_journey\.prototype\.[a-z_]+"\)/g)];
    expect(tCalls.length).toBeGreaterThan(0);
    expect(source).not.toMatch(/t\("inquiry_journey\.prototype\.[a-z_]+",\s*\{/);
  });
});
