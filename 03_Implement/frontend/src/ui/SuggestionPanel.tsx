type SuggestionPanelProps = {
  instruction: string;
  onInstructionChange: (value: string) => void;
  onSuggest: () => void;
  onApply: () => void;
  onDiscard: () => void;
  hasSuggestion: boolean;
  isPreviewEnabled: boolean;
  onPreviewToggle: (enabled: boolean) => void;
  isSuggesting: boolean;
  errorMessage: string | null;
  notes: string | null;
};

export function SuggestionPanel({
  instruction,
  onInstructionChange,
  onSuggest,
  onApply,
  onDiscard,
  hasSuggestion,
  isPreviewEnabled,
  onPreviewToggle,
  isSuggesting,
  errorMessage,
  notes,
}: SuggestionPanelProps) {
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
      <div style={{ fontWeight: 700, marginBottom: 8 }}>Draft suggestion</div>
      <textarea
        value={instruction}
        onChange={(event) => {
          onInstructionChange(event.target.value);
        }}
        placeholder="Optional instruction for draft layout"
        rows={3}
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
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 8 }}>
        <button type="button" onClick={onSuggest} disabled={isSuggesting}>
          {isSuggesting ? "Suggesting..." : "Suggest layout"}
        </button>
        <button type="button" onClick={onApply} disabled={!hasSuggestion}>
          Apply suggestion
        </button>
        <button type="button" onClick={onDiscard} disabled={!hasSuggestion}>
          Discard
        </button>
      </div>
      {hasSuggestion ? (
        <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
          <input
            type="checkbox"
            checked={isPreviewEnabled}
            onChange={(event) => {
              onPreviewToggle(event.target.checked);
            }}
          />
          Preview suggestion
        </label>
      ) : null}
      {notes ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>Notes: {notes}</div> : null}
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c" }}>{errorMessage}</div> : null}
    </section>
  );
}
