import type { Card } from "../domain/types";
import type { MergeSuggestion } from "../api/client";
import type { MergeSuggestionDecision } from "../domain/merge_suggestion_decisions";

type MergeSuggestionDraft = MergeSuggestion & {
  editedText: string;
  isEdited: boolean;
  latestDecision?: MergeSuggestionDecision;
  latestDecidedAt?: string;
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
  onDecide: (groupId: string, decision: MergeSuggestionDecision) => void;
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
  isReadOnly = false,
}: MergeSuggestionsPanelProps) {
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
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
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
          {suggestion.rationale ? (
            <div style={{ fontSize: 12, color: "#475569", marginBottom: 6 }}>Rationale: {suggestion.rationale}</div>
          ) : null}
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button type="button" disabled={isReadOnly} onClick={() => onDecide(suggestion.groupId, "accept")}>Accept</button>
            <button type="button" disabled={isReadOnly} onClick={() => onDecide(suggestion.groupId, "partial")}>Partially accept</button>
            <button type="button" disabled={isReadOnly} onClick={() => onDecide(suggestion.groupId, "reject")}>Reject</button>
            <button type="button" disabled={isReadOnly} onClick={() => onDecide(suggestion.groupId, "defer")}>Defer</button>
          </div>
          <div style={{ fontSize: 11, color: "#64748b", marginTop: 6 }}>
            Decisions are recorded only; no automatic canonical merge is executed.
          </div>
        </article>
      ))}
    </section>
  );
}
