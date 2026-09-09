// @vitest-environment happy-dom

import React, { act } from "react";
import { createRoot, type Root } from "react-dom/client";
import { afterAll, afterEach, describe, expect, it, vi } from "vitest";

import { setActiveLocale, t } from "../i18n/translate";
import { AgentTaskExportPanel } from "./AgentTaskExportPanel";

const roots: Root[] = [];
const actGlobal = globalThis as typeof globalThis & {
  IS_REACT_ACT_ENVIRONMENT?: boolean;
};
actGlobal.IS_REACT_ACT_ENVIRONMENT = true;

type Props = Parameters<typeof AgentTaskExportPanel>[0];

function baseProps(overrides: Partial<Props> = {}): Props {
  return {
    isOpen: true,
    onClose: vi.fn(),
    triggerRef: { current: null },
    safeMode: true,
    selectedCardCount: 0,
    selectedIslandCount: 0,
    taskKind: "free_analysis",
    onTaskKindChange: vi.fn(),
    desiredCount: 3,
    onDesiredCountChange: vi.fn(),
    includeUnreviewedDrafts: false,
    onIncludeUnreviewedDraftsChange: vi.fn(),
    includeSourceReferences: false,
    onIncludeSourceReferencesChange: vi.fn(),
    scopeConfirmed: false,
    onScopeConfirmedChange: vi.fn(),
    onCopyMarkdown: vi.fn(),
    onDownloadMarkdown: vi.fn(),
    onDownloadTaskJson: vi.fn(),
    ...overrides,
  };
}

async function mountAgentTaskPanel(
  props: Props,
): Promise<{ container: HTMLElement; root: Root }> {
  const container = document.createElement("div");
  document.body.append(container);
  const root = createRoot(container);
  roots.push(root);
  await act(async () => {
    root.render(React.createElement(AgentTaskExportPanel, props));
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

function labelByText(container: ParentNode, text: string): HTMLLabelElement | null {
  return [...container.querySelectorAll<HTMLLabelElement>("label")]
    .find((label) => label.textContent?.includes(text)) ?? null;
}

function buttonByText(container: ParentNode, text: string): HTMLButtonElement {
  const button = [...container.querySelectorAll<HTMLButtonElement>("button")]
    .find((candidate) => candidate.textContent === text);
  if (!button) {
    throw new Error(`button not found: ${text}`);
  }
  return button;
}

async function setInputValue(input: HTMLInputElement, value: string): Promise<void> {
  const nativeSetter = Object.getOwnPropertyDescriptor(
    HTMLInputElement.prototype,
    "value",
  )?.set;
  if (!nativeSetter) {
    throw new Error("native input value setter is unavailable");
  }
  await act(async () => {
    nativeSetter.call(input, value);
    input.dispatchEvent(new Event("input", { bubbles: true }));
  });
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

describe("AgentTaskExportPanel safety boundary", () => {
  it("keeps external export locked until a non-empty scope is explicitly confirmed", async () => {
    const onCopyMarkdown = vi.fn();
    const onDownloadMarkdown = vi.fn();
    const onDownloadTaskJson = vi.fn();
    const { container, root } = await mountAgentTaskPanel(baseProps({
      onCopyMarkdown,
      onDownloadMarkdown,
      onDownloadTaskJson,
    }));

    const scopeConfirmed = requiredElement<HTMLInputElement>(
      container,
      '[data-testid="agent-task-scope-confirmed"]',
    );
    const exportButtons = [
      buttonByText(container, t("agent_task_export.copy_task_sheet")),
      buttonByText(container, t("agent_task_export.download_task_sheet")),
      buttonByText(container, t("agent_task_export.download_task_json")),
    ];
    expect(scopeConfirmed.disabled).toBe(true);
    expect(exportButtons.every((button) => button.disabled)).toBe(true);

    await act(async () => {
      root.render(React.createElement(AgentTaskExportPanel, baseProps({
        selectedCardCount: 2,
        scopeConfirmed: false,
        onCopyMarkdown,
        onDownloadMarkdown,
        onDownloadTaskJson,
      })));
    });
    expect(scopeConfirmed.disabled).toBe(false);
    expect(exportButtons.every((button) => button.disabled)).toBe(true);

    await act(async () => {
      root.render(React.createElement(AgentTaskExportPanel, baseProps({
        selectedCardCount: 2,
        scopeConfirmed: true,
        onCopyMarkdown,
        onDownloadMarkdown,
        onDownloadTaskJson,
      })));
    });
    expect(exportButtons.every((button) => button.disabled === false)).toBe(true);

    await act(async () => {
      exportButtons.forEach((button) => button.click());
    });
    expect(onCopyMarkdown).toHaveBeenCalledTimes(1);
    expect(onDownloadMarkdown).toHaveBeenCalledTimes(1);
    expect(onDownloadTaskJson).toHaveBeenCalledTimes(1);
  });

  it("hides the unreviewed-draft opt-in in SafeMode and exposes it only outside SafeMode", async () => {
    const onIncludeUnreviewedDraftsChange = vi.fn();
    const { container, root } = await mountAgentTaskPanel(baseProps({
      safeMode: true,
      selectedIslandCount: 1,
      onIncludeUnreviewedDraftsChange,
    }));

    const unreviewedLabel = () => labelByText(
      container,
      t("agent_task_export.include_unreviewed_drafts"),
    );
    expect(unreviewedLabel()).toBeNull();
    expect(container.textContent).toContain(t("agent_task_export.safe_mode_note"));

    await act(async () => {
      root.render(React.createElement(AgentTaskExportPanel, baseProps({
        safeMode: false,
        selectedIslandCount: 1,
        onIncludeUnreviewedDraftsChange,
      })));
    });

    const label = unreviewedLabel();
    expect(label).not.toBeNull();
    const checkbox = label?.querySelector<HTMLInputElement>('input[type="checkbox"]');
    if (!checkbox) {
      throw new Error("unreviewed draft checkbox was not rendered outside SafeMode");
    }
    await act(async () => checkbox.click());
    expect(onIncludeUnreviewedDraftsChange).toHaveBeenCalledWith(true);
  });

  it("clamps desired count and forwards task/source/scope controls without broadening export scope", async () => {
    const onDesiredCountChange = vi.fn();
    const onTaskKindChange = vi.fn();
    const onIncludeSourceReferencesChange = vi.fn();
    const onScopeConfirmedChange = vi.fn();
    const { container } = await mountAgentTaskPanel(baseProps({
      safeMode: false,
      selectedCardCount: 1,
      onDesiredCountChange,
      onTaskKindChange,
      onIncludeSourceReferencesChange,
      onScopeConfirmedChange,
    }));

    const desiredCount = requiredElement<HTMLInputElement>(container, 'input[type="number"]');
    await setInputValue(desiredCount, "0");
    await setInputValue(desiredCount, "99");
    expect(onDesiredCountChange).toHaveBeenNthCalledWith(1, 1);
    expect(onDesiredCountChange).toHaveBeenNthCalledWith(2, 20);

    const taskKind = requiredElement<HTMLSelectElement>(
      container,
      '[data-testid="agent-task-kind-select"]',
    );
    await act(async () => {
      taskKind.value = "island_titles";
      taskKind.dispatchEvent(new Event("change", { bubbles: true }));
    });
    expect(onTaskKindChange).toHaveBeenCalledWith("island_titles");

    const sourceLabel = labelByText(container, t("agent_task_export.include_source_references"));
    const sourceCheckbox = sourceLabel?.querySelector<HTMLInputElement>('input[type="checkbox"]');
    if (!sourceCheckbox) {
      throw new Error("source-reference checkbox was not rendered");
    }
    await act(async () => sourceCheckbox.click());
    expect(onIncludeSourceReferencesChange).toHaveBeenCalledWith(true);

    const scopeConfirmed = requiredElement<HTMLInputElement>(
      container,
      '[data-testid="agent-task-scope-confirmed"]',
    );
    await act(async () => scopeConfirmed.click());
    expect(onScopeConfirmedChange).toHaveBeenCalledWith(true);
  });
});
