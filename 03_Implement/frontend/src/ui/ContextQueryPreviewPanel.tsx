import type { ContextQueryDraft, QueryPreviewState } from "../domain/context/query_preview";

type ContextQueryPreviewPanelProps = {
  draft: ContextQueryDraft;
  previewState: QueryPreviewState;
  latestBundleHash?: string | null;
  excludedReason?: string[];
  onPreviewConfirmedChange: (value: boolean) => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
  isReadOnly?: boolean;
};

export function ContextQueryPreviewPanel({
  draft,
  previewState,
  latestBundleHash,
  excludedReason = [],
  onPreviewConfirmedChange,
  onSubmit,
  isSubmitting = false,
  isReadOnly = false,
}: ContextQueryPreviewPanelProps) {
  const disabled = isReadOnly || isSubmitting;
  const submitBlocked = disabled || !previewState.canSubmit;
  const primaryBlocker = previewState.blockers[0] ?? null;

  const handleSubmit = () => {
    if (submitBlocked) return;
    onSubmit();
  };

  return (
    <section
      data-testid="ce1-query-preview-panel"
      style={{ border: "1px solid #cbd5e1", borderRadius: 10, padding: 12, background: "#f8fafc", display: "grid", gap: 10 }}
    >
      <header style={{ display: "grid", gap: 2 }}>
        <strong style={{ color: "#0f172a" }}>CE1 Query Preview</strong>
        <span style={{ fontSize: 12, color: "#334155" }}>
          ContextQueryを送信する前に、scope/depth/reviewFilter/safeMode/outputModeを確認してください。
        </span>
      </header>

      <div data-testid="ce1-query-preview-summary" style={{ fontSize: 12, color: "#1e293b", display: "grid", gap: 2 }}>
        <span>queryId: {draft.queryId || "(missing)"}</span>
        <span>goal: {draft.goal || "(missing)"}</span>
        <span>scope: {previewState.scope}</span>
        <span>depth: {previewState.depth}</span>
        <span>reviewFilter: {previewState.reviewFilter}</span>
        <span>safeModePolicy: {previewState.safeModePolicy}</span>
        <span>outputMode: {previewState.outputMode}</span>
      </div>

      {previewState.blockers.length > 0 ? (
        <ul data-testid="ce1-query-preview-blockers" style={{ margin: 0, paddingInlineStart: 18, color: "#b91c1c", fontSize: 12 }}>
          {previewState.blockers.map((blocker) => (
            <li key={blocker}>{blocker}</li>
          ))}
        </ul>
      ) : (
        <div data-testid="ce1-query-preview-ready" style={{ color: "#166534", fontSize: 12 }}>
          Query Preview gate passed.
        </div>
      )}

      <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12, color: "#0f172a" }}>
        <input
          type="checkbox"
          data-testid="ce1-query-preview-confirm"
          checked={draft.previewConfirmed}
          onChange={(event) => onPreviewConfirmedChange(event.currentTarget.checked)}
          disabled={disabled}
        />
        I reviewed this ContextQuery and confirm preview before submit.
      </label>

      <button
        data-testid="ce1-query-preview-submit"
        type="button"
        onClick={handleSubmit}
        disabled={submitBlocked}
        aria-disabled={submitBlocked}
        title={primaryBlocker ?? undefined}
      >
        {isSubmitting ? "Submitting..." : "Submit Context Bundle (Mock)"}
      </button>

      {primaryBlocker ? (
        <div data-testid="ce1-query-preview-gate-status" style={{ fontSize: 11, color: "#b91c1c" }}>
          Preview gate block: {primaryBlocker}
        </div>
      ) : null}

      <footer style={{ fontSize: 11, color: "#475569", display: "grid", gap: 2 }}>
        <span>latest bundleHash: {latestBundleHash ?? "(not generated)"}</span>
        <span>excludedReason: {excludedReason.length > 0 ? excludedReason.join(", ") : "(none)"}</span>
      </footer>
    </section>
  );
}
