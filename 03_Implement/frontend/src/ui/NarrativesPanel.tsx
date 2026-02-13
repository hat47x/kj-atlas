import { useMemo, useState } from "react";

import type { NarrativeIssue, NarrativeIssueReference } from "../api/client";
import {
  buildNarrativeHtml,
  buildNarrativeMarkdown,
  downloadTextFile,
  type ReadingOrderSnippetMap,
} from "../export/narrative_export";
import { buildNarrativeGrounding } from "../domain/grounding";
import type { DocumentV2 } from "../domain/types";

type NarrativeEntry = {
  id: string;
  title: string;
  text: string;
  createdAt?: string;
  basedOnReadingOrder?: string[];
  reviewed: boolean;
};

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
  onReferenceClick: (reference: NarrativeIssueReference) => void;
  readingOrderSnippets?: ReadingOrderSnippetMap;
  document: DocumentV2 | null;
  hideSourceCards: boolean;
};

const severityColorMap: Record<NarrativeIssue["severity"], string> = {
  info: "#0369a1",
  warn: "#b45309",
  error: "#b91c1c",
};

function sanitizeFileStem(value: string): string {
  const trimmed = value.trim().toLowerCase();
  const normalized = trimmed.length > 0 ? trimmed : "narrative";
  const sanitized = normalized.replace(/[^a-z0-9-_]+/g, "-").replace(/^-+|-+$/g, "");
  return sanitized.length > 0 ? sanitized : "narrative";
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
  onReferenceClick,
  readingOrderSnippets = {},
  document,
  hideSourceCards,
}: NarrativesPanelProps) {
  const [selectedNarrativeId, setSelectedNarrativeId] = useState<string | null>(null);

  const selectedNarrative = useMemo(() => {
    if (generatedNarratives.length === 0) {
      return null;
    }

    if (selectedNarrativeId) {
      return generatedNarratives.find((entry) => entry.id === selectedNarrativeId) ?? generatedNarratives[0];
    }

    return generatedNarratives[0];
  }, [generatedNarratives, selectedNarrativeId]);

  const groundingEntries = useMemo(() => {
    if (!selectedNarrative || !document) {
      return [];
    }

    return buildNarrativeGrounding(document, {
      basedOnReadingOrder: selectedNarrative.basedOnReadingOrder,
      hideSourceCards,
    });
  }, [document, hideSourceCards, selectedNarrative]);

  const handleExportMarkdown = () => {
    if (!selectedNarrative || !document) {
      return;
    }

    const content = buildNarrativeMarkdown(selectedNarrative, readingOrderSnippets, groundingEntries);
    const fileStem = sanitizeFileStem(selectedNarrative.title || selectedNarrative.id);
    downloadTextFile(`${fileStem}.md`, "text/markdown", content);
  };

  const handleExportHtml = () => {
    if (!selectedNarrative || !document) {
      return;
    }

    const content = buildNarrativeHtml(selectedNarrative, readingOrderSnippets, groundingEntries);
    const fileStem = sanitizeFileStem(selectedNarrative.title || selectedNarrative.id);
    downloadTextFile(`${fileStem}.html`, "text/html", content);
  };

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
                    setSelectedNarrativeId(entry.id);
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
      {selectedNarrative ? (
        <div style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Grounding / Citations</div>
          {groundingEntries.length === 0 ? (
            <div style={{ fontSize: 12, color: "#64748b" }}>No grounding entries.</div>
          ) : (
            <ol style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
              {groundingEntries.map((entry) => (
                <li key={`${entry.anchor}-${entry.sourceId}`} style={{ fontSize: 12, color: "#1e293b" }}>
                  <div style={{ fontWeight: 600 }}>{entry.anchor}</div>
                  {entry.kind === "missing" ? <div>Missing entry: {entry.sourceId}</div> : null}
                  {entry.kind === "card" && entry.card ? (
                    <div>
                      <div>
                        Card {entry.card.id} [{entry.card.kind}
                        {entry.card.kind === "source" ? ` canonicalId: ${entry.card.canonicalId}` : ""}]
                      </div>
                      <div style={{ whiteSpace: "pre-wrap", color: "#475569" }}>{entry.card.text || "(empty)"}</div>
                    </div>
                  ) : null}
                  {entry.kind === "island" ? (
                    <div>
                      <div>Island: {entry.islandTitle ?? entry.sourceId}</div>
                      {entry.islandSummaryText ? (
                        <div style={{ color: "#475569" }}>
                          Summary{entry.islandSummaryReviewed ? "" : " (unreviewed)"}: {entry.islandSummaryText}
                        </div>
                      ) : null}
                      <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                        {(entry.islandMembers ?? []).map((member) => (
                          <li key={member.id}>
                            {member.id} [{member.kind}
                            {member.kind === "source" ? ` canonicalId: ${member.canonicalId}` : ""}] — {member.text || "(empty)"}
                          </li>
                        ))}
                        {(entry.islandMembers ?? []).length === 0 ? <li>(no member cards)</li> : null}
                      </ul>
                    </div>
                  ) : null}
                </li>
              ))}
            </ol>
          )}
        </div>
      ) : null}
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>Consistency issues (AI-generated, unreviewed)</div>
      {issues.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>No issues returned. This is not a correctness guarantee.</div>
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
