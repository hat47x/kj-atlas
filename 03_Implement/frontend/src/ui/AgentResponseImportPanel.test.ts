import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { AgentResponseImportPanel } from "./AgentResponseImportPanel";

function buildProps(overrides: Partial<React.ComponentProps<typeof AgentResponseImportPanel>> = {}) {
  return {
    isOpen: true,
    onClose: vi.fn(),
    triggerRef: { current: null },
    pastedText: "",
    onPastedTextChange: vi.fn(),
    mode: "lenient" as const,
    onModeChange: vi.fn(),
    onParse: vi.fn(),
    parseErrors: [],
    parseWarnings: [],
    reviews: [],
    onAdopt: vi.fn(),
    onReject: vi.fn(),
    onExportPatchFile: vi.fn(),
    ...overrides,
  };
}

describe("AgentResponseImportPanel accessibility", () => {
  it("leaves the paste textarea unmarked as invalid when there are no parse errors", () => {
    const html = renderToStaticMarkup(React.createElement(AgentResponseImportPanel, buildProps()));
    const textareaMatch = html.match(/<textarea[^>]*data-testid="agent-response-paste-input"[^>]*>/);

    expect(textareaMatch).not.toBeNull();
    expect(textareaMatch![0]).not.toContain("aria-invalid=\"true\"");
    expect(textareaMatch![0]).not.toMatch(/aria-describedby="[^"]+"/);
  });

  it("associates the paste textarea with the parse-error message via aria-describedby/aria-invalid", () => {
    const html = renderToStaticMarkup(
      React.createElement(AgentResponseImportPanel, buildProps({ parseErrors: ["payload.missing_taskId"] })),
    );
    const textareaMatch = html.match(/<textarea[^>]*data-testid="agent-response-paste-input"[^>]*>/);
    expect(textareaMatch).not.toBeNull();
    expect(textareaMatch![0]).toContain('aria-invalid="true"');

    const describedByMatch = textareaMatch![0].match(/aria-describedby="([^"]+)"/);
    expect(describedByMatch).not.toBeNull();

    const errorDivId = describedByMatch![1];
    expect(html).toContain(`id="${errorDivId}"`);
    expect(html).toContain("payload.missing_taskId");
  });
});
