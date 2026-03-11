import type { HilRsRediffPayload } from "../domain/hil_rs_contract";

type HilRsRediffPreviewProps = {
  payload: HilRsRediffPayload | null;
};

export function HilRsRediffPreview({ payload }: HilRsRediffPreviewProps) {
  if (!payload) {
    return <div style={{ fontSize: 12, color: "#64748b" }}>No mock re-proposal diff yet.</div>;
  }

  return (
    <section style={{ border: "1px dashed #cbd5e1", borderRadius: 6, padding: 8, marginBottom: 8, backgroundColor: "#fff" }}>
      <div style={{ fontSize: 12, marginBottom: 4 }}>
        <strong>Proposal:</strong> {payload.proposalId}
      </div>
      <div style={{ fontSize: 12, marginBottom: 8 }}>
        <strong>Trace:</strong> {payload.traceKey}
      </div>
      <ul style={{ margin: 0, paddingLeft: 16 }}>
        {payload.diffOps.map((op) => (
          <li key={op.opId} style={{ fontSize: 12, color: "#334155" }}>
            {op.opType} / {op.targetRef}
          </li>
        ))}
      </ul>
    </section>
  );
}
