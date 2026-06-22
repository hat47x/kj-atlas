import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { HilRsWorkflowPanel } from "./HilRsWorkflowPanel";
import { setActiveLocale, t } from "../i18n/translate";

describe("HilRsWorkflowPanel", () => {
  it("renders three separated workflow sections for A2", () => {
    setActiveLocale("ja");
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
    expect(html).toContain("候補を比較");
    expect(html).toContain("違和感を記録");
    expect(html).toContain("変更内容を確認");
    expect(html).not.toContain("A2-1");
    expect(html).not.toContain("A2-2");
    expect(html).not.toContain("A2-3");
  });
});
