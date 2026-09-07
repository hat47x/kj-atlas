// @vitest-environment happy-dom

import React, { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { renderToStaticMarkup } from "react-dom/server";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale } from "../i18n/translate";
import { TenantChangeConfirmationDialog } from "./TenantChangeConfirmationDialog";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

async function mountTenantChangeDialog(
  props: Parameters<typeof TenantChangeConfirmationDialog>[0],
): Promise<{ container: HTMLElement; root: Root }> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(TenantChangeConfirmationDialog, props));
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

describe("tenant change confirmation dialog", () => {
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

  it("executes cancel-by-default, Escape cancellation, and the focus trap", async () => {
    const onDecision = vi.fn();
    const { container } = await mountTenantChangeDialog({
      requestedTenantDisplayName: "Workspace B",
      onDecision,
    });
    const dialog = container.querySelector('[role="alertdialog"]');
    const buttons = [...container.querySelectorAll<HTMLButtonElement>("button")];
    expect(dialog).not.toBeNull();
    expect(buttons).toHaveLength(3);
    if (!dialog || buttons.length !== 3) {
      throw new Error("tenant change dialog did not render the expected controls");
    }
    const [cancelButton, discardButton, saveButton] = buttons;
    expect(document.activeElement).toBe(cancelButton);

    await act(async () => {
      const escape = dispatchKey(dialog, "Escape");
      expect(escape.defaultPrevented).toBe(true);
    });
    expect(onDecision).toHaveBeenCalledTimes(1);
    expect(onDecision).toHaveBeenLastCalledWith("cancel");

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

    expect(discardButton?.disabled).toBe(false);
  });

  it("disables decisions, focuses processing status, and ignores Escape while processing", async () => {
    const onDecision = vi.fn();
    const { container, root } = await mountTenantChangeDialog({
      requestedTenantDisplayName: "Workspace B",
      onDecision,
    });
    expect(document.activeElement?.textContent).toContain("取消");

    await act(async () => {
      root.render(React.createElement(TenantChangeConfirmationDialog, {
        requestedTenantDisplayName: "Workspace B",
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
      throw new Error("tenant change dialog was not rendered while processing");
    }

    const escape = dispatchKey(dialog, "Escape");
    expect(escape.defaultPrevented).toBe(false);
    expect(onDecision).not.toHaveBeenCalled();
  });

  it("dispatches the explicit button decisions", async () => {
    const onDecision = vi.fn();
    const { container } = await mountTenantChangeDialog({
      requestedTenantDisplayName: "Workspace B",
      onDecision,
    });
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
});
