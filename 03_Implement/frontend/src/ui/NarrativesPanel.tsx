import type { Narrative } from "../domain/types";

type NarrativesPanelProps = {
  narratives: Narrative[];
  selectedNarrativeId: string | null;
  onSelectNarrative: (narrativeId: string) => void;
  onNarrativeTextChange: (narrativeId: string, text: string) => void;
  onNarrativeReviewedChange: (narrativeId: string, reviewed: boolean) => void;
  onCreateNarrative: () => void;
};

export function NarrativesPanel({
  narratives,
  selectedNarrativeId,
  onSelectNarrative,
  onNarrativeTextChange,
  onNarrativeReviewedChange,
  onCreateNarrative,
}: NarrativesPanelProps) {
  const selectedNarrative = narratives.find((narrative) => narrative.id === selectedNarrativeId) ?? narratives[0] ?? null;

  return (
    <aside
      style={{
        width: 320,
        minWidth: 320,
        borderLeft: "1px solid #e2e8f0",
        backgroundColor: "#ffffff",
        padding: 12,
        boxSizing: "border-box",
        overflowY: "auto",
      }}
    >
      <section style={{ marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>Narratives</div>
          <button
            type="button"
            onClick={onCreateNarrative}
            style={{
              border: "1px solid #cbd5e1",
              backgroundColor: "#ffffff",
              color: "#0f172a",
              borderRadius: 6,
              padding: "4px 8px",
              fontSize: 12,
              cursor: "pointer",
            }}
          >
            Add
          </button>
        </div>
        {narratives.length === 0 ? (
          <div style={{ fontSize: 12, color: "#64748b" }}>No narratives yet.</div>
        ) : (
          <div style={{ display: "grid", gap: 6 }}>
            {narratives.map((narrative) => (
              <button
                key={narrative.id}
                type="button"
                onClick={() => {
                  onSelectNarrative(narrative.id);
                }}
                style={{
                  textAlign: "left",
                  border: "1px solid #cbd5e1",
                  backgroundColor: narrative.id === selectedNarrative?.id ? "#e2e8f0" : "#ffffff",
                  borderRadius: 6,
                  padding: "6px 8px",
                  cursor: "pointer",
                }}
              >
                <div style={{ fontSize: 12, fontWeight: 600, color: "#0f172a" }}>{narrative.title ?? narrative.id}</div>
                <div style={{ fontSize: 11, color: narrative.reviewed ? "#166534" : "#b45309" }}>
                  {narrative.reviewed ? "Reviewed" : "Unreviewed AI-generated draft"}
                </div>
              </button>
            ))}
          </div>
        )}
      </section>

      {selectedNarrative ? (
        <section style={{ display: "grid", gap: 8 }}>
          <div style={{ fontSize: 12, color: "#475569" }}>
            This narrative may include unreviewed AI-generated text. Verify before reuse.
          </div>
          <label style={{ display: "grid", gap: 4, fontSize: 12, color: "#334155" }}>
            Text
            <textarea
              value={selectedNarrative.text}
              onChange={(event) => {
                onNarrativeTextChange(selectedNarrative.id, event.target.value);
              }}
              rows={12}
              style={{ width: "100%", resize: "vertical" }}
            />
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#334155" }}>
            <input
              type="checkbox"
              checked={selectedNarrative.reviewed}
              onChange={(event) => {
                onNarrativeReviewedChange(selectedNarrative.id, event.target.checked);
              }}
            />
            Reviewed by human
          </label>
        </section>
      ) : null}
    </aside>
  );
}
