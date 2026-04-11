import { useState, type MouseEvent } from "react";
import type { Card } from "../domain/types";
import type { MergeSuggestion } from "../api/client";
import type { MergeSuggestionDecision } from "../domain/merge_suggestion_decisions";
import type { MergeDecisionAuditEvent } from "../domain/merge/decision_audit_events";
import { evaluateMergeDecisionTrustBoundary } from "../domain/hil_rs_trusted_boundary";
import { normalizeHilDecisionReason } from "../domain/hil_rs_decision_reason";

type MergeSuggestionDraft = MergeSuggestion & {
  editedText: string;
  isEdited: boolean;
  latestDecision?: MergeSuggestionDecision;
  latestDecidedAt?: string;
  representativeCardId?: string;
  representativeResolvedBy?: "repOf" | "mergedIntoCardId" | "fallback" | "unresolved";
  representativeSourceCount?: number;
};

type MergeSuggestionsPanelProps = {
  isReadOnly?: boolean;
  instruction: string;
  onInstructionChange: (value: string) => void;
  onSuggest: () => void;
  isSuggesting: boolean;
  errorMessage: string | null;
  suggestions: MergeSuggestionDraft[];
  cardsById: Map<string, Card>;
  onMergedTextChange: (groupId: string, value: string) => void;
  onDecide: (
    groupId: string,
    decision: MergeSuggestionDecision,
    options: { isTrusted: boolean; decisionReason?: string }
  ) => void;
  latestAuditEventByGroup?: ReadonlyMap<string, MergeDecisionAuditEvent>;
  auditEvents?: readonly MergeDecisionAuditEvent[];
  onExportAuditEvents?: () => void;
};

function snippet(text: string): string {
  const trimmed = text.trim();
  if (trimmed.length <= 80) {
    return trimmed;
  }
  return `${trimmed.slice(0, 80)}...`;
}

function decisionLabel(decision: MergeSuggestionDecision | undefined): string {
  switch (decision) {
    case "accept":
      return "Accepted";
    case "partial":
      return "Partially accepted";
    case "reject":
      return "Rejected";
    case "defer":
      return "Deferred";
    default:
      return "Not reviewed";
  }
}

function representativeResolvedLabel(
  resolvedBy: MergeSuggestionDraft["representativeResolvedBy"]
): string {
  switch (resolvedBy) {
    case "repOf":
      return "repOf";
    case "mergedIntoCardId":
      return "mergedIntoCardId";
    case "fallback":
      return "fallback";
    case "unresolved":
      return "unresolved";
    default:
      return "unresolved";
  }
}

type TextDiffSegment = {
  value: string;
  kind: "same" | "added" | "removed";
};

function buildTextDiff(beforeText: string, afterText: string): TextDiffSegment[] {
  const beforeTokens = beforeText.split(/(\s+)/).filter((token) => token.length > 0);
  const afterTokens = afterText.split(/(\s+)/).filter((token) => token.length > 0);
  const longestCommon = Array.from({ length: beforeTokens.length + 1 }, () => new Array<number>(afterTokens.length + 1).fill(0));

  for (let beforeIndex = beforeTokens.length - 1; beforeIndex >= 0; beforeIndex -= 1) {
    for (let afterIndex = afterTokens.length - 1; afterIndex >= 0; afterIndex -= 1) {
      if (beforeTokens[beforeIndex] === afterTokens[afterIndex]) {
        longestCommon[beforeIndex]![afterIndex] = (longestCommon[beforeIndex + 1]?.[afterIndex + 1] ?? 0) + 1;
      } else {
        longestCommon[beforeIndex]![afterIndex] = Math.max(
          longestCommon[beforeIndex + 1]?.[afterIndex] ?? 0,
          longestCommon[beforeIndex]?.[afterIndex + 1] ?? 0,
        );
      }
    }
  }

  const segments: TextDiffSegment[] = [];
  const append = (kind: TextDiffSegment["kind"], token: string) => {
    const previous = segments.at(-1);
    if (previous && previous.kind === kind) {
      previous.value += token;
      return;
    }
    segments.push({ kind, value: token });
  };

  let beforeIndex = 0;
  let afterIndex = 0;
  while (beforeIndex < beforeTokens.length && afterIndex < afterTokens.length) {
    const beforeToken = beforeTokens[beforeIndex]!;
    const afterToken = afterTokens[afterIndex]!;

    if (beforeToken === afterToken) {
      append("same", beforeToken);
      beforeIndex += 1;
      afterIndex += 1;
      continue;
    }

    if ((longestCommon[beforeIndex + 1]?.[afterIndex] ?? 0) >= (longestCommon[beforeIndex]?.[afterIndex + 1] ?? 0)) {
      append("removed", beforeToken);
      beforeIndex += 1;
    } else {
      append("added", afterToken);
      afterIndex += 1;
    }
  }

  while (beforeIndex < beforeTokens.length) {
    append("removed", beforeTokens[beforeIndex]!);
    beforeIndex += 1;
  }
  while (afterIndex < afterTokens.length) {
    append("added", afterTokens[afterIndex]!);
    afterIndex += 1;
  }

  return segments;
}

export function MergeSuggestionsPanel({
  instruction,
  onInstructionChange,
  onSuggest,
  isSuggesting,
  errorMessage,
  suggestions,
  cardsById,
  onMergedTextChange,
  onDecide,
  latestAuditEventByGroup,
  auditEvents,
  onExportAuditEvents,
  isReadOnly = false,
}: MergeSuggestionsPanelProps) {
  const [trustBoundaryErrorMessage, setTrustBoundaryErrorMessage] = useState<string | null>(null);
  const [decisionReasonByGroup, setDecisionReasonByGroup] = useState<Record<string, string>>({});

  const handleDecisionClick = (
    groupId: string,
    decision: MergeSuggestionDecision,
    event: MouseEvent<HTMLButtonElement>
  ) => {
    const trustBoundary = evaluateMergeDecisionTrustBoundary({
      isReadOnly,
      isTrustedEvent: event.isTrusted,
    });

    if (!trustBoundary.allowDecision) {
      setTrustBoundaryErrorMessage(trustBoundary.errorMessage);
      return;
    }

    const decisionReason = normalizeHilDecisionReason(decisionReasonByGroup[groupId]);
    if (!decisionReason) {
      setTrustBoundaryErrorMessage("Decision reason is required before recording accept/reject/defer.");
      return;
    }

    setTrustBoundaryErrorMessage(null);
    onDecide(groupId, decision, { isTrusted: event.isTrusted, decisionReason });
  };

  return (
    <section
      style={{
        border: "1px solid #e2e8f0",
        borderRadius: 8,
        padding: 12,
        marginBottom: 12,
        backgroundColor: "#ffffff",
      }}
    >
      <div style={{ fontWeight: 700, marginBottom: 8 }}>Similar card merge candidates</div>
      <textarea
        value={instruction}
        disabled={isReadOnly}
        onChange={(event) => {
          onInstructionChange(event.target.value);
        }}
        placeholder="Optional note (kept locally for manual review)"
        rows={2}
        style={{
          width: "100%",
          resize: "vertical",
          border: "1px solid #cbd5e1",
          borderRadius: 6,
          padding: 8,
          marginBottom: 8,
          boxSizing: "border-box",
        }}
      />
      <button type="button" onClick={onSuggest} disabled={isReadOnly || isSuggesting} style={{ marginBottom: 8 }}>
        {isSuggesting ? "Collecting..." : "Collect candidates"}
      </button>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        Deterministic heuristic only (no AI decision). Final merge decision remains human-in-the-loop.
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <button
          type="button"
          onClick={onExportAuditEvents}
          disabled={isReadOnly || !onExportAuditEvents || !auditEvents || auditEvents.length === 0}
        >
          Export decision audit events (JSONL)
        </button>
        <span style={{ fontSize: 11, color: "#475569" }}>
          {auditEvents && auditEvents.length > 0 ? `${auditEvents.length} event(s)` : "No audit events yet"}
        </span>
      </div>
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      {trustBoundaryErrorMessage ? (
        <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }} aria-live="polite">
          {trustBoundaryErrorMessage}
        </div>
      ) : null}
      {suggestions.map((suggestion) => (
        <article key={suggestion.groupId} style={{ borderTop: "1px solid #e2e8f0", paddingTop: 8, marginTop: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 8, marginBottom: 4 }}>
            <div style={{ fontSize: 12, fontWeight: 600 }}>Cards in candidate group</div>
            <div style={{ fontSize: 11, color: "#334155" }}>
              Decision: {decisionLabel(suggestion.latestDecision)}
              {suggestion.latestDecidedAt ? ` (${new Date(suggestion.latestDecidedAt).toLocaleString()})` : ""}
            </div>
          </div>
          <ul style={{ margin: "0 0 8px", paddingLeft: 18 }}>
            {suggestion.cardIds.map((cardId) => {
              const card = cardsById.get(cardId);
              if (!card) {
                return (
                  <li key={cardId} style={{ fontSize: 12, color: "#64748b" }}>
                    {cardId} (card not found)
                  </li>
                );
              }

              return (
                <li key={card.id} style={{ fontSize: 12, color: "#334155" }}>
                  {card.id}: {snippet(card.text)}
                </li>
              );
            })}
          </ul>
          <textarea
            value={suggestion.editedText}
            disabled={isReadOnly}
            onChange={(event) => {
              onMergedTextChange(suggestion.groupId, event.target.value);
            }}
            rows={4}
            style={{
              width: "100%",
              resize: "vertical",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: 8,
              marginBottom: 6,
              boxSizing: "border-box",
            }}
          />
          <div
            style={{
              marginBottom: 6,
              padding: 8,
              border: "1px solid #e2e8f0",
              borderRadius: 6,
              fontSize: 12,
              color: "#334155",
              backgroundColor: "#f8fafc",
            }}
          >
            <strong>Draft diff preview:</strong>{" "}
            {buildTextDiff(suggestion.mergedTextDraft, suggestion.editedText).map((segment, segmentIndex) => {
              if (segment.kind === "same") {
                return <span key={`${suggestion.groupId}-seg-${segmentIndex}`}>{segment.value}</span>;
              }

              if (segment.kind === "removed") {
                return (
                  <del key={`${suggestion.groupId}-seg-${segmentIndex}`} style={{ backgroundColor: "#fee2e2" }}>
                    {segment.value}
                  </del>
                );
              }

              return (
                <ins
                  key={`${suggestion.groupId}-seg-${segmentIndex}`}
                  style={{ backgroundColor: "#dcfce7", textDecoration: "none" }}
                >
                  {segment.value}
                </ins>
              );
            })}
          </div>
          <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>
            Representative: {suggestion.representativeCardId ?? "(not resolved)"}
            {` [${representativeResolvedLabel(suggestion.representativeResolvedBy)}]`}
            {typeof suggestion.representativeSourceCount === "number"
              ? `, source count: ${suggestion.representativeSourceCount}`
              : ""}
          </div>
          {suggestion.rationale ? (
            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>Rationale: {suggestion.rationale}</div>
          ) : null}
          <label style={{ display: "block", fontSize: 12, color: "#334155", marginBottom: 4 }}>
            Decision reason (required)
          </label>
          <textarea
            value={decisionReasonByGroup[suggestion.groupId] ?? ""}
            disabled={isReadOnly}
            onChange={(event) => {
              setDecisionReasonByGroup((current) => ({
                ...current,
                [suggestion.groupId]: event.target.value,
              }));
            }}
            rows={2}
            placeholder="Record why you accept/partial/reject/defer this proposal"
            style={{
              width: "100%",
              resize: "vertical",
              border: "1px solid #cbd5e1",
              borderRadius: 6,
              padding: 8,
              marginBottom: 6,
              boxSizing: "border-box",
            }}
          />
          {latestAuditEventByGroup?.get(suggestion.groupId) ? (
            <div style={{ fontSize: 11, color: "#334155", marginBottom: 6 }}>
              Audit event recorded at {new Date(latestAuditEventByGroup.get(suggestion.groupId)!.decidedAt).toLocaleString()} / decision={latestAuditEventByGroup.get(suggestion.groupId)!.decision}
            </div>
          ) : null}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" disabled={isReadOnly} onClick={(event) => handleDecisionClick(suggestion.groupId, "accept", event)}>Accept</button>
            <button type="button" disabled={isReadOnly} onClick={(event) => handleDecisionClick(suggestion.groupId, "partial", event)}>Partially accept</button>
            <button type="button" disabled={isReadOnly} onClick={(event) => handleDecisionClick(suggestion.groupId, "reject", event)}>Reject</button>
            <button type="button" disabled={isReadOnly} onClick={(event) => handleDecisionClick(suggestion.groupId, "defer", event)}>Defer</button>
          </div>
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>
            Decisions are recorded only; no automatic canonical merge is executed. Trusted human interaction is required for decision commits.
          </div>
        </article>
      ))}
    </section>
  );
}
