// @vitest-environment happy-dom

import React, { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { DiagnosticsBundlePanel } from "./DiagnosticsBundlePanel";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

type Props = Parameters<typeof DiagnosticsBundlePanel>[0];

function baseProps(overrides: Partial<Props> = {}): Props {
  return {
    isOpen: true,
    onClose: vi.fn(),
    triggerRef: { current: null },
    safeMode: true,
    providerType: "local",
    documentSummary: {
      version: 3,
      updatedAt: "2026-09-09T12:00:00Z",
      cardCount: 12,
      islandCount: 4,
      edgeCount: 9,
    },
    ...overrides,
  };
}

async function mountDiagnosticsPanel(
  props: Props,
): Promise<{ container: HTMLElement; root: Root }> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(DiagnosticsBundlePanel, props));
  });
  return { container, root };
}

function requiredElement<T extends Element>(container: ParentNode, selector: string): T {
  const element = container.querySelector<T>(selector);
  if (!element) {
    throw new Error(`missing element: ${selector}`);
  }
  return element;
}

async function changeValue(
  element: HTMLInputElement | HTMLSelectElement,
  value: string,
): Promise<void> {
  await act(async () => {
    element.value = value;
    const eventName = element instanceof HTMLInputElement ? "input" : "change";
    element.dispatchEvent(new Event(eventName, { bubbles: true }));
  });
}

function dispatchKey(target: Element, key: string): KeyboardEvent {
  const event = new KeyboardEvent("keydown", {
    key,
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
  vi.restoreAllMocks();
});

afterAll(() => {
  delete actGlobal.IS_REACT_ACT_ENVIRONMENT;
});

describe("DiagnosticsBundlePanel runtime state", () => {
  it("requires classification, sanitizes HTTP status, and generates the allowlisted preview", async () => {
    const { container } = await mountDiagnosticsPanel(baseProps());
    const classification = requiredElement<HTMLSelectElement>(
      container,
      '[data-testid="diagnostics-bundle-classification-select"]',
    );
    const httpStatus = requiredElement<HTMLInputElement>(
      container,
      '[data-testid="diagnostics-bundle-http-status-input"]',
    );
    const generate = requiredElement<HTMLButtonElement>(
      container,
      '[data-testid="diagnostics-bundle-generate"]',
    );

    expect(generate.disabled).toBe(true);
    expect(container.querySelector('[data-testid="diagnostics-bundle-preview-text"]')).toBeNull();

    await changeValue(httpStatus, "5x0 4");
    expect(httpStatus.value).toBe("504");
    await changeValue(classification, "SAVE-FAILURE");
    expect(generate.disabled).toBe(false);

    await act(async () => generate.click());

    const preview = requiredElement<HTMLTextAreaElement>(
      container,
      '[data-testid="diagnostics-bundle-preview-text"]',
    );
    const bundle = JSON.parse(preview.value) as Record<string, any>;
    expect(bundle.schemaVersion).toBe("diag-bundle.v1");
    expect(bundle.incident).toEqual({
      classificationCode: "SAVE-FAILURE",
      httpStatus: 504,
    });
    expect(bundle.runtime).toEqual({ safeMode: true, providerType: "local" });
    expect(bundle.document).toEqual({
      version: 3,
      updatedAt: "2026-09-09T12:00:00Z",
      counts: { cards: 12, islands: 4, edges: 9 },
    });
  });

  it("invalidates an existing preview when the classification changes", async () => {
    const { container } = await mountDiagnosticsPanel(baseProps());
    const classification = requiredElement<HTMLSelectElement>(
      container,
      '[data-testid="diagnostics-bundle-classification-select"]',
    );
    const generate = requiredElement<HTMLButtonElement>(
      container,
      '[data-testid="diagnostics-bundle-generate"]',
    );

    await changeValue(classification, "API-UNAVAILABLE");
    await act(async () => generate.click());
    expect(container.querySelector('[data-testid="diagnostics-bundle-preview-text"]')).not.toBeNull();
    expect(container.querySelector('[data-testid="diagnostics-bundle-copy"]')).not.toBeNull();

    await changeValue(classification, "IMPORT-VALIDATION");

    expect(container.querySelector('[data-testid="diagnostics-bundle-preview-text"]')).toBeNull();
    expect(container.querySelector('[data-testid="diagnostics-bundle-copy"]')).toBeNull();
    expect(generate.disabled).toBe(false);
  });

  it("Escape discards the in-memory preview, closes, and restores trigger focus", async () => {
    const trigger = document.createElement("button");
    document.body.append(trigger);
    const onClose = vi.fn();
    const { container } = await mountDiagnosticsPanel(baseProps({
      triggerRef: { current: trigger },
      onClose,
    }));
    const dialog = requiredElement<HTMLElement>(container, '[role="dialog"]');
    const classification = requiredElement<HTMLSelectElement>(
      container,
      '[data-testid="diagnostics-bundle-classification-select"]',
    );
    const generate = requiredElement<HTMLButtonElement>(
      container,
      '[data-testid="diagnostics-bundle-generate"]',
    );

    await changeValue(classification, "WEB-ENTRY");
    await act(async () => generate.click());
    expect(container.querySelector('[data-testid="diagnostics-bundle-preview-text"]')).not.toBeNull();

    await act(async () => {
      const escape = dispatchKey(dialog, "Escape");
      expect(escape.defaultPrevented).toBe(true);
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(container.querySelector('[data-testid="diagnostics-bundle-preview-text"]')).toBeNull();
    expect(document.activeElement).toBe(trigger);
  });
});
