import type { Card } from "../domain/types";
import type { MergeSuggestion } from "../api/client";

type MergeSuggestionDraft = MergeSuggestion & {
  editedText: string;
  isEdited: boolean;
};

type MergeSuggestionsPanelProps = {
  instruction: string;
  onInstructionChange: (value: string) => void;
  onSuggest: () => void;
  isSuggesting: boolean;
  errorMessage: string | null;
  suggestions: MergeSuggestionDraft[];
  cardsById: Map<string, Card>;
  onMergedTextChange: (groupId: string, value: string) => void;
  onApply: (groupId: string) => void;
  onDismiss: (groupId: string) => void;
};

function snippet(text: string): string {
  const trimmed = text.trim();
  if (trimmed.length <= 80) {
    return trimmed;
  }
  return `${trimmed.slice(0, 80)}...`;
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
  onApply,
  onDismiss,
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
      <div style={{ fontWeight: 700, marginBottom: 8 }}>Similar card merge suggestions</div>
      <textarea
        value={instruction}
        onChange={(event) => {
          onInstructionChange(event.target.value);
        }}
        placeholder="Optional instruction for merge suggestions"
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
      <button type="button" onClick={onSuggest} disabled={isSuggesting} style={{ marginBottom: 8 }}>
        {isSuggesting ? "Suggesting..." : "Suggest merges"}
      </button>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        AI suggestions are drafts only. Review before applying.
      </div>
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{errorMessage}</div> : null}
      {suggestions.map((suggestion) => (
        <article key={suggestion.groupId} style={{ borderTop: "1px solid #e2e8f0", paddingTop: 8, marginTop: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Cards in suggestion</div>
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
          <div style={{ display: "flex", gap: 8 }}>
            <button type="button" onClick={() => onApply(suggestion.groupId)}>
              Apply merge
            </button>
            <button type="button" onClick={() => onDismiss(suggestion.groupId)}>
              Dismiss suggestion
            </button>
          </div>
        </article>
      ))}
    </section>
  );
}
