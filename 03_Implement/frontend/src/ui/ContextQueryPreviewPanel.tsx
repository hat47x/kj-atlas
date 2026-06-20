import type { ContextQueryDraft, QueryPreviewState } from "../domain/context/query_preview";
import { t } from "../i18n/translate";

const blockerMessageKeys: Record<string, string> = {
  "queryId is required": "context_query.preview.blocker.query_id_required",
  "goal is required": "context_query.preview.blocker.goal_required",
  "depth must be between 0 and 5": "context_query.preview.blocker.depth_out_of_range",
  "safeMode strict requires reviewFilter=reviewedOnly": "context_query.preview.blocker.reviewed_only_required",
  "previewConfirmed must be true before submit": "context_query.preview.blocker.confirmation_required",
};

const excludedReasonKeys: Record<string, string> = {
  unreviewed_filtered: "context_query.preview.excluded.unreviewed",
};

function localizedValue(category: "scope" | "review_filter" | "safe_mode_policy" | "output_mode", value: string): string {
  return t(`context_query.preview.value.${category}.${value}`);
}

function localizedBlocker(blocker: string): string {
  const key = blockerMessageKeys[blocker];
  return key ? t(key) : blocker;
}

function localizedExcludedReason(reason: string): string {
  const key = excludedReasonKeys[reason];
  return key ? t(key) : reason;
}

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
  const localizedPrimaryBlocker = primaryBlocker ? localizedBlocker(primaryBlocker) : null;

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
        <strong style={{ color: "#0f172a" }}>{t("context_query.preview.title")}</strong>
        <span style={{ fontSize: 12, color: "#334155" }}>
          {t("context_query.preview.description")}
        </span>
      </header>

      <div data-testid="ce1-query-preview-summary" style={{ fontSize: 12, color: "#1e293b", display: "grid", gap: 2 }}>
        <span>{t("context_query.preview.query_id")}: {draft.queryId || t("context_query.preview.missing")}</span>
        <span>{t("context_query.preview.goal")}: {draft.goal || t("context_query.preview.missing")}</span>
        <span>{t("context_query.preview.scope")}: {localizedValue("scope", previewState.scope)}</span>
        <span>{t("context_query.preview.depth")}: {previewState.depth}</span>
        <span>{t("context_query.preview.review_filter")}: {localizedValue("review_filter", previewState.reviewFilter)}</span>
        <span>{t("context_query.preview.safe_mode_policy")}: {localizedValue("safe_mode_policy", previewState.safeModePolicy)}</span>
        <span>{t("context_query.preview.output_mode")}: {localizedValue("output_mode", previewState.outputMode)}</span>
      </div>

      {previewState.blockers.length > 0 ? (
        <ul data-testid="ce1-query-preview-blockers" style={{ margin: 0, paddingInlineStart: 18, color: "#b91c1c", fontSize: 12 }}>
          {previewState.blockers.map((blocker) => (
            <li key={blocker}>{localizedBlocker(blocker)}</li>
          ))}
        </ul>
      ) : (
        <div data-testid="ce1-query-preview-ready" style={{ color: "#166534", fontSize: 12 }}>
          {t("context_query.preview.gate_passed")}
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
        {t("context_query.preview.confirm_label")}
      </label>

      <button
        data-testid="ce1-query-preview-submit"
        type="button"
        onClick={handleSubmit}
        disabled={submitBlocked}
        aria-disabled={submitBlocked}
        title={localizedPrimaryBlocker ?? undefined}
      >
        {isSubmitting ? t("context_query.preview.submitting") : t("context_query.preview.submit")}
      </button>

      {localizedPrimaryBlocker ? (
        <div data-testid="ce1-query-preview-gate-status" style={{ fontSize: 11, color: "#b91c1c" }}>
          {t("context_query.preview.gate_block", { blocker: localizedPrimaryBlocker })}
        </div>
      ) : null}

      <footer style={{ fontSize: 11, color: "#475569", display: "grid", gap: 2 }}>
        <span>{t("context_query.preview.latest_bundle_hash")}: {latestBundleHash ?? t("context_query.preview.not_generated")}</span>
        <span>
          {t("context_query.preview.excluded_reason")}:{" "}
          {excludedReason.length > 0 ? excludedReason.map(localizedExcludedReason).join(", ") : t("context_query.preview.none")}
        </span>
      </footer>
    </section>
  );
}
