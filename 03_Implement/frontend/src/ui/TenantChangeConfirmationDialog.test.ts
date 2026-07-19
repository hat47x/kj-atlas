import React from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { TenantChangeConfirmationDialog } from "./TenantChangeConfirmationDialog";

describe("tenant change confirmation dialog", () => {
  afterEach(() => setActiveLocale("ja"));

  it("offers save, discard, and cancel without exposing a tenant identifier", () => {
    const html = renderToStaticMarkup(React.createElement(
      TenantChangeConfirmationDialog,
      {
        requestedTenantDisplayName: "分析チーム",
        onDecision: vi.fn(),
      },
    ));

    expect(html).toContain('role="alertdialog"');
    expect(html).toContain('aria-modal="true"');
    expect(html).toContain("分析チーム");
    expect(html).toContain("保存して切り替え");
    expect(html).toContain("破棄して切り替え");
    expect(html).toContain("取消");
    expect(html).not.toContain("tenant-b");
  });

  it("disables every decision while processing and announces progress", () => {
    const html = renderToStaticMarkup(React.createElement(
      TenantChangeConfirmationDialog,
      {
        requestedTenantDisplayName: "Workspace B",
        isProcessing: true,
        onDecision: vi.fn(),
      },
    ));

    expect(html.match(/disabled/g)).toHaveLength(3);
    expect(html).toContain('role="status"');
    expect(html).toContain('aria-live="polite"');
  });

  it("keeps the same decision contract in English", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(
      TenantChangeConfirmationDialog,
      {
        requestedTenantDisplayName: "Workspace B",
        onDecision: vi.fn(),
      },
    ));

    expect(html).toContain("Save and switch");
    expect(html).toContain("Discard and switch");
    expect(html).toContain("Cancel");
  });

  it("defaults focus to cancel and maps Escape to the cancel decision", () => {
    const source = readFileSync(
      resolve(__dirname, "TenantChangeConfirmationDialog.tsx"),
      "utf8",
    );
    expect(source).toContain("cancelButtonRef.current?.focus()");
    expect(source).toContain('event.key === "Escape"');
    expect(source).toContain('onDecision("cancel")');
    expect(source).toContain('event.key !== "Tab"');
    expect(source).toContain('"button:not([disabled])"');
  });
});
