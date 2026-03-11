import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { HilRsWorkflowPanel } from "./HilRsWorkflowPanel";

describe("HilRsWorkflowPanel", () => {
  it("renders three separated workflow sections for A2", () => {
    const html = renderToStaticMarkup(
      React.createElement(HilRsWorkflowPanel, {
        candidateComparison: React.createElement("div", null, "candidate-slot"),
        critiqueInput: React.createElement("div", null, "critique-slot"),
        diffVisualization: React.createElement("div", null, "diff-slot"),
      }),
    );

    expect(html).toContain("A2-1 Candidate comparison");
    expect(html).toContain("A2-2 Critique input");
    expect(html).toContain("A2-3 Diff visualization");
    expect(html).toContain("candidate-slot");
    expect(html).toContain("critique-slot");
    expect(html).toContain("diff-slot");
  });
});
