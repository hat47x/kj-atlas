import { t } from "../i18n/translate";
import {
  defaultSuggestionPanelAdapter,
  type Ce2SuggestionCandidate,
  type SuggestionPanelAdapter,
} from "./suggestion_panel_adapter";

type SuggestionPanelProps = {
  isReadOnly?: boolean;
  instruction: string;
  onInstructionChange: (value: string) => void;
  onSuggest: () => void;
  onResuggest: () => void;
  onDiscard: () => void;
  hasSuggestion: boolean;
  suggestionId?: string | null;
  proposalCandidates?: Ce2SuggestionCandidate[];
  selectedProposalId?: string | null;
  onSelectProposalCandidate?: (proposalId: string) => void;
  isPreviewEnabled: boolean;
  onPreviewToggle: (enabled: boolean) => void;
  isAnnotateOverlayEnabled: boolean;
  onAnnotateOverlayToggle: (enabled: boolean) => void;
  isSuggesting: boolean;
  errorMessage: string | null;
  notes: string | null;
  resuggestAttemptCount?: number;
  resuggestAttemptLimit?: number;
  onStopResuggest?: () => void;
  adapter?: SuggestionPanelAdapter;
};

export function SuggestionPanel({
  instruction,
  onInstructionChange,
  onSuggest,
  onResuggest,
  onDiscard,
  hasSuggestion,
  suggestionId,
  proposalCandidates,
  selectedProposalId,
  onSelectProposalCandidate,
  isPreviewEnabled,
  onPreviewToggle,
  isAnnotateOverlayEnabled,
  onAnnotateOverlayToggle,
  isSuggesting,
  errorMessage,
  notes,
  resuggestAttemptCount = 0,
  resuggestAttemptLimit = 3,
  onStopResuggest,
  adapter = defaultSuggestionPanelAdapter,
  isReadOnly = false,
}: SuggestionPanelProps) {
  const ce2State = adapter.buildProposalOnlyState({
    safeModeEnabled: true,
    previewEnabled: isPreviewEnabled,
    hasSuggestion,
  });
  const candidates = adapter.buildCandidates({
    hasSuggestion,
    suggestionId,
    candidates: proposalCandidates,
  });
  const selectedCandidateId = selectedProposalId ?? candidates[0]?.proposalId ?? "";
  const selectedCandidate = candidates.find((candidate) => candidate.proposalId === selectedCandidateId) ?? null;
  const reviewSummary = adapter.summarizeReviewStates(candidates);
  const resuggestStopReached = resuggestAttemptCount >= resuggestAttemptLimit;

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
        <button type="button" onClick={onSuggest} disabled={isReadOnly || isSuggesting || resuggestStopReached}>
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
              <button type="button" disabled={isReadOnly || !resuggestStopReached} onClick={onStopResuggest}>
                Stop after {resuggestAttemptLimit} retries
              </button>
              <button type="button" disabled={isReadOnly} onClick={onDiscard}>
                {t("suggestion.panel.discard")}
              </button>
            </div>
            <div style={{ fontSize: 11, color: "#475569" }}>
              {t("suggestion.panel.critiques_hint")}
            </div>
            <div style={{ fontSize: 11, color: "#7c3aed", marginTop: 6 }}>
              {t("suggestion.panel.proposal_only_hint")}
            </div>
            <div style={{ fontSize: 11, color: resuggestStopReached ? "#b45309" : "#475569", marginTop: 6 }}>
              Self-repair attempts: {resuggestAttemptCount}/{resuggestAttemptLimit}
              {resuggestStopReached ? " (stopper active)" : ""}
            </div>
          </section>
          <section
            style={{
              border: "1px solid #e2e8f0",
              borderRadius: 6,
              padding: 8,
              marginBottom: 8,
              backgroundColor: "#ffffff",
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>Patch proposals</div>
            <div style={{ fontSize: 11, color: "#475569", marginBottom: 6 }}>
              review state: {reviewSummary.unreviewed} unreviewed / {reviewSummary.reviewed} human reviewed
            </div>
            {selectedCandidate ? (
              <div style={{ fontSize: 11, color: "#334155", marginBottom: 6 }}>
                selected: <strong>{selectedCandidate.label}</strong> ({selectedCandidate.status}, {selectedCandidate.reviewState})
              </div>
            ) : null}
            <select
              data-testid="ce2-proposal-candidate-select"
              style={{ width: "100%", marginBottom: 6 }}
              value={selectedCandidateId}
              disabled={isReadOnly || candidates.length === 0}
              onChange={(event) => {
                onSelectProposalCandidate?.(event.target.value);
              }}
            >
              {candidates.length === 0 ? <option value="">No proposals</option> : null}
              {candidates.map((candidate) => (
                <option key={candidate.proposalId} value={candidate.proposalId}>
                  {candidate.label} ({candidate.status}, {candidate.reviewState})
                </option>
              ))}
            </select>
            <div style={{ fontSize: 11, color: "#64748b" }}>
              Reversible synthesis keeps proposals isolated until explicit human approval.
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
      <div data-testid="ce2-proposal-only-state" style={{ fontSize: 11, color: "#64748b" }}>
        CE2 proposal-only blockers: {ce2State.blockers.join(",")}
      </div>
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c" }}>{errorMessage}</div> : null}
    </section>
  );
}
