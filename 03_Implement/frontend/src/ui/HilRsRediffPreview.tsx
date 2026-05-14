import type { HilRsRediffPayload } from "../domain/hil_rs_contract";
import { t } from "../i18n/translate";

type HilRsRediffPreviewProps = {
  payload: HilRsRediffPayload | null;
  onApplyProposal?: (payload: HilRsRediffPayload) => void;
  onDiscardProposal?: (proposalId: string) => void;
  requiresHumanReview?: boolean;
};

export function HilRsRediffPreview({ payload, onApplyProposal, onDiscardProposal, requiresHumanReview = true }: HilRsRediffPreviewProps) {
  if (!payload) {
    return <div style={{ fontSize: 12, color: "#64748b" }}>{t("hil_rs_rediff_preview.empty")}</div>;
  }

  return (
    <section
      aria-live="polite"
      style={{ border: "1px dashed #cbd5e1", borderRadius: 6, padding: 8, marginBottom: 8, backgroundColor: "#fff" }}
    >
      <div style={{ fontSize: 12, marginBottom: 4 }}>
        <strong>{t("hil_rs_rediff_preview.proposal")}:</strong> {payload.proposalId}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>{t("hil_rs_rediff_preview.trace")}:</strong> {payload.traceKey}
      </div>
      <div style={{ fontSize: 12, marginBottom: 4 }}>
        <strong>{t("hil_rs_rediff_preview.schema")}:</strong> {payload.schemaVersion}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>{t("hil_rs_rediff_preview.based_on_iteration")}:</strong> {payload.basedOnIteration}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8, color: "#475569" }}>
        <strong>{t("hil_rs_rediff_preview.diff_operations")}:</strong> {payload.diffOps.length}
      </div>
      {requiresHumanReview ? (
        <div style={{ fontSize: 12, marginBottom: 8, color: "#9a3412" }}>
          {t("hil_rs_rediff_preview.human_review_required")}
        </div>
      ) : null}
      {payload.diffOps.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>{t("hil_rs_rediff_preview.no_diff_ops")}</div>
      ) : null}
      <ul style={{ margin: 0, paddingLeft: 16 }}>
        {payload.diffOps.map((op) => (
          <li key={op.opId} style={{ fontSize: 12, color: "#334155" }}>
            {op.opType} / {op.targetRef}
          </li>
        ))}
      </ul>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button type="button" onClick={() => onApplyProposal?.(payload)} disabled={!onApplyProposal}>{t("hil_rs_rediff_preview.apply")}</button>
        <button type="button" onClick={() => onDiscardProposal?.(payload.proposalId)} disabled={!onDiscardProposal}>{t("hil_rs_rediff_preview.discard")}</button>
      </div>
    </section>
  );
}
