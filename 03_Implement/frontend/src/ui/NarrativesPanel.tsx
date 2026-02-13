import { useMemo, useState } from "react";

import type { NarrativeIssue, NarrativeIssueReference } from "../api/client";
import type { NarrativeCheck, NarrativeEntry } from "../domain/types";
import {
  buildNarrativeHtml,
  buildNarrativeMarkdown,
  downloadTextFile,
  type ReadingOrderSnippetMap,
} from "../export/narrative_export";

type NarrativesPanelProps = {
  narrativeText: string;
  onNarrativeTextChange: (value: string) => void;
  onCheckConsistency: () => void;
  onGenerateFromReadingOrder: () => void;
  isChecking: boolean;
  isGenerating: boolean;
  errorMessage: string | null;
  generationErrorMessage: string | null;
  issues: NarrativeIssue[];
  generatedNarratives: NarrativeEntry[];
  selectedNarrativeId: string | null;
  onSelectNarrativeId: (id: string) => void;
  onReferenceClick: (reference: NarrativeIssueReference) => void;
  readingOrderSnippets?: ReadingOrderSnippetMap;
};

const severityColorMap: Record<NarrativeIssue["severity"], string> = {
  info: "#0369a1",
  warn: "#b45309",
  error: "#b91c1c",
};

function sanitizeFileStem(value: string): string {
  const trimmed = value.trim().toLowerCase();
  const normalized = trimmed.length > 0 ? trimmed : "narrative";
  const sanitized = normalized.replaceAll(/[^a-z0-9-_]+/g, "-").replaceAll(/^-+|-+$/g, "");
  return sanitized.length > 0 ? sanitized : "narrative";
}

function countBySeverity(issues: NarrativeIssue[]): Record<NarrativeIssue["severity"], number> {
  return issues.reduce(
    (counts, issue) => {
      counts[issue.severity] += 1;
      return counts;
    },
    { info: 0, warn: 0, error: 0 } as Record<NarrativeIssue["severity"], number>
  );
}

function formatTimestamp(value: string): string {
  const timestamp = Date.parse(value);
  if (Number.isNaN(timestamp)) {
    return value;
  }

  return new Date(timestamp).toLocaleString();
}

function CheckIssueList({ issues, onReferenceClick }: { issues: NarrativeIssue[]; onReferenceClick: (reference: NarrativeIssueReference) => void }) {
  return (
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
  );
}

export function NarrativesPanel({
  narrativeText,
  onNarrativeTextChange,
  onCheckConsistency,
  onGenerateFromReadingOrder,
  isChecking,
  isGenerating,
  errorMessage,
  generationErrorMessage,
  issues,
  generatedNarratives,
  selectedNarrativeId,
  onSelectNarrativeId,
  onReferenceClick,
  readingOrderSnippets = {},
}: NarrativesPanelProps) {
  const [expandedCheckIds, setExpandedCheckIds] = useState<Set<string>>(new Set());

  const selectedNarrative = useMemo(() => {
    if (generatedNarratives.length === 0) {
      return null;
    }

    if (selectedNarrativeId) {
      return generatedNarratives.find((entry) => entry.id === selectedNarrativeId) ?? generatedNarratives[0];
    }

    return generatedNarratives[0];
  }, [generatedNarratives, selectedNarrativeId]);

  const handleExportMarkdown = () => {
    if (!selectedNarrative) {
      return;
    }

    const content = buildNarrativeMarkdown(selectedNarrative, readingOrderSnippets);
    const fileStem = sanitizeFileStem(selectedNarrative.title || selectedNarrative.id);
    downloadTextFile(`${fileStem}.md`, "text/markdown", content);
  };

  const handleExportHtml = () => {
    if (!selectedNarrative) {
      return;
    }

    const content = buildNarrativeHtml(selectedNarrative, readingOrderSnippets);
    const fileStem = sanitizeFileStem(selectedNarrative.title || selectedNarrative.id);
    downloadTextFile(`${fileStem}.html`, "text/html", content);
  };

  const selectedChecks = selectedNarrative?.checks ?? [];

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
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 8 }}>
        <button
          type="button"
          onClick={onCheckConsistency}
          disabled={isChecking || narrativeText.trim().length === 0}
          style={{ cursor: isChecking || narrativeText.trim().length === 0 ? "not-allowed" : "pointer" }}
        >
          {isChecking ? "Checking..." : "Check consistency"}
        </button>
        <button
          type="button"
          onClick={onGenerateFromReadingOrder}
          disabled={isGenerating}
          style={{ cursor: isGenerating ? "not-allowed" : "pointer" }}
        >
          {isGenerating ? "Generating..." : "Generate from Reading Order"}
        </button>
        <button
          type="button"
          onClick={handleExportMarkdown}
          disabled={!selectedNarrative}
          style={{ cursor: selectedNarrative ? "pointer" : "not-allowed" }}
        >
          Export Markdown
        </button>
        <button
          type="button"
          onClick={handleExportHtml}
          disabled={!selectedNarrative}
          style={{ cursor: selectedNarrative ? "pointer" : "not-allowed" }}
        >
          Export HTML
        </button>
      </div>
      <div style={{ fontSize: 11, color: "#7c2d12", marginBottom: 8 }}>
        Generated draft (unreviewed). Please verify against the diagram.
      </div>
      {generationErrorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{generationErrorMessage}</div> : null}
      {generatedNarratives.length > 0 ? (
        <ul style={{ margin: "0 0 8px", paddingLeft: 18, display: "grid", gap: 8 }}>
          {generatedNarratives.map((entry) => {
            const isSelected = selectedNarrative?.id === entry.id;
            return (
              <li key={entry.id} style={{ fontSize: 12, color: "#1e293b" }}>
                <button
                  type="button"
                  onClick={() => {
                    onSelectNarrativeId(entry.id);
                    onNarrativeTextChange(entry.text);
                  }}
                  style={{
                    textAlign: "left",
                    width: "100%",
                    border: isSelected ? "1px solid #2563eb" : "1px solid #cbd5e1",
                    borderRadius: 4,
                    background: isSelected ? "#eff6ff" : "#ffffff",
                    padding: 8,
                    cursor: "pointer",
                  }}
                >
                  <div style={{ fontWeight: 700 }}>{entry.title}</div>
                  <div style={{ fontSize: 11, color: "#64748b" }}>CreatedAt: {entry.createdAt ?? "(generated at export time)"}</div>
                  <div style={{ fontSize: 11, color: "#b45309" }}>Status: {entry.reviewed ? "reviewed" : "unreviewed"}</div>
                  <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>{entry.text}</div>
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
      <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Past consistency checks</div>
      {selectedChecks.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>No checks logged for the selected narrative.</div>
      ) : (
        <ul style={{ margin: "0 0 8px", paddingLeft: 18, display: "grid", gap: 8 }}>
          {[...selectedChecks].reverse().map((check: NarrativeCheck) => {
            const counts = countBySeverity(check.issues);
            const isExpanded = expandedCheckIds.has(check.id);
            return (
              <li key={check.id} style={{ fontSize: 12, color: "#1e293b" }}>
                <button
                  type="button"
                  onClick={() => {
                    setExpandedCheckIds((previous) => {
                      const next = new Set(previous);
                      if (next.has(check.id)) {
                        next.delete(check.id);
                      } else {
                        next.add(check.id);
                      }
                      return next;
                    });
                  }}
                  style={{ border: "1px solid #cbd5e1", borderRadius: 4, background: "#ffffff", width: "100%", textAlign: "left", padding: 8, cursor: "pointer" }}
                >
                  <div style={{ fontWeight: 600 }}>{formatTimestamp(check.createdAt)}</div>
                  <div style={{ fontSize: 11, color: "#64748b" }}>
                    info: {counts.info}, warn: {counts.warn}, error: {counts.error}
                  </div>
                </button>
                {isExpanded ? (
                  <div style={{ marginTop: 6 }}>
                    <CheckIssueList issues={check.issues} onReferenceClick={onReferenceClick} />
                  </div>
                ) : null}
              </li>
            );
          })}
        </ul>
      )}
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Latest consistency issues (AI-generated, unreviewed)</div>
      {issues.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>No issues returned. This is not a correctness guarantee.</div>
      ) : (
        <CheckIssueList issues={issues} onReferenceClick={onReferenceClick} />
      )}
    </section>
  );
}
