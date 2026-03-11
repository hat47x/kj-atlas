import type { ReactNode } from "react";

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
        <div style={TITLE_STYLE}>A2-1 Candidate comparison</div>
        <div style={DESCRIPTION_STYLE}>Collect and compare merge/layout candidates before any commit.</div>
        {candidateComparison}
      </section>
      <section style={SECTION_STYLE}>
        <div style={TITLE_STYLE}>A2-2 Critique input</div>
        <div style={DESCRIPTION_STYLE}>Capture critique and re-suggest iteratively while keeping human final approval.</div>
        {critiqueInput}
      </section>
      <section style={SECTION_STYLE}>
        <div style={TITLE_STYLE}>A2-3 Diff visualization</div>
        <div style={DESCRIPTION_STYLE}>Review deterministic diffs before apply/discard to keep the workflow reversible.</div>
        {diffVisualization}
      </section>
    </>
  );
}
