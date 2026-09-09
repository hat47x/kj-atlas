// @vitest-environment happy-dom

import React, { act } from "react";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRoot, type Root } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { InquiryEndConfirmationDialog } from "./InquiryEndConfirmationDialog";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

async function mountInquiryEndDialog(
  props: Parameters<typeof InquiryEndConfirmationDialog>[0],
): Promise<{ container: HTMLElement; root: Root }> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(InquiryEndConfirmationDialog, props));
  });
  return { container, root };
}

function dispatchKey(target: Element, key: string, shiftKey = false): KeyboardEvent {
  const event = new KeyboardEvent("keydown", {
    key,
    shiftKey,
    bubbles: true,
    cancelable: true,
  });
  target.dispatchEvent(event);
  return event;
}

afterEach(async () => {
  while (roots.length > 0) {
    const root = roots.pop();
    if (root) {
      await act(async () => root.unmount());
    }
  }
  document.body.replaceChildren();
  setActiveLocale("ja");
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("inquiry end confirmation dialog (DOMAIN-W-ITERATION-01 AC-13)", () => {
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

  it("defaults focus to cancel, maps Escape to cancel, and traps Tab focus", async () => {
    const onDecision = vi.fn();
    const { container } = await mountInquiryEndDialog({ onDecision });
    const dialog = container.querySelector('[role="alertdialog"]');
    const buttons = [...container.querySelectorAll<HTMLButtonElement>("button")];
    expect(dialog).not.toBeNull();
    expect(buttons).toHaveLength(3);
    if (!dialog || buttons.length !== 3) {
      throw new Error("inquiry end dialog did not render the expected controls");
    }
    const [cancelButton, discardButton, saveButton] = buttons;
    expect(document.activeElement).toBe(cancelButton);

    saveButton?.focus();
    await act(async () => {
      const tab = dispatchKey(saveButton!, "Tab");
      expect(tab.defaultPrevented).toBe(true);
    });
    expect(document.activeElement).toBe(cancelButton);

    cancelButton?.focus();
    await act(async () => {
      const reverseTab = dispatchKey(cancelButton!, "Tab", true);
      expect(reverseTab.defaultPrevented).toBe(true);
    });
    expect(document.activeElement).toBe(saveButton);

    await act(async () => {
      const escape = dispatchKey(dialog, "Escape");
      expect(escape.defaultPrevented).toBe(true);
    });
    expect(onDecision).toHaveBeenCalledTimes(1);
    expect(onDecision).toHaveBeenLastCalledWith("cancel");
    expect(discardButton?.disabled).toBe(false);
  });

  it("focuses processing status, disables decisions, and ignores Escape while processing", async () => {
    const onDecision = vi.fn();
    const { container, root } = await mountInquiryEndDialog({ onDecision });
    expect(document.activeElement?.textContent).toContain("続ける");

    await act(async () => {
      root.render(React.createElement(InquiryEndConfirmationDialog, {
        isProcessing: true,
        onDecision,
      }));
    });

    const dialog = container.querySelector('[role="alertdialog"]');
    const status = container.querySelector<HTMLElement>('[role="status"]');
    const buttons = [...container.querySelectorAll<HTMLButtonElement>("button")];
    expect(dialog).not.toBeNull();
    expect(status).not.toBeNull();
    expect(buttons).toHaveLength(3);
    expect(buttons.every((button) => button.disabled)).toBe(true);
    expect(document.activeElement).toBe(status);
    if (!dialog) {
      throw new Error("inquiry end dialog was not rendered while processing");
    }

    const escape = dispatchKey(dialog, "Escape");
    expect(escape.defaultPrevented).toBe(false);
    expect(onDecision).not.toHaveBeenCalled();
  });

  it("dispatches explicit button decisions", async () => {
    const onDecision = vi.fn();
    const { container } = await mountInquiryEndDialog({ onDecision });
    const buttons = [...container.querySelectorAll<HTMLButtonElement>("button")];
    expect(buttons).toHaveLength(3);

    for (const [button, decision] of [
      [buttons[0], "cancel"],
      [buttons[1], "discard"],
      [buttons[2], "save"],
    ] as const) {
      await act(async () => button?.click());
      expect(onDecision).toHaveBeenLastCalledWith(decision);
    }
    expect(onDecision).toHaveBeenCalledTimes(3);
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
