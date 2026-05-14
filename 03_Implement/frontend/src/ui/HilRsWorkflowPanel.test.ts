import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { HilRsWorkflowPanel } from "./HilRsWorkflowPanel";
import { t } from "../i18n/translate";

describe("HilRsWorkflowPanel", () => {
  it("renders three separated workflow sections for A2", () => {
    const html = renderToStaticMarkup(
      React.createElement(HilRsWorkflowPanel, {
        candidateComparison: React.createElement("div", null, "candidate-slot"),
        critiqueInput: React.createElement("div", null, "critique-slot"),
        diffVisualization: React.createElement("div", null, "diff-slot"),
      }),
    );

    expect(html).toContain(t("hil_rs_workflow.candidate.title"));
    expect(html).toContain(t("hil_rs_workflow.critique.title"));
    expect(html).toContain(t("hil_rs_workflow.diff.title"));
    expect(html).toContain("candidate-slot");
    expect(html).toContain("critique-slot");
    expect(html).toContain("diff-slot");
    expect(html).toContain(t("hil_rs_workflow.diff.description"));
  });
});
