import type { NarrativeIssue, NarrativeIssueReference } from "../api/client";

type NarrativesPanelProps = {
  narrativeText: string;
  onNarrativeTextChange: (value: string) => void;
  onCheckConsistency: () => void;
  isChecking: boolean;
  errorMessage: string | null;
  issues: NarrativeIssue[];
  onReferenceClick: (reference: NarrativeIssueReference) => void;
};

const severityColorMap: Record<NarrativeIssue["severity"], string> = {
  info: "#0369a1",
  warn: "#b45309",
  error: "#b91c1c",
};

export function NarrativesPanel({
  narrativeText,
  onNarrativeTextChange,
  onCheckConsistency,
  isChecking,
  errorMessage,
  issues,
  onReferenceClick,
}: NarrativesPanelProps) {
  return (
    <section style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
      <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>Narrative (draft)</div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>
        AI checks are advisory and unreviewed. Treat results as suggestions for human review.
      </div>
      <textarea
        value={narrativeText}
        onChange={(event) => {
          onNarrativeTextChange(event.target.value);
        }}
        rows={6}
        placeholder="Write or paste your narrative draft here"
        style={{ width: "100%", resize: "vertical", marginBottom: 8 }}
      />
      <button
        type="button"
        onClick={onCheckConsistency}
        disabled={isChecking || narrativeText.trim().length === 0}
        style={{ cursor: isChecking || narrativeText.trim().length === 0 ? "not-allowed" : "pointer", marginBottom: 8 }}
      >
        {isChecking ? "Checking..." : "Check consistency"}
      </button>
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Consistency issues (AI-generated, unreviewed)</div>
      {issues.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>No issues returned.</div>
      ) : (
        <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 8 }}>
          {issues.map((issue, index) => (
            <li key={`${issue.severity}-${index}`} style={{ fontSize: 12, color: "#1e293b" }}>
              <div>
                <span style={{ color: severityColorMap[issue.severity], fontWeight: 700, marginRight: 8 }}>[{issue.severity}]</span>
                {issue.message}
              </div>
              {issue.references && issue.references.length > 0 ? (
                <div style={{ marginTop: 4, display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {issue.references.map((reference) => (
                    <button
                      key={`${reference.kind}:${reference.id}`}
                      type="button"
                      onClick={() => {
                        onReferenceClick(reference);
                      }}
                      style={{ fontSize: 11, cursor: "pointer" }}
                    >
                      Focus {reference.kind}:{reference.id}
                    </button>
                  ))}
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
