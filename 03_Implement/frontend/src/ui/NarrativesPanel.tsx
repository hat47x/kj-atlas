export type NarrativeEntry = {
  id: string;
  title: string;
  text: string;
  reviewed: boolean;
  basedOnReadingOrder: string[];
  warnings?: string[];
};

type NarrativesPanelProps = {
  narratives: NarrativeEntry[];
  hasReadingOrder: boolean;
  isGenerating: boolean;
  generateError?: string;
  onGenerateFromReadingOrder: () => void;
};

export function NarrativesPanel({
  narratives,
  hasReadingOrder,
  isGenerating,
  generateError,
  onGenerateFromReadingOrder,
}: NarrativesPanelProps) {
  return (
    <section
      style={{
        position: "absolute",
        left: 16,
        bottom: 16,
        width: 360,
        maxHeight: "45vh",
        overflow: "auto",
        backgroundColor: "rgba(255, 255, 255, 0.97)",
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        padding: 12,
        boxShadow: "0 8px 20px rgba(15, 23, 42, 0.16)",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>Narratives</div>
        <button
          type="button"
          onClick={onGenerateFromReadingOrder}
          disabled={isGenerating || !hasReadingOrder}
          style={{
            border: "1px solid #cbd5e1",
            backgroundColor: "#ffffff",
            borderRadius: 6,
            padding: "6px 8px",
            fontSize: 12,
            fontWeight: 600,
            cursor: isGenerating || !hasReadingOrder ? "not-allowed" : "pointer",
          }}
        >
          {isGenerating ? "Generating..." : "Generate from Reading Order"}
        </button>
      </div>

      {!hasReadingOrder ? (
        <div style={{ fontSize: 12, color: "#64748b", marginBottom: 8 }}>Add reading order entries to generate a narrative.</div>
      ) : null}

      <div
        style={{
          fontSize: 12,
          color: "#7c2d12",
          backgroundColor: "#fff7ed",
          border: "1px solid #fdba74",
          borderRadius: 6,
          padding: "6px 8px",
          marginBottom: 8,
        }}
      >
        Generated draft (unreviewed). Please verify against the diagram.
      </div>

      {generateError ? (
        <div style={{ fontSize: 12, color: "#b91c1c", marginBottom: 8 }}>{generateError}</div>
      ) : null}

      {narratives.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>No narratives yet.</div>
      ) : (
        <div style={{ display: "grid", gap: 8 }}>
          {narratives.map((narrative) => (
            <article key={narrative.id} style={{ border: "1px solid #e2e8f0", borderRadius: 6, padding: 8, backgroundColor: "#f8fafc" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a" }}>{narrative.title}</div>
                <span
                  style={{
                    fontSize: 11,
                    color: narrative.reviewed ? "#14532d" : "#7c2d12",
                    backgroundColor: narrative.reviewed ? "#dcfce7" : "#ffedd5",
                    border: `1px solid ${narrative.reviewed ? "#86efac" : "#fdba74"}`,
                    borderRadius: 999,
                    padding: "2px 6px",
                    fontWeight: 700,
                  }}
                >
                  {narrative.reviewed ? "Reviewed" : "Unreviewed draft"}
                </span>
              </div>
              <div style={{ fontSize: 12, color: "#1e293b", whiteSpace: "pre-wrap", marginBottom: 6 }}>{narrative.text}</div>
              <div style={{ fontSize: 11, color: "#64748b", marginBottom: 4 }}>
                readingOrder: {narrative.basedOnReadingOrder.join(" → ")}
              </div>
              {narrative.warnings && narrative.warnings.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: 16, color: "#92400e", fontSize: 11 }}>
                  {narrative.warnings.map((warning, index) => (
                    <li key={`${narrative.id}_warning_${index}`}>{warning}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
