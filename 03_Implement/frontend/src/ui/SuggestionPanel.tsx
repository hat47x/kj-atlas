import { t } from "../i18n/translate";

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
      <div style={{ fontWeight: 700, marginBottom: 8 }}>{t("suggestion.panel.title")}</div>
      <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>
        {t("suggestion.panel.unreviewed_hint")}
      </div>
      <textarea
        value={instruction}
        disabled={isReadOnly}
        onChange={(event) => {
          onInstructionChange(event.target.value);
        }}
        placeholder={t("suggestion.panel.instruction_placeholder")}
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
          {isSuggesting ? t("suggestion.panel.suggesting") : t("suggestion.panel.suggest_layout")}
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
            <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>{t("suggestion.panel.iteration")}</div>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 6 }}>
              <button
                type="button"
                disabled={isReadOnly}
                onClick={() => {
                  onAnnotateOverlayToggle(!isAnnotateOverlayEnabled);
                }}
              >
                {isAnnotateOverlayEnabled ? t("suggestion.panel.stop_annotating") : t("suggestion.panel.annotate_critiques")}
              </button>
              <button type="button" onClick={onResuggest} disabled={isReadOnly || isSuggesting}>
                {isSuggesting ? t("suggestion.panel.resuggesting") : t("suggestion.panel.resuggest")}
              </button>
              <button type="button" disabled={isReadOnly} onClick={onApply}>
                {t("suggestion.panel.apply")}
              </button>
              <button type="button" disabled={isReadOnly} onClick={onDiscard}>
                {t("suggestion.panel.discard")}
              </button>
            </div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              {t("suggestion.panel.critiques_hint")}
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
            {t("suggestion.panel.preview")}
          </label>
        </>
      ) : null}
      {notes ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>{t("suggestion.panel.notes", { notes })}</div> : null}
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c" }}>{errorMessage}</div> : null}
    </section>
  );
}
