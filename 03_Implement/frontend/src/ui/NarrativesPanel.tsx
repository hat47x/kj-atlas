import { useId, useMemo, useState } from "react";

import type { NarrativeIssue, NarrativeIssueReference } from "../api/client";
import { buildNarrativeGrounding } from "../domain/grounding";
import type { DocumentV2, Narrative } from "../domain/types";
import {
  buildNarrativeHtml,
  buildNarrativeMarkdown,
  downloadTextFile,
  type ReadingOrderSnippetMap,
} from "../export/narrative_export";
import { t } from "../i18n/translate";

const claimTypeLabels: Record<string, string> = {
  fact: t("side_panel.claim_type.fact"),
  claim: t("side_panel.claim_type.claim"),
  hypothesis: t("side_panel.claim_type.hypothesis"),
  unknown: t("side_panel.claim_type.unknown"),
};

type NarrativesPanelProps = {
  narrativeText: string;
  onNarrativeTextChange: (value: string) => void;
  onCheckConsistency: (selectedNarrativeId: string | null) => void;
  onGenerateFromReadingOrder: () => void;
  isChecking: boolean;
  isGenerating: boolean;
  errorMessage: string | null;
  generationErrorMessage: string | null;
  issues: NarrativeIssue[];
  generatedNarratives: Narrative[];
  onReferenceClick: (reference: NarrativeIssueReference) => void;
  readingOrderSnippets?: ReadingOrderSnippetMap;
  document: DocumentV2 | null;
  hideSourceCards: boolean;
  onFocusItem: (kind: "card" | "island", id: string) => void;
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
  onFocusItem,
}: NarrativesPanelProps) {
  const panelTitleId = useId();
  const [selectedNarrativeId, setSelectedNarrativeId] = useState<string | null>(null);
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

  const resolveReadingOrderReferenceKind = (entryId: string): "card" | "island" | null => {
    if (!document) {
      return null;
    }

    if (document.cards.some((card) => card.id === entryId)) {
      return "card";
    }

    if (document.islands.some((island) => island.id === entryId)) {
      return "island";
    }

    return null;
  };

  return (
    <section aria-labelledby={panelTitleId} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: "1px solid #e2e8f0" }}>
      <div id={panelTitleId} style={{ fontSize: 14, fontWeight: 700, marginBottom: 8, color: "#0f172a" }}>{t("narratives.panel.title")}</div>
      <div style={{ fontSize: 11, color: "#64748b", marginBottom: 8 }}>
        {t("narratives.panel.advisory_hint")}
      </div>
      <textarea
        aria-label={t("narratives.panel.title")}
        value={narrativeText}
        onChange={(event) => {
          onNarrativeTextChange(event.target.value);
        }}
        rows={6}
        placeholder={t("narratives.panel.placeholder")}
        style={{ width: "100%", resize: "vertical", marginBottom: 8 }}
      />
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 8 }}>
        <button
          type="button"
          onClick={() => {
            onCheckConsistency(selectedNarrative?.id ?? null);
          }}
          disabled={isChecking || narrativeText.trim().length === 0}
          style={{ cursor: isChecking || narrativeText.trim().length === 0 ? "not-allowed" : "pointer" }}
        >
          {isChecking ? t("narratives.panel.checking") : t("narratives.panel.check_consistency")}
        </button>
        <button
          type="button"
          onClick={onGenerateFromReadingOrder}
          disabled={isGenerating}
          style={{ cursor: isGenerating ? "not-allowed" : "pointer" }}
        >
          {isGenerating ? t("narratives.panel.generating") : t("narratives.panel.generate_from_reading_order")}
        </button>
        <button
          type="button"
          onClick={handleExportMarkdown}
          disabled={!selectedNarrative}
          style={{ cursor: selectedNarrative ? "pointer" : "not-allowed" }}
        >
          {t("narratives.panel.export_markdown")}
        </button>
        <button
          type="button"
          onClick={handleExportHtml}
          disabled={!selectedNarrative}
          style={{ cursor: selectedNarrative ? "pointer" : "not-allowed" }}
        >
          {t("narratives.panel.export_html")}
        </button>
      </div>
      <div style={{ fontSize: 11, color: "#7c2d12", marginBottom: 8 }}>
        {t("narratives.panel.generated_draft_warning")}
      </div>
      {generationErrorMessage ? <div role="alert" style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{generationErrorMessage}</div> : null}
      {generatedNarratives.length > 0 ? (
        <ul style={{ margin: "0 0 8px", paddingLeft: 18, display: "grid", gap: 8 }}>
          {generatedNarratives.map((entry) => {
            const isSelected = selectedNarrative?.id === entry.id;
            return (
              <li key={entry.id} style={{ fontSize: 12, color: "#1e293b" }}>
                <button
                  type="button"
                  aria-pressed={isSelected}
                  onClick={() => {
                    setSelectedNarrativeId(entry.id);
                    onNarrativeTextChange(entry.text);
                    setExpandedCheckIds(new Set());
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
                  <div style={{ fontSize: 11, color: "#64748b" }}>{t("narratives.panel.created_at", { value: entry.createdAt ?? t("narratives.panel.generated_at_export_time") })}</div>
                  <div style={{ fontSize: 11, color: "#b45309" }}>{t("narratives.panel.status", { value: entry.reviewed ? t("narratives.panel.status_reviewed") : t("narratives.panel.status_unreviewed") })}</div>
                  <div style={{ whiteSpace: "pre-wrap", marginTop: 4 }}>{entry.text}</div>
                </button>
              </li>
            );
          })}
        </ul>
      ) : null}
      {selectedNarrative ? (
        <div style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>{t("narratives.panel.based_on_reading_order")}</div>
          {(selectedNarrative.basedOnReadingOrder ?? []).length === 0 ? (
            <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>{t("narratives.panel.empty")}</div>
          ) : (
            <ul style={{ margin: "0 0 8px", paddingLeft: 18, display: "grid", gap: 6 }}>
              {(selectedNarrative.basedOnReadingOrder ?? []).map((entryId) => {
                const entryKind = resolveReadingOrderReferenceKind(entryId);
                return (
                  <li key={entryId} style={{ fontSize: 12, color: "#1e293b" }}>
                    {entryKind ? (
                      <button
                        type="button"
                        onClick={() => {
                          onFocusItem(entryKind, entryId);
                        }}
                        style={{ fontSize: 11, cursor: "pointer" }}
                      >
                        {t("narratives.panel.focus_ref", { kind: entryKind, id: entryId })}
                      </button>
                    ) : (
                      <span>{entryId}</span>
                    )}
                  </li>
                );
              })}
            </ul>
          )}
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>{t("narratives.panel.past_checks")}</div>
          {(selectedNarrative.checks ?? []).length === 0 ? (
            <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>{t("narratives.panel.no_past_checks")}</div>
          ) : (
            <ul style={{ margin: "0 0 8px", paddingLeft: 18, display: "grid", gap: 6 }}>
              {(selectedNarrative.checks ?? []).map((check) => {
                const isExpanded = expandedCheckIds.has(check.id);
                const counts = {
                  info: check.issues.filter((issue) => issue.severity === "info").length,
                  warn: check.issues.filter((issue) => issue.severity === "warn").length,
                  error: check.issues.filter((issue) => issue.severity === "error").length,
                };

                return (
                  <li key={check.id} style={{ fontSize: 12 }}>
                    <button
                      type="button"
                      aria-expanded={isExpanded}
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
                      style={{ fontSize: 12, cursor: "pointer" }}
                    >
                      {isExpanded ? "▼" : "▶"} {t("narratives.panel.check_summary", { createdAt: check.createdAt, kind: check.kind, issueCount: check.issues.length, errors: counts.error, warnings: counts.warn, infos: counts.info })}
                    </button>
                    {isExpanded ? (
                      <ul style={{ margin: "6px 0 0", paddingLeft: 16, display: "grid", gap: 6 }}>
                        {check.issues.map((issue, issueIndex) => (
                          <li key={`${check.id}-${issueIndex}`} style={{ color: "#1e293b" }}>
                            <div>
                              <span style={{ color: severityColorMap[issue.severity], fontWeight: 700, marginRight: 8 }}>[{issue.severity}]</span>
                              {issue.message}
                            </div>
                            {issue.references && issue.references.length > 0 ? (
                              <div style={{ marginTop: 4, display: "flex", flexWrap: "wrap", gap: 6 }}>
                                {issue.references.map((reference) => (
                                  <button
                                    key={`${check.id}:${reference.kind}:${reference.id}`}
                                    type="button"
                                    onClick={() => {
                                      onReferenceClick(reference);
                                    }}
                                    style={{ fontSize: 11, cursor: "pointer" }}
                                  >
                                    {t("narratives.panel.focus_ref", { kind: reference.kind, id: reference.id })}
                                  </button>
                                ))}
                              </div>
                            ) : null}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          )}
          <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>{t("narratives.panel.grounding_citations")}</div>
          {groundingEntries.length === 0 ? (
            <div style={{ fontSize: 12, color: "#64748b" }}>{t("narratives.panel.no_grounding")}</div>
          ) : (
            <ol style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 6 }}>
              {groundingEntries.map((entry) => (
                <li key={`${entry.anchor}-${entry.sourceId}`} style={{ fontSize: 12, color: "#1e293b" }}>
                  <div style={{ fontWeight: 600 }}>{entry.anchor}</div>
                  {entry.kind === "missing" ? <div>{t("narratives.panel.missing_entry", { id: entry.sourceId })}</div> : null}
                  {entry.kind === "card" && entry.card ? (
                    <div>
                      <div>
                        {t("narratives.panel.card")}{" "}
                        <button
                          type="button"
                          onClick={() => {
                            if (entry.card) {
                              onFocusItem("card", entry.card.id);
                            }
                          }}
                          style={{ fontSize: 11, cursor: "pointer" }}
                        >
                          {entry.card.id}
                        </button>{" "}
                        [{entry.card.kind}
                        {entry.card.kind === "source" ? ` canonicalId: ${entry.card.canonicalId}` : ""}]
                        {entry.card.claimType && entry.card.claimType !== "unknown" ? (
                          <span style={{ color: "#334155", marginLeft: 4 }}>
                            [{claimTypeLabels[entry.card.claimType] ?? entry.card.claimType}]
                          </span>
                        ) : null}
                        {entry.card.textReviewed === false ? (
                          <span style={{ color: "#b45309", marginLeft: 4 }}>({t("side_panel.unreviewed")})</span>
                        ) : entry.card.textReviewed === true ? (
                          <span style={{ color: "#166534", marginLeft: 4 }}>({t("side_panel.reviewed")})</span>
                        ) : null}
                      </div>
                      <div style={{ whiteSpace: "pre-wrap", color: "#475569" }}>{entry.card.text || t("narratives.panel.empty")}</div>
                    </div>
                  ) : null}
                  {entry.kind === "island" ? (
                    <div>
                      <div>
                        {t("narratives.panel.island")}{" "}
                        <button
                          type="button"
                          onClick={() => {
                            onFocusItem("island", entry.sourceId);
                          }}
                          style={{ fontSize: 11, cursor: "pointer" }}
                        >
                          {entry.islandTitle ?? entry.sourceId}
                        </button>
                      </div>
                      {entry.islandSummaryText ? (
                        <div style={{ color: "#475569" }}>
                          {t("narratives.panel.summary_label", { unreviewedSuffix: entry.islandSummaryReviewed ? "" : t("narratives.panel.unreviewed_suffix") })}: {entry.islandSummaryText}
                        </div>
                      ) : null}
                      <ul style={{ margin: "4px 0 0", paddingLeft: 16 }}>
                        {(entry.islandMembers ?? []).map((member) => (
                          <li key={member.id}>
                            <button
                              type="button"
                              onClick={() => {
                                onFocusItem("card", member.id);
                              }}
                              style={{ fontSize: 11, cursor: "pointer" }}
                            >
                              {member.id}
                            </button>{" "}
                            [{member.kind}
                            {member.kind === "source" ? ` canonicalId: ${member.canonicalId}` : ""}]
                            {member.claimType && member.claimType !== "unknown" ? (
                              <span style={{ color: "#334155", marginLeft: 4 }}>
                                [{claimTypeLabels[member.claimType] ?? member.claimType}]
                              </span>
                            ) : null}
                            {member.textReviewed === false ? (
                              <span style={{ color: "#b45309", marginLeft: 4 }}>({t("side_panel.unreviewed")})</span>
                            ) : member.textReviewed === true ? (
                              <span style={{ color: "#166534", marginLeft: 4 }}>({t("side_panel.reviewed")})</span>
                            ) : null}{" "}
                            - {member.text || t("narratives.panel.empty")}
                          </li>
                        ))}
                        {(entry.islandMembers ?? []).length === 0 ? <li>{t("narratives.panel.no_member_cards")}</li> : null}
                      </ul>
                    </div>
                  ) : null}
                </li>
              ))}
            </ol>
          )}
        </div>
      ) : null}
      {errorMessage ? <div role="alert" style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      <div style={{ fontSize: 12, fontWeight: 600, color: "#334155", marginBottom: 6 }}>{t("narratives.panel.consistency_issues")}</div>
      {issues.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>{t("narratives.panel.no_issues")}</div>
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
                      {t("narratives.panel.focus_ref", { kind: reference.kind, id: reference.id })}
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
