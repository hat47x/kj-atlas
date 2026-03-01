type SuggestionPanelProps = {
  isReadOnly?: boolean;
  instruction: string;
  onInstructionChange: (value: string) => void;
  onSuggest: () => void;
  onResuggest: () => void;
  onApply: () => void;
  onDiscard: () => void;
  hasSuggestion: boolean;
  isPreviewEnabled: boolean;
  onPreviewToggle: (enabled: boolean) => void;
  isAnnotateOverlayEnabled: boolean;
  onAnnotateOverlayToggle: (enabled: boolean) => void;
  isSuggesting: boolean;
  errorMessage: string | null;
  notes: string | null;
};

export function SuggestionPanel({
  instruction,
  onInstructionChange,
  onSuggest,
  onResuggest,
  onApply,
  onDiscard,
  hasSuggestion,
  isPreviewEnabled,
  onPreviewToggle,
  isAnnotateOverlayEnabled,
  onAnnotateOverlayToggle,
  isSuggesting,
  errorMessage,
  notes,
  isReadOnly = false,
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
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        This is an unreviewed suggestion. Apply only if it feels right.
      </div>
      <textarea
        value={instruction}
        disabled={isReadOnly}
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
        <button type="button" onClick={onSuggest} disabled={isReadOnly || isSuggesting}>
          {isSuggesting ? "Suggesting..." : "Suggest layout"}
        </button>
      </div>
      {hasSuggestion ? (
        <>
          <section
            style={{
              border: "1px solid #e2e8f0",
              borderRadius: 6,
              padding: 8,
              marginBottom: 8,
              backgroundColor: "#f8fafc",
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>Iteration</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
              <button
                type="button"
                disabled={isReadOnly}
                onClick={() => {
                  onAnnotateOverlayToggle(!isAnnotateOverlayEnabled);
                }}
              >
                {isAnnotateOverlayEnabled ? "Stop annotating" : "Annotate critiques"}
              </button>
              <button type="button" onClick={onResuggest} disabled={isReadOnly || isSuggesting}>
                {isSuggesting ? "Re-suggesting..." : "Re-suggest"}
              </button>
              <button type="button" disabled={isReadOnly} onClick={onApply}>
                Apply suggestion
              </button>
              <button type="button" disabled={isReadOnly} onClick={onDiscard}>
                Discard
              </button>
            </div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              Critiques are saved in your document; suggestions are temporary until applied.
            </div>
          </section>
          <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <input
              type="checkbox"
              checked={isPreviewEnabled}
              disabled={isReadOnly}
              onChange={(event) => {
                onPreviewToggle(event.target.checked);
              }}
            />
            Preview suggestion
          </label>
        </>
      ) : null}
      {notes ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>Notes: {notes}</div> : null}
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c" }}>{errorMessage}</div> : null}
    </section>
  );
}
