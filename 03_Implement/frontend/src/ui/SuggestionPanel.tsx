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

function proposalStatusLabel(status: Ce2SuggestionCandidate["status"]): string {
  switch (status) {
    case "accepted":
      return t("suggestion.panel.proposal_status.accepted");
    case "held":
      return t("suggestion.panel.proposal_status.held");
    case "rejected":
      return t("suggestion.panel.proposal_status.rejected");
    case "proposed":
      return t("suggestion.panel.proposal_status.proposed");
  }
}

function proposalReviewStateLabel(reviewState: Ce2SuggestionCandidate["reviewState"]): string {
  switch (reviewState) {
    case "human_reviewed":
      return t("suggestion.panel.review_state.human_reviewed");
    case "unreviewed":
      return t("suggestion.panel.review_state.unreviewed");
  }
}

function proposalCandidateLabel(candidate: Ce2SuggestionCandidate): string {
  return candidate.label === "Current proposal" ? t("suggestion.panel.current_proposal") : candidate.label;
}

function proposalCandidateState(candidate: Ce2SuggestionCandidate): string {
  return t("suggestion.panel.candidate_state", {
    status: proposalStatusLabel(candidate.status),
    reviewState: proposalReviewStateLabel(candidate.reviewState),
  });
}

const proposalConditionKeys: Record<string, string> = {
  auto_apply_blocked: "suggestion.panel.condition.no_auto_apply",
  safe_mode_required: "suggestion.panel.condition.safe_mode_required",
  suggestion_required: "suggestion.panel.condition.suggestion_required",
  preview_opt_in_required: "suggestion.panel.condition.preview_required",
};

function proposalConditionLabel(condition: string): string {
  const key = proposalConditionKeys[condition];
  return key ? t(key) : condition;
}

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
                {t("suggestion.panel.stop_after_retries", { count: resuggestAttemptLimit })}
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
              {t("suggestion.panel.self_repair_attempts", {
                count: resuggestAttemptCount,
                limit: resuggestAttemptLimit,
              })}
              {resuggestStopReached ? t("suggestion.panel.self_repair_stopper_active") : ""}
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
            <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", marginBottom: 6 }}>
              {t("suggestion.panel.patch_proposals")}
            </div>
            <div style={{ fontSize: 11, color: "#475569", marginBottom: 6 }}>
              {t("suggestion.panel.review_summary", {
                unreviewed: reviewSummary.unreviewed,
                reviewed: reviewSummary.reviewed,
              })}
            </div>
            {selectedCandidate ? (
              <div style={{ fontSize: 11, color: "#334155", marginBottom: 6 }}>
                {t("suggestion.panel.selected_label")} <strong>{proposalCandidateLabel(selectedCandidate)}</strong>{" "}
                {proposalCandidateState(selectedCandidate)}
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
              {candidates.length === 0 ? <option value="">{t("suggestion.panel.no_proposals")}</option> : null}
              {candidates.map((candidate) => (
                <option key={candidate.proposalId} value={candidate.proposalId}>
                  {proposalCandidateLabel(candidate)} {proposalCandidateState(candidate)}
                </option>
              ))}
            </select>
            <div style={{ fontSize: 11, color: "#64748b" }}>
              {t("suggestion.panel.reversible_synthesis_hint")}
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
        {t("suggestion.panel.safety_conditions", {
          conditions: ce2State.blockers.map(proposalConditionLabel).join(" / "),
        })}
      </div>
      {errorMessage ? <div style={{ fontSize: 12, color: "#b91c1c" }}>{errorMessage}</div> : null}
    </section>
  );
}
