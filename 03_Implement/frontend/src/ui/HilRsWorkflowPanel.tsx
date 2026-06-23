import type { ReactNode } from "react";
import { t } from "../i18n/translate";

type HilRsWorkflowPanelProps = {
  candidateComparison: ReactNode;
  critiqueInput: ReactNode;
  diffVisualization: ReactNode;
};

const SECTION_STYLE = {
  border: "1px solid #e2e8f0",
  borderRadius: 8,
  padding: 8,
  marginBottom: 12,
  backgroundColor: "#f8fafc",
} as const;

const TITLE_STYLE = {
  fontSize: 12,
  fontWeight: 700,
  color: "#0f172a",
  marginBottom: 6,
} as const;

const DESCRIPTION_STYLE = {
  fontSize: 11,
  color: "#475569",
  marginBottom: 8,
} as const;

export function HilRsWorkflowPanel({ candidateComparison, critiqueInput, diffVisualization }: HilRsWorkflowPanelProps) {
  return (
    <>
      <section style={SECTION_STYLE}>
        <div style={TITLE_STYLE}>{t("hil_rs_workflow.candidate.title")}</div>
        <div style={DESCRIPTION_STYLE}>{t("hil_rs_workflow.candidate.description")}</div>
        {candidateComparison}
      </section>
      <section
        data-domain-workflow="critique-reproposal"
        aria-labelledby="critique-reproposal-title"
        tabIndex={-1}
        style={SECTION_STYLE}
      >
        <div id="critique-reproposal-title" style={TITLE_STYLE}>{t("hil_rs_workflow.critique.title")}</div>
        <div style={DESCRIPTION_STYLE}>{t("hil_rs_workflow.critique.description")}</div>
        {critiqueInput}
      </section>
      <section style={SECTION_STYLE}>
        <div style={TITLE_STYLE}>{t("hil_rs_workflow.diff.title")}</div>
        <div style={DESCRIPTION_STYLE}>{t("hil_rs_workflow.diff.description")}</div>
        {diffVisualization}
      </section>
    </>
  );
}
