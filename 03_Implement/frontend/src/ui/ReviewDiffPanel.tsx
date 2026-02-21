import type { DocumentV2 } from "../domain/types";
import type { MergeItem } from "../diff/merge_items";
import type { MergeItemEvaluation } from "../diff/merge_dependencies";

type ReviewDiffPanelProps = {
  comparisonFileName: string | null;
  comparisonDocument: DocumentV2 | null;
  mergeItems: MergeItem[];
  evaluations: MergeItemEvaluation[];
  selectedItemIds: Set<string>;
  autoIncludePrerequisites: boolean;
  onLoadComparisonDocument: () => void;
  onToggleAutoIncludePrerequisites: (enabled: boolean) => void;
  onItemCheckedChange: (itemId: string, checked: boolean) => void;
  onGroupCheckedChange: (group: string, checked: boolean) => void;
  onApplySelected: () => void;
  onUndoLastMerge: () => void;
  canApply: boolean;
  isComputingDiff: boolean;
  onCancelDiff: () => void;
  computeProgressMessage: string | null;
  computeProgressPercent: number;
  isFallbackMode: boolean;
};

const statusStyleByCode = {
  ok: { color: "#166534", border: "#86efac", label: "OK" },
  missing_prerequisites: { color: "#92400e", border: "#fcd34d", label: "Missing prerequisites" },
  conflict: { color: "#991b1b", border: "#fca5a5", label: "Conflicts" },
};

function groupOf(kind: MergeItem["kind"]): string {
  return kind.split(".")[0] ?? kind;
}

export function ReviewDiffPanel({ comparisonFileName, comparisonDocument, mergeItems, evaluations, selectedItemIds, autoIncludePrerequisites, onLoadComparisonDocument, onToggleAutoIncludePrerequisites, onItemCheckedChange, onGroupCheckedChange, onApplySelected, onUndoLastMerge, canApply, isComputingDiff, onCancelDiff, computeProgressMessage, computeProgressPercent, isFallbackMode }: ReviewDiffPanelProps) {
  const evaluationById = new Map(evaluations.map((entry) => [entry.item.id, entry]));
  const groups = [...new Set(mergeItems.map((item) => groupOf(item.kind)))];

  return (
    <section style={{ border: "1px solid #e2e8f0", borderRadius: 8, padding: 12, marginBottom: 12, backgroundColor: "#ffffff" }}>
      <div style={{ fontWeight: 700, marginBottom: 8 }}>Review Diff (Selective Merge)</div>
      <button type="button" onClick={onLoadComparisonDocument} style={{ marginBottom: 8 }}>
        Load comparison document (JSON)
      </button>
      {comparisonFileName ? <div style={{ fontSize: 12, color: "#334155", marginBottom: 6 }}>File: {comparisonFileName}</div> : null}
      {comparisonDocument ? <div style={{ fontSize: 12, color: "#475569", marginBottom: 8 }}>Items: {mergeItems.length}{isComputingDiff ? " · Working..." : ""}{isFallbackMode ? " · Fallback mode" : ""}</div> : null}
      {isFallbackMode ? <span style={{ fontSize: 11, border: "1px solid #f59e0b", color: "#92400e", borderRadius: 999, padding: "1px 6px", marginRight: 8 }}>fallback mode</span> : null}
      {isComputingDiff ? <button type="button" onClick={onCancelDiff}>Cancel</button> : null}
      {isComputingDiff && computeProgressMessage ? <div style={{ fontSize: 12 }}>{computeProgressMessage}</div> : null}
      {isComputingDiff ? <div style={{ marginTop: 4, height: 6, borderRadius: 999, background: "#e2e8f0", overflow: "hidden" }}><div style={{ width: `${Math.max(0, Math.min(100, computeProgressPercent))}%`, height: "100%", background: "#2563eb" }} /></div> : null}

      <label style={{ display: "block", fontSize: 12, marginBottom: 8 }}>
        <input type="checkbox" checked={autoIncludePrerequisites} onChange={(event) => onToggleAutoIncludePrerequisites(event.target.checked)} /> Auto-include prerequisites
      </label>

      {groups.map((group) => {
        const inGroup = mergeItems.filter((item) => groupOf(item.kind) === group);
        return (
          <details key={group} open>
            <summary>
              {group} ({inGroup.length}){" "}
              <button type="button" onClick={() => onGroupCheckedChange(group, true)} style={{ marginLeft: 8 }}>
                Select all
              </button>
              <button type="button" onClick={() => onGroupCheckedChange(group, false)} style={{ marginLeft: 4 }}>
                Select none
              </button>
            </summary>
            <ul style={{ listStyle: "none", paddingLeft: 0, marginTop: 6 }}>
              {inGroup.map((item) => {
                const evaluation = evaluationById.get(item.id);
                const status = statusStyleByCode[evaluation?.status ?? "ok"];
                return (
                  <li key={item.id} style={{ fontSize: 12, marginBottom: 6, border: "1px solid #e2e8f0", borderRadius: 6, padding: 6 }}>
                    <label>
                      <input type="checkbox" checked={selectedItemIds.has(item.id)} onChange={(event) => onItemCheckedChange(item.id, event.target.checked)} /> {item.kind} {item.entityRef.id}
                      {item.field ? `.${item.field}` : ""}
                    </label>
                    <span style={{ marginLeft: 8, border: `1px solid ${status.border}`, color: status.color, borderRadius: 999, padding: "1px 6px" }}>{status.label}</span>
                    {evaluation && evaluation.missingPrerequisites.length > 0 ? (
                      <details style={{ marginTop: 4 }}>
                        <summary>Explain why blocked</summary>
                        <div>Missing: {evaluation.missingPrerequisites.map((entry) => `${entry.kind}:${entry.id}`).join(", ")}</div>
                      </details>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </details>
        );
      })}

      <div style={{ marginTop: 8 }}>
        <button type="button" onClick={onApplySelected} disabled={!canApply}>Apply selected merge</button>
        <button type="button" onClick={onUndoLastMerge} style={{ marginLeft: 8 }}>Revert last merge</button>
      </div>
    </section>
  );
}
