import type { HilRsRediffPayload } from "../domain/hil_rs_contract";

type HilRsRediffPreviewProps = {
  payload: HilRsRediffPayload | null;
  onApplyProposal?: (payload: HilRsRediffPayload) => void;
  onDiscardProposal?: (proposalId: string) => void;
  requiresHumanReview?: boolean;
};

export function HilRsRediffPreview({ payload, onApplyProposal, onDiscardProposal, requiresHumanReview = true }: HilRsRediffPreviewProps) {
  if (!payload) {
    return <div style={{ fontSize: 12, color: "#64748b" }}>No mock re-proposal diff yet.</div>;
  }

  return (
    <section
      aria-live="polite"
      style={{ border: "1px dashed #cbd5e1", borderRadius: 6, padding: 8, marginBottom: 8, backgroundColor: "#fff" }}
    >
      <div style={{ fontSize: 12, marginBottom: 4 }}>
        <strong>Proposal:</strong> {payload.proposalId}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>Trace:</strong> {payload.traceKey}
      </div>
      <div style={{ fontSize: 12, marginBottom: 4 }}>
        <strong>Schema:</strong> {payload.schemaVersion}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>Based on iteration:</strong> {payload.basedOnIteration}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8, color: "#475569" }}>
        <strong>Diff operations:</strong> {payload.diffOps.length}
      </div>
      {requiresHumanReview ? (
        <div style={{ fontSize: 12, marginBottom: 8, color: "#9a3412" }}>
          Human approval required. Proposal remains unreviewed until explicitly applied.
        </div>
      ) : null}
      {payload.diffOps.length === 0 ? (
        <div style={{ fontSize: 12, color: "#64748b" }}>No diff operations returned for this proposal.</div>
      ) : null}
      <ul style={{ margin: 0, paddingLeft: 16 }}>
        {payload.diffOps.map((op) => (
          <li key={op.opId} style={{ fontSize: 12, color: "#334155" }}>
            {op.opType} / {op.targetRef}
          </li>
        ))}
      </ul>
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button type="button" onClick={() => onApplyProposal?.(payload)} disabled={!onApplyProposal}>Apply proposal</button>
        <button type="button" onClick={() => onDiscardProposal?.(payload.proposalId)} disabled={!onDiscardProposal}>Discard proposal</button>
      </div>
    </section>
  );
}
